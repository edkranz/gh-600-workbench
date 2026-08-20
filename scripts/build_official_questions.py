#!/usr/bin/env python3
"""Turn the six official Microsoft Learn knowledge checks into data/questions.official.json.

Correct answers and per-choice rationales come from Learn's own quiz-validation
endpoint, so the wording is verbatim from the module authors.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ["SCRAPE_DIR"]

# (module id, question index) -> (domain, objective, unit that teaches it)
MAP = {
 ("m1", 0): ("d1", "1.1.1", "m1-define-agentic-ai"),
 ("m1", 1): ("d1", "1.3.2", "m1-describe-github-system-record-control-plane"),
 ("m1", 2): ("d1", "1.3.1", "m1-describe-github-system-record-control-plane"),
 ("m1", 3): ("d1", "1.1.2", "m1-identify-risks-traceability"),
 ("m1", 4): ("d1", "1.1.2", "m1-apply-contributor-model-agent-generated-work"),

 ("m2", 0): ("d1", "1.2.4", "m2-pull-request-governance-controls"),
 ("m2", 1): ("d1", "1.3.1", "m2-pull-request-governance-controls"),
 ("m2", 2): ("d1", "1.3.2", "m2-agent-operations-controls"),
 ("m2", 3): ("d1", "1.3.1", "m2-reliable-workflows"),
 ("m2", 4): ("d1", "1.1.2", "m2-plan-reason-execution"),

 ("m3", 0): ("d2", "2.3.1", "m3-execution-context-boundaries"),
 ("m3", 1): ("d2", "2.3.4", "m3-execution-context-boundaries"),
 ("m3", 2): ("d2", "2.1.3", "m3-execution-context-boundaries"),
 ("m3", 3): ("d2", "2.3.5", "m3-agent-execution-limits-protections"),
 ("m3", 4): ("d2", "2.3.3", "m3-interact-github-apis-workflows"),
 ("m3", 5): ("d2", "2.2.1", "m3-mcp-servers-registry-allowlists"),
 ("m3", 6): ("d2", "2.2.4", "m3-mcp-servers-registry-allowlists"),
 ("m3", 7): ("d2", "2.3.6", "m3-agent-execution-limits-protections"),
 ("m3", 8): ("d2", "2.1.3", "m3-execution-context-boundaries"),
 ("m3", 9): ("d2", "2.4.5", "m3-agent-execution-limits-protections"),

 ("m4", 0): ("d3", "3.1.1", "m4-agent-memory-strategies"),
 ("m4", 1): ("d3", "3.2.1", "m4-agent-state-context-drift"),
 ("m4", 2): ("d3", "3.2.3", "m4-agent-state-context-drift"),
 ("m4", 3): ("d4", "4.1.1", "m4-evaluation-signals-quality-gates"),
 ("m4", 4): ("d4", "4.2.1", "m4-agent-failures-behavior-improvement"),
 ("m4", 5): ("d4", "4.3.1", "m4-agent-failures-behavior-improvement"),

 ("m5", 0): ("d5", "5.1.1", "m5-agent-orchestration-github-workflows"),
 ("m5", 1): ("d5", "5.1.2", "m5-execution-isolation-permissions-concurrency"),
 ("m5", 2): ("d5", "5.1.3", "m5-conflict-resolution-github-arbitration"),
 ("m5", 3): ("d5", "5.3.1", "m5-scale-failure-recovery"),
 ("m5", 4): ("d5", "5.3.3", "m5-scale-failure-recovery"),

 ("m6", 0): ("d6", "6.2.3", "m6-define-risk-based-autonomy"),
 ("m6", 1): ("d6", "6.2.4", "m6-enforce-governance-github-controls"),
 ("m6", 2): ("d6", "6.2.3", "m6-control-agent-capabilities"),
 ("m6", 3): ("d6", "6.2.4", "m6-design-human-workflows"),
 ("m6", 4): ("d6", "6.2.2", "m6-enforce-governance-github-controls"),
}

MOD_ID = {
 "learn.github.foundations-agentic-ai": "m1",
 "learn.github.design-agent-architecture-integration": "m2",
 "learn.github.agent-tooling-mcp-execution-environments": "m3",
 "learn.github.memory-state-evaluation": "m4",
 "learn.github.multi-agent-systems-orchestration": "m5",
 "learn.github.governance-guardrails-operations": "m6",
}


def detag(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    s = html.unescape(s)
    s = s.replace("‑", "-")
    return re.sub(r"\s+", " ", s).strip()


def trim_verdict(s):
    """Learn prefixes every rationale with 'Correct!' / 'Incorrect.' - the UI shows
    that separately, so strip it and keep the actual reasoning."""
    return re.sub(r"^(Correct!?|Incorrect\.?)\s*", "", s).strip()


units = json.load(open(os.path.join(SRC, "units_with_answers.json")))
out = []
for uid, rec in units.items():
    if not rec["quiz"]:
        continue
    mid = MOD_ID[rec["module"]]
    for q in rec["quiz"]:
        domain, objective, unit = MAP[(mid, q["index"])]
        opts = []
        for a in q["answers"]:
            why = trim_verdict(detag(a["explanationHtml"]))
            if not why:
                why = ("This is the answer the module teaches."
                       if a["isCorrect"] else
                       "This option does not match what the module teaches.")
            opts.append({"text": a["text"], "correct": bool(a["isCorrect"]), "why": why})
        correct_why = next(o["why"] for o in opts if o["correct"])
        out.append({
            "id": f"off-{mid}-{q['index']+1}",
            "source": "official",
            "sourceLabel": "Microsoft Learn knowledge check",
            "domain": domain,
            "objective": objective,
            "module": mid,
            "unit": unit,
            "type": "multi" if q["multi"] else "single",
            "text": q["text"],
            "options": opts,
            "takeaway": correct_why,
        })

path = os.path.join(ROOT, "data", "questions.official.json")
json.dump(out, open(path, "w"), indent=1)
print(f"wrote {path}: {len(out)} questions")
