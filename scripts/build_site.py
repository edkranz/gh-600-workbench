#!/usr/bin/env python3
"""Inline data, styles, and script into a single self-contained dist/index.html."""
import base64, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D, S = os.path.join(ROOT, "data"), os.path.join(ROOT, "src")

obj = json.load(open(os.path.join(D, "objectives.json")))
modules = json.load(open(os.path.join(D, "modules.json")))
questions = []
for f in sorted(glob.glob(os.path.join(D, "questions.*.json"))):
    questions += json.load(open(f))
flashcards = json.load(open(os.path.join(D, "flashcards.json")))
reference = json.load(open(os.path.join(D, "reference.json")))

# the two teaching diagrams travel inside the page as data URIs so it stays
# self-contained (and so a strict CSP cannot blank them out)
assets = {}
for path in glob.glob(os.path.join(ROOT, "assets", "*.webp")):
    name = os.path.basename(path)
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    assets["assets/" + name] = f"data:image/webp;base64,{b64}"

for m in modules:
    for u in m["units"]:
        for rel, uri in assets.items():
            u["markdown"] = u["markdown"].replace("(" + rel + ")", "(" + uri + ")")

payload = {
    "exam": obj["exam"],
    "domains": obj["domains"],
    "modules": modules,
    "questions": questions,
    "flashcards": flashcards,
    "reference": reference,
}

data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
# a literal </script> anywhere in the JSON would close the host tag early
data = data.replace("</", "<\\/")

html = open(os.path.join(S, "template.html"), encoding="utf-8").read()
html = html.replace("/*__STYLES__*/", open(os.path.join(S, "styles.css"), encoding="utf-8").read())
html = html.replace("/*__APP__*/", open(os.path.join(S, "app.js"), encoding="utf-8").read())
html = html.replace("/*__DATA__*/", data)

dist = os.path.join(ROOT, "docs")   # GitHub Pages serves this folder
os.makedirs(dist, exist_ok=True)

# artifact.html is the bare fragment the Artifact host wraps in its own skeleton
frag_path = os.path.join(dist, "artifact.html")
open(frag_path, "w", encoding="utf-8").write(html)

# index.html is a valid standalone document for opening straight off disk
head, _, tail = html.partition('<script type="application/json"')
doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n"
       "<meta charset=\"utf-8\">\n"
       "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
       + head.strip() + "\n</head>\n<body>\n"
       + '<script type="application/json" ' + tail.strip()
       + "\n</body>\n</html>\n")
out = os.path.join(dist, "index.html")
open(out, "w", encoding="utf-8").write(doc)

kb = os.path.getsize(out) / 1024
print(f"wrote {out} and {frag_path}  ({kb:,.0f} KB)")
print(f"  {len(modules)} modules / {sum(len(m['units']) for m in modules)} units")
print(f"  {len(questions)} questions, {len(flashcards)} flashcards, {len(reference)} reference docs")
