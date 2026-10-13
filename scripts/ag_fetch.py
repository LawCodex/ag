#!/usr/bin/env python3
"""Fetch the Laws of Antigua and Barbuda from laws.gov.ag (Ministry of Legal
Affairs).

Index pages used:
  * /caps/?variable=Volume%20N  (N=1..9): Revised Edition 1992 chapters,
    with later principal Acts slotted in as chapters (e.g. Cap. 25A);
  * /laws/alphabetical/?letter=X: every current Act (chapters + annual Acts,
    including amending Acts). Repealed laws are listed on a separate page and
    are not fetched.
PDFs are cached in _raw/ag/pdf/. robots.txt has no Crawl-delay; we wait
1.5 s between requests anyway.
Usage: ag_fetch.py
"""
import json
import os
import re
import string
import subprocess
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

BASE = "https://laws.gov.ag/"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "ag"))
DELAY = 1.5
s = requests.Session()
s.headers["User-Agent"] = UA


def get(url):
    for i in range(5):
        try:
            r = s.get(url, timeout=300)
            if r.status_code in (200, 404, 403, 410):
                return r
        except requests.RequestException as e:
            print("  retry", url, e, file=sys.stderr)
        time.sleep(5 * (i + 1))
    raise RuntimeError("failed " + url)


class _Failed:
    status_code = 0
    content = b""
    headers = {}


FAILED = _Failed()


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    if head != b"%PDF-" or b"%%EOF" not in tail:
        return False
    return subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def rows(html):
    soup = BeautifulSoup(html, "lxml")
    out = []
    for tr in soup.find_all("tr"):
        a = tr.find("a", href=re.compile(r"\.pdf$", re.I))
        if not a:
            continue
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        out.append({"title": a.get_text(" ", strip=True), "url": a["href"].strip(), "cells": tds})
    return out


def build_index():
    ip = os.path.join(RAW, "index.json")
    if os.path.exists(ip):
        return json.load(open(ip))
    caps, acts = [], []
    for v in range(1, 10):
        url = BASE + "caps/?variable=" + urllib.parse.quote("Volume %d" % v)
        for r in rows(get(url).text):
            r["volume"] = v
            r["cap"] = r["cells"][0].replace("Cap.", "").strip() if r["cells"] else ""
            r["year"] = r["cells"][-1] if r["cells"] else ""
            caps.append(r)
        time.sleep(DELAY)
    for L in string.ascii_uppercase:
        url = BASE + "laws/alphabetical/?letter=" + L
        for r in rows(get(url).text):
            r["year"] = r["cells"][-1] if r["cells"] else ""
            acts.append(r)
        time.sleep(DELAY)
    idx = {"caps": caps, "acts": acts}
    json.dump(idx, open(ip, "w"), indent=1)
    return idx


def fname(url):
    fn = urllib.parse.unquote(url.split("/")[-1])
    ym = re.search(r"/uploads/(\d{4})/(\d{2})/", url)
    pre = (ym.group(1) + ym.group(2) + "-") if ym else ""
    return pre + re.sub(r"[^A-Za-z0-9._-]", "_", fn)


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    idx = build_index()
    urls = []
    for r in idx["caps"] + idx["acts"]:
        if r["url"] not in urls:
            urls.append(r["url"])
    print(len(idx["caps"]), "caps,", len(idx["acts"]), "alphabetical,", len(urls), "unique PDFs", flush=True)
    bad = []
    for n, u in enumerate(urls):
        p = os.path.join(RAW, "pdf", fname(u))
        if pdf_ok(p):
            continue
        ok = False
        for attempt in range(3):
            try:
                r = get(u)
            except RuntimeError as e:
                print('  giving up', e, flush=True)
                r = FAILED
            if r.status_code == 200 and r.content[:5] == b"%PDF-":
                cl = r.headers.get("content-length")
                if not cl or int(cl) == len(r.content):
                    open(p, "wb").write(r.content)
                    if pdf_ok(p):
                        ok = True
                        break
            elif r.status_code != 200:
                break
            time.sleep(DELAY * 2)
        if not ok:
            bad.append({"url": u, "status": r.status_code})
        print(n, fname(u), ok, r.status_code, flush=True)
        time.sleep(DELAY)
    json.dump(bad, open(os.path.join(RAW, "failed.json"), "w"), indent=1)
    print("failed:", len(bad))


if __name__ == "__main__":
    main()
