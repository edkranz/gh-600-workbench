# GH-600 Flashcards

> One card per skill bullet in the official exam outline. Question = the bullet's testable claim. Answer = the concrete GitHub primitive(s) that satisfy it.
>
> Suggested workflow: cover the **A:** with your hand, read the **Q:**, recall, then reveal. Anything you miss twice goes into `knowledge-gaps.md`.

---

## Domain 1 — Prepare agent architecture & SDLC processes (15–20%)

### 1.1 Integrate agents into the SDLC

**Q1.** What is the conceptual lifecycle every agent task should follow?
**A.** `plan → act → evaluate`. The plan is inspectable, the act is bounded by tools/permissions, and the evaluate step gates the merge.

**Q2.** Name three common agent anti-patterns to mitigate.
**A.** (1) Acting before producing a structured plan; (2) granting blanket repo-wide write access instead of branch-scoped; (3) running without producing inspectable artifacts (PRs, run logs, traces).

**Q3.** What three things must be defined for *every* agent task?
**A.** Inputs (what the agent receives), outputs (what artifacts it must produce — usually a PR), and success criteria (the checks that must pass for the work to be accepted).

### 1.2 Boundaries: planning vs. reasoning vs. action

**Q4.** Why configure planning as a distinct phase from execution?
**A.** A separately produced plan is *inspectable*: a human or another agent can review and approve it before any irreversible action runs. This is the basis of human-in-the-loop without bottlenecking.

**Q5.** What does a "structured plan" output from an agent look like in practice?
**A.** Machine-parseable artifact (markdown checklist, JSON, or a PR description) listing intended steps, files to touch, tools to invoke, and rollback steps — committed as a draft PR, issue comment, or workflow artifact *before* execution begins.

**Q6.** How do you prevent an agent from acting until its plan is approved?
**A.** Gate execution on an external signal — a required reviewer's approval, a "planner" job that uploads the plan as an artifact, then a manually-triggered `workflow_dispatch` or environment approval to start the "act" job.

### 1.3 Observability and control

**Q7.** What are the standard "inspectable artifacts" an agent should produce in GitHub?
**A.** Pull requests, run logs, workflow artifacts (uploaded via `actions/upload-artifact`), check-run outputs, issue comments, and security alerts (code scanning, secret scanning, Dependabot).

**Q8.** How do you raise an agent's autonomy level without losing safety?
**A.** Restrict the *blast radius* (branch scope, allow-listed tools, least-privilege token) rather than restricting the agent's actions case-by-case. Then required checks and CODEOWNERS act as the safety net.

**Q9.** How do you add human intervention *without* slowing delivery?
**A.** Require approval only for irreversible or compliance-sensitive actions (production deploys, external API calls, dependency bumps). Use [environment protection rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) to scope approvals; let routine PRs flow.

---

## Domain 2 — Implement tool use & environment interaction (20–25%) ★ highest weighted ★

### 2.1 Select and configure agent tools

**Q10.** Where do you declare what tools a Copilot custom agent can use?
**A.** In the agent's manifest / configuration — tools are listed explicitly, with permissions (read/write/execute) per tool. The agent cannot invoke tools not on its list.

**Q11.** What's the principle behind agent tool permissions?
**A.** **Least privilege per tool, scoped per task.** Each tool gets the narrowest permission needed; the agent's overall token gets the union, not the maximum.

### 2.2 Configure MCP servers

**Q12.** What does an MCP (Model Context Protocol) server do for an agent?
**A.** Exposes external tools, APIs, or data sources to the agent through a standardized protocol, so the agent can invoke them without bespoke integration code per tool.

**Q13.** How do you add an MCP server as a tool to a Copilot agent?
**A.** Register the server in the agent's MCP configuration (local config file or organization-level setting), declare which of the server's tools the agent may use, and ensure the server appears in the org/enterprise **MCP registry**.

**Q14.** What is the GitHub **remote MCP server** for?
**A.** A hosted MCP server that exposes GitHub's own APIs (issues, PRs, code search, etc.) as MCP tools — letting Copilot custom agents act on the GitHub platform itself without per-action API plumbing.

**Q15.** What does an **MCP allow list** do?
**A.** Restricts which MCP servers an agent (or organization's agents) may connect to. Any server not on the allow list is blocked — the primary defense against supply-chain attacks via untrusted MCP servers.

**Q16.** Where do MCP registries fit in?
**A.** They're the curated catalog of approved MCP servers for the org/enterprise. Agents discover available servers through the registry; admins control the registry to enforce the allow list centrally.

### 2.3 Integrate agents within development environments

**Q17.** How do you scope a Copilot custom agent to a single repository?
**A.** Define the agent in that repo's `.github/` directory (custom instructions / agent config) so it isn't visible at org scope, and/or limit the token used by the agent's workflow to that single repo.

**Q18.** How do you invoke an agent inside a CI workflow?
**A.** Trigger a GitHub Actions workflow on the relevant event (`pull_request`, `issue_comment`, `workflow_dispatch`); a step in that workflow runs the agent (e.g., via Copilot setup steps or a custom action), with the workflow's `GITHUB_TOKEN` providing scoped access.

**Q19.** What does "branch-based scope" mean for an agent?
**A.** The agent can only read/write a specific branch (often a feature branch it creates), enforced by token permissions and branch protection rules on protected branches.

**Q20.** What lets an agent autonomously create branches and PRs?
**A.** A token with `contents: write` and `pull-requests: write` permissions (either a fine-grained PAT, a GitHub App installation token, or a properly scoped `GITHUB_TOKEN`), plus workflow code that invokes the REST/GraphQL endpoints or `gh pr create`.

**Q21.** How does an agent handle environment-specific constraints (network egress, secrets)?
**A.** **Copilot cloud agent firewall** controls outbound network access; **environment secrets and protection rules** gate access to credentials per environment (dev/staging/prod); the agent must operate within those constraints rather than around them.

### 2.4 Safe execution paths and error handling

**Q22.** Where does error handling live in an agent workflow?
**A.** At every boundary: tool-call failure handlers in the agent loop, `continue-on-error` / step-level `if: failure()` in the GitHub Actions wrapping job, and a finalizer step that always uploads logs and posts a comment.

**Q23.** How are retries implemented safely?
**A.** Bounded retry count, exponential backoff, idempotency keys on the underlying operation, and *retry only on transient errors* (network, rate limit) — not on logic errors that would compound damage.

**Q24.** How are rollbacks implemented for agent-authored changes?
**A.** PR-based changes give natural rollback (revert the merge). For runtime changes, use environment promotion patterns: roll back by re-deploying the previous artifact. Agents shouldn't perform direct prod mutations without a versioned, reversible artifact.

**Q25.** What is an "escalation path" for an agent?
**A.** A predefined route to human attention when the agent's confidence is low or it hits an unsafe condition — typically by tagging a CODEOWNER, opening an issue with a `needs-human` label, or pausing in an environment that requires approval.

**Q26.** How do you ensure traceability for agent actions?
**A.** Every agent action runs inside a workflow run with full logs, every artifact (plans, diffs, evaluations) is uploaded as a workflow artifact or PR comment, and every commit is signed/attributed to the agent's identity (bot account or GitHub App).

---

## Domain 3 — Manage memory, state & execution (10–15%)

### 3.1 Memory strategies

**Q27.** When do you use short-term vs. long-term vs. external memory?
**A.** **Short-term** for context within a single task/run (prompt window). **Long-term** for stable facts about the project/team (custom instructions, AGENTS.md, repo-level config). **External** for task-spanning artifacts (issue history, PR comments, knowledge bases accessed via MCP).

**Q28.** What does "scope agent memory to task-relevant information" mean?
**A.** Only inject memory items that the *current task* needs. Avoid loading the entire project context — it dilutes signal, increases cost, and leaks information across task boundaries.

**Q29.** How do you define memory expiration, pruning, and reset rules?
**A.** Expire ephemeral memory at task end; prune long-term memory items that aren't referenced for N runs; reset memory on context change (new branch, new issue) — implemented via the agent's config and/or a memory store TTL.

### 3.2 State persistence and drift

**Q30.** What is a "durable artifact" for agent task progress?
**A.** A persisted, inspectable record — PR description checkboxes, an issue with progress comments, a workflow artifact JSON, or a state file in a tracking branch — that survives a run termination.

**Q31.** How does an agent resume work without repeating steps?
**A.** Read its durable state artifact at the start of every run, skip already-completed steps, and continue from the last incomplete step. Idempotent tools make this safe.

**Q32.** What is "context drift" during extended execution?
**A.** Gradual divergence between the agent's working assumptions and the actual repo/task state — e.g., the agent edits an outdated copy of a file because it's still working from cached context. Detected by re-reading source state at checkpoints and comparing to in-memory state.

### 3.3 Continuity across tools and environments

**Q33.** How do you share agent state across tools and runs?
**A.** A canonical state artifact (issue, PR, dedicated tracking branch, or external store) that every tool reads/writes. No tool keeps private mutable state.

**Q34.** How do you prevent conflicting context?
**A.** Single source of truth (one state artifact), serialized writes (no two agents updating the same state simultaneously), and explicit handoffs between agents.

**Q35.** How do you prevent stale context?
**A.** Re-read the canonical state at the start of each tool invocation, and validate any cached assumption against current repo state before acting on it.

---

## Domain 4 — Evaluation, error analysis & tuning (15–20%)

### 4.1 Success criteria and evaluation signals

**Q36.** How are success criteria specified for an agent task?
**A.** As pass/fail checks against expected outcomes: tests must pass, code scanning must be clean, the PR must meet template requirements, performance metrics must stay within bounds. Encoded as **required status checks**.

**Q37.** Qualitative vs. quantitative evaluation signals — examples of each.
**A.** **Quantitative**: test pass rate, code scanning alerts count, performance delta, coverage delta. **Qualitative**: reviewer comments, custom-rubric LLM-judge scores, adherence to coding conventions.

**Q38.** How do you align evaluation with development intent?
**A.** The eval signals should be the *same signals a human developer would be judged on* — tests, lint, security scans, review comments — not artificial agent-only metrics. This keeps agents accountable to the team's actual quality bar.

**Q39.** What automated scanning tools produce evaluation signals?
**A.** GitHub **code scanning** (CodeQL), **secret scanning**, **Dependabot**, **dependency review action**, and any third-party scanners surfaced as **check runs** or SARIF uploads.

### 4.2 Failure analysis

**Q40.** What artifacts do you inspect to diagnose an agent failure?
**A.** Workflow run **logs**, the agent's structured **plan**, **execution traces** (tool calls in order), final **outputs/diffs**, and any **uploaded artifacts** (intermediate state, evaluations).

**Q41.** Three root-cause categories for agent failures.
**A.** (1) **Reasoning errors** — wrong plan, wrong inference; (2) **Tool misuse** — calling the right tool incorrectly or the wrong tool; (3) **Context/environment issues** — stale context, missing permissions, network/firewall blocks.

### 4.3 Tuning

**Q42.** How do you tune an agent that produces wrong reasoning?
**A.** Revise its **custom instructions** / system prompt, add few-shot examples in the agent config, or constrain its allowed plans via a structured planning schema.

**Q43.** How do you tune memory usage problems?
**A.** Adjust what's loaded into context (scope memory more tightly), shorten or expire stale memory, or move stable facts from prompt-context into long-term memory.

**Q44.** How do you tune tool-usage problems?
**A.** Remove or rename ambiguously named tools, tighten permissions, add tool descriptions/examples to the agent config, or route through an orchestrator agent that picks the tool for sub-agents.

---

## Domain 5 — Orchestrate multi-agent coordination (15–20%)

### 5.1 Operate multi-agent workflows

**Q45.** Common orchestration patterns for coordinating multiple agents.
**A.** **Sequential pipeline** (planner → coder → reviewer), **fan-out/fan-in** (planner splits work to N parallel agents, then merges), **supervisor pattern** (one agent dispatches and reviews others), **debate/critic pattern** (two agents argue, third decides).

**Q46.** How do you isolate agents for parallel execution?
**A.** Each agent works on its own branch (no shared working directory), with non-overlapping file scopes, separate workflow runs, and independent token scopes. Merge conflicts are detected at the PR layer.

**Q47.** How do you detect overlapping code changes between agents?
**A.** Branch-level conflict detection at merge time, file-scope declarations in each agent's plan compared before execution, or a coordination layer (supervisor) that allocates non-overlapping file sets.

**Q48.** Resolving contradictory outputs from multiple agents — approaches.
**A.** A **judge/reconciler agent** with a defined arbitration rule, a **voting** scheme over N agent outputs, or **human-in-the-loop** review when disagreement exceeds a threshold.

### 5.2 Multi-agent observability

**Q49.** What artifacts make multi-agent workflows auditable?
**A.** Per-agent workflow runs with logs, a top-level orchestration record (issue or workflow run) that links every sub-run, decision logs at each handoff, and a final reconciled output artifact.

**Q50.** How do you perform post-hoc analysis of multi-agent behavior?
**A.** Replay traces from logs, compare each agent's plan vs. outcome, look for repeated handoff failures, and use the audit trail to identify which agent introduced the divergence.

### 5.3 Failure detection and recovery

**Q51.** How do you identify a stalled agent execution?
**A.** Workflow timeouts (`timeout-minutes`), heartbeat artifacts the agent updates periodically, and orchestrator checks that flag sub-agents that have produced no progress within a budget.

**Q52.** Recovery patterns for multi-agent failures.
**A.** **Rollback** the entire pipeline (revert orchestrator's branch), **rerun** the failed sub-agent in isolation, **fall back** to a simpler agent or human, and **circuit-break** further automation when failure rates exceed a threshold.

### 5.4 Lifecycle of agents in multi-agent workflows

**Q53.** How do you safely add a new agent to an existing workflow?
**A.** Deploy in shadow mode first (run alongside, compare outputs, no merge authority), gate behind a feature flag, then promote once metrics are equivalent or better.

**Q54.** How do you replace an agent without disrupting active workflows?
**A.** Versioned agent configs, route a percentage of traffic to the new agent (canary), then swap once parity confirmed. In-flight runs complete on the old version.

**Q55.** How do you retire an agent while preserving auditability?
**A.** Archive the agent's config in git history, retain all past workflow runs and artifacts (subject to retention policy), and document the retirement decision in a CHANGELOG or governance doc so the audit trail survives.

---

## Domain 6 — Guardrails & accountability (10–15%)

### 6.1 Autonomy levels

**Q56.** How do you classify agent actions by risk?
**A.** Triage on three axes: **operational risk** (does failure break things?), **security risk** (could it leak or compromise secrets/data?), **compliance risk** (does it touch regulated systems or require auditable change-control?). Highest risk → most human oversight.

**Q57.** How do you "right-size" human intervention?
**A.** Map each action category to an autonomy level: fully autonomous for low-risk (lint fixes, doc updates), approval-gated for medium-risk (logic changes, dependency bumps), human-authored for highest-risk (production deploys, secrets, schema migrations).

### 6.2 Guardrails and human-in-the-loop

**Q58.** What actions require explicit human authorization?
**A.** Irreversible changes (data deletion, schema destructive ops), compliance-sensitive changes, anything touching production secrets, dependency additions, and CI/CD pipeline modifications.

**Q59.** How do you block actions that violate policy?
**A.** **Pre-action policy checks** in the agent (refusal logic), **org-level rulesets** preventing forbidden push patterns, **required workflows** that enforce policy scans, and **CODEOWNERS** on sensitive paths requiring named approvers.

**Q60.** How do you enforce least-privilege execution context?
**A.** Use the smallest-scope token possible (`GITHUB_TOKEN` with minimal `permissions:` block, fine-grained PAT scoped to one repo, or GitHub App installation token per repo), environment-scoped secrets, branch-scoped workflows.

**Q61.** What does "controlled path for irreversible changes" mean?
**A.** Wrap the change in a workflow that requires environment approval, runs only on a specific protected branch, produces an inspectable plan before applying, and emits an immutable audit record.

**Q62.** How do you preserve velocity while still enforcing guardrails?
**A.** Approvals only where they actually reduce risk. Routine, reversible PRs flow through automated checks; high-risk operations get gated. Every approval should buy meaningful safety, not perform compliance theater.

---

## Cross-cutting / "system of record" cards

**Q63.** What does "GitHub as the system of record" mean for an agent?
**A.** All agent activity is anchored in a GitHub primitive — commit, PR, issue, workflow run, artifact, or check — so there's no off-platform state to lose, dispute, or hide. Everything is auditable, attributable, and replayable.

**Q64.** What does "GitHub as the control plane" mean?
**A.** The same GitHub primitives that record activity (branch protection, CODEOWNERS, required checks, environments) also *enforce* policy. Control and observation use the same surface.

**Q65.** Where do custom instructions live for an agent?
**A.** Repository-level: `.github/copilot-instructions.md` (or `AGENTS.md` per repo). Org-level: organization custom instructions. The agent reads these in addition to its task-specific prompt.

**Q66.** What's the "contributor model" for agent-generated work?
**A.** Agents are treated as contributors: they open PRs, get reviewed by humans/CODEOWNERS, follow the same branch protection rules, and their work is judged by the same standards. They don't get a bypass lane.

**Q67.** Copilot **setup steps** — what are they?
**A.** Per-repository configuration steps that prepare the Copilot agent's environment for that codebase (install dependencies, set up tools, configure language servers) so it has the context to be effective on first invocation.
