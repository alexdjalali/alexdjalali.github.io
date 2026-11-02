---
title: "Anatomy of an AI Engineering System"
date: 2026-02-26
draft: false
description: "How seventeen slash commands, seven templates and three model tiers, each of them short and single-purpose, turn Claude Code into a full software development lifecycle."
images:
  - "images/og/anatomy-of-an-ai-engineering-system.png"
tags: ["ai", "software-engineering", "developer-tools", "claude", "architecture"]
keywords: ["claude code", "ai skills", "software development lifecycle", "prompt engineering", "slash commands", "ai-assisted development"]
series: ["AI-Assisted Engineering"]
---

In [a previous post](/posts/how-i-learned-to-love-the-bomb/) I described how I went from skeptic of AI-assisted programming to building an engineering system around it. I talked about standards files and quality gates, and about the idea that an unconstrained model writes mediocre code while a constrained one writes code that looks like yours. What I didn't show was the machinery itself, the thing that actually turns a blank terminal into a full development lifecycle.

So here it is, opened up: seventeen slash commands, seven templates and three model tiers. Each skill is short and does one thing. Chained together, they form a pipeline that mirrors the way software has always been built, only faster.

## The Lifecycle as a Directed Graph

Software development, done traditionally, follows a predictable arc. You understand the problem, make the architectural decisions, break the work into deliverable pieces, plan each piece, implement it with tests, verify it, commit it, review it and ship it. Every methodology from waterfall to agile to shape-up is a variation on this sequence. The differences are in the feedback loops and the batch sizes, not in the fundamental ordering.

My skills encode that arc as a directed graph of slash commands:

```
/adr → /arch → /rfp → /spec → /spec-plan → /spec-implement → /spec-verify → /github
```

Each node is a standalone skill that reads what its predecessors produced and leaves artifacts for its successors. `/adr` writes an Architecture Decision Record. `/arch` draws Mermaid diagrams from an analysis of the codebase. `/rfp` decomposes an epic into stories that can each be tested on their own. `/spec` dispatches to planning, implementation or verification, depending on where the plan currently sits. And `/github` handles branches, commits, pull requests and merges.

What holds the graph together is that every skill ends by offering to route you to the next one. This is the entire routing logic at the end of `/adr`:

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

The developer chooses the next step; the system suggests but never dictates. You can enter the graph anywhere (straight to `/spec` for a small feature, say, or `/adr` for a structural change), and the downstream skills work regardless of how you got there.

## Each Skill is Short

The longest skill in the system is `/spec-plan`, at roughly 120 lines of markdown, and most are under 60. `/preflight`, which runs formatting, linting, type checking and tests across three languages, is about 40 lines. `/tdd`, which runs the full red-green-refactor cycle with property-based testing, is around 50.

That brevity is deliberate. A skill is not a manual; it's a set of constraints, a sequence of steps and a definition of done. The model already knows how to write Go or run pytest. What it doesn't know is *your* conventions: which linter, which formatter, which test markers, which directory layout, and what counts as "done" in your particular codebase. The skill supplies exactly that difference between general capability and your expectations, and nothing more.

Here, for instance, is the entire rules section of `/debug`, four lines that define how it behaves:

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

That is the whole enforcement mechanism. There's no essay on why TDD matters and no motivational preamble, because the model already knows what TDD is. The skill tells it which constraints *you* won't bend on, and stops.

Short skills also have the virtue of being debuggable. When something goes wrong (and it will), you want to be able to read the whole skill in thirty seconds, find the step that produced the bad output, and fix it. A 500-line prompt is an untestable monolith; a 50-line prompt is, more or less, a function.

## Templates as Shared Memory

Skills don't work in isolation. They share structure through seven templates that live in `~/.claude/templates/`:

- **adr.md**: Architecture Decision Record with alternatives table, consequences, and quality checklist
- **epic.md**: Epic specification with stories table and risk matrix
- **story.md**: User story with acceptance criteria and coding patterns checklist
- **plan.md**: Implementation plan with task breakdown, feature inventory, and progress tracking
- **commit.md**: Conventional commit format with scope and type conventions
- **pr.md**: Pull request with summary, changes by area, and test plan
- **repo.md**: Monorepo scaffold with layered architecture and directory conventions

When `/adr` creates an ADR, it stamps out `adr.md` and fills in the blanks. When `/rfp` decomposes an epic, each story follows `story.md`. When `/spec-plan` writes an implementation plan, it follows `plan.md`, complete with a status header (`PENDING`, `COMPLETE`, `VERIFIED`), an approval flag, and an iteration counter that goes up whenever verification fails and the plan loops back to implementation.

In effect, the templates are memory shared across sessions. A plan written by `/spec-plan` on Monday is picked up by `/spec-implement` on Tuesday and `/spec-verify` on Wednesday, and the status header is how they hand off: `/spec` reads it and dispatches to the right phase. Nobody has to remember where they left off, because the artifact carries the state.

It also explains why the skills can stay short. The structural decisions live in the templates, so the skill says *what to do* and the template says *what the output looks like*. It's separation of concerns, applied to prompts.

## The Spec Pipeline as a Filesystem

Every skill reads from and writes to a specific path, which is to say that the directory structure *is* the workflow engine:

```
docs/
├── adr/                    # Architecture Decision Records
└── spec/
    ├── arch/               # Mermaid architecture diagrams
    ├── epics/              # Epic specifications
    ├── stories/            # Implementation stories
    └── plans/              # Implementation plans
```

`/repo` scaffolds this structure on day one as part of the standard monorepo template, and from then on every skill knows exactly where to find its inputs and where to leave its outputs. `/adr` writes numbered files to `docs/adr/`, `/arch` writes diagrams to `docs/spec/arch/`, `/rfp` reads an epic from `docs/spec/epics/` and creates stories in `docs/spec/stories/`, and `/spec-plan` writes plans to `docs/spec/plans/`. There's no configuration and no database, only files in agreed-upon places.

The naming conventions are part of that contract. Epics are `epic-NN-<slug>.md`. Stories use `<epic>.<story>-<slug>.md`, so story 5.3 of epic 5 lands at `docs/spec/stories/5.3-repository-layer.md`. Plans are `YYYY-MM-DD-<slug>.md`. The skills rely on these conventions to find related artifacts on their own. When `/rfp` decomposes epic 5, it creates stories 5.1 through 5.N and updates the epic's table of stories with relative links:

```markdown
## Stories

| #   | Story            | Status | File                                   |
| --- | ---------------- | ------ | -------------------------------------- |
| 5.1 | Core interfaces  | Todo   | [5.1-core-interfaces.md](../stories/5.1-core-interfaces.md) |
| 5.2 | Repository layer | Todo   | [5.2-repository-layer.md](../stories/5.2-repository-layer.md) |
| 5.3 | Service layer    | Todo   | [5.3-service-layer.md](../stories/5.3-service-layer.md) |
```

Status lives inside each file rather than in which directory the file sits. Each story has a `Status` field that moves from `Todo` to `In Progress` to `Complete`. When `/spec-verify` finishes verifying a story's plan, it updates both the story and the epic's table in one pass, and `/rfp status` scans the whole tree to produce a progress report:

```markdown
| # | Epic                       | Total | Done | Remaining | Progress         |
|---|----------------------------|-------|------|-----------|------------------|
| 1 | Repository Restructure     | 9     | 9    | 0         | ████████░░ 100%  |
| 2 | Foundation Fault Tolerance | 8     | 5    | 3         | █████░░░░░  63%  |
```

Keeping all of this in files has one practical advantage over any database or project-management tool: it's under version control. Every status change, every new story and every plan iteration is a git commit. `git log docs/spec/stories/5.3-service-layer.md` shows a story's whole life from creation to completion, and `git diff` between iterations 1 and 3 of a plan shows exactly what verification changed.

Every template also has a section for references (links to ADRs, architecture diagrams, epics and stories). When `/spec-plan` writes a plan, it cites the ADR that motivated the work and the story that scoped it, and when `/github` writes a pull request description, it links back to the plan, the story and the ADR. The result is a chain you can follow from decision to implementation to commit. Six months later, when someone asks why we restructured the event pipeline, the pull request leads to the plan, the plan to the story, the story to the epic, and the epic to the ADR that records the decision, the alternatives and the trade-offs we accepted.

I should be clear that the AI doesn't maintain this chain because it has a good memory. It maintains it because the templates have a `References` section and the skills say *fill it in*. Structure, in my experience, beats intelligence.

## Model Tiers

Not every skill needs the same model; reviewing an architecture decision calls for rather more than running a linter does. The skills say which tier they want with a single line of YAML frontmatter. `/adr` opens with:

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

That is the entire model-selection mechanism. Opus handles the work that needs judgment: `/adr`, `/arch`, `/spec-plan`, `/spec-verify`, `/review`, `/repo` and `/debug`. These skills read large codebases, make design decisions, weigh trade-offs and catch subtle errors, and they benefit from deeper reasoning and a broader grasp of context.

Sonnet handles the work that needs execution: `/spec` (the dispatcher), `/spec-implement`, `/tdd`, `/github`, `/preflight`, `/learn`, `/patterns`, `/sync` and `/vault`. These follow well-defined steps (run the tests, format the code, create the branch, commit in conventional format), and the instructions are precise enough that a faster, cheaper model carries them out reliably.

The division mirrors how engineering teams already work. Senior architects make the structural decisions, and everyone follows the same process for committing code and running CI. You don't need your most expensive resource checking whether `ruff format` passed.

So a typical `/spec` session starts on Opus for planning (exploring the codebase, designing the approach, breaking the work into tasks), drops to Sonnet for implementation, where it runs a TDD cycle per task, and goes back up to Opus for verification, where it launches review agents and looks for regressions. The tier follows the cognitive demand of each phase.

## The Spec Workflow

The centerpiece is `/spec`, a three-phase workflow that manages the whole implementation cycle.

The first phase is planning (`/spec-plan`, on Opus). It explores the codebase, identifies the affected files, similar features and existing patterns, and designs 3 to 12 implementation tasks, each testable on its own. It then launches two verification agents in parallel, one checking the plan against the requirements and one challenging its assumptions and looking for ways it could fail. Nothing proceeds until the developer approves the plan.

The second phase is implementation (`/spec-implement`, on Sonnet). It takes the approved plan and works through the tasks in order, using `/tdd` for each red-green-refactor cycle and ticking the plan's checkboxes as it goes. In a git worktree it commits per task. There are no sub-agents here; everything runs in the main context so that nothing is lost between tasks.

The third phase is verification (`/spec-verify`, on Opus). It launches two review agents, one for process compliance and one for code quality, runs the full test suite, checks coverage and file lengths, and traces call chains in both directions. Then it builds the thing, deploys it to a test environment, runs the actual program and the end-to-end tests. If anything fails, it adds fix tasks to the plan, resets the status and loops back to the second phase.

That loop is the important part, and `/spec` encodes it as a small state machine:

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

Verification, in other words, doesn't merely report problems; it feeds them back into implementation as new tasks, and the plan's iteration counter records how often that has happened. Most features verify on the first pass. Complex migrations sometimes take two or three. The system handles both without anyone stepping in after the initial approval.

## Quality Gates are Non-Negotiable

`/preflight` runs before every commit and applies four gates in order:

1. **Format:** `ruff format` for Python, `gofumpt` for Go, `prettier` for TypeScript, fixing in place.
2. **Lint:** `ruff check --fix`, `golangci-lint run`, `eslint --fix`, reporting whatever is left.
3. **Type check:** `basedpyright`, `go vet`, `tsc --noEmit`. There is no auto-fix here; you fix it or you don't commit.
4. **Tests:** `pytest`, `go test`, `vitest`. Changed modules must have passing tests.

I don't treat this as optional. `/github commit` calls `/preflight` before staging anything, and if the third or fourth gate fails, the commit simply doesn't happen; the AI fixes the problem and tries again. The bar is the same whether the code was written by hand, by Sonnet or by Opus.

## The Feedback Loop

The pipeline skills handle the forward path, from decision to shipped code. A second set handles the path back: learning from what happened and improving the system itself.

`/debug` applies the scientific method to bugs. It reproduces the bug with a failing test, isolates the root cause by bisection, diagnoses it, fixes it through `/tdd`, and checks for regressions. Its main job is to prevent the most common failure mode of AI debugging, which is changing code at random until the symptom goes away without anyone understanding why.

`/learn` watches a session for non-obvious discoveries and turns them into reusable skill files. It defines its own triggers:

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

Each extracted skill lands in `.claude/skills/`, so the next session benefits from what this one learned. Over a few weeks the system accumulates the sort of institutional knowledge that would otherwise evaporate every time the context window resets.

`/patterns` audits the codebase for duplication, anti-patterns, coupling and complexity hotspots. It's what I run when something feels wrong but I can't yet point to a specific bug, and it produces a report ranked by severity and offers to fix what it found.

`/sync` keeps the documentation current. It reads the codebase, compares it with the existing rules and skills, updates whatever has gone stale, and writes new rules for patterns it finds but can't see documented anywhere. The system, in a modest way, maintains itself.

None of these are part of the main pipeline. They are the maintenance loop that keeps the pipeline honest, and without them the skills would calcify, correct on the day they were written and less relevant every week after.

## Why This Works

As far as I can tell, the system works for the same reason any good engineering process works: it separates decisions from execution, makes the decisions explicit, and automates the execution.

The developer decides the architecture (through `/adr`), approves the plan (through `/spec-plan`) and reviews the result (through `/spec-verify`). The model does the mechanical translation, the 400 lines of well-structured, well-tested implementation that used to take an afternoon. The templates keep the structure consistent, the model tiers put capability where it matters, and the quality gates keep things from sliding backward.

None of it requires the model to be brilliant. It requires the model to follow instructions reliably and the instructions to be precise, which is a rather more modest demand. If there's a lesson here, it's one I learned long before language models, building formal grammars in graduate school: most of the power of a system lies in the constraints you place on it, and the AI is no exception.
