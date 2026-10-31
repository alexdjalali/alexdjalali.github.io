# a.j.djalali

Personal academic blog built with [Hugo](https://gohugo.io/) on an in-repo theme ("Byrne's Euclid", [ADR-0009](docs/adr/0009-byrne-euclid-redesign-in-repo-theme.md)). Deployed to GitHub Pages at [alexdjalali.github.io](https://alexdjalali.github.io/).

## Structure

```
content/
  about.md                  Landing page with avatar and post cards
  cv.md                     Resume / CV with timeline styling
  publications.md           Publications, conferences, dissertation, and patents
  presentations.md          Talks and conference presentations
  projects.md               Present and past project cards
  media.md                  Media recommendations with card-deck navigation
  gear.md                   Development environment and tools
  ai-disclaimer.md          AI usage disclosure
  posts/                    Blog posts (LaTeX math via KaTeX, collapsible code blocks)
  search/                   Site search index
assets/
  css/tokens.css            Design tokens: palette, IBM Plex fonts (the only file with colour literals)
  css/base.css              Reset, typography, shell (header, Books nav, footer)
  css/custom.css            Legacy styles, removed as each page type is restyled
  js/clickable-list.js      Clickable list item handler
  js/collapsible-code.js    Expandable code blocks with copy-to-clipboard
layouts/
  posts/list.html           Posts index with year/month timeline grouping
  cv/single.html            CV page layout
  presentations/single.html Reveal.js presentation embed layout
  _partials/                Head, header (four Books), footer, JSON-LD, custom icons
presentations/              Presentation source files (Markdown, demos)
static/
  bib/                      25 individual BibTeX files (publications, dissertation, patents)
  images/                   Avatar, favicon, OG images, presentation diagrams
  presentations/            Compiled slide decks; tiya-applied-ai/ is a full course kit (rebuild with its build/make.sh)
resume/                     Resume source (LaTeX) and compiled PDF
hugo.toml                   Site configuration, nav, social links, KaTeX, Google Analytics
```

## Features

- **LaTeX math rendering** via KaTeX with Goldmark passthrough delimiters (`$...$` inline, `$$...$$` display)
- **Collapsible code blocks** with language headers and copy-to-clipboard
- **Pinterest-style post cards** on the homepage (2-column CSS grid)
- **Timeline-styled lists** for publications, CV entries, and posts index
- **Downloadable BibTeX** for all publications and patents
- **Reveal.js presentations** embedded via custom layout
- **Card-deck navigation** for Media and Gear pages
- **Light only**: five-colour palette (red, yellow, blue, black, white); no dark mode
- **JSON-LD** structured data for SEO
- **Google Analytics** (G-R50JVPX7MP)

## Local Development

```sh
hugo server -D
```

Requires Hugo v0.124.0+ (extended). Current: v0.156.0.

## Deployment

Pushes to `main` deploy automatically via GitHub Pages. The site is served from the `public/` directory at `https://alexdjalali.github.io/`.
