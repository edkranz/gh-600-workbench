#!/usr/bin/env python3
"""Merge the parsed community mock exam with our per-option annotations."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

parsed = json.load(open(os.path.join(HERE, "mock_parsed.json")))
ann = json.load(open(os.path.join(HERE, "mock_annotations.json")))

SOURCE_URL = "https://github.com/jtur671/gh-600-study-guide/blob/main/mock-exam.md"


def demark(s):
    """The source is markdown; the quiz renderer shows plain text."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!`)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s)
    return s.strip()


out = []
for n in sorted(parsed, key=int):
    q, a = parsed[n], ann[n]
    stem = demark(a.get("stemOverride") or q["stem"])
    correct = set(a["correct"])
    opts = [
        {"text": demark(t), "correct": i in correct, "why": a["why"][i]}
        for i, t in enumerate(q["options"])
    ]
    qtype = a.get("type") or ("multi" if len(correct) > 1 else "single")
    out.append({
        "id": f"mock-{n}",
        "source": "community-mock",
        "sourceLabel": "Community mock exam (gh-600-study-guide)",
        "sourceUrl": SOURCE_URL,
        "domain": a["domain"],
        "objective": a["objective"],
        "module": a["unit"].split("-")[0],
        "unit": a["unit"],
        "type": qtype,
        "text": stem,
        "options": opts,
        "takeaway": q["rationale"],
    })

path = os.path.join(ROOT, "data", "questions.community.json")
json.dump(out, open(path, "w"), indent=1)
print(f"wrote {path}: {len(out)} questions "
      f"({sum(1 for q in out if q['type']=='multi')} multi-select)")
