#!/usr/bin/env python3
"""Turn the scraped Microsoft Learn units into data/modules.json."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ["SCRAPE_DIR"]

MODULE_ORDER = [
    ("learn.github.foundations-agentic-ai",                 "m1", ["d1"]),
    ("learn.github.design-agent-architecture-integration",  "m2", ["d1"]),
    ("learn.github.agent-tooling-mcp-execution-environments","m3", ["d2"]),
    ("learn.github.memory-state-evaluation",                "m4", ["d3", "d4"]),
    ("learn.github.multi-agent-systems-orchestration",      "m5", ["d5"]),
    ("learn.github.governance-guardrails-operations",       "m6", ["d6"]),
]

# banner images carry no teaching value -> drop; the two diagrams are inlined as local assets
KEEP_IMAGES = {
    "agent-lifecycle-diagram.png": "assets/agent-lifecycle-diagram.webp",
    "assistant-vs-agent-comparison.png": "assets/assistant-vs-agent-comparison.webp",
}

units = json.load(open(os.path.join(SRC, "units_with_answers.json")))
hier = json.load(open(os.path.join(SRC, "hierarchy.json")))


def clean(md):
    # linked-image wrappers: [![alt](img)](img#lightbox)
    def img_sub(m):
        alt, path = m.group(1), m.group(2)
        if path in KEEP_IMAGES.values():
            return m.group(0)          # already rewritten by the wrapper pass
        base = path.split("/")[-1].split("#")[0]
        if base in KEEP_IMAGES:
            return f"![{alt}]({KEEP_IMAGES[base]})"
        return ""
    md = re.sub(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\([^)]+\)", img_sub, md)
    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img_sub, md)
    # relative Learn links -> absolute
    md = re.sub(r"\]\(/en-us/", "](https://learn.microsoft.com/en-us/", md)
    # pandoc emits "lang-YAML" style fences; normalise to plain language names
    md = re.sub(r"``` lang-(\w+)", lambda m: "```" + m.group(1).lower(), md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def slug(uid):
    return uid.split(".")[-1]


modules = []
for muid, mid, domains in MODULE_ORDER:
    meta = hier[muid]
    title = {
        "learn.github.foundations-agentic-ai": "Foundations of Agentic AI in GitHub",
        "learn.github.design-agent-architecture-integration": "Designing Agent Architecture and SDLC Integration",
        "learn.github.agent-tooling-mcp-execution-environments": "Tooling, MCP, and Agent Execution Environments",
        "learn.github.memory-state-evaluation": "Memory, State, and Evaluation",
        "learn.github.multi-agent-systems-orchestration": "Multi-Agent Systems and Orchestration",
        "learn.github.governance-guardrails-operations": "Governance, Guardrails, and Operations",
    }[muid]
    mod_slug = muid.split(".")[-1]
    m = {
        "id": mid,
        "uid": muid,
        "slug": mod_slug,
        "title": title,
        "domains": domains,
        "url": f"https://learn.microsoft.com/en-us/training/modules/{mod_slug}/",
        "units": [],
    }
    for u in meta["units"]:
        rec = units[u["uid"]]
        is_kc = bool(rec["quiz"])
        m["units"].append({
            "id": f'{mid}-{slug(u["uid"])}',
            "uid": u["uid"],
            "title": u["title"],
            "url": "https://learn.microsoft.com/en-us" + u["url"],
            "minutes": u.get("durationInMinutes"),
            "kind": "knowledge-check" if is_kc else ("exercise" if "exercise" in rec["slug"] else "reading"),
            "markdown": clean(rec["markdown"]),
        })
    modules.append(m)

out = os.path.join(ROOT, "data", "modules.json")
json.dump(modules, open(out, "w"), indent=1)
total = sum(len(m["units"]) for m in modules)
chars = sum(len(u["markdown"]) for m in modules for u in m["units"])
print(f"wrote {out}: {len(modules)} modules, {total} units, {chars:,} chars of content")
