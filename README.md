# GH-600 Agentic AI Workbench

Study and quiz platform for **GH-600 — GitHub Certified: Agentic AI Developer**.

**▶ [Open the site](https://edkranz.github.io/gh-600-workbench/)**

## What's in it

- **All 52 units** of the two official *Developing in Agentic AI Systems* learning paths, readable in full.
- **204 questions** covering every one of the 65 published exam objectives:
  - 36 official Microsoft Learn knowledge-check questions, with the module authors' own per-option rationales
  - 56 from the community guide [jtur671/gh-600-study-guide](https://github.com/jtur671/gh-600-study-guide)
  - 112 written for this project to cover objectives the other two banks leave untested
- Every answer — right or wrong — explains **each option** and links to the unit that teaches it.
- **Practice exam**: 50 questions weighted to the published domain percentages, 120-minute clock, scaled score against the 700 pass mark, per-domain breakdown.
- 137 flashcards, a searchable index, and the community reference shelf (labs, FAQ, diagrams).

Progress is stored in your browser's local storage. No accounts, no backend.

## Repo layout

| Path | What it is |
|---|---|
| `docs/` | Built site (GitHub Pages serves this) |
| `data/` | Content and question bank as JSON — edit these |
| `src/` | `app.js`, `styles.css`, `template.html` |
| `scripts/` | Build and content-extraction scripts |

## Build

```bash
python3 scripts/build_site.py     # data + src -> docs/index.html
python3 scripts/coverage.py       # check every objective still has questions
```

`scripts/build_modules.py` and `build_official_questions.py` re-scrape Microsoft Learn and need `SCRAPE_DIR` pointing at a working directory; everything else runs from the JSON already in `data/`.

## Caveats

Unofficial and not affiliated with GitHub or Microsoft. No real exam items appear here — the GH-600 is under NDA, and anything sold online as leaked questions is fabricated or stolen. Cross-check against the [official study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600).

Module text and knowledge-check content are © Microsoft/GitHub, reproduced here for personal study.
