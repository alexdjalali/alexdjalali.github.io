---
title: "Your Docs Are a Corpus Now"
date: 2026-11-01T12:00:00-04:00
draft: false
description: "Why a repository's twelve hundred markdown files now have three readers (people, a wiki and a retrieval index), and what happened when we adopted Google's Open Knowledge Format, turned our READMEs into a company wiki and pointed our own RAG product at our own codebase."
images:
  - "images/og/your-docs-are-a-corpus-now.png"
tags: ["ai", "software-engineering", "developer-tools", "architecture", "claude"]
keywords: ["open knowledge format", "okf", "rag", "retrieval augmented generation", "backstage", "techdocs", "mcp server", "docs as code", "dogfooding", "claude code", "ai coding agents"]
series: ["AI-Assisted Engineering"]
---

The platform I work on answers natural-language questions over an organization's documents, with citations. For six months, its own documentation was exactly the kind of corpus we tell customers we can fix: 1,128 markdown files under `docs/` and 138 READMEs scattered across the tree, with no record of who wrote what or whether any of it was still true. Agents read those files every day, and they had no way of telling a current runbook from a story that closed in July. (The irony was not lost on me.)

So we are dogfooding, in three steps, each of which depends on the one before it:

1. **One format.** Every doc and README becomes a concept in a single [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) bundle, that is, markdown with typed, machine-checked frontmatter.
2. **One wiki.** Backstage and TechDocs render that bundle for people who never clone the repository.
3. **One index.** Our own retrieval product ingests the repository, code and docs together, and serves it to coding agents through an MCP server.

The first step has shipped. The second and third are designed and decided, with an approved implementation plan, and are being built as I write. What follows is what we built, what the migration turned up, and why I've come to think "docs" is the wrong word for what a repository's prose has become.

> **About the data.** As in [Six Months of Enterprise Development with AI](/posts/six-months-of-enterprise-development-with-ai/), the codebase is proprietary. I report counts from its git history, ADRs and audits, and I have rewritten command names and examples to be generic. Where something is planned rather than built, I say so.

## Three Readers, One Set of Files

The decision that set everything else in motion was noticing that the same markdown file now has three readers. A person wants navigation, search and an owner to ask. A wiki renderer wants titles, descriptions and a folder structure it can turn into a site. And a retriever wants chunks, metadata it can filter on, and a stable anchor it can cite.

Write for only one of them and the other two suffer. A wiki that lives in a separate product drifts away from the code. A RAG index over raw files can't tell a deprecated design from a current one. A tidy folder tree with no metadata leaves an agent opening forty files to find the one it needed.

On the face of it these are three different problems, but upon closer inspection all three readers need the same thing: structured metadata on unstructured prose, kept in git and checked in CI. That, more or less, is what OKF is.

## Why the Open Knowledge Format

Google Cloud published OKF as a vendor-neutral specification for "knowledge as plain markdown files with YAML frontmatter." Version 0.2 is short enough to read in one sitting, and it asks for very little:

- **One required key,** `type`. It recommends `title`, `description`, `resource` and `tags`.
- **Provenance and trust:** `sources`, `generated` (who or what produced a concept) and `verified` (who confirmed it).
- **Lifecycle:** `status` and `stale_after`.
- **Two reserved filenames:** `index.md` (a directory listing, for progressive disclosure) and `log.md` (a dated history of changes).
- **Links as edges:** markdown links between concepts form a graph.

It imposes no folder scheme, no renderer and no query language. Backstage, MkDocs and our ingestion pipeline already read markdown with frontmatter, so adopting OKF cost us a schema rather than a platform.

We considered the alternatives and turned them down for concrete reasons, which the ADR records:

| Alternative | Why not |
|---|---|
| Add frontmatter, keep the layout | 594 story files still dominate search and the wiki |
| Diátaxis's four folders only | No home for ADRs, runbooks or delivery records, about a third of the corpus |
| A custom frontmatter schema | A private format: no shared contract with Backstage, MkDocs, or anyone else's agents |
| A wiki product instead of git | Docs leave code review and drift from the code they describe |

The risk, of course, is that OKF is young. Google's announcement describes v0.1, and the repository had already moved to v0.2 by the time we adopted it. We pin `okf_version: "0.2"` at the root of the bundle and keep our required keys a subset of the spec's, so that a change to the spec means updating a guard rather than migrating a thousand files again.

## What We Decided

The ADR made eight decisions, and five of them carry most of the weight.

First, the type vocabulary is closed and lives in config. There are eleven types: `ADR`, `Design`, `Epic`, `RCA`, `Audit`, `Guide`, `Reference`, `Explanation`, `Runbook`, `README` and `Wireframe Set`. We require `type` and `title` (stricter than the spec), plus `description` for anything an index lists, and a README's `resource` is the path of its component.

Second, freshness is data. Every concept records `generated` (a person, or `<agent>/<model>`) and, once someone has checked it against the code, `verified`. Reader docs carry `stale_after`. A stale doc gets reported rather than deleted, and superseded material gets `status: deprecated`. "Is this doc current?" stops being a guess and becomes a query.

Third, the folders are organized by what the reader needs rather than by who wrote the document:

| Folder | Holds |
|---|---|
| `guides/` | how-to manuals, onboarding |
| `reference/` | generated reference: CLI, config, endpoints |
| `explanation/` | architecture, charter, technologies |
| `decisions/` | ADRs |
| `operations/` | runbooks, infrastructure |
| `delivery/` | epics, designs, RCAs, audits, roadmap |
| `design/wireframes/` | wireframe sets |

Fourth, and this was the biggest single change, closed stories fold into their epic. In my last post I cited our 594 stories as a sign of throughput. As a corpus, I'm sorry to report, they are mostly noise. The issue tracker is the system of record for execution, yet the story files sat right beside the material a new engineer needs, and they outranked it in every search. Each epic is now a directory, with the epic itself as a concept and a `log.md` holding one dated entry per closed story (its summary, its ticket and its commit). Open stories stay as files until they close.

Fifth, the skills read the layout from the repository. My Claude Code skills had hard-coded the old paths: `docs/local/plans` 21 times, `docs/spec/stories` 17, `docs/spec/rca` 17, `docs/spec/epics` 14 and `docs/adr` 13. Moving a folder would have quietly broken the very tools that write the docs. Each repository now declares its layout in a small YAML file (artifact to path), the skills resolve paths through it, and a repository without one falls back to the old paths and carries on as before.

This is what a concept looks like after the migration:

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

The migration was ten stories in a single pull request, which touched 1,980 files. That sounds alarming, but the diff was almost entirely the output of tools, because the order of operations was the whole strategy.

We built the tools before moving anything. A generic OKF parser, index renderer and conformance checker went into our shared engine library, and the repository's CLI gained the type vocabulary and a generator for the skills' layout file.

Next came a guard in report-only mode. The first run of `check okf` against the untouched tree gave us a baseline: 1,293 files without frontmatter, 147 dead cited paths, and 48 cited CLI commands that no longer existed. It reported all of this and blocked nothing.

Then we derived the frontmatter rather than writing it by hand. A generator stamped all 1,293 files, taking each file's type from its folder, its title from its heading, its description from its first sentence, its status from any status line, and `generated` from the commit that added it. Crucially, it never sets `verified`. A machine can say who wrote a document; only a check against the code can say whether it is true.

Then the moves, with link rewriting. A `docs move <from> <to>` command runs `git mv` on a folder, rewrites every relative link from each file's new location, updates path mentions in code and config, and appends each old path to a redirects file. Records such as ADRs and closed stories keep their wording exactly as written; only their links move. The redirects file has 1,264 entries, and the wiki will serve them, so that links in old tickets and pull requests keep working.

Finally we folded, indexed and blocked. 356 closed story files became entries in epic logs, every `index.md` was generated from frontmatter (never edited by hand, and drift fails CI like any other generator), and only then did the guard start blocking.

Each move was its own commit and could be reverted on its own. I never needed that, as it happens, but having it is the reason I was willing to rewrite a thousand files in one pull request.

## Then the Names

Once the shape was enforced, a smaller problem surfaced. The bundle used three filename schemes (`NNNN-slug`, `YYYY-MM-DD-slug` and a plain `slug`), and nothing said which kind of document got which. A few files broke their folder's pattern, all of them because a skill had named them on its own initiative.

That matters once a wiki publishes the bundle, since a rename then breaks a URL. So a follow-up ADR sorts documents into three classes. Records, written once about a point in time, carry their date; these are designs, RCAs, audits and plans. Sequenced documents, cited by number or read in order, carry their number; these are ADRs, epics, stories and architecture chapters. And living documents, edited in place, carry a plain slug; these are guides, reference pages and runbooks.

Each type declares its pattern as data, in the same config file as the vocabulary, and the guard, the move command and the skills all read that one rule. The ADR's own reason for not simply writing the convention down in prose is worth quoting: *rules in prose are ignored*. Our skills had already drifted from the folders they wrote to, which rather proved the point.

## Conformant Is Not the Same as True

A green `check okf` tells you the bundle is well formed: the frontmatter parses, the types are known, the links resolve and the cited paths exist. It tells you nothing about whether the instructions actually work.

So before the wiki publishes anything, we audited the content. Every reader doc was scanned for CLI commands and flags, `localhost` ports, config keys, environment variables, dependency pins and `file:line` references, and each candidate was checked by hand against the code at a pinned commit.

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

There were fifteen findings across 241 documents: six instructions that fail when you follow them (wrong ports, environment variables that nothing reads, two retired CLI flags) and seven stale facts (counts, a dependency pin, a config key that had been renamed).

Two results stood out. The 141 generated endpoint pages had no drift at all, which is the strongest argument I know for generating reference docs. And the single worst document in the repository was the one every agent reads first. The agent instructions file had five findings on its own, mostly in its *Configuration* and *Ports* sections, which agents copy into commands verbatim. When I wrote last time that agents are only as good as the machinery around them, this is the machinery I meant, and it was wrong.

Every finding has since been fixed, and the audit itself is an OKF `Audit` concept in the bundle.

## Step 2: The Wiki

GitHub renders single files well enough, but it gives you no navigation across folders, no search over rendered docs, and no idea who owns what. Product, support and new hires need all three.

We chose Backstage with TechDocs, running in our own cluster behind single sign-on, and the design follows almost entirely from the OKF decision. TechDocs renders the bundle as it is: OKF's `title`, `description`, `tags` and `status` drive page titles, search snippets and a deprecation banner, and MkDocs ignores the keys it doesn't use, so the files stay conformant. The catalog is generated rather than written by hand; a generator writes Backstage's entities (systems, components, APIs, owners) from the build and deploy manifests and the proto contracts we already maintain, so the catalog can't drift from the build when both come from the same rows. CI builds the docs on merge and publishes them to object storage, so Backstage never builds anything at request time. And the redirects file becomes HTTP redirects, so a two-month-old ticket that links to `docs/adr/0042-…` still lands on the right page.

The alternative I was most tempted by was an AI-generated repository wiki, the DeepWiki-style approach in which you point a model at the code and get prose back. It costs nothing to author, which is appealing. We turned it down because it generates prose from code instead of publishing the docs we actually review. We have 124 ADRs, and they hold the *why*, which no model reading the code can reconstruct. The wiki ought to show what we decided, not what a model supposes we decided.

## Step 3: RAG-ify the Repository

This is the dogfooding part proper. Engineers and agents in this repository answer "how does X work?" with local tools: a code graph, semantic search and grep. Those tools are fast and good at code, but none of them reach the decisions, designs and runbooks behind the code with citations, and none of them exercise the product we actually sell.

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

Each of the pieces is designed so that a customer whose knowledge lives in repositories could use it too.

A git connector does a full import on the first sync and thereafter ingests only the files whose blob SHA has changed since the last checkpoint. A push webhook triggers a sync, with a poll as backstop. Deleted files are swept, but only after a *complete* listing, because a sweep after a partial listing would quietly wipe half the index.

Code is chunked by symbol and prose by heading. Tree-sitter splits Go, Python and TypeScript at function and type boundaries, markdown splits at `##`, and every chunk keeps its anchor, so a citation reads `path:lines@commit`.

OKF frontmatter becomes retrieval metadata. `okf_type`, `okf_status`, `okf_tags` and staleness are attached to every chunk and can be filtered at query time, and deprecated documents are excluded by default. This is where the first step pays off. Without frontmatter, the retriever can't distinguish a superseded design from a current one; with it, the distinction is a `WHERE` clause.

The repository is ingested into a dedicated internal organization, with the same tenancy, clearance and audit trail a customer gets, and it never mixes with customer data.

And a separate MCP server, built to the same standard as the rest of the product, serves it. We already had an MCP server, the one that exposes our developer CLI (lint, test, deploy) to agents on a laptop, but that server has no notion of a user, so adding query tools to it would have meant a service token that bypasses clearance. The new server is its own deployable. It authenticates the calling person through the MCP authorization flow (OAuth 2.1), exchanges that for an API token, and queries *as that person*. It holds no data and no credential that bypasses a user.

Before any of this opens up, there's a gate: an evaluation set of questions with known cited files. The server opens to all of engineering when recall@5 reaches 0.80, and not before.

The point of dogfooding is the feedback loop. When an agent in our repository gets a bad answer with a wrong citation, that is no longer a complaint about tooling. It's a product bug, filed by the very people who can fix it, against the code they're already working in.

## Optimizing the Agents

The index covers committed `main`. Agents also work against an uncommitted working tree, and that is where most of their tokens go. Spotify [reported](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90) cutting Claude Code's token usage by about 90% by routing reads through a cheaper model, on the premise that most of an agent's spending on a large file is input and output rather than reasoning.

So the same epic adds a local half. There's an `ai read --question … --paths …` operation in the CLI that wraps the named files, sends them with a single question to a small local model (a 7B model on Ollama in development), and returns terse bullets led by exact names and line numbers. The file contents never pass through the frontier model's context, and over a byte cap the operation fails and asks for fewer paths rather than truncating silently. There's a read-size hook, a Claude Code `PreToolUse` hook that blocks a whole-file read of anything over 350 lines and points the agent at the bulk-read tool instead; ranged reads pass through, since an edit still needs the exact lines, and the hook does nothing unless a repository opts in. And a related ADR routes all LLM work through named profiles rather than hard-coded model names, with every profile's tokens recorded in the same ledger the product uses for customers, so the agents' spending becomes a metric we can see per mode.

Put together, an agent has three ways to learn something: the index for knowledge that has been decided and committed, with citations; the cheap reader for the working tree; and a direct read for the exact lines it's about to edit. The frontier model's context is reserved for that last case.

## What I Have Learned So Far

I nearly started with Backstage, because it's the part people can see. That would have been a mistake. Both the wiki and the retriever are consumers of the format, and every field we added to the frontmatter for one of them helped the other at no extra cost. The format has to come first.

Machines may stamp `generated`, but only checks may stamp `verified`. Deriving 1,293 blocks of frontmatter automatically was fine. Letting that generator claim the documents were true would have produced the worst kind of metadata, which is metadata that is confident and unearned.

Report first, then block. Because the guard ran in report-only mode until the tree conformed, the baseline numbers became a list to burn down rather than 1,293 failures in CI.

Audit the file your agents read first. Our agent instructions file had more findings than any other document in the repository, and agents act on it without questioning it. If you audit one document this quarter, make it that one.

Rules in prose get ignored, so encode them as data. The type vocabulary, the layout and the naming patterns all live in config, and the guard, the move command and the skills all read them from there. The one convention we left in prose, file naming, is precisely the one that drifted.

And generated docs don't drift. 141 generated endpoint pages had no findings; 241 hand-written reader docs had fifteen. Generate everything you can.

## What's Next

The naming guard and the content fixes are committed. Next come the Backstage app and the generated catalog on the dev stack, then the git connector, the splitters and the metadata filters, then the MCP server and its token exchange, and finally the evaluation gate. A few of those steps are waiting on credentials that only a person can create (a GitHub App, a grant from the identity provider, a staging account). I'll write the follow-up once recall@5 has a number, whether or not that number clears 0.80. If it doesn't, you'll hear about that too.
