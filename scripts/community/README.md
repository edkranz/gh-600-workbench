# GH-600 Study Guide — GitHub Certified: Agentic AI Developer

Free, open study materials for **GH-600 — _Developing in Agentic AI Systems_**, GitHub's
certification for engineers who build, operate, and govern AI agents inside the software
development lifecycle.

> ⚠️ **Unofficial.** This is an independent, community-made study aid — not affiliated with
> or endorsed by GitHub or Microsoft. Always cross-check against the
> [official study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600).

📺 **Companion video series (PromptLab)** — a free 7-video walkthrough, one per exam domain
plus a 20-minute audio overview:

### ▶ [Watch the full GH-600 playlist on YouTube](https://www.youtube.com/playlist?list=PLxgUmxsBhjMhyjJhNM9dxSCdJj2yExS2Y)

---

## The exam at a glance

- **Code:** GH-600 — _Developing in Agentic AI Systems_
- **Status:** Beta through **May 31, 2026**; general availability **July 2026**
- **Format:** ~40–60 questions, 120 minutes (+30 min available if you are not testing in your first language)
- **Passing score:** 700 / 1000
- **Beta discount:** the first 100 candidates get **80% off** with promo code `GH600Flanders` at registration
- ⚠️ The beta is **not available** in Turkey, Pakistan, India, or China — confirm regional availability before registering
- Beta results are scored in **8–12 weeks**; passing the beta earns the same credential as the GA exam

## The six domains

| # | Domain | Weight |
|---|--------|--------|
| 1 | Prepare agent architecture & SDLC processes | 15–20% |
| 2 | Implement tool use & environment interaction | **20–25%** |
| 3 | Manage memory, state & execution | 10–15% |
| 4 | Evaluation, error analysis & tuning | 15–20% |
| 5 | Orchestrate multi-agent coordination | 15–20% |
| 6 | Guardrails & accountability | 10–15% |

Domain 2 is the heaviest slice of the exam — budget study time proportionally, not evenly.

## What's in this repo

| File | What it is |
|------|-----------|
| [`flashcards.md`](flashcards.md) | 67 flashcards, one per skill bullet, grouped by domain |
| [`mock-exam.md`](mock-exam.md) | 41 practice questions in exam style, with a full answer key |
| [`lab-guide.md`](lab-guide.md) | 6 hands-on labs for the tool-use and custom-agent domains |
| [`diagrams.md`](diagrams.md) | 5 Mermaid diagrams of the core concepts |
| `media/gh-600.apkg` | The 67 flashcards as an Anki deck, tagged by exam domain |
| `media/nlm-flashcards.apkg` | A second Anki deck (70 cards) |
| `media/briefing.md`, `study-guide.md`, `faq.md`, `quiz.md` | Condensed study aids |
| `scripts/` | Python helpers (flashcards → Anki deck, mind map → Mermaid) |

## Suggested 4-week study sequence

**Week 1 — Foundations & vocabulary.** Work through the official
[Foundations of Agentic AI in GitHub](https://learn.microsoft.com/en-us/training/modules/foundations-agentic-ai/)
module. Read the [GH-600 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600)
end to end until phrases like _"system of record and control plane"_ are reflexive.
Review the Domain 1 set in `flashcards.md`.

**Week 2 — Tool use & MCP (the 20–25% domain).** Work through
[Tooling, MCP, and Agent Execution Environments](https://learn.microsoft.com/en-us/training/modules/agent-tooling-mcp-execution-environments/).
Do the MCP labs in `lab-guide.md` — spin up a real MCP server, configure an allow list,
test the agent firewall. Review the Domain 2 flashcards.

**Week 3 — Architecture & governance.** Work through
[Designing Agent Architecture and SDLC Integration](https://learn.microsoft.com/en-us/training/modules/design-agent-architecture-integration/).
Do the custom-agent and branch-protection labs in `lab-guide.md`. Review the Domain 1 + 6 flashcards.

**Week 4 — Gap closure & mock exam.** Domains 3–5 have no dedicated free module; read the
official docs: [Copilot memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory) (D3),
the [implementation-planner tutorial](https://docs.github.com/en/copilot/tutorials/customization-library/custom-agents/implementation-planner) (D4),
and the [custom-agents SDK](https://docs.github.com/en/copilot/how-tos/copilot-sdk/use-copilot-sdk/custom-agents) (D5).
Sit `mock-exam.md` under timed conditions, then re-read the source doc for every miss.

## Using the Anki decks

Import `media/gh-600.apkg` (or `nlm-flashcards.apkg`) into [Anki](https://apps.ankiweb.net/).
Cards are tagged `Domain-1` … `Domain-6` so you can study one domain at a time.
To regenerate the deck from `flashcards.md`:

```bash
pip install genanki
python3 scripts/convert_flashcards.py
```

## Official sources

- [GH-600 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/gh-600)
- [Certification landing page](https://learn.microsoft.com/en-us/credentials/certifications/agentic-ai-developer/)
- [Microsoft Reactor deep-dive session (May 28, 2026)](https://developer.microsoft.com/en-us/reactor/events/27225/)
- [Announcement blog](https://techcommunity.microsoft.com/blog/skills-hub-blog/new-github-certified-agentic-ai-developer/4517571)

---

Found this useful? The [video series](https://www.youtube.com/playlist?list=PLxgUmxsBhjMhyjJhNM9dxSCdJj2yExS2Y)
covers each domain in depth. Corrections and pull requests are welcome — and don't buy
"braindump" question packs: the beta is under NDA, so any "leaked questions" online are
either fake or stolen.
