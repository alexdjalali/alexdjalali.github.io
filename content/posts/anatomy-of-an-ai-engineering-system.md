---
title: "Anatomy of an AI Engineering System"
date: 2026-02-26
draft: false
description: "Seventeen slash commands, seven templates, and three model tiers — how a set of short, composable skills turns Claude Code into a full software development lifecycle."
images:
  - "images/og/anatomy-of-an-ai-engineering-system.png"
tags: ["ai", "software-engineering", "developer-tools", "claude", "architecture"]
keywords: ["claude code", "ai skills", "software development lifecycle", "prompt engineering", "slash commands", "ai-assisted development"]
series: ["AI-Assisted Engineering"]
---

In [a previous post](/posts/how-i-learned-to-love-the-bomb/) I described the shift from AI skepticism to building an engineering system around it. I mentioned standards files, quality gates, and the idea that unconstrained AI produces mediocre code while constrained AI produces code that looks like yours. What I didn't show was the implementation — the actual mechanism that turns a blank terminal into a full development lifecycle.

This post opens it up. Seventeen slash commands. Seven templates. Three model tiers. Each skill is short, composable, and single-purpose. Together they form a pipeline that mirrors how software has always been built — just faster.

## The Lifecycle as a Directed Graph

Traditional software development follows a predictable arc: understand the problem, make architectural decisions, break the work into deliverable pieces, plan each piece, implement with tests, verify, commit, review, ship. Every methodology from waterfall to agile to shape-up is a variation on this sequence. The differences are in the feedback loops and the batch sizes, not in the fundamental ordering.

My skills encode this arc as a directed graph of slash commands:

```
/adr → /arch → /rfp → /spec → /spec-plan → /spec-implement → /spec-verify → /github
```

Each node in the graph is a standalone skill that reads the outputs of its predecessors and produces artifacts for its successors. `/adr` writes an Architecture Decision Record. `/arch` generates Mermaid diagrams from codebase analysis. `/rfp` decomposes an epic into independently testable stories. `/spec` dispatches to planning, implementation, or verification based on where the plan currently sits. `/github` handles branching, committing, PRs, and merges.

The key property is that every skill terminates by offering to route you to the next one. Here's how `/adr` does it — the entire routing logic at the end of the skill:

```markdown
Use AskUserQuestion:

  question: "What's the next step for this decision?"
  header: "Pipeline"
  options:
    - "/arch — Diagram affected architecture"
    - "/rfp — Decompose into stories"
    - "/spec — Implement directly"
    - "Done — Record only"

Based on the user's choice, invoke the corresponding skill:
- /arch: Skill(skill='arch', args='<scope derived from ADR context>')
- /rfp: Skill(skill='rfp', args='<epic description from ADR>')
- /spec: Skill(skill='spec', args='<task description from ADR>')
- Done: End the workflow
```

The developer chooses the next step. The system suggests; it doesn't dictate. You can enter the graph at any point — jump straight to `/spec` for a small feature, start at `/adr` for a structural change — and the downstream skills will work regardless of how you arrived.

## Each Skill is Short

The longest skill in the system is `/spec-plan` at roughly 120 lines of markdown. Most are under 60. `/preflight` — which runs formatting, linting, type checking, and tests across three languages — is about 40 lines. `/tdd` — which implements the full red-green-refactor cycle with property-based testing — is around 50.

This is deliberate. A skill isn't a manual. It's a set of constraints, a sequence of steps, and a definition of done. The model already knows how to write Go or run pytest. What it doesn't know is *your* conventions: which linter, which formatter, which test markers, which directory structure, what constitutes "done" in your specific codebase. That's what the skill provides — the delta between general capability and your particular expectations.

Here's the entire rules section of `/debug` — four lines that define its behavioral contract:

```markdown
## Rules
- NEVER change code before understanding the root cause
- NEVER fix a bug without a test that reproduces it
- NEVER apply a fix that you can't explain
- If the fix is complex, consider whether the underlying design needs an ADR
```

And here are the rules from `/tdd`:

```markdown
## Rules
- NEVER write implementation before a failing test
- NEVER write more test than needed for the current step
- NEVER skip the refactor step (even if the code "looks fine")
- If a test passes on first run, the test is probably wrong — investigate
```

That's the whole enforcement mechanism. No lengthy prose about why TDD matters. No motivational preamble. The model already knows what TDD is. The skill tells it *your* non-negotiable constraints and nothing more.

Short skills are also debuggable skills. When something goes wrong — and it will — you want to be able to read the entire skill in thirty seconds, identify which step produced the bad output, and adjust. A 500-line prompt is an untestable monolith. A 50-line prompt is a function.

## Templates as Shared Memory

Skills don't work in isolation. They share structure through a set of seven templates that live in `~/.claude/templates/`:

- **adr.md** — Architecture Decision Record with alternatives table, consequences, and quality checklist
- **epic.md** — Epic specification with stories table and risk matrix
- **story.md** — User story with acceptance criteria and coding patterns checklist
- **plan.md** — Implementation plan with task breakdown, feature inventory, and progress tracking
- **commit.md** — Conventional commit format with scope and type conventions
- **pr.md** — Pull request with summary, changes by area, and test plan
- **repo.md** — Monorepo scaffold with layered architecture and directory conventions

When `/adr` creates an ADR, it stamps out the `adr.md` template and fills in the blanks. When `/rfp` decomposes an epic into stories, each story uses the `story.md` template. When `/spec-plan` produces an implementation plan, it follows `plan.md` — complete with a status header (`PENDING`, `COMPLETE`, `VERIFIED`), an approved flag, and an iteration counter that increments when verification fails and the plan loops back to implementation.

The templates serve as shared memory across sessions. A plan file written by `/spec-plan` on Monday is picked up by `/spec-implement` on Tuesday and `/spec-verify` on Wednesday. The status header is the handoff mechanism. `/spec` reads it and dispatches to the right phase automatically. No human has to remember where they left off. The artifact carries the state.

This also means skills don't need to be long, because the structural decisions live in templates. The skill says *what to do*. The template says *what the output looks like*. Separation of concerns, applied to prompts.

## The Spec Pipeline as a Filesystem

Every skill reads from and writes to a specific path. The directory structure *is* the workflow engine:

```
docs/
├── adr/                    # Architecture Decision Records
└── spec/
    ├── arch/               # Mermaid architecture diagrams
    ├── epics/              # Epic specifications
    ├── stories/            # Implementation stories
    └── plans/              # Implementation plans
```

`/repo` scaffolds this structure on day one — it's part of the standard monorepo template. From that point forward, every skill in the pipeline knows exactly where to find its inputs and where to deposit its outputs. `/adr` writes numbered files to `docs/adr/`. `/arch` writes diagrams to `docs/spec/arch/`. `/rfp` reads an epic from `docs/spec/epics/` and creates stories in `docs/spec/stories/`. `/spec-plan` creates plans in `docs/spec/plans/`. No configuration. No database. Just files in agreed-upon locations.

The naming conventions are part of the contract. Epics are `epic-NN-<slug>.md`. Stories use `<epic>.<story>-<slug>.md` — so story 5.3 of epic 5 lands at `docs/spec/stories/5.3-repository-layer.md`. Plans are `YYYY-MM-DD-<slug>.md`. The skills use these conventions to discover related artifacts automatically. When `/rfp` decomposes epic 5, it creates stories 5.1 through 5.N and updates the epic's stories table with relative links:

```markdown
## Stories

| #   | Story            | Status | File                                   |
| --- | ---------------- | ------ | -------------------------------------- |
| 5.1 | Core interfaces  | Todo   | [5.1-core-interfaces.md](../stories/5.1-core-interfaces.md) |
| 5.2 | Repository layer | Todo   | [5.2-repository-layer.md](../stories/5.2-repository-layer.md) |
| 5.3 | Service layer    | Todo   | [5.3-service-layer.md](../stories/5.3-service-layer.md) |
```

Status tracking happens in-file, not by moving files between directories. Each story has a `Status` field that progresses from `Todo` to `In Progress` to `Complete`. When `/spec-verify` finishes verifying a story's plan, it updates the story's status field and the epic's table in one pass. `/rfp status` scans the entire tree to generate a progress report:

```markdown
| # | Epic                       | Total | Done | Remaining | Progress         |
|---|----------------------------|-------|------|-----------|------------------|
| 1 | Repository Restructure     | 9     | 9    | 0         | ████████░░ 100%  |
| 2 | Foundation Fault Tolerance | 8     | 5    | 3         | █████░░░░░  63%  |
```

The filesystem approach has a practical advantage over any database or project management tool: it's version-controlled. Every status change, every story creation, every plan iteration is a git commit. You can `git log docs/spec/stories/5.3-service-layer.md` and see the full history of a story from creation through implementation to completion. You can `git diff` a plan between iteration 1 and iteration 3 to see exactly what the verification phase changed.

Every template includes a section for references — links to ADRs, architecture diagrams, epic specs, and story files. When `/spec-plan` creates a plan, it cross-references the ADR that motivated the work and the story that scoped it. When `/github` generates a PR description, it links back to the plan, the story, and the ADR. This creates a traceable chain from decision to implementation to commit. Six months later, when someone asks "why did we restructure the event pipeline?", the PR links to the plan, the plan links to the story, the story links to the epic, and the epic links to the ADR that documents the decision, the alternatives considered, and the trade-offs accepted.

The AI doesn't maintain this chain because it has good memory. It maintains it because the templates have a `References` section and the skills say *fill it in*. Structure beats intelligence.

## Model Tiers

Not every skill needs the same model. Reviewing an architecture decision requires different capability than running a linter. The skills encode this by specifying which model tier to use:

The encoding is a single YAML frontmatter line at the top of each skill file. `/adr` opens with:

```yaml
---
model: opus
---
```

And `/preflight` opens with:

```yaml
---
model: sonnet
---
```

That's the entire model selection mechanism. **Opus** handles the work that requires judgment: `/adr`, `/arch`, `/spec-plan`, `/spec-verify`, `/review`, `/repo`, and `/debug`. These skills involve reading large codebases, making design decisions, evaluating trade-offs, and catching subtle errors. They benefit from deeper reasoning and broader context comprehension.

**Sonnet** handles the work that requires execution: `/spec` (dispatcher), `/spec-implement`, `/tdd`, `/github`, `/preflight`, `/learn`, `/patterns`, `/sync`, and `/vault`. These skills follow well-defined steps — run the tests, format the code, create the branch, commit with conventional format. The instructions are precise enough that a faster, cheaper model executes them reliably.

The division mirrors how engineering teams work. Senior architects make the structural decisions. Everyone follows the same process for committing code and running CI. You don't need your most expensive resource reviewing whether `ruff format` passed.

In practice, this means a typical `/spec` session starts with Opus for planning — exploring the codebase, designing the approach, breaking work into tasks — then drops to Sonnet for implementation, where it runs TDD cycles on each task, and finally escalates back to Opus for verification, where it launches review agents and checks for regressions. The model tier follows the cognitive demand of each phase.

## The Spec Workflow

The centerpiece is `/spec`, a three-phase workflow that manages the full implementation cycle:

**Phase 1 — Plan** (`/spec-plan`, Opus): Explores the codebase. Identifies affected files, similar features, existing patterns. Designs 3–12 implementation tasks, each independently testable. Launches two verification agents in parallel — one checks alignment with requirements, one challenges assumptions and finds failure modes. The plan doesn't proceed until the developer approves it.

**Phase 2 — Implement** (`/spec-implement`, Sonnet): Takes the approved plan and executes each task sequentially using `/tdd` for the red-green-refactor cycle. Updates the plan's checkboxes after every completed task. Commits per-task when working in a git worktree. No sub-agents — everything runs in the main context to preserve continuity.

**Phase 3 — Verify** (`/spec-verify`, Opus): Launches two review agents — one for process compliance, one for code quality. Runs the full test suite, checks coverage, validates file lengths, traces call chains upstream and downstream. Then builds, deploys to a test environment, executes the actual program, and runs end-to-end tests. If anything fails, it adds fix tasks to the plan, resets the status, and loops back to Phase 2.

The loop is the important part. The `/spec` skill encodes it as a status machine:

```markdown
PENDING (Not Approved) → spec-plan    → User approves
PENDING (Approved)     → spec-implement → All tasks done → COMPLETE
COMPLETE               → spec-verify   → All checks pass → VERIFIED
```

And the feedback path:

```markdown
spec-verify finds issues → Status: PENDING → spec-implement fixes →
  COMPLETE → spec-verify → ... → VERIFIED
```

Verification doesn't just report problems — it feeds them back into implementation as new tasks. The plan file's iteration counter tracks how many times this has happened. Most features verify on the first pass. Complex migrations sometimes take two or three iterations. The system handles both without human intervention beyond the initial approval.

## Quality Gates are Non-Negotiable

`/preflight` runs before every commit. Four gates, in order:

1. **Format** — `ruff format` for Python, `gofumpt` for Go, `prettier` for TypeScript. Auto-fixes in place.
2. **Lint** — `ruff check --fix`, `golangci-lint run`, `eslint --fix`. Reports remaining errors.
3. **Type check** — `basedpyright`, `go vet`, `tsc --noEmit`. No auto-fix available. You fix it or you don't commit.
4. **Tests** — `pytest`, `go test`, `vitest`. Changed modules must have passing tests.

This isn't a suggestion. `/github commit` delegates to `/preflight` before staging anything. If gate 3 or 4 fails, the commit doesn't happen. The AI fixes the issue and tries again. The same bar applies whether the code was written by hand, by Sonnet, or by Opus.

## The Feedback Loop

The pipeline skills handle the forward path — from decision to shipped code. A second set of skills handles the feedback path: learning from what happened and improving the system itself.

`/debug` applies the scientific method to bugs. Reproduce with a failing test, isolate the root cause through bisection, diagnose, fix via `/tdd`, verify no regressions. It prevents the most common AI failure mode: randomly changing code until the symptom disappears without understanding the cause.

`/learn` watches for non-obvious discoveries during a session and extracts them into reusable skill files. The skill defines its own trigger conditions:

```markdown
| Trigger                      | Example                                              |
| ---------------------------- | ---------------------------------------------------- |
| **Non-obvious debugging**    | Spent 10+ minutes investigating; solution wasn't in docs |
| **Misleading errors**        | Error message pointed wrong direction                |
| **Workarounds**              | Found limitation and creative solution               |
| **Tool integration**         | Figured out how to use tool/API in undocumented way  |
| **Trial-and-error**          | Tried multiple approaches before finding what worked |
| **Repeatable workflow**      | Multi-step task that will recur; worth standardizing |
```

Each extracted skill lands at `.claude/skills/`. The next session benefits from what this session learned. Over weeks, the system accumulates institutional knowledge that would otherwise evaporate when the context window resets.

`/patterns` audits the codebase for DRY violations, anti-patterns, coupling problems, and complexity hotspots. It's the skill I run when something feels wrong but I can't point to a specific bug. It produces a severity-ranked report and offers to fix what it finds.

`/sync` keeps the documentation layer current. It reads the codebase, compares what it finds against existing rules and skills, updates what's stale, and creates new rules for patterns it discovers but can't find documented anywhere. The system doesn't just execute — it maintains itself.

These aren't part of the main pipeline. They're the maintenance loop that keeps the pipeline honest. Without them, the skills would calcify — correct when written, increasingly irrelevant as the codebase evolves.

## Why This Works

The system works for the same reason any good engineering process works: it separates decisions from execution, makes the decisions explicit, and automates the execution.

The developer decides the architecture (via `/adr`), approves the plan (via `/spec-plan`), and reviews the output (via `/spec-verify`). The model executes the mechanical translation — the 400 lines of well-structured, well-tested implementation that used to take an afternoon. The templates ensure structural consistency. The model tiers allocate capability where it matters. The quality gates prevent regression.

None of this requires the model to be brilliant. It requires the model to follow instructions reliably, and it requires the instructions to be precise. Seventeen short skills, each doing one thing, chained together through file-based artifacts and status headers. That's the whole system.

The source of leverage isn't the AI. It's the constraints you put around it.
