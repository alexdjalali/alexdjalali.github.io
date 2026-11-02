---
title: "Your Docs Are a Corpus Now"
date: 2026-11-01T12:00:00-04:00
draft: false
description: "Twelve hundred markdown files, three readers: people, a wiki, and a retrieval index. How we adopted Google's Open Knowledge Format, turned our READMEs into a company wiki, and started pointing our own RAG product at our own codebase so the agents stop guessing."
images:
  - "images/og/your-docs-are-a-corpus-now.png"
tags: ["ai", "software-engineering", "developer-tools", "architecture", "claude"]
keywords: ["open knowledge format", "okf", "rag", "retrieval augmented generation", "backstage", "techdocs", "mcp server", "docs as code", "dogfooding", "claude code", "ai coding agents"]
series: ["AI-Assisted Engineering"]
---

The platform I work on answers natural-language questions over an organization's documents, with citations. For six months its own documentation was the kind of corpus we tell customers we can fix: 1,128 markdown files under `docs/`, 138 READMEs scattered across the tree, no record of who wrote what or whether any of it was still true. Agents read those files every day. They had no way to tell a current runbook from a closed story written in July.

So we are dogfooding. The plan has three steps, and each one depends on the one before it:

1. **One format.** Every doc and README becomes a concept in a single [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) bundle: markdown with typed, machine-checked frontmatter.
2. **One wiki.** Backstage and TechDocs render that bundle for people who never clone the repository.
3. **One index.** Our own retrieval product ingests the repository, code and docs together, and serves it to coding agents through an MCP server.

Step 1 has shipped. Steps 2 and 3 are designed and decided, with an approved implementation plan, and are being built now. This post covers what we built, what the migration surfaced, and why I think "docs" is the wrong word for what a repository's prose has become.

> **About the data.** As in [Six Months of Enterprise Development with AI](/posts/six-months-of-enterprise-development-with-ai/), the codebase is proprietary. I report counts from its git history, ADRs and audits, and I have rewritten command names and examples to be generic. Where something is planned rather than built, I say so.

## Three Readers, One Set of Files

The decision that set everything else up was recognizing that the same markdown file now has three readers:

- **A person**, who wants navigation, search, and an owner to ask.
- **A wiki renderer**, which wants titles, descriptions, and a folder structure it can turn into a site.
- **A retriever**, which wants chunks, metadata to filter on, and a stable anchor to cite.

Write for only one of them and the other two degrade. A wiki that lives in a separate product drifts from the code. A RAG index over raw files can't tell a deprecated design from a current one. A tidy folder tree with no metadata leaves an agent opening forty files to find the one it needed.

What all three need is the same thing: **structured metadata on unstructured prose, kept in git, checked in CI.** That is what OKF is.

## Why the Open Knowledge Format

Google Cloud published OKF as a vendor-neutral specification for "knowledge as plain markdown files with YAML frontmatter." Version 0.2 is small enough to read in one sitting:

- **One required key**, `type`. Recommended: `title`, `description`, `resource`, `tags`.
- **Provenance and trust**: `sources`, `generated` (who or what produced a concept), `verified` (who confirmed it).
- **Lifecycle**: `status` and `stale_after`.
- **Two reserved filenames**: `index.md` (a directory listing for progressive disclosure) and `log.md` (a dated change history).
- **Markdown links between concepts are graph edges.**

It doesn't impose a folder scheme, a renderer, or a query language. Backstage, MkDocs and our ingestion pipeline already read markdown with frontmatter, so adopting OKF cost us a schema rather than a platform.

We considered the alternatives and rejected them for concrete reasons, which the ADR records:

| Alternative | Why not |
|---|---|
| Add frontmatter, keep the layout | 594 story files still dominate search and the wiki |
| Diátaxis's four folders only | No home for ADRs, runbooks or delivery records, about a third of the corpus |
| A custom frontmatter schema | A private format: no shared contract with Backstage, MkDocs, or anyone else's agents |
| A wiki product instead of git | Docs leave code review and drift from the code they describe |

The risk is that OKF is young. Google's announcement describes v0.1, and the repository was already at v0.2 when we adopted it. We pin `okf_version: "0.2"` at the bundle root and keep our required keys a subset of the spec's, so a spec change becomes a guard update rather than a migration.

## What We Decided

The ADR made eight decisions. Five of them carry most of the weight.

**A closed type vocabulary, in config.** Eleven types: `ADR`, `Design`, `Epic`, `RCA`, `Audit`, `Guide`, `Reference`, `Explanation`, `Runbook`, `README`, `Wireframe Set`. We require `type` and `title`, which is stricter than the spec, and `description` for anything an index lists. A README's `resource` is its component's path.

**Freshness is data.** Every concept records `generated` (a person, or `<agent>/<model>`) and, once someone checks it against the code, `verified`. Reader docs carry `stale_after`. A stale doc gets reported, not deleted; superseded material gets `status: deprecated`. "Is this doc current?" becomes a query instead of a guess.

**Organize by what the reader needs, not by who wrote it.**

| Folder | Holds |
|---|---|
| `guides/` | how-to manuals, onboarding |
| `reference/` | generated reference: CLI, config, endpoints |
| `explanation/` | architecture, charter, technologies |
| `decisions/` | ADRs |
| `operations/` | runbooks, infrastructure |
| `delivery/` | epics, designs, RCAs, audits, roadmap |
| `design/wireframes/` | wireframe sets |

**Closed stories fold into their epic.** This was the biggest single change. I wrote about our 594 stories in the last post as a sign of throughput. As a corpus they are noise: the issue tracker is the system of record for execution, but the story files sat beside the material a new engineer needs, and they outranked it in every search. Each epic is now a directory with the epic as a concept and a `log.md` holding one dated entry per closed story, with its summary, ticket and commit. Open stories remain files until they close.

**The skills read the layout from the repository.** My Claude Code skills hard-coded the old paths: `docs/local/plans` 21 times, `docs/spec/stories` 17, `docs/spec/rca` 17, `docs/spec/epics` 14, `docs/adr` 13. Moving a folder would have quietly broken the tools that write the docs. Each repository now declares its layout in a small YAML file (artifact → path), the skills resolve paths through it, and a repository without one falls back to the old paths and keeps working.

Here is what a concept looks like after the migration:

```yaml
---
type: Runbook
title: Rotate the ingestion queue credentials
description: Rotate the queue's access keys without dropping in-flight messages.
status: stable
generated: {by: 'human:alex-djalali', at: "2026-11-01T02:27:22Z"}
verified: {by: 'human:alex-djalali', at: "2026-11-01T18:04:10Z"}
stale_after: 2027-02-01
---
```

## How It Shipped

The migration was ten stories in a single pull request: **1,980 files changed.** The diff was almost entirely tooling output, because the order of operations was the whole strategy:

1. **Tools before moves.** A generic OKF parser, index renderer and conformance checker went into our shared engine library. The repository's CLI then gained the type vocabulary and a generator for the skills' layout file.
2. **A guard in report-only mode.** The first run of `check okf` against the unchanged tree gave a baseline: **1,293 files without frontmatter, 147 dead cited paths, 48 cited CLI commands that no longer exist.** The guard reported and blocked nothing.
3. **Derived frontmatter, not hand-written frontmatter.** A generator stamped all 1,293 files, taking each file's type from its folder, its title from the heading, its description from the first sentence, its status from any status line, and `generated` from the commit that added it. **It never sets `verified`.** A machine can say who wrote a document. Only a check against the code can say it is true.
4. **Moves with link rewriting.** A `docs move <from> <to>` command runs `git mv` on a folder, rewrites every relative link from each file's new location, updates repo-root path mentions in code and config, and appends each old path to a redirects file. Records such as ADRs and closed stories keep their wording as written; only their links move. The redirects file has **1,264 entries**, and the wiki will serve them so that links in old tickets and PRs keep working.
5. **Fold, index, block.** 356 closed story files became epic log entries, every `index.md` was generated from frontmatter (and is never hand-edited; drift fails CI like every other generator), and then the guard switched to blocking.

Each move was its own commit, so each one could be reverted alone. I didn't need that, but having it is why I was willing to rewrite a thousand files in one PR.

## Then the Names

Once the shape was enforced, a smaller problem surfaced. The bundle used three filename schemes (`NNNN-slug`, `YYYY-MM-DD-slug`, plain `slug`) with nothing saying which kind of document got which. A few files broke their folder's pattern, all because a skill had named them on its own.

That matters once a wiki publishes the bundle, because a rename then breaks a URL. So a follow-up ADR splits documents into three classes:

- **Records**, written once about a point in time, carry their date: designs, RCAs, audits, plans.
- **Sequenced documents**, cited by number or read in order, carry their number: ADRs, epics, stories, architecture chapters.
- **Living documents**, edited in place, carry a plain slug: guides, reference, runbooks.

Each type declares its pattern as data in the same config file as the vocabulary. The guard, the move command and the skills all read that one rule. The ADR's own justification for not writing the convention down in prose: *rules in prose are ignored.* Our skills had already drifted from the folders they wrote to.

## Conformant Is Not the Same as True

A green `check okf` says the bundle is well-formed: frontmatter parses, types are known, links resolve, cited paths exist. It says nothing about whether the instructions work.

So before the wiki publishes anything, we audited content. Every reader doc was scanned for CLI commands and flags, `localhost` ports, config keys, environment variables, dependency pins and `file:line` references, and each candidate was checked by hand against the code at a pinned commit.

| Checked | Count | Findings |
|---|---|---|
| READMEs | 133 | 1 |
| Runbooks | 36 | 1 |
| Explanations | 33 | 4 |
| Guides | 23 | 0 |
| Reference (hand-written) | 10 | 3 |
| Infrastructure | 3 | 1 |
| Other (wireframe set, untyped) | 2 | 0 |
| The root `CLAUDE.md` | 1 | **5** |
| Generated endpoint reference | 141 | 0 (in sync) |

Fifteen findings across 241 documents: **six instructions that fail when you follow them** (wrong ports, environment variables nothing binds, two retired CLI flags) and seven stale facts (counts, a dependency pin, a config key that was renamed).

Two results stand out. The 141 generated endpoint pages had zero drift, which is the strongest argument I have for generating reference docs. And the single worst document in the repository was the one every agent reads first. The agent instructions file had five findings on its own, mostly in the *Configuration* and *Ports* sections, which agents copy into commands verbatim. When I wrote last time that agents are only as good as the machinery around them, this is the machinery I meant, and it was wrong.

Every finding has been fixed, and the audit is itself an OKF `Audit` concept in the bundle.

## Step 2: The Wiki

GitHub renders single files. It doesn't give you navigation across folders, search over rendered docs, or any idea of who owns what. Product, support and new hires need all three.

We chose **Backstage with TechDocs**, running in our own cluster behind SSO. The design follows from the OKF decision:

- **TechDocs renders the bundle as-is.** OKF's `title`, `description`, `tags` and `status` drive page titles, search snippets and a deprecation banner. MkDocs ignores keys it doesn't use, so the files remain conformant.
- **The catalog is generated, not hand-written.** A generator writes Backstage's catalog entities (systems, components, APIs, owners) from the build and deploy manifests and the proto contracts we already maintain. The catalog can't drift from the build because both come from the same rows.
- **CI builds the docs** on merge and publishes them to object storage. Backstage never builds at request time.
- **The redirects file becomes HTTP redirects**, so a two-month-old ticket that links to `docs/adr/0042-…` still lands on the right page.

The alternative I was most tempted by was an AI-generated repository wiki, the DeepWiki-style approach where you point a model at the code and get prose back. It costs nothing to author. We rejected it because it **generates prose from code instead of publishing the docs we review.** We have 124 ADRs. They hold the *why*, and a model reading the code can't reconstruct it. The wiki should show what we decided, not what a model guesses we decided.

## Step 3: RAG-ify the Repository

This is the dogfooding part. Engineers and agents in this repository answer "how does X work?" with local tools: a code graph, semantic search, grep. Those tools are fast and good at code. None of them reach the decisions, designs and runbooks behind the code with citations, and none of them exercise the product we actually sell.

So the repository becomes a tenant of its own product:

{{< mermaid >}}
graph TD
    GH[Git repository · main] -->|push webhook / poll| CONN[git connector<br/>tree diff by blob SHA]
    CONN --> ING[Ingestion<br/>code by symbol · markdown by heading]
    ING -->|OKF frontmatter → metadata| KB[(Knowledge base<br/>internal org)]
    AGENT[Coding agent] -->|OAuth 2.1| MCP[Product MCP server<br/>ask · search · get_document · read]
    MCP -->|the caller's own token| API[Public API<br/>org scoping · clearance · audit]
    API --> RET[Retrieval<br/>metadata filters] --> KB
    EVAL[Eval set<br/>recall@5 ≥ 0.80] --> API
{{< /mermaid >}}

The pieces, each designed to be reusable by customers whose knowledge lives in repositories:

- **A git connector.** It does a full import on first sync, then ingests only files whose blob SHA changed since the last checkpoint. A push webhook triggers a sync, and a poll serves as backstop. Deleted files are swept, but only after a *complete* listing, because a sweep after a partial listing would wipe half the index.
- **Code is chunked by symbol, prose by heading.** Tree-sitter splits Go, Python and TypeScript at function and type boundaries. Markdown splits at `##`. Every chunk keeps its anchor, so a citation reads `path:lines@commit`.
- **OKF frontmatter becomes retrieval metadata.** `okf_type`, `okf_status`, `okf_tags` and staleness are attached to every chunk and can be filtered at query time. Deprecated documents are excluded by default. This is where step 1 pays off: without frontmatter the retriever can't distinguish a superseded design from the current one, and with it the distinction is a `WHERE` clause.
- **An internal org, same path as a customer.** The repository is ingested into a dedicated organization with the same tenancy, clearance and audit trail a customer gets, and it never mixes with customer data.
- **A separate, product-grade MCP server.** We already had an MCP server, the one that exposes our developer CLI (lint, test, deploy) to agents on a laptop. That server has no concept of a user, so adding query tools to it would have required a service token that bypasses clearance. The new server is its own deployable. It authenticates the calling person through the MCP authorization flow (OAuth 2.1), exchanges that for an API token, and queries *as that person*. It holds no data and no credential that bypasses a user.
- **A gate before rollout.** An evaluation set of questions with known cited files. The server opens to all of engineering when recall@5 reaches 0.80, not before.

The point of dogfooding is the feedback loop. When an agent in our repository gets a bad answer with a wrong citation, that isn't a tooling complaint. It's a product bug, filed by the people who can fix it, against the code they're already working in.

## Optimizing the Agents

The index covers committed `main`. Agents also work against an uncommitted working tree, and that is where most of their tokens go. Spotify [reported](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90) cutting Claude Code token usage by about 90% by routing reads through a cheaper model. The premise is that most of an agent's spend on a large file is I/O, not reasoning.

The same epic adds the local half:

- **`ai read --question … --paths …`**: a CLI operation that wraps the named files, sends them with one question to a small local model (a 7B model on Ollama in dev), and returns terse bullets led by exact names and line numbers. The file contents never pass through the frontier model's context. Over a byte cap, it fails and asks for fewer paths rather than truncating silently.
- **A read-size hook.** A Claude Code `PreToolUse` hook blocks a whole-file read of a file over 350 lines and points the agent to the bulk-read tool. Ranged reads pass through, because an edit still needs exact lines. The hook does nothing unless a repository opts in.
- **Named modes, measured.** A related ADR routes all LLM work through named profiles instead of hard-coded model names, with every profile's tokens recorded in the same ledger the product uses for customers. The agents' spend becomes a metric we can see per mode.

Put together, an agent has three ways to learn something: the index for decided and committed knowledge with citations, the cheap reader for the working tree, and a direct read for the exact lines it's about to edit. The frontier model's context is reserved for that last case.

## What I Have Learned So Far

**The format comes before the wiki and the index.** I nearly started with Backstage, because it's the visible part. Both the wiki and the retriever are consumers of the format, and every field we added to frontmatter for one of them benefited the other at no extra cost.

**Machines stamp `generated`. Only checks stamp `verified`.** Deriving 1,293 frontmatter blocks automatically was fine. Letting that generator claim the documents were true would have been the worst kind of metadata: confident and unearned.

**Report, then block.** The guard ran in report-only mode until the tree was conformant, so the baseline numbers became a burn-down list instead of 1,293 CI failures.

**Audit the file your agents read first.** Our agent instructions file had more findings than any other document in the repository, and agents act on it without questioning it. If you audit one document this quarter, audit that one.

**Rules in prose get ignored, so encode them as data.** The type vocabulary, the layout and the naming patterns all live in config, and the guard, the move command and the skills read from it. The one convention we left in prose, file naming, was the one that drifted.

**Generated docs don't drift.** 141 generated endpoint pages, zero findings. 241 hand-written reader docs, fifteen findings. Generate everything you can.

## What's Next

The naming guard and content fixes are committed. Next come the Backstage app and generated catalog on the dev stack, then the git connector, splitters and metadata filters, then the MCP server and its token exchange, and finally the evaluation gate. Some of these steps are waiting on credentials that only a human can create: a GitHub App, an identity-provider grant, a staging account. I'll write the follow-up once recall@5 has a number, whether or not it clears 0.80.
