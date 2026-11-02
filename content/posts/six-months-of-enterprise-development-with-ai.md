---
title: "Six Months of Enterprise Development with AI"
date: 2026-10-28T12:00:00-04:00
draft: false
description: "What six months, 1,200 commits and 594 stories of building a production AI platform with agents taught me about what holds, what breaks, and where AI still falls down."
images:
  - "images/og/six-months-of-enterprise-development-with-ai.png"
tags: ["ai", "software-engineering", "architecture", "process"]
keywords: ["ai software development", "lessons learned", "guardrails", "static analysis", "claude code", "skills", "infrastructure drift", "ai coding agents"]
series: ["AI-Assisted Engineering"]
---

For the last six months I have been building a production AI platform (and the shared toolkit extracted from it) with agents writing the large majority of the code. I don't mean autocomplete, and I don't mean a demo. I mean roughly 1,200 commits, 63 epics, 594 stories, 359 implementation plans and 117 Architecture Decision Records, with real tenants, real cloud accounts and the occasional page at 2 AM.

I described the system that makes this possible in [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/), and the conversion that led to it in [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/). Here I want to report what happened when that system met six months of enterprise work: what held, what broke, and where I was simply wrong. A companion post, [Rethinking Agile in the Age of AI](/posts/rethinking-agile-in-the-age-of-ai/), takes these lessons and asks what they mean for the way teams plan and run their work.

> **About the data.** Everything below comes from scanning the git history, plan files, story files and agent transcripts of the codebases I worked in. The codebases are proprietary, so I report aggregates only (no names, paths or identifiers), and code samples are rewritten to be generic. Commit categories come from classifying commit subjects by keyword and are approximate. Where a sample is small, I say so.

## Lesson 1: Code Got Cheap, Decisions Didn't

Start with the numbers, which are hard to argue with. A story (one commit, one green tree) takes an agent one to two hours to build, and a task inside it (one red-green-refactor cycle) takes minutes. The median story in my plans has seven tasks, and the median plan has eight.

What doesn't compress is judgment. Which tier owns this logic? Is this a new pattern, or an instance of an old one? Can this change be undone? Fred Brooks divided software complexity into the *essential* (the problem itself) and the *accidental* (the friction of expressing it in code). Agents make short work of the accidental part. What remains is the essential part, and the essential part is design.

In practice, that means my job changed. I write far less code than I did a year ago and far more of three other things: decisions (117 ADRs in six months), plans that I approve before any code is written, and the machinery that checks the output. Most of what follows is about that third thing, because it's where I learned the most, mostly by getting it wrong first.

## Misstep 1: Building Without a Theory

The worst part of the codebase was the developer CLI, and I have no one to blame for it but myself.

For every service tier I had a theory before the first line was written: a layered architecture, interfaces in a dependency-free core, implementations selected by configuration, and decorators for the cross-cutting concerns. (I have written about that theory in [The Ideal Repository Structure](/posts/the-ideal-repository-structure/).) The agents followed it, and those tiers stayed coherent.

For the CLI, I had no theory at all. It began as a handful of scripts and grew by accretion, one more check here, one more deploy helper or generator there, each added by an agent that did exactly what it was asked, in whatever shape happened to be convenient at the time. Six months later it was the largest component in the repository, with roughly 96,000 lines of production Go and 109,000 lines of tests. One service package dispatched through a 33-case `switch`. Nine packages each declared their own `Violation` struct. And 44% of the service layer turned out to be a single kind of work (repository guards) implemented 32 different ways.

The commit history tells the story plainly enough:

{{< mermaid >}}
xychart-beta
    title "Share of commits that were fixes or refactors"
    x-axis ["CLI (no theory)", "Rest of codebase (theory first)"]
    y-axis "Percent of commits" 0 --> 60
    bar [51, 32]
{{< /mermaid >}}

In the CLI, 38% of commits were fixes and 14% were refactors; everywhere else, refactors were 5%. Without a theory, every change was a local optimum, and every local optimum eventually had to be torn out. It felt like constant refactoring because, well, it was.

The fix was to write the theory I should have started with. The CLI, it turns out, does exactly three kinds of work. There are *tool runs*, which invoke an external binary over a set of targets; *guards*, which inspect the repository and report violations; and *procedures*, which drive external systems through typed clients. Once those three nouns existed, the rebuild was more or less mechanical. Tool runs became data executed by a single runner, guards became declarative rows evaluated against a parsed model of the repository, and procedures became services over typed clients. A line-count ratchet (a ceiling that each milestone lowers and no commit may exceed) now enforces the result, taking the CLI from about 95,000 production lines toward 35,000.

The lesson, as far as I can tell, is that agents don't create architecture; they amplify whatever architecture you give them. Give them a theory and they extend it consistently. Give them none and they'll produce thirty-two locally reasonable answers to the same question. A person notices the duplication around the third copy, whereas an agent will cheerfully write the thirty-second.

## Misstep 2: Trusting the Agent's Word

The seven-tier layer model was in the agent's rules from day one: imports flow downward, siblings never import each other, and every selectable behavior goes through a factory. The agent read those rules at the start of every session, and whenever I asked, it reported that the code conformed to them, with complete confidence.

It was wrong, and so was I for believing it.

{{< mermaid >}}
timeline
    title Enforcing the layer model
    Month 0 : Layer model written into the agent's rules
            : Agent reports conformance
    Month 3 : First conformance audit
            : Skeleton conformant, connective tissue not
    Month 4.5 : Structural guard in CI
              : Interfaces must compose with a core contract
    Month 6 : Import rules generated from the layer model
            : Violations become build failures
{{< /mermaid >}}

The first audit, in month three, found the skeleton sound and the connective tissue riddled with exceptions: factories bypassed, siblings importing each other, infrastructure concerns leaking upward. The conformance epic that followed ran to 42 stories, and mechanical enforcement didn't arrive until months four through six. Every week in between, the agents produced code that *looked* conformant, passed review, and quietly widened the gap.

If I had to keep only one thing from these six months, it would be this: an unenforced rule is a suggestion, and agents report on suggestions as though they were facts. There's no malice in it. The model genuinely compares its output against the rule and concludes that it complied. The only conformance check you can rely on is one that runs without the model's participation.

## Lesson 2: Guardrails Are the Process

That misstep changed how I think about the whole system. The skills and standards files I described in *Anatomy* tell the agent what to do; guardrails *check that it happened*. Over six months, the center of gravity moved decisively from the former to the latter:

{{< mermaid >}}
xychart-beta
    title "Architecture decisions recorded (cumulative)"
    x-axis [May, Jun, Jul, Aug, Sep, Oct]
    y-axis "ADRs" 0 --> 120
    bar [0, 0, 24, 40, 79, 117]
{{< /mermaid >}}

{{< mermaid >}}
xychart-beta
    title "Lines of lint configuration"
    x-axis [May, Jun, Jul, Aug, Sep, Oct]
    y-axis "Lines" 0 --> 1400
    line [263, 270, 418, 418, 731, 1375]
{{< /mermaid >}}

First the decisions got written down, and then they got compiled into checks. By the end, the repository carried 272 declarative guards, a lint configuration five times its original size (much of it *generated* from the layer model), and a growing set of ratchets.

I've come to think of guardrails as a ladder, on which each rung is cheaper to trust than the one below it:

| Rung | Mechanism | What it catches | Who checks |
|---|---|---|---|
| 1 | Prose rules (`CLAUDE.md`, standards files) | Nothing, on its own | The agent, on its honor |
| 2 | Skills and templates | Skipped process steps | The workflow |
| 3 | Formatters, linters, type checkers | Style, smells, type errors | The toolchain |
| 4 | Architectural lints (import guards, banned APIs) | Layer violations, forbidden dependencies | The build |
| 5 | Repository-model guards | Cross-file and cross-language invariants | A query engine over the repo |
| 6 | Ratchets | Regression of any measured quantity | A counter that only goes down |
| 7 | Generators and scaffolds | Wrong shape at birth | Nobody — the right shape is the default |

Rungs 4 through 7 are where the leverage is.

Architectural lints turn the layer model into compile errors. In Go, one import guard rejects any package that imports upward, another bans the standard library's `errors.New` so that every error carries a code, and another bans the standard logger so that everything goes through the logging interface. In Python, `import-linter` does the same job. None of these rules are written by hand; they're generated from the layer model, so when the model changes, the rules regenerate, and CI fails on any drift.

Repository-model guards are the part I find most exciting, because they are a kind of meta-programming: code that reasons about code. Rather than having each check crawl the filesystem on its own, a single run builds a snapshot of the repository (parsed Go, parsed YAML, rendered manifests, the protobuf descriptor set), and every guard is a query against that snapshot. The guards are data, not code. Of the 272, 119 are text matches, 103 are [CEL](https://cel.dev/) expressions, 45 are Go functions over the parsed AST, and 5 are checks on YAML structure. Before the rebuild, the same checks were about 21,000 lines of hand-written Go. Here is a typical one, made generic:

```yaml
- name: chart dependencies are pinned in the lock file
  kind: expr
  files: {paths: [deploy/chart/Chart.yaml, deploy/chart/Chart.lock]}
  message: Chart.lock must pin every Chart.yaml dependency at its version
  expr: >-
    cel.bind(chart, decode('yaml', file['deploy/chart/Chart.yaml'].text),
      cel.bind(lock, decode('yaml', file['deploy/chart/Chart.lock'].text),
        chart.dependencies.all(d, lock.dependencies.exists(l,
          l.name == d.name && l.version == d.version))))
```

The invariants these guards hold are ones no linter ships with, because they're specific to *this* architecture:

- Every endpoint has documentation, an end-to-end test case, and a telemetry test case.
- Every indexed list-query field has a backing index in the migration DDL.
- The Go and Python error taxonomies agree, code for code.
- Every config-selected implementation gets its `Kind` from configuration, never from a hard-coded literal.
- Every interface outside the core composes with a core contract.
- Committed configuration contains no account-qualified identifiers; CI workflows read no repository-held secrets.

If that sounds like the inspections in a JetBrains IDE, it should. IntelliJ doesn't grep your code; it builds a semantic model (the PSI tree) and runs hundreds of inspections against it. Repository-model guards are the same idea pointed at architecture rather than syntax: inspections for *your* theory of the codebase, versioned right alongside it.

Ratchets handle what you can't fix in one commit. A ratchet records a measured count (production lines, exempted files, direct I/O call sites outside the client tier) and fails any commit that raises it, and lowering the ceiling is how progress gets recorded. The one rule I'm strict about is that a ratchet is lowered by fixing the code and never raised to make a commit pass.

Generators sit on the top rung because they prevent violations instead of detecting them. Adding a CLI command is a single generator invocation that scaffolds every tier at the right path and in the right shape. The agent doesn't have to remember the conventions, because the scaffold *is* the convention.

This is also why I prefer strict languages, though I think "fast languages like Go and Rust" is the wrong way to put it. The value isn't execution speed. It's that the compiler becomes the first reviewer. Go enforces the dependency rule through import paths and checks interface satisfaction at compile time with `var _ Interface = (*Impl)(nil)`, and typed Python with a strict checker and `import-linter` gets you most of the way there. What matters is a fast, strict feedback loop that the agent can't talk its way past.

I suspect this sort of programmatic guardrailing is where the profession is heading. A senior engineer's output is becoming less the code itself and more the machinery that keeps all code, human or machine, inside the theory.

## Misstep 3: AI Falls Down on Infrastructure

If you want to know where agents struggle, look at what you end up fixing. I classified all 322 fix commits:

{{< mermaid >}}
pie showData
    title What the 322 fixes were about
    "Cloud & deploy" : 96
    "Application logic" : 80
    "Permissions & identity" : 64
    "Drift & generated code" : 52
    "CI & toolchain" : 30
{{< /mermaid >}}

Three-quarters of all fixes had nothing to do with application logic. Even that understates it, since the agents wrote far more application code than infrastructure. Normalize by the amount of feature work in each category and the picture gets sharper:

{{< mermaid >}}
xychart-beta
    title "Fixes per feature commit, by category"
    x-axis ["Drift", "Permissions", "Cloud & deploy", "CI & toolchain", "App logic"]
    y-axis "Fixes per feature" 0 --> 4
    bar [3.47, 1.73, 1.39, 1.07, 0.39]
{{< /mermaid >}}

Application code needed a fix for roughly every two and a half features. Permissions needed almost two fixes per feature. Drift (generated code out of date, lock files out of sync, pinned versions that disagreed across environments) needed three and a half. Nor did any of this improve with time:

{{< mermaid >}}
xychart-beta
    title "Share of fixes that were not application logic, by month"
    x-axis [Apr, May, Jun, Jul, Aug, Sep, Oct]
    y-axis "Percent" 0 --> 100
    bar [92, 72, 85, 64, 65, 89, 75]
{{< /mermaid >}}

The failure modes were, frankly, monotonous. A worker that sends to a queue, deployed without the IAM grant to send to it. A CI workflow missing the token permission it needs to authenticate to the cloud. A trust policy pointing at the wrong organization. Clients regenerated in one module and not in another. An image pinned to one digest in staging and a different one in the overlay that was supposed to match it.

Behind all of them is the same pattern: infrastructure has no compiler, and its invariants span systems the agent can't see all at once. The permission lives in a Terraform module, while the call that needs it lives in a Python worker three directories away. The desired state is in the repository; the actual state is in a cloud account. Application code gets a type checker and a test suite that runs in seconds. Infrastructure gets a deploy, a timeout, and a log line in some other console.

Guardrails are the answer here as well; they're just harder to build. The guards that paid off most were the ones that pulled infrastructure into the repository model: policy checks on *rendered* Kubernetes manifests rather than on templates, CEL rules comparing Helm charts against their lock files, generators that derive each environment's config from a single topology source so that environments can't disagree, and drift checks that fail CI when generated artifacts go stale. My rule of thumb is that if two files must agree, either generate one from the other or write the guard that compares them.

## Lesson 3: The Build Got Fast, the Tail Didn't

When I first measured epics, I concluded that they took about a day: planned in the morning, merged that night. That was wrong, because merged isn't done. Here are three epics on a common timeline, from the first commit to stable:

{{< mermaid >}}
gantt
    title Three epics from first commit to stable
    dateFormat YYYY-MM-DD
    axisFormat Day %-j
    tickInterval 1week
    section Observability
    Build (100 commits)            :a1, 2026-01-01, 13d
    PR review (5 hours)            :milestone, after a1, 0d
    Staging fixes (8 follow-up PRs) :a2, after a1, 5d
    section Lint gate
    Build (3 PRs)                  :b1, 2026-01-01, 4d
    section Localization
    Build and merge                :c1, 2026-01-01, 1d
    Intermittent follow-up fixes   :c2, after c1, 42d
{{< /mermaid >}}

The pattern held across the whole history. Feature pull requests went from open to merged in one to five hours, but since I was effectively the only reviewer and the only one merging, that number measures my availability rather than any team's review process. One person reading every pull request is itself a bottleneck that doesn't scale, which is a large part of why I moved the mandatory human checkpoint from the pull request to the plan. Beyond review, the time went first to the build loop (preflight, review passes, verification iterations) and then to the tail: staging, CD gates, vulnerability scans, permissions, and the edge cases in data that only show up with real tenants. The lint-gate epic was pure code and closed in four days with no tail. The observability epic added a service and its infrastructure and took two and a half weeks. The localization epic merged in a day and was still producing bug fixes six weeks later.

The build loop itself is in good health. A person approves every plan before any code is written, and after that, automated review, the full gate and live execution run without me, looping back to implementation whenever they find a problem:

{{< mermaid >}}
xychart-beta
    title "Verification passes needed per plan (245 plans)"
    x-axis ["1 pass", "2 passes", "3 passes", "4+ passes"]
    y-axis "Plans" 0 --> 180
    bar [168, 68, 7, 2]
{{< /mermaid >}}

Sixty-nine percent of plans verified on the first pass, and nearly all the rest on the second. The agents are good at closing the loop they can see. What they can't see is production, and that is where the time goes.

## Lesson 4: The Old Units Stopped Meaning Anything

The stories in these codebases still carry story points, mostly out of habit. This is what they look like:

{{< mermaid >}}
pie showData
    title Story points assigned to 593 stories
    "3 points" : 217
    "5 points" : 215
    "2 points" : 89
    "8 points" : 46
    "Other (1, 4, 6, 13)" : 26
{{< /mermaid >}}

Seventy-three percent of stories are a 3 or a 5. Where I could match a story to its implementation plan, points correlated with task count at r = 0.12, which is to say not at all (there were only 22 matched pairs, so treat that as a hint rather than a verdict). Points measured *human effort*, and human effort is no longer what varies.

Token usage is a tempting replacement, and it is useful, though not as a measure of effort. Across the agent sessions I still had transcripts for, output tokens per commit varied fourfold (from 74K to 317K), and about 99% of all tokens were the agent re-reading its context. So token cost mostly measures *how much of the codebase a story forces the agent to hold in its head*, which makes it a measure of coupling. A story that is expensive in tokens is usually crossing too many boundaries; it's a design smell before it's a line in the budget.

What does predict duration, judging by everything above, is whether the work follows an existing pattern or sets a new one, how many human decisions it needs, and how much it touches outside the code. I turn those into an estimation model in [Rethinking Agile in the Age of AI](/posts/rethinking-agile-in-the-age-of-ai/).

## Lesson 5: Skills Are the Team's Process

If guardrails are how conventions get enforced, skills are how *process* gets shared. A skill is a short markdown file that encodes a workflow (plan, implement, verify; write an ADR; decompose an epic; diagnose a bug), and every agent session runs the same one. Standardizing on skills, or on whatever your tool calls them, is how a team stops having twelve different AI workflows.

Six months in, I have a fairly firm opinion about where skills should live:

| Kind | Encodes | Lives | Examples |
|---|---|---|---|
| **Off-the-shelf** | Commodity tasks anyone does the same way | Vendor plugins | Browser automation, generic code review, library docs lookup |
| **Global, custom** | *How you work* — your process | Dotfiles, shared across every repo | Plan → implement → verify, ADRs, epic decomposition, bug diagnosis |
| **Local, custom** | *This codebase's theory* | The repository's `.claude/` directory | The code-addition checklist, a test-policy override, project workflow rules |

My current setup is 14 global skills, 17 global rules and 18 templates, and in each production repository, six local rule files and no local skills at all. That ratio is deliberate. Process is global, theory is local, and commodity work is off the shelf. The plan-implement-verify loop is the same in every repository I touch, so it lives once, in my dotfiles. What a valid service looks like in *this* codebase lives with that codebase, versioned alongside the code it describes.

Off-the-shelf skills are fine for commodity work, but they encode someone else's defaults. A generic review skill knows nothing of your layer model or your error taxonomy, or that you ban hand-rolled test fakes. The leverage is in the custom layer, and the custom layer should stay *small*. In February I had seventeen skills; I now have fourteen, because several collapsed into others or became rules. The longest is 61 lines. A skill is a function, not a manual.

The last property matters most: skills graduate into guardrails. A rule that starts as prose in a skill ("never import a sibling service") becomes a lint as soon as it can be checked. The skill tells the agent what to do, and the guard makes sure it did. Misstep 2 is simply what happens when a rule stays on the prose rung for too long.

## What I'd Tell a Team Starting Today

If a team asked me where to start, I would tell them roughly this, in this order:

1. **Write the theory first:** the repository structure, the tier boundaries and the domain's nouns, all before the first agent session. The one component I didn't do this for cost me months.
2. **Enforce what you write.** If a rule matters, make it a build failure. The agent will tell you it complied; believe the build instead.
3. **Build guardrails as you would a product:** architectural lints, repository-model guards, ratchets and generators. This is where senior engineering effort now pays off most.
4. **Point the guardrails at infrastructure,** since that's where three-quarters of the bugs were. Generate whatever must agree, and guard whatever can't be generated.
5. **Measure to stable, not to merge.** The build is fast; the tail is where the time goes.
6. **Keep skills small,** global for process and local for theory, and graduate them into guards.

In [the talk I gave at Georgia Tech](/presentations/enforcing-engineering-discipline.html), I argued that AI doesn't fix a broken process; it accelerates whatever process you already have. Six months of data agree. Where I had a theory and enforced it, the agents extended it faithfully. Where I had a theory and didn't enforce it, they drifted while reporting success. And where I had no theory at all, they built a 96,000-line monument to its absence, which I am still, slowly, taking down.

None of these lessons stop at the codebase. They reach into how work is planned, estimated, reviewed and declared done, which is the subject of the [next post](/posts/rethinking-agile-in-the-age-of-ai/).
