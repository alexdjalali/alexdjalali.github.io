---
title: "Six Months of Enterprise Development with AI"
date: 2026-10-28T12:00:00-04:00
draft: false
description: "AI is here. Six months, 1,200 commits, and 594 stories of building a production AI platform with agents — what held, what broke, and what the data says about where AI still falls down."
images:
  - "images/og/six-months-of-enterprise-development-with-ai.png"
tags: ["ai", "software-engineering", "architecture", "process"]
keywords: ["ai software development", "lessons learned", "guardrails", "static analysis", "claude code", "skills", "infrastructure drift", "ai coding agents"]
series: ["AI-Assisted Engineering"]
---

AI is here. Not as autocomplete, and not as a demo. For the last six months I have built a production AI platform — and the shared toolkit extracted from it — with agents writing the large majority of the code. Roughly 1,200 commits. 63 epics, 594 stories, 359 implementation plans, 117 Architecture Decision Records. Real tenants, real cloud accounts, real pages at 2 AM.

I described the system that makes this possible in [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/), and the conversion that led to it in [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/). This post is about what happened when that system met six months of enterprise work: what held, what broke, and where I was wrong. A companion post, [Rethinking Agile in the Age of AI](/posts/rethinking-agile-in-the-age-of-ai/), takes these lessons and asks what they mean for how teams plan and run work.

> **About the data.** Everything below comes from scanning the git history, plan files, story files, and agent transcripts of the codebases I worked in. The codebases are proprietary, so I report aggregates only — no names, paths, or identifiers, and code samples are rewritten to be generic. Commit categories come from keyword classification of commit subjects and are approximate. Where a sample is small, I say so.

## Lesson 1: Code Got Cheap. Decisions Didn't.

The arithmetic is stark. A story — one commit, one green tree — takes an agent one to two hours to build. A task inside it — one red-green-refactor cycle — takes minutes. The median story in my plans has seven tasks; the median plan has eight.

What doesn't compress is judgment. Which tier owns this logic? Is this a new pattern or an instance of an old one? Is this change reversible? Fred Brooks split software complexity into *essential* (the problem itself) and *accidental* (the friction of expressing it). Agents eat accidental complexity for breakfast. What remains is the essential part — and the essential part is design.

In practice that means my job changed. I write far less code than I did a year ago, and far more of three other things: decisions (117 ADRs in six months), plans I approve before any code is written, and the machinery that checks the output. The rest of this post is about the third one, because that is where I learned the most — mostly by getting it wrong first.

## Misstep 1: Building Without a Theory

The worst part of the codebase was the developer CLI, and it was my fault.

For every service tier, I had a theory before the first line was written: a layered architecture, interfaces in a dependency-free core, implementations selected by configuration, decorators for cross-cutting concerns. I have written about that theory in [The Ideal Repository Structure](/posts/the-ideal-repository-structure/). The agents followed it, and those tiers stayed coherent.

For the CLI, I had no theory. It started as a handful of scripts and grew by accretion — one more check, one more deploy helper, one more generator — each added by an agent that did exactly what was asked, in whatever shape was locally convenient. Six months later it was the largest component in the repository: roughly 96,000 lines of production Go and 109,000 lines of tests. One service package alone dispatched through a 33-case `switch`. Nine packages each declared their own `Violation` struct. Forty-four percent of the service layer turned out to be one kind of work — repository guards — implemented 32 different ways.

The commit history tells the story:

{{< mermaid >}}
xychart-beta
    title "Share of commits that were fixes or refactors"
    x-axis ["CLI (no theory)", "Rest of codebase (theory first)"]
    y-axis "Percent of commits" 0 --> 60
    bar [51, 32]
{{< /mermaid >}}

In the CLI, 38% of commits were fixes and 14% were refactors. Everywhere else, refactors were 5%. Without a theory, every change was a local optimum, and every local optimum eventually had to be torn out. It felt like constant refactoring because it was.

The fix was to write the theory I should have started with. The CLI does exactly three kinds of work — **tool runs** (invoke an external binary over a set of targets), **guards** (inspect the repository and report violations), and **procedures** (drive external systems through typed clients). Once those three nouns existed, the rebuild was mechanical: tool runs became data executed by one runner, guards became declarative rows evaluated against a parsed model of the repository, and procedures became services over typed clients. A line-count ratchet now enforces the result — a ceiling that each milestone lowers and no commit may exceed — taking the CLI from about 95,000 production lines toward 35,000.

The lesson: agents don't create architecture; they amplify whatever architecture you give them. Give them a theory and they extend it consistently. Give them none and they will produce thirty-two locally reasonable answers to the same question. A human notices the duplication on the third copy. An agent will happily write the thirty-second.

## Misstep 2: Trusting the Agent's Word

The seven-tier layer model was in the agent's rules from day one. Imports flow downward. No lateral imports between siblings. Every selectable behavior goes through a factory. The agent read these rules at the start of every session, and when asked, it reported conformance. Confidently.

It was wrong.

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

The first audit, at month three, found the skeleton sound and the connective tissue riddled with exceptions — factories bypassed, siblings importing each other, infrastructure concerns leaking upward. The conformance epic that followed ran to 42 stories. Mechanical enforcement didn't arrive until months four through six. Every week in between, agents produced code that *looked* conformant, passed review, and quietly widened the gap.

This is the most important thing I learned: **an unenforced rule is a suggestion, and agents report on suggestions as if they were facts.** Not maliciously — the model genuinely pattern-matches its output against the rule and concludes it complied. The only reliable conformance check is one that runs without the model's participation.

## Lesson 2: Guardrails Are the Process

That misstep reshaped how I think about the whole system. The skills and standards files I described in *Anatomy* tell the agent what to do. Guardrails *check that it happened*. Over six months the center of gravity moved decisively from the first to the second:

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

Decisions got written down, and then the decisions got compiled into checks. By the end, the repository carried 272 declarative guards, a lint configuration five times its original size — much of it *generated* from the layer model — and a growing set of ratchets.

I now think of guardrails as a ladder, where each rung is cheaper to trust than the one below:

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

**Architectural lints** turn the layer model into compile errors. In Go, an import guard rejects any package that imports upward; another bans the standard library's `errors.New` so every error carries a code; another bans the standard logger so everything goes through the logging interface. In Python, `import-linter` does the same job. These rules are generated from the layer model, not hand-written — when the model changes, the rules regenerate, and CI fails on drift.

**Repository-model guards** are the part I find most exciting, because they are meta-programming: code that reasons about code. Instead of each check crawling the filesystem on its own, one run builds a snapshot of the repository — parsed Go, parsed YAML, rendered manifests, the protobuf descriptor set — and every guard is a query against it. Guards are data, not code. Of the 272, 119 are text matches, 103 are [CEL](https://cel.dev/) expressions, 45 are Go functions over the parsed AST, and 5 are YAML structure checks. Before the rebuild, the same checks were about 21,000 lines of hand-written Go. A typical one, made generic:

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

The invariants these guards hold are ones no linter ships with, because they are specific to *this* architecture:

- Every endpoint has documentation, an end-to-end test case, and a telemetry test case.
- Every indexed list-query field has a backing index in the migration DDL.
- The Go and Python error taxonomies agree, code for code.
- Every config-selected implementation gets its `Kind` from configuration, never from a hard-coded literal.
- Every interface outside the core composes with a core contract.
- Committed configuration contains no account-qualified identifiers; CI workflows read no repository-held secrets.

If that sounds like the inspections in a JetBrains IDE, it should. IntelliJ doesn't grep your code; it builds a semantic model (the PSI tree) and runs hundreds of inspections against it. Repository-model guards are the same idea pointed at architecture instead of syntax — inspections for *your* theory of the codebase, versioned alongside it.

**Ratchets** handle what you can't fix in one commit. A ratchet records a measured count — production lines, exempted files, direct I/O call sites outside the client tier — and fails any commit that raises it. Lowering the ceiling is how progress is recorded. The rule I enforce: a ratchet is lowered by fixing the code, never raised to make a commit pass.

**Generators** are the top rung because they prevent violations rather than detecting them. Adding a CLI command is a single generator invocation that scaffolds every tier at the right path with the right shape. The agent doesn't need to remember the conventions; the scaffold *is* the convention.

This is also why I prefer strict languages — and why "fast languages like Go and Rust" is the wrong way to say it. The value isn't execution speed. It is that the compiler is the first reviewer: Go enforces the dependency rule through import paths and checks interface satisfaction at compile time with `var _ Interface = (*Impl)(nil)`. Typed Python with a strict checker and `import-linter` gets most of the way there. What matters is a fast, strict feedback loop the agent can't talk its way past.

I think programmatic guardrailing is where the profession is heading. The senior engineer's output is becoming less the code and more the machinery that keeps all code — human or machine — inside the theory.

## Misstep 3: AI Falls Down on Infrastructure

If you want to know where agents struggle, look at what you fix. I classified all 322 fix commits:

{{< mermaid >}}
pie showData
    title What the 322 fixes were about
    "Cloud & deploy" : 96
    "Application logic" : 80
    "Permissions & identity" : 64
    "Drift & generated code" : 52
    "CI & toolchain" : 30
{{< /mermaid >}}

Three-quarters of all fixes were not application logic. The raw counts understate it, because the agents wrote far more application code than infrastructure. Normalized by the feature work in each category, the picture sharpens:

{{< mermaid >}}
xychart-beta
    title "Fixes per feature commit, by category"
    x-axis ["Drift", "Permissions", "Cloud & deploy", "CI & toolchain", "App logic"]
    y-axis "Fixes per feature" 0 --> 4
    bar [3.47, 1.73, 1.39, 1.07, 0.39]
{{< /mermaid >}}

Application code needed a fix for roughly every two and a half features. Permissions needed almost two fixes per feature. Drift — generated code out of date, lock files out of sync, pinned versions that disagreed across environments — needed three and a half. And it didn't improve with time:

{{< mermaid >}}
xychart-beta
    title "Share of fixes that were not application logic, by month"
    x-axis [Apr, May, Jun, Jul, Aug, Sep, Oct]
    y-axis "Percent" 0 --> 100
    bar [92, 72, 85, 64, 65, 89, 75]
{{< /mermaid >}}

The failure modes were monotonous. A worker that sends to a queue, deployed without the IAM grant to send. A CI workflow missing the token permission it needs to authenticate to the cloud. A trust policy pointing at the wrong organization. Generated clients regenerated in one module and not another. An image pinned to one digest in staging and another in the overlay that was supposed to match it.

The pattern behind them is the same: **infrastructure has no compiler, and its invariants span systems the agent can't see at once.** The permission lives in a Terraform module; the call that needs it lives in a Python worker three directories away. The desired state is in the repository; the actual state is in a cloud account. Application code gets a type checker and a test suite that runs in seconds. Infrastructure gets a deploy, a timeout, and a log line in another console.

Guardrails are the answer here too — just harder to build. The guards that paid off most were the ones that pulled infrastructure into the repository model: policy checks on *rendered* Kubernetes manifests rather than templates, CEL rules that compare Helm charts against their lock files, generators that derive per-environment config from one topology source so environments can't disagree, and drift checks that fail CI when generated artifacts are stale. The rule of thumb: if two files must agree, make one of them generated from the other, or write the guard that compares them.

## Lesson 3: The Build Got Fast. The Tail Didn't.

When I first measured epics, I concluded they took about a day: planned in the morning, merged that night. That was wrong, because merge isn't done. Here are three epics on a common timeline, from first commit to stabilized:

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

The pattern held across the history. Feature PRs went from open to merged in one to five hours — but I was effectively the only reviewer and the only one merging, so that number measures my availability, not a team's review process. One person reading every PR is itself a bottleneck that doesn't scale, and it's a big part of why I moved the mandatory human checkpoint from the PR to the plan. Beyond review, the time went to the build loop (preflight, review passes, verification iterations) and then to the tail: staging, CD gates, vulnerability scans, permissions, and data edge cases that only show up with real tenants. The lint-gate epic was pure code and closed in four days with no tail. The observability epic added a service and its infrastructure and took two and a half weeks. The localization epic merged in a day and was still producing bug fixes six weeks later.

The build loop itself is healthy. Every plan is approved by a human before any code is written; after that, automated review, the full gate, and live execution run without me, looping back to implementation when they find problems:

{{< mermaid >}}
xychart-beta
    title "Verification passes needed per plan (245 plans)"
    x-axis ["1 pass", "2 passes", "3 passes", "4+ passes"]
    y-axis "Plans" 0 --> 180
    bar [168, 68, 7, 2]
{{< /mermaid >}}

Sixty-nine percent of plans verified on the first pass; nearly all the rest on the second. The agents are good at closing the loop they can see. What they can't see — production — is where the time goes.

## Lesson 4: The Old Units Stopped Meaning Anything

The stories in these codebases still carry story points, out of habit. Here is what they look like:

{{< mermaid >}}
pie showData
    title Story points assigned to 593 stories
    "3 points" : 217
    "5 points" : 215
    "2 points" : 89
    "8 points" : 46
    "Other (1, 4, 6, 13)" : 26
{{< /mermaid >}}

Seventy-three percent of stories are a 3 or a 5. Where I could match a story to its implementation plan, points correlated with task count at r = 0.12 — effectively noise (only 22 matched pairs, so treat that as a hint, not a verdict). Points measured *human effort*. Human effort is no longer what varies.

Token usage is tempting as a replacement, and it is useful — but not as an effort measure. Across the agent sessions I still had transcripts for, output tokens per commit varied fourfold (74K to 317K), and about 99% of all tokens were the agent re-reading its context. Token cost mostly measures *how much of the codebase a story forces the agent to hold in its head*. That makes it a coupling metric. A story that is expensive in tokens is usually crossing too many boundaries — a design smell before it is a budget line.

What does predict duration, from everything above: whether the work follows an existing pattern or sets a new one, how many human decisions it needs, and how much it touches outside the code. I turn those into an estimation model in [Rethinking Agile in the Age of AI](/posts/rethinking-agile-in-the-age-of-ai/).

## Lesson 5: Skills Are the Team's Process

If guardrails are how conventions are enforced, skills are how *process* is shared. A skill is a short markdown file that encodes a workflow — plan, implement, verify; write an ADR; decompose an epic; diagnose a bug — and every agent session runs the same one. Standardizing on skills (or your tool's equivalent) is how a team stops having twelve different AI workflows.

Six months in, I have a clear opinion about where skills should live:

| Kind | Encodes | Lives | Examples |
|---|---|---|---|
| **Off-the-shelf** | Commodity tasks anyone does the same way | Vendor plugins | Browser automation, generic code review, library docs lookup |
| **Global, custom** | *How you work* — your process | Dotfiles, shared across every repo | Plan → implement → verify, ADRs, epic decomposition, bug diagnosis |
| **Local, custom** | *This codebase's theory* | The repository's `.claude/` directory | The code-addition checklist, a test-policy override, project workflow rules |

My current setup is 14 global skills, 17 global rules, and 18 templates — and in each production repository, six local rule files and zero local skills. That ratio is deliberate. **Process is global; theory is local; commodity work is off-the-shelf.** The plan-implement-verify loop is the same in every repository I touch, so it lives once, in dotfiles. What a valid service looks like in *this* codebase lives with that codebase, versioned with the code it describes.

Off-the-shelf skills are fine for commodity work, but they encode someone else's defaults. A generic review skill doesn't know your layer model, your error taxonomy, or that you ban hand-rolled test fakes. The leverage is in the custom layer — and the custom layer should stay *small*. In February I had seventeen skills; I now have fourteen, because several collapsed into others or became rules. The longest is 61 lines. A skill is a function, not a manual.

The last property matters most: **skills graduate into guardrails.** A rule that starts as prose in a skill ("never import a sibling service") becomes a lint once it can be checked. The skill tells the agent what to do; the guard makes sure it did. Misstep 2 is what happens when a rule stays at the prose rung too long.

## What I'd Tell a Team Starting Today

1. **Write the theory first.** Repository structure, tier boundaries, the domain's nouns — before the first agent session. The component I didn't do this for cost me months.
2. **Enforce what you write.** If a rule matters, it's a build failure. The agent will tell you it complied; believe the build.
3. **Build guardrails like a product.** Architectural lints, repository-model guards, ratchets, generators. This is where senior engineering effort now pays off most.
4. **Point the guardrails at infrastructure.** That's where three-quarters of the bugs were. Generate what must agree; guard what can't be generated.
5. **Measure to stable, not to merge.** The build is fast. The tail is where the time goes.
6. **Keep skills small — global for process, local for theory** — and graduate them into guards.

In [the talk I gave at Georgia Tech](/presentations/enforcing-engineering-discipline.html), I argued that AI doesn't fix a broken process — it accelerates whatever process you already have. Six months of data agree. Where I had a theory and enforced it, agents extended it faithfully. Where I had a theory and didn't enforce it, they drifted while reporting success. Where I had no theory, they built a 96,000-line monument to its absence.

Those lessons don't stop at the codebase. They reach into how work is planned, estimated, reviewed, and declared done — which is the subject of the [next post](/posts/rethinking-agile-in-the-age-of-ai/).
