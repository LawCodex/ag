#!/usr/bin/env python3
"""Convert the PDFs fetched by ag_fetch.py into Markdown.

  chapters/cap-NNN-<slug>.md   Revised Edition chapters (laws.gov.ag "Caps")
  acts/<year>/<slug>.md        other current Acts from the alphabetical list
                               (annual Acts incl. amending Acts)
  constitution/                the Antigua and Barbuda Constitution Order 1981
Subsidiary-legislation scans listed under the volumes are skipped.
PDFs without a text layer (scans) are not OCR'd; they are listed in
_raw/ag/gaps.json.
Usage: ag_convert.py
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ag_pdf2md  # noqa: E402
from ag_fetch import RAW, fname  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TODAY = datetime.date.today().isoformat()


def slug(s, n=80):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", " and ")).strip("-")
    return s[:n].rstrip("-")


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write(path, meta, title, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fm = ["---"]
    for k, v in meta.items():
        if v is None or v == "":
            continue
        fm.append("%s: %s" % (k, yq(v) if isinstance(v, str) and k not in ("type", "jurisdiction", "language", "status", "retrieved", "date") else v))
    fm.append("---")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(fm) + "\n\n# " + title + "\n\n" + body)


def main():
    idx = json.load(open(os.path.join(RAW, "index.json")))
    gaps, done, counts = [], set(), {}
    jobs = []
    for c in idx["caps"]:
        if not c["cap"]:
            continue  # subsidiary-legislation scans listed per volume
        m = re.search(r"/cap-(\d+[a-z]?)(?:-\d)?\.pdf$", c["url"], re.I)
        cap = (m.group(1) if m else c["cap"]).upper().lstrip("0") or "0"
        jobs.append(("chapter", cap, c))
    capurls = {c["url"] for _, _, c in jobs}
    for a in idx["acts"]:
        if a["url"] in capurls:
            continue
        jobs.append(("act", None, a))
    seen_paths = set()
    for kind, cap, it in jobs:
        if it["url"] in done:
            continue
        done.add(it["url"])
        pdf = os.path.join(RAW, "pdf", fname(it["url"]))
        if not os.path.exists(pdf):
            gaps.append({"title": it["title"], "url": it["url"], "reason": "download failed"})
            continue
        pages = ag_pdf2md.pages_of(pdf)
        if ag_pdf2md.is_scan(pages):
            gaps.append({"title": it["title"], "url": it["url"], "reason": "scanned PDF without text layer"})
            continue
        body = ag_pdf2md.convert(pages, drop_lines=[r"^LAWS OF ANTIGUA AND BARBUDA$"])
        title = it["title"].strip()
        is_const = "constitution order" in title.lower()
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", it.get("year", "") or "")
        year = m.group(1) if m else ""
        if is_const:
            path = os.path.join(OUT, "constitution", "antigua-and-barbuda-constitution-order-1981.md")
            ident, typ = "Cap. %s" % cap if cap else "S.I. 1981 No. 1106", "constitution"
        elif kind == "chapter":
            num = re.match(r"(\d+)([A-Z]*)", cap)
            fn = "cap-%03d%s-%s.md" % (int(num.group(1)), num.group(2).lower(), slug(title))
            path = os.path.join(OUT, "chapters", fn)
            ident, typ = "Cap. %s" % cap, "act"
        else:
            path = os.path.join(OUT, "acts", year or "undated", slug(title) + ".md")
            ident, typ = "", "act"
        base = path
        k = 2
        while path in seen_paths:
            path = base[:-3] + "-%d.md" % k
            k += 1
        seen_paths.add(path)
        meta = {"title": title, "identifier": ident, "type": typ, "jurisdiction": "ag", "language": "en",
                "date": year if year and kind == "act" else "", "year": year,
                "status": "in_force", "source": it["url"], "retrieved": TODAY}
        if kind == "chapter":
            meta["volume"] = "Revised Edition 1992, Volume %s" % it.get("volume", "")
        meta.pop("date")
        write(path, meta, title, body)
        cat = "constitution" if is_const else kind
        counts[cat] = counts.get(cat, 0) + 1
    json.dump(gaps, open(os.path.join(RAW, "gaps.json"), "w"), indent=1)
    print(counts, "gaps:", len(gaps))


if __name__ == "__main__":
    main()
