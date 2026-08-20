# GH-600 Hands-On Lab Guide

> Six labs targeting the highest-weighted exam domain (Tool use + MCP, 20–25%) and the architecture/guardrails domain (15–20% + 10–15%). Do these in a **sandbox repository** you can wreck. Each lab is ~20–40 minutes.
>
> Prerequisites: a GitHub account with **Copilot enabled**, `gh` CLI installed (`brew install gh`), and Node 18+. Some MCP/custom-agent features may require Copilot Business/Enterprise — check your subscription if a step is rejected.

---

## Lab 0 — Sandbox setup (5 min)

```bash
# Create a clean sandbox repo
mkdir -p ~/sandbox-gh600 && cd ~/sandbox-gh600
git init -b main
echo "# GH-600 Sandbox" > README.md
git add . && git commit -m "init"

# Create the remote and push (private)
gh auth status   # confirm you're logged in
gh repo create gh600-sandbox --private --source=. --remote=origin --push

# Sanity check
gh repo view --web
```

You now have a private remote `gh600-sandbox` you can mutate freely.

---

## Lab 1 — Repo-level custom instructions for Copilot (15 min)

**Why this lab:** Repository custom instructions are the canonical home for long-term agent memory (Domain 3 + cross-cutting). Knowing where they live and how they're picked up is a guaranteed exam concept.

```bash
mkdir -p .github
cat > .github/copilot-instructions.md <<'EOF'
# Project conventions for Copilot

## Code style
- Prefer named exports over default exports.
- Async functions only — never use `.then()` chains.
- One assertion per test.

## Pull request etiquette
- Title format: `<area>: <imperative summary>` (e.g., `auth: rotate session token on login`).
- PR body must include a "Why" section before any "What" section.
- Link an issue or skip linking entirely — don't fake-link.

## Tools to avoid
- Do not call external network APIs unless explicitly listed in `.github/mcp-allowlist.yml`.
EOF

git add .github/copilot-instructions.md
git commit -m "Add Copilot custom instructions"
git push
```

**Verify**: open Copilot Chat in this repo from VS Code (or `gh copilot` in the terminal) and ask "What's our PR title format?" — the instructions should ground the answer.

`★ Insight ─────────────────────────────────────`
The exam treats `.github/copilot-instructions.md` (or `AGENTS.md`) as the canonical surface for **long-term, project-stable agent memory**. Org-level instructions are layered on top. When you read an exam question about "where should team conventions live for an agent," the answer is almost always this file — *not* the user prompt, *not* environment secrets.
`─────────────────────────────────────────────────`

---

## Lab 2 — Configure an MCP server for your agent (30 min)

**Why this lab:** MCP is the most heavily weighted concept on the exam. Touching one for real is non-negotiable.

We'll add the **GitHub remote MCP server** (exposes GitHub APIs as tools) to a local Copilot setup, then add an allow list.

### Step 2.1 — Inspect what Copilot uses for MCP locally

In VS Code, open Settings → search "MCP" — or check `~/.config/github-copilot/mcp.json` (path may vary by client). Most Copilot installations now have a registry-driven MCP config; you'll either edit a local config or use the Copilot UI to "Add MCP server."

```bash
# Example local config (path varies by client)
mkdir -p ~/.config/github-copilot
cat > ~/.config/github-copilot/mcp.json <<'EOF'
{
  "servers": {
    "github-remote": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "auth": "github-token"
    }
  }
}
EOF
```

> 📝 If your Copilot version manages this via a UI registry instead of a local file, use the UI flow — the *concepts* (server name, URL, auth) are identical.

### Step 2.2 — Add a repository-level MCP allow list

The exam-bullet says **"Configure MCP allow lists."** Practice it:

```bash
cat > .github/mcp-allowlist.yml <<'EOF'
# Repository MCP allow list
# Only servers listed here may be invoked by agents operating on this repo.
allowed_servers:
  - github-remote      # GitHub APIs via remote MCP
  - docs-search        # internal documentation search
denied_servers:
  - "*"                # implicit deny for anything not listed above
EOF

git add .github/mcp-allowlist.yml
git commit -m "Add MCP allow list"
git push
```

> 📝 In an enterprise org, the real allow list lives in **organization settings → Copilot → MCP** (or the equivalent admin panel). The repo-local version above is a *policy intent* file your CI can read. Either way, the exam concept is: untrusted servers must be blocked by name.

### Step 2.3 — Test the agent calling MCP

In Copilot Chat in VS Code, ask: "Use the `github-remote` MCP server to list open issues in this repo." If it does — your MCP config works. If it refuses or fails, check (in order): the server URL, your token scopes, the allow list, the agent's tool permissions.

`★ Insight ─────────────────────────────────────`
The most common cause of "MCP works for me but not for them" in a real org is the allow list, not the server config. Memorize this exam reflex: **MCP problem + works elsewhere = check the allow list first.** Question 9 in your mock exam tests exactly this.
`─────────────────────────────────────────────────`

---

## Lab 3 — Custom Copilot agent in a workflow (30 min)

**Why this lab:** Domain 1 + 2 — agent invoked in CI, with branch-based scope and least-privilege permissions.

```bash
mkdir -p .github/workflows
cat > .github/workflows/agent-triage.yml <<'EOF'
name: Agent triage

on:
  issues:
    types: [opened, labeled]

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  triage:
    if: contains(github.event.issue.labels.*.name, 'needs-triage')
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      # ---- 1. PLAN ----
      - name: Produce structured plan
        id: plan
        run: |
          cat > plan.md <<'PLAN'
          # Triage plan for issue #${{ github.event.issue.number }}

          Steps:
          1. Read the issue body and labels.
          2. Categorize: bug | feature | question | docs.
          3. Assign appropriate label.
          4. Comment with category and reasoning.
          PLAN
          echo "plan<<EOF" >> $GITHUB_OUTPUT
          cat plan.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Upload plan as artifact
        uses: actions/upload-artifact@v4
        with:
          name: triage-plan-${{ github.event.issue.number }}
          path: plan.md

      # ---- 2. ACT ----
      # (Real version would invoke a Copilot agent or MCP-backed action.
      # For the lab we stub the action; the plan/act/evaluate shape is what matters.)
      - name: Categorize and label
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          body="${{ github.event.issue.body }}"
          if echo "$body" | grep -qiE "error|crash|broken|bug"; then
            label="bug"
          elif echo "$body" | grep -qiE "would be nice|feature|request"; then
            label="feature"
          else
            label="question"
          fi
          gh issue edit ${{ github.event.issue.number }} --add-label "$label"
          echo "category=$label" >> $GITHUB_OUTPUT

      # ---- 3. EVALUATE ----
      - name: Comment with traceability record
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue comment ${{ github.event.issue.number }} --body "🤖 Agent triage complete.
          
          See workflow run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          Plan artifact: triage-plan-${{ github.event.issue.number }}"
EOF

git add .github/workflows/agent-triage.yml
git commit -m "Add plan/act/evaluate triage agent workflow"
git push
```

**Test it:**
```bash
gh issue create --title "App crashes on startup" --body "Getting an error when I open the app" --label needs-triage
# Watch the workflow run
gh run watch
```

**What this lab demonstrates (each maps to an exam bullet):**
- ✅ Plan → Act → Evaluate separation (Domain 1)
- ✅ Structured plan output as workflow artifact (Domain 1)
- ✅ Inspectable artifacts within standard tooling (Domain 1)
- ✅ Agent invoked in a CI workflow (Domain 2)
- ✅ Least-privilege `permissions:` block (Domain 6)
- ✅ Traceability via run-link comment (Domain 2)

---

## Lab 4 — PR governance for agent-authored work (20 min)

**Why this lab:** Domain 1 + 6 — branch protection, CODEOWNERS, required checks. This is the "GitHub as control plane" embodiment.

```bash
# CODEOWNERS — require human review on sensitive paths
mkdir -p .github
cat > .github/CODEOWNERS <<'EOF'
# Anything in .github/workflows requires platform-team approval
.github/workflows/   @your-username

# Anything touching auth requires the security team
/src/auth/           @your-username

# Migrations are highest-risk
/migrations/         @your-username
EOF

# PR template that the agent must fill out
mkdir -p .github
cat > .github/PULL_REQUEST_TEMPLATE.md <<'EOF'
## Why
<!-- The motivation for this change. Required. -->

## What
<!-- Concrete changes made. -->

## Plan artifact
<!-- Link to the workflow artifact containing the agent's structured plan. -->

## Risk
- [ ] Reversible (no data loss, no prod impact)
- [ ] Irreversible (requires explicit human approval)
EOF

git add .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md
git commit -m "Add CODEOWNERS and PR template for agent governance"
git push

# Branch protection on main
gh api -X PUT "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/branches/main/protection" \
  --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true
  },
  "restrictions": null
}
EOF
```

> ⚠️ `gh api` for branch protection requires admin on the repo. If you get 403, set the protection via the Settings UI instead.

`★ Insight ─────────────────────────────────────`
The audience-profile phrase "GitHub as the control plane" is concretely *this lab*: CODEOWNERS routes review, branch protection enforces it, the PR template constrains agent output to required fields. The agent has no special powers — it must pass the same gates a human contributor passes. This is the **contributor model** Domain 1 expects you to recognize.
`─────────────────────────────────────────────────`

---

## Lab 5 — Copilot cloud agent firewall (15 min)

**Why this lab:** Domain 2 bullet "Configure an agent to handle environment-specific constraints." The cloud-agent firewall is the named feature.

The cloud agent firewall is configured at **organization or repository settings → Copilot → Coding agent → Firewall**. From the CLI you can inspect with:

```bash
# Inspect the current firewall config (org-level)
gh api orgs/<your-org>/copilot/cloud-agent/firewall 2>/dev/null || \
  echo "API surface may differ — use the Settings UI"
```

In the UI:
1. Settings → Copilot → Coding agent → Firewall
2. Set the **allow list** to only the hosts your agent needs (e.g., `api.github.com`, your package registry)
3. Confirm the default policy is **deny**

**Read** [Customize the agent firewall](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/customize-the-agent-firewall) — the exam may use the exact terminology from this doc.

---

## Lab 6 — Environment protection for irreversible actions (15 min)

**Why this lab:** Domain 6's "Require explicit authorization or controlled paths for irreversible or compliance-sensitive changes."

```bash
# Create a 'production' environment with required reviewers
gh api -X PUT "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/environments/production" \
  --input - <<EOF
{
  "wait_timer": 0,
  "reviewers": [
    {"type": "User", "id": $(gh api user -q .id)}
  ],
  "deployment_branch_policy": {
    "protected_branches": true,
    "custom_branch_policies": false
  }
}
EOF
```

Then a workflow that targets this environment:

```bash
cat > .github/workflows/deploy.yml <<'EOF'
name: Deploy

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true

permissions:
  contents: read
  deployments: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production    # ← this is the gate
    steps:
      - run: echo "Deploying ${{ inputs.version }} (would actually deploy here)"
EOF

git add .github/workflows/deploy.yml
git commit -m "Add prod deploy workflow gated by environment"
git push

# Trigger and watch the approval flow
gh workflow run deploy.yml -f version=v1.2.3
gh run watch
```

You'll see the run pause for your approval — that's the controlled path for irreversible actions.

---

## Lab cleanup

When done practicing:

```bash
# Delete the sandbox repo (local + remote)
cd ~ && rm -rf ~/sandbox-gh600
gh repo delete <your-username>/gh600-sandbox --yes
```

---

## What you should be able to explain after these labs

For each item below, you should be able to say *which feature, where it lives, and what it controls* without looking it up:

- [ ] `.github/copilot-instructions.md` — long-term agent memory at repo scope
- [ ] MCP server config — where it's declared, how it's invoked
- [ ] MCP allow list — what's blocked vs. allowed, where it's enforced
- [ ] GitHub remote MCP server — what APIs it exposes
- [ ] Workflow `permissions:` block — least-privilege per workflow
- [ ] `workflow_dispatch` + environment approval — controlled path for irreversible actions
- [ ] CODEOWNERS — path-scoped required reviewers
- [ ] Branch protection / required PR reviews — enforce CODEOWNERS at merge
- [ ] Cloud agent firewall — egress allow list for the Copilot cloud agent
- [ ] PR template — constrain agent output to required fields
- [ ] Workflow artifact upload — durable, inspectable plan/state output

If any of those make you reach for docs, redo that lab.
