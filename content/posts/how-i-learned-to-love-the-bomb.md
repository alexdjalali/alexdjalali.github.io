---
title: "How I Learned to Love the Bomb"
date: 2026-02-22
draft: false
description: "Why I went from skeptic of AI-assisted programming to building an engineering system around it, and why what won me over was not the models but the discipline you wrap around them."
images:
  - "images/og/how-i-learned-to-love-the-bomb.png"
tags: ["ai", "software-engineering", "developer-tools", "claude"]
series: ["AI-Assisted Engineering"]
keywords: ["ai tools", "software engineering", "developer productivity", "claude ai", "cursor editor"]
---

When GitHub Copilot showed up in 2021 and started finishing my sentences, I reacted roughly the way a novelist would if someone offered to autocomplete their paragraphs: politely, and with no intention of ever using it. I had spent the better part of two decades building software the old-fashioned way. I read the docs, I typed every line, and I had opinions about whitespace (I still do, for the record).

I was hardly alone. The developers I respected most were skeptical, and the arguments more or less wrote themselves. It hallucinates. It produces code that is subtly wrong in ways that cost you an afternoon to find. It has no sense of architecture. It makes junior developers worse by letting them skip the part where they actually learn something. I made these arguments often, and I believed them. Some of them are still true. Where I went wrong was the conclusion I drew from them.

## The Resistance

My skepticism was not uninformed, or so I told myself. I had spent years building natural language systems, first at [ClearGraph](https://www.crunchbase.com/organization/cleargraph), then at [Tableau](https://www.tableau.com/), then at [Salesforce](https://www.salesforce.com/) (and I had a PhD in linguistics from Stanford to fall back on). I understood language models, or at least I understood what they were good at (pattern matching, surface fluency) and what they were bad at (reasoning, consistency, knowing when they don't know something). When people told me GPT-3 was going to replace software engineers, I could explain, at length and with citations, why that was wrong.

And in 2022 it *was* wrong. The trouble is that I let being right about the timeline make me complacent about the trajectory. While I was explaining why AI-generated code was unreliable, the tools got better. While I was pointing out hallucination rates, context windows went from 4K tokens to 128K to something that is, for practical purposes, unlimited. And while I was insisting that real engineering required human judgment, a generation of developers started shipping production code with AI assistance, and some of them (this is the part that stung) were moving faster than I was.

## Bill Kennedy

The person who changed my mind was [Bill Kennedy](https://www.ardanlabs.com/about/).

Bill runs [Ardan Labs](https://www.ardanlabs.com/) and has spent years teaching Go to engineers who care about doing it right. He is, to put it mildly, not a hype guy. He is rigorous, opinionated about engineering discipline, and allergic to shortcuts. So when Bill started talking seriously about AI-assisted development, I couldn't wave it away the way I had waved away the evangelists on Twitter. Here was someone who had looked at the tools, measured what came out of them, and concluded that the leverage was real, provided you brought the same discipline to AI-assisted code that you would bring to any other code.

His argument was never "AI writes code for you." It was closer to this: AI is a force multiplier for engineers who already know what good looks like. The standards don't relax, and the bar doesn't drop. You simply move faster through the parts that were never the hard parts to begin with. That distinction mattered a great deal to me, because it is the difference between replacing your judgment and freeing it up for the work that actually needs it.

## Georgia Tech

Even so, I didn't start using these tools in earnest until I joined [Georgia Tech](https://www.gatech.edu/) as Research Faculty. ClearGraph, Tableau, Salesforce, co-founding [PerceptivePanda](https://web.archive.org/web/20250119063219/https://www.perceptivepanda.com/), the [Zapier](https://zapier.com/) acquisition: all of that was done the old way, every line written by hand.

At Georgia Tech the context shifted. I was working across several codebases and several languages, moving back and forth between research and engineering, and the surface area was broader than anything I had dealt with inside a single company. Bill's phrase kept coming back to me (*a force multiplier for engineers who already know what good looks like*), so I started small.

First it was autocomplete. Fine, I thought, let Copilot finish the obvious boilerplate; I am not going to type `if err != nil { return fmt.Errorf("failed to parse config: %w", err) }` for the ten-thousandth time if a machine will do it for me. That isn't intelligence, it's typing. Then it was exploration. I started asking Claude about codebases I didn't know: what a module does, where the entry points are, how errors are handled. Having a conversation with something that has read more or less every Go package on GitHub turns out to be a genuinely useful way to find your bearings in unfamiliar territory. Then it was drafting. I would describe a function signature, its expected behavior and its edge cases, and the model would produce a first draft. I rewrote 60% of it, then 40%, then 20%. The drafts kept getting better, and I kept getting faster.

Within a few months these tools were load-bearing in my workflow, and the question had changed from *should I use them* to *how do I use them without losing the things that matter*.

## The Problem with "Vibe Coding"

What I did not want to become was a prompt jockey: someone who types "build me an app" into a chat window and ships whatever comes back. The industry now has a name for this, *vibe coding*, and I think it is genuinely dangerous.

Granted, the output isn't always bad; sometimes it is remarkably good. The danger lies elsewhere. Vibe coding divorces the developer from the decisions. If you let a model choose your architecture, your error handling, your test coverage and your dependency graph, you haven't saved any time. You have accumulated technical debt at machine speed, and you won't know it for a while, because the code runs and the tests (if there are any) pass.

The developers who will do well with these tools are not the ones who prompt the hardest. They are the ones who know what good engineering looks like and refuse to accept less, no matter who (or what) wrote the code.

## The System

So I built a system. It is not a product or a framework so much as a set of engineering standards that I enforce across every AI tool I use: the same rules, the same quality gates and the same architectural patterns, whether the code comes from [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://www.cursor.com/) or [Kilo Code](https://kilocode.ai/).

At its core is a document I call my global standards. It lives in my dotfiles and is symlinked into each tool's configuration directory, and it covers four things.

- **Process.** Every structural change follows the same pipeline: an ADR first, then architecture diagrams, then a decomposition into stories, then a plan, then the implementation, then verification. The AI doesn't get to skip steps.
- **Quality gates.** Before every commit, formatting, linting, type checking and unit tests must pass. There are no exceptions and no "I'll fix it later." The AI writes the code, and the code meets the same bar as anything I would write by hand.
- **Architecture patterns.** A clean layered architecture with dependency injection, the repository pattern for data access, and early returns over nested conditionals; persistence models, domain entities and DTOs kept separate. These are constraints, not suggestions.
- **Anti-patterns.** Files over 800 lines, functions over 50, nesting deeper than four levels, hardcoded secrets, mutable shared state, `any` types without narrowing, import cycles. If the AI produces any of these, it gets rejected, every time.

Each language then gets its own standards file. For Python that means `uv` for packages, `ruff` for linting, `basedpyright` for type checking, `pytest` with markers per layer, `attrs` classes for models, Google-style docstrings and property-based testing with `hypothesis`. For Go it means `gofumpt`, `golangci-lint`, table-driven tests with `t.Run()` subtests, small consumer-defined interfaces and structured logging with `zap`. For TypeScript it means `pnpm`, strict `tsc`, `vitest`, functional React components and Tailwind utilities (never `@apply`).

None of this is aspirational; it is enforced. When I open Claude Code, it reads my `CLAUDE.md` and knows the rules before I type a single prompt. When I open Cursor, the `.cursorrules` file tells it how this particular project works, down to the import paths for the error hierarchy and the logging package. When I open Kilo Code, the same standards are waiting in `~/.kilocode/rules/`. The upshot is that three AI tools, built by three different companies, all produce code that looks like *my* code.

## What It Actually Looks Like

A typical session goes something like this. Say I'm adding a new domain entity to a Go service. I open Claude Code and describe what I need:

> Add a `workspace` domain entity with CRUD operations, Ent repository, and HTTP controller. Follow the existing `user` domain as the reference implementation.

Claude Code reads my standards, looks at the existing `user` domain for its patterns, and produces a plan (a plan, mind you, not code). The plan names the files it will create, the interfaces it will implement and the tests it will write. I review it, adjust it, and only then does it execute.

What comes out has structured logging with `zap`, errors wrapped with `cockroachdb/errors`, context as the first parameter, table-driven tests, and the full layered architecture from `cmd` through `controller` and `core` down to `foundation`. That isn't because the model is brilliant. It's because I told it exactly what good looks like and handed it a reference implementation to follow.

When something falls short, I reject it, and the model takes the correction on board for the rest of the session. Over time my standards files get more precise, because the mistakes I keep seeing tell me what I failed to say. It is a pleasant sort of feedback loop: the AI forces me to be explicit about what I want, and that explicitness makes the AI more reliable.

## TDD Still Matters

Of all the standards, the one I enforce hardest is test-driven development. Write the failing test first; red, green, refactor. Every tool I use knows the rule.

If anything, this matters more with AI-generated code, not less. A person writing code carries a mental model of its invariants. A model writing code carries a statistical approximation of what code in this context usually looks like. Tests are what bridge that gap. If the implementation satisfies tests I wrote, tests that encode my understanding of the requirements, then I can trust the output regardless of whether a person or a machine produced it. Developers who skip the tests because "the AI wrote it and it looks right" are in for some expensive lessons.

## The Uncomfortable Truth

Here is the part I find a little hard to admit: I am faster now, and meaningfully so. Not at the parts of programming that matter most (design, architecture, understanding the problem), but at the mechanical translation of decisions into working code. When I know exactly what I want and need 400 lines of well-structured, tested and documented implementation, that used to take an afternoon. Now it takes twenty minutes.

That leaves two possibilities. Either the mechanical translation was never where my value as an engineer lived, or I spent a good deal of my career on work that didn't need my full attention. (Probably both.) The developers threatened by this shift are the ones whose main skill is typing speed and syntax recall. The ones amplified by it are those whose main skill is judgment: knowing what to build, how to structure it, which trade-offs to accept and, crucially, when the AI's output is wrong.

## What I Got Wrong

I got two things wrong, as far as I can tell.

First, I thought the quality floor was fixed. I assumed AI-generated code would always be mediocre and that serious engineers would always have to rewrite it. What I didn't anticipate is that the floor is a function of the constraints you impose. Left unconstrained, yes, a model writes mediocre code. Give it 70 pages of standards, enforced quality gates, reference implementations and a person who knows what good looks like, and the floor rises dramatically.

Second, I thought adoption was binary: either you are a "real" developer who writes everything by hand, or you are a prompt engineer shipping slop. In reality it's a spectrum, and the interesting part of that spectrum is where human judgment and machine capability overlap. That is where the leverage is.

## Adapt or Die

The title, for those who haven't seen *Dr. Strangelove*, is borrowed from Kubrick, whose subtitle is *How I Learned to Stop Worrying and Love the Bomb*. The analogy is imperfect (no one is riding a language model into oblivion, so far as I know), but the arc is right: I stopped worrying, mostly, once I understood that the thing to fear was not the tool but using it without discipline.

The tools exist, and they are getting better. The developers who refuse to engage with them aren't preserving craftsmanship; they are ceding ground to developers who use AI *and* have good judgment. The answer is not to abandon your standards but to encode them: write them down, make them machine-readable, and enforce them automatically. Then use every tool available to you, AI included, to ship better software faster.

Bill was right. The leverage is real, but only if you bring the discipline with you. I still have opinions about whitespace, I still believe in TDD, and I still think architecture matters more than velocity. I just let a machine do the typing.
