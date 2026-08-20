#!/usr/bin/env python3
"""Build data/flashcards.json and data/reference.json from the community study guide."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(os.path.dirname(os.path.abspath(__file__)), "community")
REPO = "https://github.com/jtur671/gh-600-study-guide"

DOMAIN_BY_NUM = {"1": "d1", "2": "d2", "3": "d3", "4": "d4", "5": "d5", "6": "d6"}

# ---------------------------------------------------------------- flashcards
cards = []
md = open(os.path.join(C, "flashcards.md"), encoding="utf-8").read()
domain, section = None, None
for block in md.split("\n"):
    h2 = re.match(r"^## Domain (\d)", block)
    if h2:
        domain = DOMAIN_BY_NUM[h2.group(1)]
        continue
    if block.startswith("## Cross-cutting"):
        domain = None
        section = "Cross-cutting"
        continue
    h3 = re.match(r"^### (.+)$", block)
    if h3:
        section = h3.group(1).strip()
        continue
    q = re.match(r"^\*\*Q(\d+)\.\*\* (.+)$", block)
    if q:
        cards.append({"id": f"fc-{q.group(1)}", "domain": domain, "section": section,
                      "front": q.group(2).strip(), "back": ""})
        continue
    a = re.match(r"^\*\*A\.\*\* (.+)$", block)
    if a and cards:
        cards[-1]["back"] = a.group(1).strip()

nlm = json.load(open(os.path.join(C, "notebooklm-flashcards.json"), encoding="utf-8"))
for i, c in enumerate(nlm["cards"], 1):
    cards.append({"id": f"nlm-{i}", "domain": None, "section": "Rapid recall",
                  "front": c["front"].strip(), "back": c["back"].strip()})


def demark(s):
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", s)          # links -> text
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\$\\rightarrow\$", "->", s)
    s = re.sub(r"\$([^$]+)\$", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


for c in cards:
    c["front"] = demark(c["front"])
    c["back"] = demark(c["back"])

cards = [c for c in cards if c["front"] and c["back"]]
json.dump(cards, open(os.path.join(ROOT, "data", "flashcards.json"), "w"), indent=1)
print(f"flashcards.json: {len(cards)} cards")

# ----------------------------------------------------------------- reference
DOCS = [
    ("ref-study-guide", "Condensed study guide", "study-guide.md",
     "A single-sitting distillation of the whole syllabus, ending with short-answer practice and a glossary.",
     f"{REPO}/blob/main/media/study-guide.md"),
    ("ref-briefing", "Executive briefing", "briefing.md",
     "The themes an examiner keeps returning to, with the quotable phrasing the modules use.",
     f"{REPO}/blob/main/media/briefing.md"),
    ("ref-faq", "Domain-by-domain FAQ", "faq.md",
     "Direct answers to the questions each domain tends to raise, organised by exam domain.",
     f"{REPO}/blob/main/media/faq.md"),
    ("ref-labs", "Hands-on lab guide", "lab-guide.md",
     "Six practical labs: custom instructions, MCP servers and allow lists, an agent in a workflow, PR governance, the agent firewall, and environment protection.",
     f"{REPO}/blob/main/lab-guide.md"),
    ("ref-diagrams", "Concept diagrams", "diagrams.md",
     "Five Mermaid diagrams of the core mechanisms: the lifecycle loop, risk-tiered autonomy, MCP governance, multi-agent isolation, and the failure-recovery path.",
     f"{REPO}/blob/main/diagrams.md"),
    ("ref-readme", "Study plan and exam logistics", "README.md",
     "The four-week study sequence, domain weightings, and exam logistics from the community guide.",
     f"{REPO}/blob/main/README.md"),
]

refs = []
for rid, title, fname, blurb, url in DOCS:
    body = open(os.path.join(C, fname), encoding="utf-8").read()
    body = re.sub(r"\$\\rightarrow\$", "->", body)
    body = re.sub(r"^# .*\n", "", body, count=1)   # title is rendered by the app
    refs.append({"id": rid, "title": title, "summary": blurb,
                 "source": "Community study guide (jtur671/gh-600-study-guide)",
                 "sourceUrl": url, "markdown": body.strip()})

json.dump(refs, open(os.path.join(ROOT, "data", "reference.json"), "w"), indent=1)
print(f"reference.json: {len(refs)} documents, "
      f"{sum(len(r['markdown']) for r in refs):,} chars")
