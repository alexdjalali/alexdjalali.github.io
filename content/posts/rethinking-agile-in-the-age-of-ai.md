---
title: "Rethinking Agile in the Age of AI"
date: 2026-10-28T12:30:00-04:00
draft: false
description: "Agile's values still hold, but its practices were tuned for a world where code was expensive. What six months of AI-driven development suggests about roles, design, review, estimation and the Definition of Done."
images:
  - "images/og/rethinking-agile-in-the-age-of-ai.png"
tags: ["ai", "software-engineering", "process"]
keywords: ["agile and ai", "rethinking agile", "story points", "ai estimation", "definition of done", "code review sampling", "agile manifesto"]
series: ["AI-Assisted Engineering"]
---

Agile as most teams practice it was built for a pace of work that AI has quietly made obsolete, and I don't think most teams have noticed yet.

In [Six Months of Enterprise Development with AI](/posts/six-months-of-enterprise-development-with-ai/) I reported what happened when agents wrote most of the code on a production platform: 1,200 commits, 594 stories, 117 Architecture Decision Records, and a set of lessons and missteps backed by the git history. Here I want to ask what those lessons mean for how teams work.

My answer, in short, is that Agile's values still hold but its *practices* were tuned for a world in which code was expensive to write. We had two-week sprints because a story took days, story points because human effort was the scarce resource, and line-by-line review because every line had a human author. AI made code cheap and decisions expensive, and the practices have to be retuned around that. (A few of the retunings, I should warn you, borrow without apology from the up-front discipline Agile was reacting against.)

In [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/) I wrote that every methodology "from waterfall to agile to shape-up is a variation on this sequence. The differences are in the feedback loops and the batch sizes, not in the fundamental ordering." AI changed both the batch sizes and the feedback loops, and what follows is my attempt to say what has to change with them.

## Roles: Everyone Moves Up a Level

Engineers, first of all, become architects. A story takes an agent an hour or two, and a task takes minutes. What doesn't compress is judgment: which tier owns this logic, whether this is a new pattern, whether the change can be undone. Fred Brooks called this *essential* complexity, as opposed to the *accidental* complexity of expressing it in code, and agents absorb the accidental part rather well. The essential part is now the job. Brooks's *surgical team* (one surgeon, and a team that amplifies them) is a far better model for AI-assisted development than the interchangeable developers that velocity charts quietly assume.

Product owners, in turn, become spec writers. An acceptance criterion like "users can manage their settings" was fine when a developer could walk over and ask what it meant. An agent won't ask; it will guess. So acceptance criteria have to be precise enough for a machine to check, which means they look more and more like test cases.

And juniors need a new path. The obvious objection is this: if engineers have to be architects, how does anyone build architectural judgment without years of implementation behind them? I don't think the answer is to keep juniors typing. It's to teach architecture directly, by having them inherit real systems, read those systems through their types and boundaries, write ADRs, and defend their decisions in front of peers. That is the premise of [the course I designed](/posts/professional-software-engineering-for-ai-and-distributed-systems/), in which students inherit a deliberately broken system and finish the semester with an architecture defense.

## Design: Emergent Architecture Doesn't Survive Machine Speed

"Let the architecture emerge" worked when a person wrote every line, because that person noticed the duplication around the third copy. An agent will cheerfully write the thirty-second.

I'm not speaking hypothetically. In the [previous post](/posts/six-months-of-enterprise-development-with-ai/#misstep-1-building-without-a-theory) I described the one component I built without a theory: a developer CLI that grew to 96,000 lines, with 32 different implementations of the same kind of work, where 51% of commits were fixes or refactors, against 32% in the parts of the codebase that had a theory from day one.

So here is the one thing I think Agile should borrow from Waterfall: decide the structure first. Before the first agent session, a team needs a theory of the codebase (its repository structure, its tier boundaries, the nouns of its domain, a reference implementation for each kind of component), written down somewhere the agent will read it. I don't mean a 200-page specification. I mean a few pages, an ADR for each structural decision, and one gold-standard module per tier. Everything after that can stay as iterative as you like.

This is also why the choice of language matters more than it used to, and not because "fast" languages are fast. Strict languages put the compiler in the review loop. Go's import paths and compile-time interface assertions, or typed Python with a strict checker and an import linter, give the agent feedback it can't argue with.

## The Definition of Done: Machine-Checked and Stable

Two of the missteps from the previous post change what "done" ought to mean.

The first is that done has to be machine-checked. The layer model was in the agent's rules from day one, and the agent reported conformance from day one. An audit in month three found the connective tissue riddled with violations, and mechanical enforcement only arrived in months four through six. An unenforced rule is a suggestion, and agents report on suggestions as though they were facts. A team's working agreements ("we use the repository pattern," "services don't import controllers") used to be enforced by social pressure and code review, and at machine speed neither of those scales. If a rule matters, it should be a build failure.

That turns working agreements into code: import guards generated from the layer model, guards that check invariants across files, ratchets that only go down, and generators that make the right shape the default. In the previous post I called this [a ladder of guardrails](/posts/six-months-of-enterprise-development-with-ai/#lesson-2-guardrails-are-the-process). Climbing it is now a core engineering activity, and code review shifts from *finding* violations to *writing the checks* that make them impossible.

The second is that done means stable in staging, not merged. Three-quarters of the fixes in my data were not application logic at all; they were cloud configuration, permissions, drift and CI. Per feature, drift needed 3.5 fixes and permissions 1.7, against 0.39 for application code. An epic that merges in a day can go on producing bug fixes for six weeks, so if "done" means merged, a team will systematically believe that AI is ten times faster than it really is.

## Sprints: The Build Fits in an Afternoon, the Tail Doesn't Fit in a Sprint

The hierarchy of epic, story and task survives, but each level now needs two numbers: how long the agent takes to build it, and how long until it's stable.

| Level | Defined by | Agent build | Done-done | Where the time goes |
|---|---|---|---|---|
| **Initiative** (new) | A set of ADRs; a roadmap phase | — | Weeks to a month | Human decisions |
| **Epic** | One design doc; one PR | 1–3 days | ≈ 1 week (4 days to 2.5 weeks) | Verification, CI/CD, staging |
| **Story** | One commit; 3–12 tasks | 1–2 hours | ≈ 1 day | Verification passes, gates |
| **Task** | One TDD cycle | Minutes | Minutes | — |

A two-week sprint, then, is too long for the build and meaningless for the tail. Stories get built in an afternoon, while epics stabilize on a schedule set by production rather than by the calendar. Continuous flow fits this far better than time-boxed iterations do, provided you put a work-in-progress limit on *human decisions*, since those are what actually block.

The new top level matters, too. Above the epic sits what I've been calling the initiative: a structural change defined by a handful of ADRs and delivered as a sequence of epics over several weeks. That is where the human's architectural time goes, and it's the right level for roadmaps and conversations with stakeholders.

## Code Review: From Ceremony to Sampling

Let's be honest: nobody reads every line anymore. On my project I was effectively the only reviewer, and reading every pull request was the one part of the loop that scaled with me rather than with the agents. On a team, pretending otherwise is how review turns into rubber-stamping. The real question is where human attention should go.

My answer is to move the mandatory checkpoint upstream, from the pull request to the plan. In my pipeline a human approves every plan (the files it touches, its tasks, the tests that define done) before any code is written. After that, automated review, the full gate and live execution run without me. Sixty-nine percent of plans verify on the first pass, and nearly all the rest on the second. So humans review every plan, machines review every line of code, and humans *sample* the code.

The sample should be weighted by risk rather than drawn at random:

- **Always reviewed:** authentication, permissions, migrations, public contracts, infrastructure (which is exactly where the bugs cluster).
- **Sampled lightly:** application code following an established pattern, already held in shape by guardrails.
- **Reviewed as a pattern, once:** the first instance of a new kind of component, which becomes the reference the rest follow.

This is just statistical quality control, which manufacturing has practiced for a century. It is also, I'll concede, a Waterfall-style sign-off on design, except that it happens per story and takes minutes.

## Estimation: Retire Story Points

In my data, 73% of stories were scored a 3 or a 5, and the points barely correlated with the work actually required. Points measured human effort, and human effort is no longer what varies.

What varies is human attention and operational risk, so I score work on five axes instead:

| Axis | 1 — Low | 2 — Medium | 3 — High |
|---|---|---|---|
| **Decisions** — human calls the work needs | None; the plan is obvious | One or two open questions | Needs an ADR, or three-plus decisions |
| **Novelty** — pattern-following or pattern-setting | Follows a gold-standard reference | Extends an existing pattern | Sets a new pattern |
| **Operational surface** — what it touches outside code | Code only | CI, config, generated artifacts | Cloud, identity, permissions, data |
| **Blast radius** — cost of being wrong | Internal and reversible | Shared library or internal API | Migration, auth, public contract |
| **Context cost** — breadth the agent must hold | One tier | Two or three tiers | Cross-cutting; high tokens |

The total, which runs from 5 to 15, sets a class, and the class tells you how to run the work rather than merely how big it is:

| Score | Class | How to run it | Expect |
|---|---|---|---|
| 5–7 | **Delegate** | Agent-led; plan approval; light sampled review | Story-sized; done in about a day |
| 8–10 | **Design first** | Human writes or approves an ADR; then delegate | A few stories; verification may loop |
| 11–12 | **Gate and soak** | Guards before code; full review of risky files; staging soak | Epic-sized; budget a week including the tail |
| 13–15 | **Spike** | Human-led, timeboxed; split before building | Unknown until the spike returns |

In practice two of the axes do most of the work, and plotting them places the epics from the previous post rather neatly:

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

The lint-gate epic (pure code, extending existing patterns) closed in four days with no tail. The observability epic (a new service with its own infrastructure) took two and a half weeks. The CLI rebuild set new patterns and needed a design phase before any agent touched it.

Tokens belong in the model too, though as a design signal rather than a measure of effort. Token cost per story varied fourfold across my sessions, and nearly all of the variation was the agent re-reading context. An expensive story is usually one that crosses too many boundaries, so tracking tokens per story is a good way to find coupling.

You should calibrate the thresholds to your own history; mine are only a starting point. The structural limits I would keep fixed are 3 to 12 tasks per story, one commit per story and one design doc per epic. A story that needs a thirteenth task is two stories.

All of which turns the estimation meeting into a decision meeting. Planning poker asked "how much effort?" The new questions are what we need to decide, whether a reference implementation exists, and what the work touches outside the code. Clear the open decisions, set the review budget, flag anything with a large operational surface for a staging soak, and let throughput follow. A team's capacity is bounded by how many decisions it can make well in a week, not by how many points it can burn.

## Retrospectives: Output Artifacts, Not Action Items

The output of a retro used to be a list of action items that had evaporated by the next sprint. Now the output can be committed.

When something goes wrong, the fix lands on the right rung of the ladder: a skill gets a new step, a rule gets a new line, a guard gets a new row, or a ratchet gets a lower ceiling. Those changes are versioned and enforced in every agent session from then on, so improving the process no longer depends on people remembering what they agreed to.

Where those artifacts live matters as well. My rule of thumb is that process is global, theory is local, and commodity work is off the shelf. The team's workflow (plan, implement, verify; write an ADR; decompose an epic) should be a small set of shared skills, the same in every repository. Each codebase's theory, meaning what a valid service looks like *here*, lives with that codebase. Off-the-shelf skills handle the commodity tasks. And anything that can be checked eventually graduates from a skill into a guard.

## The Loop

Put together, the retuned process looks something like this:

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

There are two loops worth noticing. The inner one (build, check, fix) runs without a human and closes in minutes. The outer one, from the retro back into guardrails and decisions, is where the team actually gets better, and it is the part Agile always cared about most.

## Metrics: Retire Velocity

Velocity measured effort burned, which means very little once effort is nearly free. These are what I track instead:

- **Lead time to stable:** from the first commit to stable in staging, not to the merge.
- **Verification passes per plan:** the rework rate; mine averages about 1.4.
- **Fixes per feature, by category:** where the system is weak (for me, infrastructure).
- **Tokens per story:** a signal of coupling in the architecture.
- **Decisions per week:** the real limit on capacity.
- **Change failure rate and time to restore:** the DORA metrics from [*Accelerate*](https://itrevolution.com/product/accelerate/), which were always the right outcome measures.

## Re-reading the Manifesto

I went back and re-read the Agile Manifesto while writing this. Its four values still hold, as far as I'm concerned, but two of them read rather differently now.

| Value | Then | Now |
|---|---|---|
| Individuals and interactions over processes and tools | People over bureaucracy | Still true, and the most valuable interaction is the decision, which is now most of the job |
| **Working software over comprehensive documentation** | Don't write documents nobody reads | Documentation is what the agent builds from. ADRs, plans, rules, and skills are how working software gets made |
| Customer collaboration over contract negotiation | Stay close to the user | Unchanged, though acceptance criteria now have to be precise enough for a machine to check |
| **Responding to change over following a plan** | Don't lock in a plan | Plans are cheap to write and cheap to rewrite. Approve the plan, follow it, change it the moment it's wrong |

## What to Change on Monday

If you want somewhere to start, this is roughly the order I would go in:

1. Write the theory before the first agent session: the structure, the boundaries, the nouns, and one reference module per tier.
2. Make working agreements into build failures, then keep climbing the guardrail ladder.
3. Redefine done as machine-checked and stable in staging.
4. Move the human gate to the plan, and sample code review by risk.
5. Replace planning poker with a decision meeting, and score work on decisions, novelty, operational surface, blast radius and context cost.
6. Drop the sprint in favor of flow, with a limit on open decisions.
7. Make every retro commit something: a skill, a rule, a guard or a ratchet.

In [the talk I gave at Georgia Tech](/presentations/enforcing-engineering-discipline.html), I argued that AI doesn't fix a broken process; it accelerates whatever process you already have. Agile's ceremonies were tuned for expensive code, and if you run them unchanged at machine speed, AI amplifies their overhead along with everything else. Retune them around decisions, theory and guardrails, and the leverage is real.

I suspect the original signatories would recognize most of this. They were, after all, reacting to a process that had stopped fitting the work, which is more or less where we find ourselves again.
