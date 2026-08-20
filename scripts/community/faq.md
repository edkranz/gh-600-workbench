# GH-600: GitHub Certified Agentic AI Developer – Comprehensive FAQ Reference

## 1. Exam Overview and Domain Weighting
This FAQ reference is grounded in the GH-600 certification standards, focusing on the professional requirements for building, supervising, and governing AI agents within the GitHub ecosystem. It provides a structured breakdown of the competencies required to integrate agents into the Software Development Lifecycle (SDLC) using GitHub as both the system of record and the primary control plane.

| Exam Domain | Weighting |
| :--- | :--- |
| Domain 1: Prepare Agent Architecture & SDLC Processes | 15–20% |
| Domain 2: Implement Tool Use & Environment Interaction | 20–25% |
| Domain 3: Manage Memory, State & Execution | 10–15% |
| Domain 4: Evaluation, Error Analysis & Tuning | 15–20% |
| Domain 5: Orchestrate Multi-Agent Coordination | 15–20% |
| Domain 6: Guardrails & Accountability | 10–15% |

---

## 2. Domain 1: Prepare Agent Architecture & SDLC Processes (15–20%)

**Q: What is the fundamental difference between an AI assistant and an AI agent in a GitHub context?**
**A:** An assistant is reactive and suggestion-only; it requires a user to manually apply commands or code. An agent is goal-driven and capable of taking independent action within a repository, such as creating branches, modifying files, and opening pull requests to move work forward through a "Plan-Act-Evaluate" loop.

**Q: How is a "structured plan" defined in the agentic lifecycle?**
**A:** A plan is a reviewable artifact (often in a PR description or a markdown file) that outlines the intended goal, scope, steps, risks, and validation criteria. Architecturally, separating planning from execution ensures intent is validated before irreversible actions occur.

**Q: Why is the pull request considered an "architectural control point" for agents?**
**A:** Pull requests serve as the primary mechanism for governance. They ensure that agent-generated changes are not pushed directly to protected branches but are instead routed through a workflow where required checks, CODEOWNERS reviews, and human approvals are enforced.

**Q: What are the three core components that must be defined for every agent task?**
**A:** 
1. **Inputs:** The context, constraints, and boundaries the agent requires (e.g., issue links, repository scope).
2. **Outputs:** The specific artifacts the agent must produce (e.g., a structured plan and a pull request).
3. **Success Criteria:** Objective signals used to evaluate results (e.g., passing CI checks or resolving a security vulnerability).

**Q: What is the distinction between GitHub as a "system of record" versus a "control plane"?**
**A:** This is a dual role: as a **system of record**, GitHub stores all artifacts and evidence (commits, PR timelines, logs). As a **control plane**, GitHub enforces policy and gates activity. The architectural insight is that the same primitives—such as PRs and rulesets—both record the activity and enforce the policy.

---

## 3. Domain 2: Implement Tool Use & Environment Interaction (20–25%)

**Q: What are the four states of tool enablement for a custom agent?**
**A:** 
*   **All tools enabled: Omit the `tools` key or use `tools: ["*"]`.**
*   **All tools disabled: Use an empty list: `tools: []`.**
*   **Specific tools: Provide a named list of allowed tools (e.g., `tools: ["read", "edit"]`).**
*   **MCP-server-scoped: Prefix tool names with the server name (e.g., `tools: ["github/*"]`).**

**Q: What is the processing order and override hierarchy for Model Context Protocol (MCP) configurations?**
**A:** The processing order is: (1) Out-of-the-box MCP servers (GitHub and Playwright), (2) Custom agent-specific `mcp-servers`, and (3) Repository-level MCP settings. In conflict resolution, the **"Lowest Level Wins"** principle applies: a repository-level configuration overrides an organization-level or enterprise-level configuration of the same name.

**Q: What are the specific limitations of the Agent Firewall?**
**A:** The firewall only applies to processes started by the agent via its **Bash tool** within the GitHub Actions appliance environment. It does **not** cover egress traffic from MCP servers or processes defined in `copilot-setup-steps.yml`, as these operate outside the Bash tool's execution boundary.

**Q: How do "Agents secrets" differ from "GitHub Actions secrets"?**
**A:** They are two separate stores. GitHub Actions secrets are for standard CI/CD and are invisible to Copilot. **Agents secrets and variables** are specifically configured at the organization or repository level for the Copilot cloud agent to use during its sessions.

**Q: What is the purpose of the GitHub remote MCP server?**
**A:** It is a hosted server that exposes GitHub’s internal APIs (such as issues, pull requests, and code search) as tools. This allows custom agents to perform platform-level actions without requiring bespoke API integration code.

---

## 4. Domain 3: Manage Memory, State & Execution (10–15%)

**Q: What is the "28-day rule" regarding agent memory?**
**A:** Any stored fact or preference in Copilot Memory that is not used or validated is automatically deleted after 28 days. This prevents "context drift" caused by the accumulation of stale information.

**Q: What is the difference between repository-level facts and user-level preferences?**
**A:** Repository-level facts (e.g., coding conventions) are available to all users with memory access in that repo. User-level preferences (e.g., personal coding style) are tied to a specific user and are currently exclusive to Copilot Pro/Pro+ plans.

**Q: How does Copilot validate a repository-level memory before using it?**
**A:** Stored facts include **citations** to the code that supports them. Before applying a memory, Copilot validates these citations against the **current branch** to ensure the information is still substantiated by the current codebase.

**Q: How is "context drift" defined in agent execution?**
**A:** Context drift is the divergence between the agent's internal assumptions and the actual state of the repository. It often occurs in long-running sessions or when external changes are made to the code that the agent's memory does not yet reflect.

---

## 5. Domain 4: Evaluation, Error Analysis & Tuning (15–20%)

**Q: What are the six surfaces available for tracking agent sessions?**
**A:** 
1. The **Agents tab** on GitHub.com.
2. **GitHub CLI** (`gh agent-task`).
3. **VS Code** via the GitHub PR extension.
4. **JetBrains IDEs** via the **GitHub Cloud Agent Jobs** button.
5. **Eclipse** via the agents icon.
6. **GitHub Mobile** via the Home tab.

**Q: How can a developer trace a specific commit back to its session log?**
**A:** Every agent-authored commit is signed and includes a link to the corresponding agent session logs directly within the commit message, providing a primary traceability primitive.

**Q: What are the three primary categories of root-cause failures for agents?**
**A:** 
1. **Reasoning:** The agent developed an incorrect plan or misunderstood the goal.
2. **Tool:** The agent used a tool incorrectly or the tool itself failed.
3. **Context:** The agent lacked necessary permissions, encountered stale data (drift), or hit firewall restrictions.

**Q: What is the "Contributor Model" for evaluating agent output?**
**A:** This model dictates that agent work is judged by the same engineering standards as humans. There is a **"No Bypass" rule**: agents are subject to the exact same CODEOWNERS and branch protection rules as any other contributor.

**Q: Which CLI command is the primary tool for real-time observability?**
**A:** Use the command `gh agent-task view --log --follow`. Note that this requires GitHub CLI **v2.80.0+**.

---

## 6. Domain 5: Orchestrate Multi-Agent Coordination (15–20%)

**Q: How does the runtime perform "intent matching" for sub-agents?**
**A:** The runtime analyzes the user's prompt against the `name` and `description` fields defined in each agent's configuration to select the specialist most suited to the task.

**Q: What are the five lifecycle events emitted during sub-agent execution?**
**A:** 
1. `subagent.selected`
2. `subagent.started`
3. `subagent.completed`
4. `subagent.failed`
5. `subagent.deselected`

**Q: What is the role of the `toolCallId` in multi-agent orchestration?**
**A:** The `toolCallId` serves as the join key used to track the start, completion, and failure events of a specific sub-agent invocation within a single execution tree.

**Q: How can a developer prevent an agent from being automatically selected by the runtime?**
**A:** The `infer` property is **RETIRED**. To block the runtime from auto-selecting an agent based on intent matching, you must now use the `disable-model-invocation: true` property.

---

## 7. Domain 6: Guardrails & Accountability (10–15%)

**Q: Who is authorized to trigger the Copilot cloud agent?**
**A:** Only users with **write access** to the repository can trigger the agent. Comments or assignments from users with read-only access are ignored to prevent unauthorized execution.

**Q: What is the "any-yes-routes-up" triage logic for risk-based autonomy?**
**A:** If *any* dimension of a task is identified as high-risk, the task escalates to a tier requiring stricter oversight. Triage is performed across three axes: **operational, security, and compliance**.

**Q: How is accountability maintained when an agent authors code?**
**A:** Accountability is preserved through **co-author attribution**. The agent is the author, but the human initiator is recorded as the co-author. Commits are signed and appear as "Verified."

**Q: What is the role of the `.github-private` repository?**
**A:** This repository hosts organization-level custom agent profiles in the `/agents/` directory, making them available across all repositories in the organization.

**Q: What are the primary defenses against agents executing unreviewed code?**
**A:** The **"Approve and run workflows"** gate ensures Actions do not run on agent PRs until a write-access user manually approves them. Furthermore, agents **cannot** mark their own PRs as "Ready for Review" or approve their own work.

---

## 8. Administrative and Custom Agent Configuration Reference

**Q: What are the size and naming constraints for agent profiles?**
**A:** 
*   **Prompt Limit:** The prompt body in the markdown file cannot exceed 30,000 characters.
*   **Naming Convention:** Agent files must use the `.agent.md` extension.
*   **Characters:** Filenames are restricted to alphanumeric characters (`a-z`, `A-Z`, `0-9`), dots (`.`), hyphens (`-`), and underscores (`_`).

**Q: What are the required fields in an agent profile YAML frontmatter?**
**A:** The **`description`** field is the only mandatory property; it is critical for intent matching.

**Q: Where are custom agents stored?**
**A:** At the repository level, they must be in `.github/agents/`. At the organization level, they are stored in the `agents/` directory of the `.github-private` repository. Naming conflict resolution follows the "Lowest Level Wins" hierarchy (Repo > Org > Enterprise).