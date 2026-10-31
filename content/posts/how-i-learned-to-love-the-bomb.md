---
title: "How I Learned to Love the Bomb"
date: 2026-02-22
draft: false
description: "A developer's journey from AI skepticism to building an entire engineering system around it. Adapt or die — and what adaptation actually looks like."
images:
  - "images/og/how-i-learned-to-love-the-bomb.png"
tags: ["ai", "software-engineering", "developer-tools", "claude", "cursor"]
keywords: ["ai tools", "software engineering", "developer productivity", "claude ai", "cursor editor"]
---

I spent the better part of two decades building software the old-fashioned way. I read the docs. I typed every line. I had opinions about whitespace. When GitHub Copilot showed up in 2021 and started finishing my sentences, my reaction was roughly the same as a novelist watching someone autocomplete their paragraphs: *No thank you.*

I wasn't alone. The developers I respected most were skeptical. The arguments wrote themselves: it hallucinates, it produces subtly wrong code, it doesn't understand architecture, it makes junior developers worse by letting them skip the part where they actually learn. I repeated these arguments often, and I believed them. Some of them are still true.

But here's what happened: I was wrong about the conclusion.

## The Resistance

My skepticism wasn't uninformed. I'd spent years building natural language systems — first at [ClearGraph](https://www.crunchbase.com/organization/cleargraph), then at [Tableau](https://www.tableau.com/), then at [Salesforce](https://www.salesforce.com/). I understood language models. I knew what they were good at (pattern matching, surface fluency) and what they were bad at (reasoning, consistency, knowing when they don't know something). When people told me GPT-3 was going to replace software engineers, I had the technical background to explain exactly why that was wrong.

And it was wrong — in 2022. The problem is that I let being right about the timeline make me complacent about the trajectory.

While I was explaining why AI-generated code was unreliable, the tools got better. While I was pointing out hallucination rates, context windows grew from 4K to 128K to effectively unlimited. While I was insisting that real engineering required human judgment, a generation of developers started shipping production code with AI assistance and — here's the part that stung — some of them were moving faster than I was.

## Bill Kennedy

The person who changed my mind was [Bill Kennedy](https://www.ardanlabs.com/about/).

Bill runs [Ardan Labs](https://www.ardanlabs.com/) and has spent years teaching Go to engineers who care about doing it right. He's not a hype guy. He's the opposite — rigorous, opinionated about engineering discipline, allergic to shortcuts. So when Bill started talking seriously about AI-assisted development, I couldn't dismiss it the way I'd dismissed the Twitter evangelists. This wasn't someone chasing a trend. This was someone who had looked at the tools, measured the output, and concluded that the leverage was real — *if* you brought the same discipline to AI-assisted code that you'd bring to any other code.

Bill's argument wasn't "AI writes code for you." It was closer to: "AI is a force multiplier for engineers who already know what good looks like." The standards don't relax. The quality bar doesn't drop. You just move faster at the parts that were never the hard parts to begin with.

That distinction mattered to me. It was the difference between "replace your judgment" and "free up your judgment for the work that actually needs it."

## Georgia Tech

I didn't start using AI tools seriously until I joined [Georgia Tech](https://www.gatech.edu/) as Research Faculty. Through ClearGraph, Tableau, Salesforce, co-founding [PerceptivePanda](https://web.archive.org/web/20250119063219/https://www.perceptivepanda.com/), the [Zapier](https://zapier.com/) acquisition — all of that was done the old way. Every line written by hand.

At Georgia Tech, the context shifted. I was working across multiple codebases, multiple languages, moving between research and engineering. The surface area was broader than anything I'd dealt with at a single company. Bill's words kept echoing: *force multiplier for engineers who already know what good looks like.*

So I started small. First it was autocomplete. Fine, let Copilot finish the obvious boilerplate. I'm not going to type `if err != nil { return fmt.Errorf("failed to parse config: %w", err) }` for the ten thousandth time if a machine will do it for me. That's not intelligence, that's typing.

Then it was exploration. I started asking Claude questions about codebases I was unfamiliar with. Not to write code — just to orient. What does this module do? Where are the entry points? What's the error handling strategy? It turned out that having a conversation with something that had read every Go package on GitHub was genuinely useful for navigating unfamiliar territory.

Then it was drafting. I'd describe a function signature, the expected behavior, the edge cases. The model would produce a first draft. I'd rewrite 60% of it. Then 40%. Then 20%. The drafts kept getting better, and I kept getting faster.

Within months, AI tools were load-bearing infrastructure in my workflow. The question had shifted from *should I use these tools* to *how do I use them without losing the things that matter*.

## The Problem with "Vibe Coding"

Here's what I didn't want to become: a prompt jockey. Someone who types "build me an app" into a chat window and ships whatever comes back. The industry has a word for this now — *vibe coding* — and I find it genuinely dangerous.

Not because the output is always bad. Sometimes it's remarkably good. The danger is that it divorces the developer from the decisions. When you let a model choose your architecture, your error handling strategy, your test coverage, your dependency graph — you haven't saved time. You've accumulated technical debt at machine speed. You just don't know it yet, because the code runs and the tests (if there are any) pass.

The developers who are going to thrive with AI are not the ones who prompt the hardest. They're the ones who know what good engineering looks like and refuse to accept anything less, regardless of who — or what — wrote the code.

## The System

So I built a system. Not a product, not a framework — a set of engineering standards that I enforce across every AI tool I use. The same rules, the same quality gates, the same architectural patterns, whether the code is coming from [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://www.cursor.com/), or [Kilo Code](https://kilocode.ai/).

The core of it is a document I call my global standards. It lives in my dotfiles and gets symlinked into every tool's configuration directory. It specifies:

**Process** — every structural change follows a pipeline: ADR first, then architecture diagrams, then decompose into stories, then plan, then implement, then verify. AI doesn't get to skip steps.

**Quality gates** — before every commit, four things must pass: formatting, linting, type checking, and unit tests. No exceptions. No "I'll fix it later." The AI writes the code, and the code meets the same bar as anything I'd write by hand.

**Architecture patterns** — clean layered architecture with dependency injection, repository pattern for data access, early returns over nested conditionals. Separate your persistence models from your domain entities from your DTOs. These aren't suggestions. They're constraints.

**Anti-patterns** — files over 800 lines, functions over 50 lines, nesting deeper than 4 levels, hardcoded secrets, mutable shared state, `any` types without narrowing, import cycles. If the AI produces any of these, it gets rejected. Every time.

Each language gets its own standards file. Python means `uv` for package management, `ruff` for linting, `basedpyright` for type checking, `pytest` with markers per layer, `attrs` classes for models, Google-style docstrings, and property-based testing with `hypothesis`. Go means `gofumpt` for formatting, `golangci-lint` for linting, table-driven tests with `t.Run()` subtests, small consumer-defined interfaces, and structured logging with `zap`. TypeScript means `pnpm`, strict `tsc`, `vitest`, functional React components, and Tailwind utilities — never `@apply`.

These aren't aspirational documents. They're enforced. When I open Claude Code, it reads my `CLAUDE.md` and knows the rules before I type a single prompt. When I open Cursor, the `.cursorrules` file tells it how this specific project works — down to the import paths for the error hierarchy and the structured logging package. When I open Kilo Code, the same standards are waiting in `~/.kilocode/rules/`.

The result is that I get three different AI tools, built by three different companies, all producing code that looks like *my* code. Same patterns. Same conventions. Same quality bar.

## What It Actually Looks Like

Here's a typical session. I'm adding a new domain entity to a Go service. I open Claude Code and describe what I need:

> Add a `workspace` domain entity with CRUD operations, Ent repository, and HTTP controller. Follow the existing `user` domain as the reference implementation.

Claude Code reads my standards, examines the existing `user` domain for patterns, and produces a plan. Not code — a plan. It identifies the files it needs to create, the interfaces it needs to implement, the tests it needs to write. I review the plan. I adjust it. Then it executes.

The code that comes out has structured logging with `zap`, errors wrapped with `cockroachdb/errors`, context as the first parameter, table-driven tests, the full layered architecture from `cmd` to `controller` to `core` to `foundation`. Not because the model is brilliant, but because I told it exactly what good looks like and gave it a reference implementation to follow.

When something doesn't meet the bar, I reject it. The model learns from the correction within the session. Over time, my standards files get more precise based on the patterns of mistakes I see. It's a feedback loop: the AI makes me more explicit about what I want, and that explicitness makes the AI more reliable.

## TDD Still Matters

One of the standards I enforce hardest is TDD. Write the failing test first. Red, green, refactor. Every AI tool I use knows this rule.

This matters more with AI-generated code, not less. When a human writes code, they have a mental model of the invariants. When a model writes code, it has a statistical approximation of what code in this context usually looks like. Tests are the mechanism that bridges that gap. If the model's implementation satisfies the tests I wrote — tests that encode my understanding of the requirements — then I have confidence in the output regardless of whether a human or a machine produced it.

The developers who skip tests because "the AI wrote it and it looks right" are going to learn expensive lessons.

## The Uncomfortable Truth

Here's the part that's hard to say: I'm faster now. Meaningfully faster. Not at the parts of programming that matter most — design, architecture, understanding the problem — but at the mechanical translation of decisions into working code. The part where you know exactly what you want and you need to produce 400 lines of well-structured, well-tested, well-documented implementation. That part used to take an afternoon. Now it takes twenty minutes.

This means one of two things. Either the mechanical translation was never where my value as an engineer lived, or I was spending a lot of my career on work that didn't require my full attention. Probably both.

The developers who are threatened by this are the ones whose primary skill is typing speed and syntax recall. The developers who are amplified by it are the ones whose primary skill is judgment: knowing what to build, how to structure it, what trade-offs to accept, and — critically — knowing when the AI's output is wrong.

## What I Got Wrong

I got two things wrong about AI and software engineering.

First, I thought the quality floor was fixed. I assumed that AI-generated code would always be mediocre and that serious engineers would always need to rewrite it. What I didn't anticipate was that the quality floor is a function of the constraints you impose. Unconstrained, yes, AI writes mediocre code. But with 70 pages of standards, enforced quality gates, reference implementations, and a human who knows what good looks like? The floor rises dramatically.

Second, I thought adoption was binary. Either you're a "real" developer who writes everything by hand, or you're a prompt engineer who ships slop. The reality is a spectrum, and the interesting part of that spectrum is where human judgment and AI capability overlap. That's where the leverage is.

## Adapt or Die

The tools exist. They're getting better. The developers who refuse to engage with them aren't preserving craftsmanship — they're ceding ground to developers who use AI *and* have good judgment.

The answer isn't to abandon your standards. It's to encode them. Write them down. Make them machine-readable. Enforce them automatically. Then use every tool available to you — AI included — to ship better software faster, without compromising on the things that actually matter.

Bill was right. The leverage is real. But only if you bring the discipline with you.

I still have opinions about whitespace. I still believe in TDD. I still think architecture matters more than velocity. I just let a machine handle the typing.
