#!/usr/bin/env python3
"""Inline every certification's data, plus styles and script, into one page."""
import base64, glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D, S = os.path.join(ROOT, "data"), os.path.join(ROOT, "src")

certs = json.load(open(os.path.join(D, "certs.json")))

# teaching diagrams travel as data URIs so the page stays self-contained
assets = {}
for path in glob.glob(os.path.join(ROOT, "assets", "*.webp")):
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    assets["assets/" + os.path.basename(path)] = f"data:image/webp;base64,{b64}"


def load(cert_id, name, default):
    p = os.path.join(D, "certs", cert_id, name)
    return json.load(open(p)) if os.path.exists(p) else default


bundles, summary = {}, []
for c in certs:
    cid = c["id"]
    obj = load(cid, "objectives.json", None)
    if obj is None:
        continue
    modules = load(cid, "modules.json", [])
    for m in modules:
        for u in m["units"]:
            for rel, uri in assets.items():
                u["markdown"] = u["markdown"].replace("(" + rel + ")", "(" + uri + ")")
    questions = []
    for f in sorted(glob.glob(os.path.join(D, "certs", cid, "questions.*.json"))):
        questions += json.load(open(f))
    bundles[cid] = {
        "exam": obj["exam"], "domains": obj["domains"], "modules": modules,
        "questions": questions,
        "flashcards": load(cid, "flashcards.json", []),
        "reference": load(cid, "reference.json", []),
    }
    summary.append(f'  {cid}: {len(modules)} modules / {sum(len(m["units"]) for m in modules)} units, '
                   f'{len(questions)} questions, {len(bundles[cid]["flashcards"])} cards, '
                   f'{len(bundles[cid]["reference"])} refs')

payload = {"certs": certs, "data": bundles}
data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")

html = open(os.path.join(S, "template.html"), encoding="utf-8").read()
html = html.replace("/*__STYLES__*/", open(os.path.join(S, "styles.css"), encoding="utf-8").read())
html = html.replace("/*__APP__*/", open(os.path.join(S, "app.js"), encoding="utf-8").read())
html = html.replace("/*__DATA__*/", data)

dist = os.path.join(ROOT, "docs")   # GitHub Pages serves this folder
os.makedirs(dist, exist_ok=True)
open(os.path.join(dist, "artifact.html"), "w", encoding="utf-8").write(html)

head, _, tail = html.partition('<script type="application/json"')
doc = ('<!doctype html>\n<html lang="en">\n<head>\n'
       '<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       + head.strip() + "\n</head>\n<body>\n"
       + '<script type="application/json" ' + tail.strip()
       + "\n</body>\n</html>\n")
out = os.path.join(dist, "index.html")
open(out, "w", encoding="utf-8").write(doc)

print(f"wrote {out}  ({os.path.getsize(out)/1024:,.0f} KB)")
print("\n".join(summary))
