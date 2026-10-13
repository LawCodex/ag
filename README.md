# Antigua and Barbuda — LawCodex

Legislation of Antigua and Barbuda as plain Markdown. Part of
[LawCodex](https://github.com/LawCodex).

**Status: full.** The repo covers every chapter and current Act that the official site
publishes with a text layer, about 97% of them.

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | The Antigua and Barbuda Constitution Order 1981 (S.I. 1981 No. 1106; Cap. 23) | 1 |
| `chapters/` | Chapters of the Laws of Antigua and Barbuda, Revised Edition 1992 (Volumes 1–9), with later principal Acts slotted in as chapters (e.g. Cap. 25A). File name `cap-NNN-<slug>.md` | 469 |
| `acts/<year>/` | Every other current Act in the official alphabetical list: annual Acts not consolidated into a chapter, including amending Acts, loan and appropriation Acts. A few items have no year (`acts/undated/`) | 641 |

**Total: 1,111 texts.**

### Source

**Laws of Antigua and Barbuda**, Ministry of Legal Affairs: https://laws.gov.ag/

- "Caps" (by volume, Revised Edition 1992): https://laws.gov.ag/caps/?variable=Volume%201 … 9
- "Alphabetical" (all current Acts): https://laws.gov.ag/laws/alphabetical/?letter=A … Z

Repealed laws (listed separately on the site) are not included. Each file's `source` field is
the official PDF URL.

## Caveats

- Most chapter PDFs are scans of the 1992 Revised Edition with a text layer added by Adobe
  "Paper Capture". The text is that OCR layer, as published. Expect OCR errors such as
  "T H E", "Corning" for "Coming" and broken words. Marginal notes from the printed page are
  interleaved with the section text.
- The chapter PDFs reflect the Revised Edition as published on the site. Amendments made
  after 1992 are generally **not** consolidated into them. The amending Acts are under
  `acts/<year>/`.
- Section headings (`### N.`) are inferred from the numbering and may be missing where the OCR
  garbled a section number.

## What is not covered (gaps)

- **Subsidiary legislation.** The "Caps" volume pages also list the subsidiary legislation
  for each chapter (files `CAP-NNN-…`, uploaded December 2022). They are scanned images
  without a text layer, so they were not converted. The
  site's separate "Sub-Laws" (Volumes 10–15) and "Statutory" (S.R.O.s by year) sections were
  not fetched.
- **Bills** and **repealed laws** are not included.
- These 35 Acts are on the site only as scanned images with no text layer, so they were not
  OCR'd: Accreditation Act 2006; Antigua and Barbuda Sales Tax (Transitional Provision and Consequential Amendments) (Amendment) Act, 2011; Antigua and Barbuda Sales Tax (Transitional Provisions and Consequential Amendment) (Amendment) Act, 2008; Antigua and Barbuda Sales Tax Act, 2006; Antigua and Barbuda Sales Tax Transitional Provision and Consequential (Amendments) Act 2006; Appropriate Act, 2005; Banco de DeSarollo Economico Y Social de Venezuela (Bandes) (Loan) Act, 2006; Civil Aviation (Remotely Piloted Aircraft Systems) (RPAS) Regulations 2019; Companies Amendment Act, 2003; Cooperative Societies Act, 2010; Corporate Management and Trust Service Providers (Amendment) Act, 2010; Defamation Act, 2015; Electronic Crimes (Amendment) Act, 2019; Electronic Transactions Act 2013; Electronic Transfer of Funds Crimes Act; Finance Administration Act, 2006; International Business Corporations (Amendment) Act 2010; International Foundations Act, 2007; Law Revision ( Miscellaneous) (Amendment) Act, 1999; Magistrate’s Code of Procedure (Amendment) Act, 2004; Magistrate’s Court District ‘B’ (Parham, All Saints and Bolans) Order, 2019; Medical Benefits Act, 2010; Money Laundering (Prevention) (Amendment) Act, 2001; Money Laundering (Prevention) (Amendment) Act, 2013; Office of the Director of Audit Act, 2014; Plant Protection Act, 2012; Registered Land Amendment Act, 2007; Representation of the People (Amendment) Act, 2011 No. 12 of 2011; Representation of the People (Validation of Acts and Decisions of the Commissioners) Act, 2013; Resolution of the House of Representatives Ratifying the Constitutive Agreement of the Bank of Aruba, 2019; Securities Act, 2001; Supplementary Appropriation 2014 (Ratification) Act, 2015; Supplementary Appropriation Act, 1996; Supplementary Appropriation Act, 2015; Tax Information Exchange (Miscellaneous Amendments) Act, 2011.

## Format

One Markdown file per law with YAML front matter (`title`, `identifier` (Cap. number),
`type`, `jurisdiction`, `language`, `year`, `status`, `source`, `retrieved`, `volume`).
Text was extracted with `pdftotext` (poppler) and kept as extracted. Running page headers
("LAWS OF ANTIGUA AND BARBUDA", chapter running titles) and page numbers were removed. PART /
CHAPTER / SCHEDULE lines become `##` headings and sections become `### N.` headings.

## Licence / copyright

Official legislative texts of Antigua and Barbuda, published by the Government for free public
access. The site states no terms restricting reuse. This is not an official publication.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils (pdftotext, pdfinfo)
python3 scripts/ag_fetch.py     # index + PDFs into ../_raw/ag (1.5 s between requests)
python3 scripts/ag_convert.py   # Markdown
```

Retrieved: 2026-10-13.
