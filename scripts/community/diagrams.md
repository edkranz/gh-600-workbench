# GH-600 Diagrams (Mermaid source)

Centralized source for the 5 study diagrams. Each block is also inlined into the relevant module/research markdown so it renders in NotebookLM, GitHub, and Notion automatically — but maintain them here first.

---

## 1. Plan → Act → Evaluate lifecycle

**Embedded in**: `modules/01-foundations/03-agent-lifecycle.md`
**Exam domain**: 1 (Architecture & SDLC processes)

```mermaid
flowchart LR
    Plan["📋 Plan<br/>(inspectable artifact)"]
    Act["⚙️ Act<br/>(bounded execution)"]
    Eval{"✅ Evaluate<br/>(signals gate merge)"}
    Plan --> Act --> Eval
    Eval -->|checks fail / unmet| Plan
    Eval -->|all checks pass| Merge["🔀 Merge / Done"]
```

The loop is the key: evaluate failures don't terminate the agent — they feed back into a new plan. Linear flow is the anti-pattern.

---

## 2. Risk-tiered autonomy decision tree

**Embedded in**: `research/01-gap-docs/build-guardrails.md`
**Exam domain**: 6 (Guardrails & accountability)

```mermaid
flowchart TD
    Start["Agent action"]
    Op{Operational<br/>risk?}
    Sec{Security<br/>risk?}
    Comp{Compliance<br/>risk?}
    Auto["🟢 Fully autonomous<br/>lint · docs · tests"]
    Gate["🟡 Approval-gated<br/>logic · deps · schema"]
    Human["🔴 Human-authored<br/>prod deploy · secrets · deletes"]
    Start --> Op
    Op -->|No| Sec
    Op -->|Yes| Human
    Sec -->|No| Comp
    Sec -->|Yes| Human
    Comp -->|No| Auto
    Comp -->|Yes| Gate
```

Any-yes-routes-up: if *any* risk dimension trips, escalate. The exam will test this triage order.

---

## 3. MCP server / registry / allow list interaction

**Embedded in**: `modules/03-tooling-mcp/03-mcp-servers-registries-allowlists.md`
**Exam domain**: 2 (Tool use & environment interaction — highest weighted)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Agent
    participant Reg as MCP Registry
    participant Pol as Org Allow List
    participant Srv as MCP Server
    Dev->>Reg: Discover available servers
    Reg-->>Dev: Server catalog
    Dev->>Pol: Request to enable server X
    alt Server on allow list
        Pol-->>Dev: ✅ Allowed
        Dev->>Srv: Invoke tool
        Srv-->>Dev: Tool result
    else Not on allow list
        Pol-->>Dev: ❌ Blocked
    end
```

The allow list is enforced *after* registry discovery, *before* the tool call. Skipping the allow-list check is the most common exam-trap scenario.

---

## 4. SDLC integration: control plane + system of record

**Embedded in**: `modules/02-architecture/05-pr-governance.md`
**Exam domain**: 1 (Architecture & SDLC) + 6 (Guardrails)

```mermaid
flowchart TB
    subgraph CI["CI/CD Pipeline (GitHub Actions)"]
        direction TB
        Trigger["Workflow trigger<br/>(PR · issue · dispatch)"]
        PlanJob["Plan job<br/>uploads plan artifact"]
        ActJob["Act job<br/>scoped token · branch"]
        EvalJob["Eval job<br/>checks · scans"]
        Trigger --> PlanJob --> ActJob --> EvalJob
    end
    subgraph Control["GitHub Control Plane"]
        BP["Branch protection"]
        CO["CODEOWNERS"]
        EP["Environment approval"]
        RS["Rulesets"]
    end
    subgraph Record["GitHub System of Record"]
        PR["Pull Request"]
        Runs["Workflow runs + logs"]
        Art["Artifacts + traces"]
        Alerts["Security alerts"]
    end
    Control -.->|enforces| CI
    CI -.->|produces| Record
    Record -.->|audited via| Control
```

Same GitHub primitives both *record* activity and *enforce* policy — that's what "system of record AND control plane" means in the audience profile.

---

## 5. Sub-agent lifecycle (Copilot SDK state machine)

**Embedded in**: `research/01-gap-docs/custom-agents-sdk.md`
**Exam domain**: 5 (Multi-agent orchestration)

```mermaid
stateDiagram-v2
    [*] --> Selected: subagent.selected
    Selected --> Started: subagent.started
    Started --> Completed: subagent.completed
    Started --> Failed: subagent.failed
    Completed --> Deselected: subagent.deselected
    Failed --> Deselected: subagent.deselected
    Deselected --> [*]
```

Five events, three terminal-ish states. `toolCallId` is the join key across all events for a given sub-agent invocation.

---

## How to update

1. Edit the Mermaid block here first.
2. Search the target file for the existing block (each embedded copy has a `<!-- diagrams.md:N -->` marker).
3. Replace with the new version.

If you add a new diagram, append it here, then embed with the same marker convention.
