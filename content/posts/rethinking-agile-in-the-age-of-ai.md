---
title: "Rethinking Agile in the Age of AI"
date: 2026-10-28
draft: true
description: "Agile's values still hold, but its practices were tuned for expensive code. What six months of AI-driven development says about roles, design, review, estimation, and the Definition of Done."
images:
  - "images/og-default.png"
tags: ["ai", "agile", "software-engineering", "estimation", "process"]
keywords: ["agile and ai", "rethinking agile", "story points", "ai estimation", "definition of done", "code review sampling", "agile manifesto"]
series: ["Software Architecture"]
---

AI is here, and Agile as most teams practice it can't keep up.

In [Six Months of Enterprise Development with AI](/posts/six-months-of-enterprise-development-with-ai/) I reported what happened when agents wrote most of the code on a production platform: 1,200 commits, 594 stories, 117 Architecture Decision Records — and a set of lessons and missteps, backed by the git history. This post asks what those lessons mean for how teams work.

My answer: Agile's values still hold. Its *practices* were tuned for a world where code was expensive to write. Two-week sprints, because a story took days. Story points, because human effort was the scarce resource. Line-by-line review, because every line had a human author. AI made code cheap and decisions expensive. The practices have to be retuned around that — and a few of the retunings borrow, unapologetically, from the up-front discipline Agile was reacting against.

In [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/) I wrote that every methodology "from waterfall to agile to shape-up is a variation on this sequence. The differences are in the feedback loops and the batch sizes, not in the fundamental ordering." AI changed the batch sizes and the feedback loops. Here is what has to change with them.

## Roles: Everyone Moves Up a Level

**Engineers become architects.** A story takes an agent an hour or two; a task takes minutes. What doesn't compress is judgment — which tier owns this logic, whether this is a new pattern, whether the change is reversible. Brooks called this *essential* complexity, as opposed to the *accidental* complexity of expressing it in code. Agents absorb the accidental part. The essential part is the job now. Brooks's *surgical team* — one surgeon, a team that amplifies them — is a better model for AI-assisted development than the interchangeable developers assumed by velocity charts.

**Product owners become spec writers.** An acceptance criterion like "users can manage their settings" was fine when a developer would walk over and ask. An agent won't ask; it will guess. Acceptance criteria have to be precise enough for a machine to check, which means they increasingly look like test cases.

**Juniors need a new path.** The obvious objection: if engineers must be architects, how does anyone build architectural judgment without years of implementation? I don't think the answer is to keep juniors typing. It is to teach architecture directly — inheriting real systems, reading them through their types and boundaries, writing ADRs, and defending decisions in front of peers. That is the premise of [the course I'm building at Georgia Tech](/posts/professional-software-engineering-for-ai-and-distributed-systems/): students inherit a deliberately broken system and end the semester with an architecture defense.

## Design: Emergent Architecture Doesn't Survive Machine Speed

"Let the architecture emerge" worked when a human wrote every line, because the human noticed the duplication on the third copy. An agent will happily write the thirty-second.

That is not a hypothetical. In the [previous post](/posts/six-months-of-enterprise-development-with-ai/#misstep-1-building-without-a-theory) I described the one component I built without a theory — a developer CLI that grew to 96,000 lines, with 32 different implementations of the same kind of work and a fix-or-refactor rate of 51% of commits, against 32% in the parts of the codebase that had a theory from day one.

So this is the one thing Agile should borrow from Waterfall: **decide the structure first.** Before the first agent session, a team needs a theory of the codebase — repository structure, tier boundaries, the nouns of the domain, a reference implementation for each kind of component — written down where the agent reads it. Not a 200-page specification. A few pages, an ADR per structural decision, and one gold-standard module per tier. Everything after that stays iterative.

This is also why language choice matters more than it used to. Not because "fast languages" are fast, but because strict ones put the compiler in the review loop. Go's import paths and compile-time interface assertions, or typed Python with a strict checker and an import linter, give the agent feedback it can't argue with.

## The Definition of Done: Machine-Checked and Stable

Two missteps from the previous post change what "done" means.

**Done is machine-checked.** The layer model was in the agent's rules from day one, and the agent reported conformance from day one. A month-three audit found the connective tissue riddled with violations; mechanical enforcement arrived at months four through six. An unenforced rule is a suggestion, and agents report on suggestions as if they were facts. A team's working agreements — "we use the repository pattern," "services don't import controllers" — used to be enforced by social pressure and code review. At machine speed, neither scales. If a rule matters, it is a build failure.

That makes **working agreements code**: import guards generated from the layer model, repository-model guards that check cross-file invariants, ratchets that only go down, and generators that make the right shape the default. In the previous post I called this [a ladder of guardrails](/posts/six-months-of-enterprise-development-with-ai/#lesson-2-guardrails-are-the-process). Climbing it is now a core engineering activity, and code review shifts from *finding* violations to *authoring the checks* that make them impossible.

**Done is stable in staging, not merged.** Three-quarters of the fixes in my data were not application logic — they were cloud configuration, permissions, drift, and CI. Per feature, drift needed 3.5 fixes and permissions 1.7, against 0.39 for application code. An epic that merges in a day can produce bug fixes for six weeks. If "done" means merged, a team will systematically believe AI is ten times faster than it is.

## Sprints: The Build Fits in an Afternoon, the Tail Doesn't Fit in a Sprint

The epic → story → task hierarchy survives, but each level needs two numbers: how long the agent takes to build it, and how long until it is stable.

| Level | Defined by | Agent build | Done-done | Where the time goes |
|---|---|---|---|---|
| **Initiative** (new) | A set of ADRs; a roadmap phase | — | Weeks to a month | Human decisions |
| **Epic** | One design doc; one PR | 1–3 days | ≈ 1 week (4 days to 2.5 weeks) | Verification, CI/CD, staging |
| **Story** | One commit; 3–12 tasks | 1–2 hours | ≈ 1 day | Verification passes, gates |
| **Task** | One TDD cycle | Minutes | Minutes | — |

A two-week sprint is too long for the build and meaningless for the tail. Stories are built in an afternoon; epics stabilize on a schedule set by production, not by a calendar. Continuous flow fits this better than time-boxed iterations — with a work-in-progress limit on *human decisions*, since those are what actually block.

The new top level matters. Above the epic sits the **initiative**: a structural change defined by a handful of ADRs and delivered as a sequence of epics over weeks. That's where the human's architectural time goes, and it's the right level for roadmaps and stakeholder conversations.

## Code Review: From Ceremony to Sampling

Nobody reads every line anymore. On my project I was effectively the only reviewer, and reading every PR was the one part of the loop that scaled with me instead of with the agents. On a team, pretending otherwise is how review turns into rubber-stamping. The question is where human attention goes.

**Move the mandatory checkpoint upstream, from the pull request to the plan.** In my pipeline, a human approves every plan — the files it touches, the tasks, the tests that define done — before any code is written. After that, automated review, the full gate, and live execution run without me. Sixty-nine percent of plans verify on the first pass, and nearly all the rest on the second. Humans review 100% of plans; machines review 100% of code; humans *sample* the code.

The sample should be weighted by risk, not random:

- **Always reviewed:** authentication, permissions, migrations, public contracts, infrastructure — exactly where the bugs cluster.
- **Sampled lightly:** application code following an established pattern, already held in shape by guardrails.
- **Reviewed as a pattern, once:** the first instance of a new kind of component, which becomes the reference the rest follow.

This is statistical quality control, the way manufacturing has done it for a century. It is also a Waterfall-style sign-off on design — but per story, and measured in minutes.

## Estimation: Retire Story Points

In my data, 73% of stories were a 3 or a 5, and points barely correlated with the work actually required. Points measured human effort. Human effort is no longer what varies.

What varies is **human attention and operational risk**. Score work on five axes:

| Axis | 1 — Low | 2 — Medium | 3 — High |
|---|---|---|---|
| **Decisions** — human calls the work needs | None; the plan is obvious | One or two open questions | Needs an ADR, or three-plus decisions |
| **Novelty** — pattern-following or pattern-setting | Follows a gold-standard reference | Extends an existing pattern | Sets a new pattern |
| **Operational surface** — what it touches outside code | Code only | CI, config, generated artifacts | Cloud, identity, permissions, data |
| **Blast radius** — cost of being wrong | Internal and reversible | Shared library or internal API | Migration, auth, public contract |
| **Context cost** — breadth the agent must hold | One tier | Two or three tiers | Cross-cutting; high tokens |

The total, from 5 to 15, sets a class — and the class says how to run the work, not just how big it is:

| Score | Class | How to run it | Expect |
|---|---|---|---|
| 5–7 | **Delegate** | Agent-led; plan approval; light sampled review | Story-sized; done in about a day |
| 8–10 | **Design first** | Human writes or approves an ADR; then delegate | A few stories; verification may loop |
| 11–12 | **Gate and soak** | Guards before code; full review of risky files; staging soak | Epic-sized; budget a week including the tail |
| 13–15 | **Spike** | Human-led, timeboxed; split before building | Unknown until the spike returns |

Two of the axes do most of the work. Plotting them places the epics from the previous post:

{{< mermaid >}}
quadrantChart
    title Where an epic's time goes
    x-axis Code only --> Cloud and identity
    y-axis Follows a pattern --> Sets a pattern
    quadrant-1 Spike
    quadrant-2 Design first
    quadrant-3 Delegate
    quadrant-4 Gate and soak
    Lint-gate epic: [0.2, 0.3]
    Localization epic: [0.6, 0.2]
    Observability epic: [0.85, 0.7]
    CLI rebuild: [0.3, 0.9]
{{< /mermaid >}}

The lint-gate epic — pure code, extending existing patterns — closed in four days with no tail. The observability epic — a new service with its own infrastructure — took two and a half weeks. The CLI rebuild set new patterns and needed a design phase before any agent touched it.

**Tokens belong in the model, but as a design signal.** Token cost per story varied fourfold in my sessions, and nearly all of it was the agent re-reading context. Expensive stories are usually crossing too many boundaries. Track tokens per story to find coupling, not to measure effort.

Calibrate the thresholds to your own history; mine are a starting point. The structural limits I'd keep fixed: 3–12 tasks per story, one commit per story, one design doc per epic. A story that needs a thirteenth task is two stories.

**The estimation meeting becomes a decision meeting.** Planning poker asked "how much effort?" The new questions are: What do we need to decide? Does a reference implementation exist? What does this touch outside the code? Clear the open decisions, set the review budget, flag high-surface work for a staging soak — and let throughput follow. A team's capacity is bounded by how many decisions it can make well in a week, not by how many points it can burn.

## Retrospectives: Output Artifacts, Not Action Items

The output of a retro used to be a list of action items that evaporated by the next sprint. Now it can be committed.

When something goes wrong, the fix lands at the right rung: a skill gets a new step, a rule gets a new line, a guard gets a new row, a ratchet gets a lower ceiling. Those changes are versioned and enforced on every agent session from then on. Process improvement stops depending on people remembering what they agreed to.

Where those artifacts live matters too. **Process is global; theory is local; commodity work is off-the-shelf.** The team's workflow — plan, implement, verify; write an ADR; decompose an epic — should be a small set of shared skills, the same in every repository. Each codebase's theory — what a valid service looks like *here* — lives with that codebase. Off-the-shelf skills handle commodity tasks. And anything that can be checked graduates from a skill into a guard.

## Here's the Loop

Put together, the retuned process looks like this:

{{< mermaid >}}
flowchart TD
    D[Decision meeting<br/>ADRs, open questions] --> P[Plan approval<br/>human gate]
    P --> B[Agent build<br/>TDD per task]
    B --> G[Guardrails<br/>lints, guards, ratchets]
    G -->|fail| B
    G --> R[Risk-weighted<br/>sampled review]
    R --> S[Staging soak<br/>stable = done]
    S --> T[Retro<br/>skills, rules, guards]
    T --> G
    T --> D
{{< /mermaid >}}

Two loops matter. The inner one — build, check, fix — runs without a human and closes in minutes. The outer one — retro back into guardrails and decisions — is where the team gets better, and it is the part Agile always cared about most.

## Metrics: Retire Velocity

Velocity measured effort burned. It means nothing when effort is nearly free. Track instead:

- **Lead time to stable** — first commit to stabilized in staging, not to merge.
- **Verification passes per plan** — the rework rate; mine averages about 1.4.
- **Fixes per feature, by category** — where the system is weak. For me, infrastructure.
- **Tokens per story** — a coupling signal for the architecture.
- **Decisions per week** — the real capacity limit.
- **Change failure rate and time to restore** — the DORA metrics from [*Accelerate*](https://itrevolution.com/product/accelerate/), which were always the right outcome measures.

## Re-reading the Manifesto

The Agile Manifesto's four values still hold. Two of them read differently now.

| Value | Then | Now |
|---|---|---|
| Individuals and interactions over processes and tools | People over bureaucracy | Still true — and the most valuable interaction is the decision, which is now most of the job |
| **Working software over comprehensive documentation** | Don't write documents nobody reads | Documentation is what the agent builds from. ADRs, plans, rules, and skills are how working software gets made |
| Customer collaboration over contract negotiation | Stay close to the user | Unchanged — and acceptance criteria now have to be precise enough for a machine to check |
| **Responding to change over following a plan** | Don't lock in a plan | Plans are cheap to write and cheap to rewrite. Approve the plan, follow it, change it the moment it's wrong |

## What to Change on Monday

1. **Write the theory before the first agent session.** Structure, boundaries, nouns, one reference module per tier.
2. **Make working agreements build failures.** Then invest in climbing the guardrail ladder.
3. **Redefine done** as machine-checked and stable in staging.
4. **Move the human gate to the plan** and sample code review by risk.
5. **Replace planning poker with a decision meeting**, and score work on decisions, novelty, operational surface, blast radius, and context cost.
6. **Drop the sprint for flow**, with a WIP limit on open decisions.
7. **Make retros commit something** — a skill, a rule, a guard, a ratchet.

In [the talk I gave at Georgia Tech](/presentations/enforcing-engineering-discipline.html), I argued that AI doesn't fix a broken process — it accelerates whatever process you already have. Agile's ceremonies were tuned for expensive code. Run them unchanged at machine speed and AI amplifies their overhead along with everything else. Retune them around decisions, theory, and guardrails, and the leverage is real.

The discipline is yours. The enforcement is code.
