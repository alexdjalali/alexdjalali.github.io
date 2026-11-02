# CLAUDE.md

A.J. Djalali's personal site: a Hugo blog on an in-repo theme ("Byrne's Euclid", `docs/adr/0009-*`),
deployed to GitHub Pages at <https://alexdjalali.github.io/>. `README.md` holds the full mechanics
(layout, figures, social cards, tags); this file holds the rules for writing and publishing.

## Voice — every post is written in A.J.'s voice

Prose on this site must read like A.J. wrote it, not like a language model did. His voice comes
from two sources, and a post blends them:

- **The dissertation** (*The syntax and semantics of ordinary comparative constructions in
  English*, Stanford 2015, `content/publications.md`): careful, first-person argument.
- **The Doommantia music reviews** (2010, linked from `content/about.md`): conversational, funny,
  opinionated, full of asides. **Keep the humor and the asides; drop the swearing and the anger.**
  No profanity, no insults, no contempt for people who disagree.

### What the voice does

1. **First person, arguing a position.** "I will argue that…", "I opt for…", "As far as I'm
   concerned…", "The point I want to make is this: …". He states the claim, then earns it.
2. **Names the options, then picks one.** "Empirical inadequacies … afford us (at least) two
   options. We can be evolutionary … or we can be revolutionary … I opt for …"
3. **Parenthetical asides carry the hedges and the wit.** Hedges: "(at least)", "(obviously)",
   "(to name just a few)", "to my mind at least". Wit: "(I'm beginning to wonder if I just had
   this conversation in my head.)", "(Yes, I realize the irony of what I just wrote.)", "(Of course
   there is nothing new under the sun …)". Use them often, but not in every paragraph.
4. **Opens with a scene or a stance, not a summary.** The Sleep review opens on putting *Holy
   Mountain* on for friends; the dissertation opens on the example sentence. Start with the
   concrete thing that happened or the claim in dispute.
5. **Analogies from far afield.** Gödel and Tarski to defend a stoner-metal record; John Carpenter
   to place a band. Reach for math, logic, linguistics, philosophy, film, music, when the analogy
   actually explains something, and own it when it's a stretch ("the Gödel analogy might be
   slightly off here").
6. **Signposting phrases, used sparingly.** "That is to say", "More to the point", "On the face of
   it", "upon closer investigation", "In other words", "Crucially", "Granted, …", "To be fair, …",
   "Case in point", "Really, though", "All I'm really trying to say is …", "Let's just say …".
7. **Credits others and admits limits.** Cites the people whose ideas he builds on. Says plainly
   where his own approach falls short ("my analysis was not without problems").
8. **Self-deprecating, never self-important.** "I'm a poor formal semanticist with no real job
   prospects" energy: dry about himself, generous to the reader.
9. **Sentences vary.** Long, clause-heavy sentences with Latinate words ("Spartan",
   "misbehaved", "amalgamation") sit next to short, plain ones. Paragraphs are real paragraphs,
   not one-line fragments.
10. **Ends with a turn, not a recap.** A wry closer ("In conclusion, I conclude you should buy this
    album"), a question back to the reader, or an honest statement of what's next.

### What reads as AI — remove it

- Staccato fragment runs used for drama: "Code got cheap. Decisions didn't." "Not as autocomplete,
  and not as a demo."
- "It isn't X; it's Y" / "X, not Y" reversals as a habit; "Here's the thing"; "The arithmetic is
  stark"; "This is where … comes in"; "Let that sink in".
- Rule-of-three lists everywhere (three adjectives, three clauses, three bullets).
- Every paragraph led by a **bold phrase**; bullets where prose would do; a table for anything
  with two columns.
- Headings like "Lesson 1: …", "Key Takeaways", "The Bottom Line", "Why This Matters".
- A closing section that restates the post.
- Heavy em-dash use. Prefer parentheses (his habit), commas, or a new sentence.
- Vocabulary: "delve", "leverage", "robust", "seamless", "landscape", "journey", "unlock",
  "game-changer", "in today's world", "it's worth noting".

Keep tables and lists where the content really is tabular or a sequence (ADR alternatives, step
orders, benchmark numbers). Keep code blocks and diagrams.

### Rewriting an existing post

Preserve every fact, number, link, code block, table of data, diagram and heading anchor that other
posts link to. Change the prose, not the claims. Keep the front matter (`title`, `date`, `slug`
via filename) unless asked; the `description` may be rewritten in the voice.

## Writing a post

- **File:** `content/posts/<slug>.md`. Front matter: `title`, `date` (ISO with offset), `draft`,
  `description` (rendered as the post's "To prove:" line), `images: ["images/og/<slug>.png"]`,
  `tags`, `keywords`, and `series` when it fits (`Software Architecture` or `AI-Assisted
  Engineering`). `math: true` opts into KaTeX.
- **Tags:** use existing slugs from `content/tags/`. A new tag needs `content/tags/<slug>/_index.md`
  and must group at least two posts (unless it's a topic's first post).
- **Diagrams:** `{{< mermaid >}} … {{< /mermaid >}}`.
- **Facts come from sources.** Every number, date, name and claim about a codebase is read from the
  repo, ADR, audit, git history or a fetched page in the same session. Never invent figures.
- **Proprietary work is anonymized.** Posts about client or employer codebases report aggregates
  only: no company, product or repo names, no internal paths or identifiers, and code samples
  rewritten to be generic. Say so in an "About the data" note. Say plainly what has shipped and
  what is only designed or planned.
- **AI disclosure:** posts carry the AI badge (`content/ai-disclaimer.md` explains it); A.J.
  directs and approves everything that's published.

## Figures and social cards

Every post has a generated SVG figure and a PNG social card (`README.md` → *Adding a figure for a
new post*). For a custom figure:

1. Write a test in `tools/figures/tests/unit/test_post_figures_b.py` (or `_a`) that pins what the
   figure encodes, and add the builder to the determinism parametrize list.
2. Add `tools/figures/src/figures/posts/<name>.py` with `@register("<slug>")`, import it in
   `posts/__init__.py`. Draw in the Byrne palette (`R`, `Y`, `B`, `K` from `figures.svg`) with
   `Fig` washes, lines and labels; the figure should encode the post's argument or its numbers.
3. `cd tools/figures && uv run figures generate`, then look at
   `static/images/og/<slug>.png` before committing.

Generated output (`layouts/_partials/figures/**`, `static/images/og/**`) is never hand-edited.

## Checks and publishing

Run before every commit that touches posts or figures:

```sh
cd tools/figures && uv run ruff check . && uv run ruff format --check . && uv run basedpyright src \
  && uv run figures check && uv run pytest -q
cd ../.. && hugo --quiet -d /tmp/site-check      # or `hugo server -D` to read it
```

- Commits are conventional: `feat(posts): …`, `fix(posts): …`, `fix(css): …`.
- **A push to `main` publishes.** CI (`.github/workflows/hugo.yml`) runs `figures check`, unit
  tests, the Hugo build, integration tests, an offline link check and Lighthouse, then deploys.
  Watch it with `gh run watch`.
- Commit and push only when A.J. asks.

## Where things are

- `content/posts/` posts · `content/*.md` Book pages · `content/tags/` tag names
- `layouts/` the whole theme · `assets/` CSS/JS · `data/` timeline, technologies, schema.org
- `tools/figures/` figure and social-card generator (uv, ruff, basedpyright, pytest)
- `docs/adr/` design decisions for the site
