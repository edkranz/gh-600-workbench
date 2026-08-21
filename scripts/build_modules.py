#!/usr/bin/env python3
"""Turn scraped Microsoft Learn units into data/certs/<cert>/modules.json.

Usage:  SCRAPE_ROOT=<dir> python3 scripts/build_modules.py <certId>
The scrape dir must hold hierarchy.json and units_with_answers.json.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = sys.argv[1] if len(sys.argv) > 1 else "gh-600"
CFG = json.load(open(os.path.join(ROOT, "scripts", "cert_config.json")))[CERT]
SRC = os.path.join(os.environ["SCRAPE_ROOT"], CFG["scrapeDir"])
KEEP_IMAGES = CFG["keepImages"]


def html_to_md(fragment):
    p = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                       input=fragment.encode(), capture_output=True)
    return p.stdout.decode()


def clean(md):
    def img_sub(m):
        alt, path = m.group(1), m.group(2)
        if path in KEEP_IMAGES.values():
            return m.group(0)                       # already rewritten
        base = path.split("/")[-1].split("#")[0]
        return f"![{alt}]({KEEP_IMAGES[base]})" if base in KEEP_IMAGES else ""
    md = re.sub(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\([^)]+\)", img_sub, md)
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img_sub, md)
    md = re.sub(r"\]\(/en-us/", "](https://learn.microsoft.com/en-us/", md)
    md = re.sub(r"``` lang-(\w+)", lambda m: "```" + m.group(1).lower(), md)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


units = json.load(open(os.path.join(SRC, "units_with_answers.json")))
hier = json.load(open(os.path.join(SRC, "hierarchy.json")))

modules = []
for muid, meta in CFG["moduleMeta"].items():
    mod_slug = muid.split(".")[-1]
    m = {"id": meta["id"], "uid": muid, "slug": mod_slug, "title": meta["title"],
         "domains": meta["domains"],
         "url": f"https://learn.microsoft.com/en-us/training/modules/{mod_slug}/",
         "units": []}
    for u in hier[muid]["units"]:
        rec = units[u["uid"]]
        # unit ids are load-bearing: questions and stored read-progress key on them
        slug = (u["uid"].split(".")[-1] if CFG.get("unitIdSource") == "uid"
                else u["url"].strip("/").split("/")[-1])
        is_kc = bool(rec["quiz"])
        m["units"].append({
            "id": f'{meta["id"]}-{slug}',
            "uid": u["uid"],
            "title": u["title"],
            "url": "https://learn.microsoft.com/en-us" + u["url"],
            "minutes": u.get("durationInMinutes"),
            "kind": "knowledge-check" if is_kc else ("exercise" if "exercise" in slug else "reading"),
            "markdown": clean(rec["markdown"]),
        })
    modules.append(m)

out = os.path.join(ROOT, "data", "certs", CERT, "modules.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(modules, open(out, "w"), indent=1)
print(f"{CERT}: {len(modules)} modules, {sum(len(m['units']) for m in modules)} units, "
      f"{sum(len(u['markdown']) for m in modules for u in m['units']):,} chars -> {out}")
