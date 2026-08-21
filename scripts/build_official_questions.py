#!/usr/bin/env python3
"""Build data/certs/<cert>/questions.official.json from scraped knowledge checks.

Correct answers and per-choice rationales come from Learn's own quiz-validation
endpoint, so the wording is the module authors' own.

Usage: SCRAPE_ROOT=<dir> python3 scripts/build_official_questions.py <certId>
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = sys.argv[1] if len(sys.argv) > 1 else "gh-600"
CFG = json.load(open(os.path.join(ROOT, "scripts", "cert_config.json")))[CERT]
SRC = os.path.join(os.environ["SCRAPE_ROOT"], CFG["scrapeDir"])
MOD_ID = {uid: meta["id"] for uid, meta in CFG["moduleMeta"].items()}

# (module id, knowledge-check unit id, question index) -> (domain, objective, teaching unit)
MAP = json.load(open(os.path.join(ROOT, "scripts", f"official_map.{CERT}.json")))


def kc_suffix(uid):
    """Modules with more than one knowledge check need the ids kept apart."""
    tail = uid.split(".")[-1]
    return "" if tail == "knowledge-check" else "-" + tail.rsplit("-", 1)[-1]


def detag(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s or "")).replace("‑", "-")
    return re.sub(r"\s+", " ", s).strip()


def trim_verdict(s):
    return re.sub(r"^(Correct!?|Incorrect\.?|That's correct\.?|That's incorrect\.?)\s*", "", s).strip()


units = json.load(open(os.path.join(SRC, "units_with_answers.json")))
out, missing = [], []
for uid, rec in units.items():
    if not rec["quiz"]:
        continue
    mid = MOD_ID[rec["module"]]
    for q in rec["quiz"]:
        key = f'{uid}#{q["index"]}'
        if key not in MAP:
            missing.append(key + "  " + q["text"][:70]); continue
        domain, objective, unit = MAP[key]
        opts = []
        for a in q["answers"]:
            why = trim_verdict(detag(a["explanationHtml"]))
            if not why:
                why = ("This is the answer the module teaches." if a["isCorrect"]
                       else "This option does not match what the module teaches.")
            opts.append({"text": a["text"], "correct": bool(a["isCorrect"]), "why": why})
        out.append({
            # ids must stay stable across rebuilds: existing progress is keyed on
            # them. Progress is per-cert, so the same id in two certs is harmless.
            "id": f'off-{mid}{kc_suffix(uid)}-{q["index"]+1}',
            "source": "official", "sourceLabel": "Microsoft Learn knowledge check",
            "domain": domain, "objective": objective, "module": mid, "unit": unit,
            "type": "multi" if q["multi"] else "single",
            "text": q["text"], "options": opts,
            "takeaway": next(o["why"] for o in opts if o["correct"]),
        })

if missing:
    print(f"!! {len(missing)} unmapped questions:")
    for m in missing[:40]:
        print("   ", m)
    sys.exit(1)

path = os.path.join(ROOT, "data", "certs", CERT, "questions.official.json")
json.dump(out, open(path, "w"), indent=1)
print(f"{CERT}: {len(out)} official questions -> {path}")
