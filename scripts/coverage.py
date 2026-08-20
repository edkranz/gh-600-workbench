#!/usr/bin/env python3
"""Report objectives and units that have no question pointing at them."""
import glob, json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

obj = json.load(open(os.path.join(D, "objectives.json")))
mods = json.load(open(os.path.join(D, "modules.json")))
qs = []
for f in sorted(glob.glob(os.path.join(D, "questions.*.json"))):
    qs += json.load(open(f))

all_obj = {o["id"]: (d["id"], o["text"])
           for d in obj["domains"] for g in d["groups"] for o in g["objectives"]}
# intro/summary units restate what the other units teach, so they need no question of their own
SKIP = ("-introduction", "-summary")
content_units = {u["id"]: (m["id"], u["title"])
                 for m in mods for u in m["units"]
                 if u["kind"] != "knowledge-check" and not u["id"].endswith(SKIP)}

by_obj = Counter(q["objective"] for q in qs)
by_unit = Counter(q["unit"] for q in qs)
by_domain = Counter(q["domain"] for q in qs)
by_source = Counter(q["source"] for q in qs)

print(f"{len(qs)} questions total")
print("  by source:", dict(by_source))
print("  by domain:", {d["id"]: by_domain.get(d["id"], 0) for d in obj["domains"]})

missing_obj = [(k, v) for k, v in all_obj.items() if by_obj.get(k, 0) == 0]
thin_obj = [(k, by_obj[k]) for k in all_obj if by_obj.get(k, 0) == 1]
missing_unit = [(k, v) for k, v in content_units.items() if by_unit.get(k, 0) == 0]

print(f"\nOBJECTIVES WITH NO QUESTION ({len(missing_obj)}/{len(all_obj)}):")
for k, (d, t) in sorted(missing_obj):
    print(f"  {k} [{d}] {t}")
print(f"\nOBJECTIVES WITH ONLY ONE ({len(thin_obj)}):")
for k, n in sorted(thin_obj):
    print(f"  {k} [{all_obj[k][0]}] {all_obj[k][1]}")
print(f"\nCONTENT UNITS WITH NO QUESTION ({len(missing_unit)}/{len(content_units)}):")
for k, (m, t) in sorted(missing_unit):
    print(f"  {k} - {t}")

ids = [q["id"] for q in qs]
dupes = [i for i, n in Counter(ids).items() if n > 1]
if dupes:
    print("\n!! DUPLICATE IDS:", dupes)
    sys.exit(1)
