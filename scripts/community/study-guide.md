# GH-600 Study Guide: Developing in Agentic AI Systems

This study guide provides a comprehensive synthesis of the GH-600 "GitHub Certified: Agentic AI Developer" certification requirements. It covers agent architecture, Model Context Protocol (MCP), GitHub governance, and safe execution patterns within the software development lifecycle (SDLC).

---

## Part 1: Core Concepts of Agentic AI

### Defining Agents vs. Assistants
The shift from AI assistants to AI agents marks a transition from reactive suggestion-based tools to goal-driven systems capable of autonomous execution.

| Feature | AI Assistant | AI Agent |
| :--- | :--- | :--- |
| **Primary Behavior** | Reactive: responds to prompts with suggestions or explanations. | Goal-driven: interprets high-level goals and decides on intermediate steps. |
| **Action Capability** | Suggestion-only: requires the user to manually apply changes. | Tool-use: creates durable artifacts (branches, commits, pull requests). |
| **Control** | User maintains constant control over next steps. | Agent independently moves work forward inside a repository. |
| **Feedback Loop** | Linear interaction. | Iterative: refines approach based on CI signals, security scans, and reviews. |

### The Agent Lifecycle: Plan → Act → Evaluate
Reliable agent systems follow a continuous loop rather than a linear sequence:

1.  **Plan:** The agent interprets a goal and creates a structured, reviewable description of intended changes. High-quality plans include scope, success criteria, and escalation paths.
2.  **Act:** The agent executes the plan by performing repository actions, such as creating branches, modifying files, and opening pull requests.
3.  **Evaluate:** The system (and humans) uses objective signals—workflow results, security alerts, and human reviews—to judge the outcome. If the evaluation fails, the cycle repeats (Plan again → Act again).

---

## Part 2: GitHub as the System of Record and Control Plane

GitHub provides the infrastructure to both record what an agent does and enforce policy on those actions.

### Mapping Agent Responsibilities to the SDLC
Mapping agent work to specific SDLC stages allows for enforceable boundaries and improved auditability.

| SDLC Stage | Typical Agent Responsibility | Primary GitHub Artifact |
| :--- | :--- | :--- |
| **Planning** | Drafting scope, step-by-step plans, and success criteria. | Issues, PR descriptions, Agents tab. |
| **Implementation** | Creating branches, making file changes, and opening PRs. | Branches, Commits, Pull Requests. |
| **Validation** | Running tests, attaching artifacts, and iterating on failures. | Workflow runs, status checks, uploaded artifacts. |
| **Deployment** | (Usually restricted) Preparing environments for human approval. | Environments, Deployment approvals. |

### Governance Primitives
*   **Pull Requests (PRs):** The central architectural control point. Work is proposed and discussed here before merging.
*   **CODEOWNERS:** Automatically routes reviews to specific experts for sensitive file paths (e.g., infrastructure or workflows).
*   **Required Status Checks:** Converts "evaluation" into enforceable policy; the PR cannot be merged unless CI passes.
*   **Rulesets/Branch Protection:** Prevents direct pushes to default branches and enforces consistent guardrails.
*   **Environments:** Gated control points that pause execution for secrets access or production deployments until a human approves.

---

## Part 3: Custom Agents and Tooling

### Custom Agent Configuration
Custom agents are defined via **agent profiles**—Markdown files with YAML frontmatter.

*   **Location:** 
    *   **Repository-level:** `.github/agents/NAME.agent.md`
    *   **Organization-level:** `/agents/NAME.md` within a `.github-private` repository.
*   **Key YAML Properties:**
    *   `description` (Required): Explains the agent's purpose.
    *   `tools`: A list of allowed tools (e.g., `read`, `edit`, `search`). If omitted, all tools are enabled.
    *   `disable-model-invocation`: Set to `true` to block the runtime from auto-selecting the agent.
    *   `user-invocable`: Set to `false` for programmatic-only agents.
*   **Prompt Body:** Markdown instructions below the YAML frontmatter, limited to **30,000 characters**.

### Model Context Protocol (MCP)
MCP is a standardized protocol allowing agents to connect to external tools and services.

1.  **MCP Servers:** Expose specific tools (e.g., the GitHub MCP server exposes repository APIs).
2.  **MCP Registries:** Centralized catalogs of approved servers for an organization.
3.  **MCP Allow Lists:** Security policies that restrict which servers an agent is permitted to connect to.

---

## Part 4: Managing State, Memory, and Orchestration

### Memory Strategies
Copilot Memory allows the agent to build understanding over time, reducing prompt overhead.

*   **Repository-level Facts:** Project-specific rules, conventions, and architectural decisions. Created by users with write access and stored with code citations.
*   **User-level Preferences:** Personal interaction styles (available on Pro/Pro+ plans).
*   **28-Day Expiry:** Stored facts or preferences are automatically deleted if unused for 28 days; the timer resets upon successful use.
*   **Validation:** Copilot re-validates citations against current code before using a stored memory to prevent acting on stale data.

### Multi-Agent Orchestration (Copilot SDK)
Agents can act as "parent" sessions that delegate sub-tasks to specialized "sub-agents."

*   **Sub-agent Events:** The parent session tracks sub-agent status through five lifecycle events: `selected`, `started`, `completed`, `failed`, and `deselected`.
*   **Intent Matching:** The runtime selects a sub-agent based on its `name` and `description`.
*   **toolCallId:** The unique identifier used to join events across a sub-agent's execution tree.

---

## Part 5: Guardrails, Risk, and Accountability

### Security Mitigations
GitHub applies built-in mitigations for agentic risks:

*   **Unvalidated Code:** Agents use **CodeQL** (security issues), the **GitHub Advisory Database** (vulnerable dependencies), and **Secret Scanning** to validate their own output before finishing a PR.
*   **Execution Isolation:** Agents push to a single `copilot/` branch or the existing PR branch; they cannot push directly to default branches.
*   **Approval Gates:** Workflows on agent-authored PRs are blocked by default until a user with write access clicks "Approve and run workflows."
*   **The Contributor Model:** Agents are treated as standard contributors. Their work is evaluated by the same engineering standards as humans (scope, checks, reviews, policy).

### The Agent Firewall
Controls network egress from the agent environment to prevent data exfiltration.

*   **Scope:** Applies only to processes started via the **Bash tool**. It does **not** cover MCP servers or `copilot-setup-steps.yml`.
*   **Rule Types:** 
    *   **Domain:** Allows domain and all subdomains.
    *   **URL:** Restricted to specific scheme, host, and path-prefix.
*   **Visibility:** If a request is blocked, a warning is posted to the PR body or as a comment.

---

## Part 6: Short-Answer Practice Quiz

1.  **What is the "Plan-first" pull request pattern, and when should it be used?**
    *   *Answer:* A workflow where the agent opens a PR containing only a structured plan for approval before writing any code. It should be used for high-risk changes (e.g., infrastructure or security-sensitive areas) where alignment on intent is critical.
2.  **How does the `CODEOWNERS` file improve agent safety?**
    *   *Answer:* It ensures that changes to sensitive file paths are automatically routed to the correct human experts for review, preventing agents from modifying critical files without specialized oversight.
3.  **What is the difference between "GitHub Actions secrets" and "Agents secrets"?**
    *   *Answer:* GitHub Actions secrets are protected and inaccessible to Copilot. Agents secrets are specifically configured at the org or repo level to be readable by Copilot cloud agent for provisioning tasks.
4.  **How are agent commits identified for audit purposes?**
    *   *Answer:* Commits are authored by "Copilot" with the human requester as a co-author. They are signed and appear as "Verified" on GitHub, often containing a link to the session logs in the commit message.
5.  **Which MCP component is used to prevent supply-chain attacks from untrusted servers?**
    *   *Answer:* The MCP Allow List (often combined with a Registry) which restricts server connections to only those approved by organization administrators.

---

## Part 7: Essay Questions for Deeper Exploration

1.  **The "System of Record" vs. "Control Plane":** Explain how GitHub's dual role as both a system of record and a control plane creates a "trust but verify" environment for agentic AI. How do these roles interact when an agent attempts a high-risk production deployment?
2.  **The Impact of State and Memory on Reliability:** Discuss the risks of "context drift" in long-running agent sessions. How does Copilot Memory’s 28-day expiration and citation validation mechanism address the challenges of maintaining a "stateless" vs. "stateful" architecture?
3.  **Risk-Based Autonomy:** Propose a tiered autonomy model for a large enterprise. For which file paths would you allow "automerge," and for which would you require environment approvals and multiple human reviews? Justify your choices using the "blast radius" concept.

---

## Part 8: Comprehensive Glossary

*   **Agent Profile:** A Markdown file (YAML + instructions) used to define the behavior, tools, and identity of a custom agent.
*   **Blast Radius:** The potential extent of impact or damage if an agent action fails or is malicious; minimized via least-privilege permissions and branch isolation.
*   **Context Drift:** A divergence between the agent's internal reasoning/memory and the actual state of the repository, often caused by stale or cached information.
*   **Copilot Setup Steps:** A file (`copilot-setup-steps.yml`) used to prepare the agent's environment, such as installing dependencies or setting up tools.
*   **Durable Artifact:** A persisted record of progress (e.g., a PR checklist or workflow artifact) that allows an agent to resume work after a failure or interruption.
*   **Escalation Path:** A predefined procedure for an agent to hand off a task to a human when it encounters uncertainty, errors, or low confidence.
*   **GITHUB_TOKEN:** A temporary security token used in workflows; best practice dictates setting this to "read-only" by default to enforce least privilege.
*   **MCP (Model Context Protocol):** An open standard that enables agents to interact with external tools and APIs through a consistent interface.
*   **Plan (Artifact):** A structured description in a PR or issue outlining the goal, steps, risks, and validation criteria for an agent's intended work.
*   **Prompt Injection:** A security risk where malicious user input (like hidden HTML comments) attempts to override the agent's system instructions.
*   **SARIF (Static Analysis Results Interchange Format):** A standard format for code scanning results; used by agents to provide objective evidence of security validation.
*   **Traceability:** The ability to reconstruct the "monologue" of an agent’s reasoning, tool usage, and decision-making via logs, artifacts, and PR history.