# GitHub Cert Tracker

Study and quiz platform for GitHub certifications. Pick a cert, browse the official material, drill the question bank, sit a weighted mock.

**▶ [Open the site](https://edkranz.github.io/gh-600-workbench/)**

## Certifications covered

| | Cert | Units | Questions | Objectives |
|---|---|---|---|---|
| **GH-600** | Agentic AI Developer | 52 | 254 | 65 |
| **GH-100** | GitHub Enterprise Administrator | 69 | 110 | 39 |

GH-100 also links Microsoft's [official free practice assessment](https://learn.microsoft.com/en-us/credentials/certifications/github-administration/practice/assessment?assessment-type=practice&assessmentId=1841205577&practice-assessment-type=certification) — GH-600 has none.

## What's in it

- **Every unit** of the official learning paths, readable in full.
- **Every published objective** covered by at least two questions, drawn from:
  - official Microsoft Learn knowledge checks, with the module authors' own per-option rationales
  - the community guide [jtur671/gh-600-study-guide](https://github.com/jtur671/gh-600-study-guide) (GH-600)
  - an [advanced implementation guide](https://gist.github.com/naim149/a8aa41c7468685b7d984822c38863aae) for exact keys, flags and product behaviour (GH-600)
  - questions written for this project to cover what the other banks leave untested
- Every answer — right or wrong — explains **each option** and links to the unit that teaches it.
- **Practice exam**: 50 questions weighted to the published domain percentages, 120-minute clock, scaled score against the 700 pass mark, per-domain breakdown.
- 137 flashcards, a searchable index, and the community reference shelf (labs, FAQ, diagrams).

Progress is stored in your browser's local storage. No accounts, no backend.

## Repo layout

| Path | What it is |
|---|---|
| `docs/` | Built site (GitHub Pages serves this) |
| `data/certs.json` | Cert registry — add an entry to add a cert |
| `data/certs/<id>/` | Per-cert objectives, modules, questions, reference |
| `src/` | `app.js`, `styles.css`, `template.html` |
| `scripts/` | Build and content-extraction scripts |

## Build

```bash
python3 scripts/build_site.py     # all certs -> docs/index.html
python3 scripts/coverage.py       # every objective still has questions?
```

`build_modules.py` and `build_official_questions.py` rebuild a cert from scraped
Microsoft Learn content: `SCRAPE_ROOT=<dir> python3 scripts/build_modules.py gh-100`.
`scripts/cert_config.json` maps Learn module uids to local ids and domains.
Everything else runs from the JSON already in `data/`.

## Caveats

Unofficial and not affiliated with GitHub or Microsoft. No real exam items appear here — these exams are under NDA, and anything sold online as leaked questions is fabricated or stolen. Cross-check against the official study guides ([GH-600](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600), [GH-100](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-100)).

Module text and knowledge-check content are © Microsoft/GitHub, reproduced here for personal study.
