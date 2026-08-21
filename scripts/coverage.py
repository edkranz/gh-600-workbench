#!/usr/bin/env python3
"""Report objectives and units with no question, for every certification."""
import glob, json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
SKIP = ("-introduction", "-summary", "1-introduction", "introduction")
fail = False

for cert in json.load(open(os.path.join(D, "certs.json"))):
    cid = cert["id"]
    base = os.path.join(D, "certs", cid)
    if not os.path.exists(os.path.join(base, "objectives.json")):
        continue
    obj = json.load(open(os.path.join(base, "objectives.json")))
    mods = json.load(open(os.path.join(base, "modules.json")))
    qs = []
    for f in sorted(glob.glob(os.path.join(base, "questions.*.json"))):
        qs += json.load(open(f))

    all_obj = {o["id"]: (d["id"], o["text"])
               for d in obj["domains"] for g in d["groups"] for o in g["objectives"]}
    units = {u["id"]: u for m in mods for u in m["units"]}
    content = {uid for uid, u in units.items()
               if u["kind"] != "knowledge-check" and not uid.endswith(SKIP)}

    by_obj, by_unit = Counter(q["objective"] for q in qs), Counter(q["unit"] for q in qs)
    print(f"\n{'='*70}\n{cert['code']} — {cert['name']}: {len(qs)} questions")
    print("  by source:", dict(Counter(q["source"] for q in qs)))
    print("  by domain:", {d["id"]: sum(1 for q in qs if q["domain"] == d["id"]) for d in obj["domains"]})

    bad = [q["id"] for q in qs if q["objective"] not in all_obj or q["unit"] not in units]
    miss_o = sorted(k for k in all_obj if not by_obj.get(k))
    thin_o = sorted(k for k in all_obj if by_obj.get(k) == 1)
    miss_u = sorted(u for u in content if not by_unit.get(u))

    if bad:
        print(f"  !! DANGLING REFS: {bad}"); fail = True
    print(f"  objectives with no question ({len(miss_o)}/{len(all_obj)}): {miss_o or 'none'}")
    print(f"  objectives with only one   ({len(thin_o)}): {thin_o or 'none'}")
    print(f"  content units with none    ({len(miss_u)}/{len(content)}): {miss_u or 'none'}")
    dupes = [i for i, n in Counter(q["id"] for q in qs).items() if n > 1]
    if dupes:
        print(f"  !! DUPLICATE IDS: {dupes}"); fail = True

sys.exit(1 if fail else 0)
