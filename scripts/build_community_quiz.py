#!/usr/bin/env python3
"""Convert the community study guide's structured quiz (media/quiz.json) to our schema.

These 15 items already carry a per-option rationale, so they import cleanly. They
reach beyond the Learn modules into GitHub product documentation (Copilot Memory
retention, agent profile files, the cloud agent firewall), which is why several are
tagged 'beyond-modules'.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_URL = "https://github.com/jtur671/gh-600-study-guide/blob/main/media/quiz.json"

# question index (1-based) -> domain, objective, unit, beyond-the-modules?
MAP = {
 1:  ("d1", "1.1.1", "m1-define-agentic-ai", False),
 2:  ("d1", "1.1.1", "m2-agent-responsibilities", False),
 3:  ("d1", "1.2.1", "m2-plan-reason-execution", False),
 4:  ("d2", "2.1.2", "m3-execution-context-boundaries", True),
 5:  ("d2", "2.1.2", "m3-execution-context-boundaries", True),
 6:  ("d3", "3.1.3", "m4-agent-memory-strategies", True),
 7:  ("d2", "2.3.6", "m3-execution-context-boundaries", True),
 8:  ("d2", "2.3.1", "m3-agent-execution-limits-protections", True),
 9:  ("d2", "2.2.4", "m3-mcp-servers-registry-allowlists", False),
 10: ("d6", "6.1.1", "m6-define-risk-based-autonomy", False),
 11: ("d2", "2.3.3", "m3-interact-github-apis-workflows", False),
 12: ("d2", "2.1.3", "m2-agent-operations-controls", True),
 13: ("d3", "3.3.3", "m4-memory-state-continuity", True),
 14: ("d6", "6.2.2", "m1-describe-github-system-record-control-plane", False),
 15: ("d2", "2.4.5", "m3-agent-execution-limits-protections", True),
}


def clean(s):
    """NotebookLM exported with LaTeX-style $...$ inline wrappers; strip them."""
    s = re.sub(r"\$([^$]+)\$", r"\1", s or "")
    return re.sub(r"\s+", " ", s).strip()


raw = json.load(open(os.path.join(HERE, "community_quiz_raw.json")))
out = []
for i, q in enumerate(raw["questions"], 1):
    domain, objective, unit, beyond = MAP[i]
    opts = [{"text": clean(o["text"]), "correct": bool(o["isCorrect"]),
             "why": clean(o.get("rationale", ""))} for o in q["answerOptions"]]
    rec = {
        "id": f"cq-{i}",
        "source": "community-quiz",
        "sourceLabel": "Community question bank (gh-600-study-guide)",
        "sourceUrl": SOURCE_URL,
        "domain": domain,
        "objective": objective,
        "module": unit.split("-")[0],
        "unit": unit,
        "type": "single",
        "text": clean(q["question"]),
        "options": opts,
        "takeaway": next(o["why"] for o in opts if o["correct"]),
    }
    if q.get("hint"):
        rec["hint"] = clean(q["hint"])
    if beyond:
        rec["beyondModules"] = True
    out.append(rec)

path = os.path.join(ROOT, "data", "questions.communityquiz.json")
json.dump(out, open(path, "w"), indent=1)
print(f"wrote {path}: {len(out)} questions")
