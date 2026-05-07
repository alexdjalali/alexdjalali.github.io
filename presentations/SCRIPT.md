# Screencast Script — Enforcing Engineering Discipline with AI

## Slide 1: Title

> I'm Alex Djalali. I'm research faculty at Georgia Tech, and before that I spent years as a software architect and principal engineer at Salesforce and Tableau.
>
> Today I want to talk about how AI fits into the engineering lifecycle you already believe in — not as a replacement for your judgment, but as the mechanism that enforces the discipline you've always practiced.

---

## Slide 2: The Software Engineering Lifecycle

> Every rigorous engineering team follows the same phases: architecture, design, plan, implement, test, verify, ship.
>
> This isn't new. This isn't controversial. We all agree on this.
>
> The question has never been whether this lifecycle matters. The question is whether we actually follow it — every time, under pressure, at speed. And the honest answer, for most teams, is: not always.

---

## Slide 3: The Risk: Vibe Coding

> This is what's at stake. On the left — the skipped lifecycle. Someone says "build me an app," the AI builds it, and you ship it. Architecture? The AI decided. Design? Skipped. Tests? Maybe later. The code compiles, so it must be fine. That's tech debt at machine speed.
>
> On the right — the enforced lifecycle. Architecture is a human decision. Design is human decomposition. The plan gets human approval. Implementation follows TDD with the AI executing. And verification gates are non-negotiable. That's leverage at machine speed.
>
> The danger of vibe coding isn't bad syntax — AI syntax is fine. The danger is that it lets you bypass the process that catches bad decisions.

---

## Slide 4: The Thesis

> Here's the core claim of this talk: AI doesn't replace the engineering lifecycle. It enforces it.
>
> You already know what good engineering looks like. The problem was never knowledge — it was consistency. Under deadline pressure, corners get cut. AI is the mechanism that makes your standards non-negotiable. It doesn't get tired. It doesn't skip steps on a Friday afternoon.
>
> The source of leverage isn't the AI itself. It's the constraints you put around it.

---

## Slide 5: Decide — Architecture, Design & Planning

> The lifecycle starts with decisions, not code.
>
> Architecture: you write ADRs that capture the "why" behind structural choices. AI can explore options and draft proposals, but humans decide and own the outcome.
>
> Design: epics get decomposed into stories with clear scope. AI identifies sub-tasks, but humans set the boundaries.
>
> Planning: AI reads the codebase and proposes concrete tasks. But — and this is critical — no code gets written until a human approves the plan.
>
> Judgment stays with the engineer. AI accelerates the exploration, not the decision-making.

---

## Slide 6: Build — Implementation & TDD

> Once the plan is approved, implementation follows TDD. Failing test first. Always.
>
> Red — write a failing test that encodes the requirement. Green — write the minimum code to pass. Refactor — clean up while the tests stay green.
>
> Here's why this matters so much with AI: AI-generated code is a statistical approximation of what you asked for. Tests are encoded invariants — they don't approximate, they assert. Without TDD, you're trusting a statistical approximation. With TDD, you're verifying against a specification.
>
> Tests bridge the gap between human intent and AI output.

---

## Slide 7: Ship — Verification & Delivery

> Four gates before every commit. No exceptions.
>
> Format catches style inconsistencies — auto-fixable. Lint catches code smells and anti-patterns — mostly auto-fixable. Type check catches type errors and interface mismatches — the AI fixes these. Tests catch behavioral regressions — again, the AI fixes and retries.
>
> The same bar applies regardless of who wrote the code. Human or AI — the gates don't care.
>
> Then delivery closes the loop: conventional commits, PRs that link back to the plan, full traceability from decision to epic to story to plan to PR.

---

## Slide 8: Encoding Your Standards

> So how do you actually make this work? The mechanism is simple: write your standards in a file the AI can read.
>
> For Claude Code, that's a CLAUDE.md file. For Cursor, it's a rules directory. For any project, it's a settings file. One file — readable by any AI tool — containing your language conventions, architecture rules, quality thresholds, and anti-patterns to avoid.
>
> Structure beats intelligence. A well-written standards file does more for code quality than a better model.

---

## Slide 9: Skills — Reusable Workflows as Commands

> Standards tell AI what matters. Skills tell it what to do.
>
> Skills are markdown files that encode entire workflows, invoked with a slash command. /spec runs the full plan-implement-verify cycle. /tdd runs red-green-refactor. /preflight enforces the four quality gates before every commit. /adr generates architecture decision records. /rfp decomposes epics into stories.
>
> Each skill is a structured prompt — not a script. It tells the AI what phases to follow, what gates to enforce, and what output to produce. And because they're just markdown files in your dotfiles, you can version them, share them across teams, and evolve them over time.

---

## Slide 10: Solving the Cold Start Problem

> Standards and skills handle the process. But on a greenfield project, AI still has no patterns to follow. The output is generic. This is the cold start problem.
>
> You solve it from two directions. Reference code — pull in gold-standard repos from your past projects, curate open-source examples worth following, or seed the project with one clean module. AI extrapolates from concrete examples far better than it interprets abstract rules.
>
> And templates — every document the AI produces has a defined shape. Plans have approval gates built in. Stories have acceptance criteria. Commits follow a convention. The template ensures consistent output every time.
>
> Standards set the rules. Reference code shows the patterns. Templates shape the output.

---

## Slide 11: Templates — Structured Output Every Time

> Here's what a template looks like in practice. This is the plan template — the most important one.
>
> Every feature goes through this before any code is written. Notice the approval gate at the top: "Approved: No." That means the AI cannot proceed to implementation until a human explicitly changes it to "Approved: Yes."
>
> The task structure forces explicit file paths, test files, and definitions of done. No ambiguity. No hand-waving. The template enforces the gate — no code until the plan is approved.

---

## Slide 12: The Full Lifecycle

> Here's the full pipeline — all phases connected.
>
> The key feature is the feedback loop from verification back to implementation. When the quality gates catch an issue, it doesn't end the process — it feeds back into it. The AI fixes and retries. Most features verify on the first pass. Complex changes sometimes take two or three iterations. The system handles both.
>
> And you enter wherever makes sense. Not everything needs an ADR. A small bug fix can start at planning. A structural change starts at architecture. The lifecycle is a directed graph, not a rigid waterfall.

---

## Slide 13: AI Amplifies What's Already There

> This is the slide for the skeptics.
>
> On the left — good discipline plus AI. Explicit architecture leads to a consistent codebase. TDD leads to reliable implementations. Quality gates prevent regression. Clear standards produce reproducible output. That's leverage at scale.
>
> On the right — bad discipline plus AI. No architecture means an inconsistent mess, just faster. No tests means confident bugs. No gates means tech debt at machine speed. Vague standards mean random output. That's liability at scale.
>
> You play like you practice. AI doesn't fix a broken process. It accelerates whatever process you already have.

---

## Slide 14: Actionable Takeaways

> Here's what you can do Monday morning.
>
> One — write your standards down. If they only live in people's heads, AI can't follow them.
>
> Two — seed with reference code. One gold-standard module teaches AI more than a page of rules.
>
> Three — pick one quality gate and make it non-negotiable. Start with formatting. It's the easiest win.
>
> Four — enforce TDD. AI-generated code needs tests more, not less.
>
> Five — separate judgment from execution. Humans approve plans. AI implements them.
>
> One standards file plus one reference module. That's the minimum viable version. Start there.

---

## Slide 15: Close

> The lifecycle hasn't changed. It's the same phases we've always agreed on. AI is the mechanism that makes it enforceable — consistently, without fatigue, without shortcuts.
>
> The discipline is yours. The enforcement is automated.
>
> My dotfiles repo is linked here — it has the full CLAUDE.md, all the standards files, every template, and every skill I showed today. And my email is on screen if you want to follow up.
>
> Thanks for watching.
