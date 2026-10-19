"""Render each deck in slides_data.py as a self-contained, presentable HTML slide deck."""

import html
import pathlib
import re

from slides_data import DECKS, SLIDES, Slide

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent
e = html.escape

CSS = """
/* Layout: one 16:9 slide at a time, scaled to the window, on a dark surround; controls and notes sit below. */
:root {
  --navy: #051E39; --navy-2: #003D69; --blue: #004C97;
  --gold: #B39051; --gold-dark: #8F713D; --gold-light: #DEBD88;
  --diploma: #F9F6E5; --white: #FFFFFF; --ink: #051E39; --ink-soft: #3A4A5C;
  --surround: #020F1E; --bar-ink: #D4D9DF;
  --red: #B3261E; --amber: #9A5B00; --green: #066034;
  --f-display: "Roboto Slab", "Rockwell", Georgia, serif;
  --f-body: "Roboto", "Helvetica Neue", Arial, sans-serif;
  --f-mono: "Roboto Mono", ui-monospace, Menlo, monospace;
}
html, body { height: 100%; margin: 0; }
body { background: var(--surround); color: var(--bar-ink); font-family: var(--f-body); }
.deck { min-height: 100%; display: grid; grid-template-rows: 1fr auto; gap: 10px; padding: 12px 16px; box-sizing: border-box; }
.viewport { display: grid; place-items: center; min-height: 0; }
.slide {
  display: none; position: relative; overflow: hidden; box-sizing: border-box;
  width: min(100%, calc((100dvh - 120px) * 16 / 9)); aspect-ratio: 16 / 9; max-width: 100%;
  container-type: inline-size; background: var(--white); color: var(--ink);
  box-shadow: 0 20px 60px -20px rgba(0,0,0,.6); border-radius: 4px;
}
.slide.on { display: block; }
.notes-on .slide { width: min(100%, calc((100dvh - 260px) * 16 / 9)); }
.in { position: absolute; inset: 0; padding: 6cqw 7cqw 7cqw; display: grid; align-content: start; gap: 2.4cqw; }
h1, h2 { font-family: var(--f-display); margin: 0; text-wrap: balance; line-height: 1.12; }
h2 { font-size: 4.3cqw; font-weight: 700; }
ul { margin: 0; padding-left: 2.4cqw; display: grid; gap: 1.3cqw; font-size: 2.45cqw; line-height: 1.35; }
li::marker { color: var(--gold); }
.foot { position: absolute; left: 7cqw; right: 7cqw; bottom: 2.6cqw; display: flex; align-items: center; gap: 2cqw; font-size: 1.15cqw; color: var(--ink-soft); }
.foot .gt-logo { height: 2.2cqw; width: auto; color: var(--navy); }
.foot .n { margin-left: auto; font-family: var(--f-mono); }
.tag { justify-self: start; font-size: 1.35cqw; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; padding: .5cqw 1.2cqw; border-radius: 99px; }
.exercise { background: var(--diploma); }
.exercise .tag { background: var(--gold-dark); color: var(--white); }
.demo .tag { background: var(--navy); color: var(--white); }
.title, .section { color: var(--white); }
.title { background: var(--navy); }
.section { background: linear-gradient(to right, #051E39, #003D69, #004C97, #051E39); }
.title .in, .section .in { align-content: center; padding-bottom: 9cqw; }
.title .gt-logo { position: absolute; top: 5cqw; left: 7cqw; height: 4.4cqw; width: auto; color: var(--white); }
.title .eyebrow, .section .eyebrow { font-family: var(--f-mono); font-size: 1.6cqw; letter-spacing: .1em; text-transform: uppercase; color: var(--gold-light); }
.title h1 { font-size: 6.2cqw; max-width: 20ch; }
.section h1 { font-size: 5.6cqw; max-width: 22ch; }
.title .meta, .section .meta { display: grid; gap: .6cqw; font-size: 2.1cqw; color: #D4D9DF; }
.title::after, .section::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1.1cqw; background: linear-gradient(to right, #8F713D, #B39051, #DEBD88, #8F713D); }
.cols { display: grid; grid-template-columns: repeat(var(--n), minmax(0, 1fr)); gap: 2.4cqw; margin-top: 1.2cqw; }
.col { display: grid; align-content: start; gap: 1cqw; border-top: .5cqw solid var(--gold); padding-top: 1.6cqw; }
.col b { font-family: var(--f-display); font-size: 2.6cqw; color: var(--gold-dark); line-height: 1.15; }
.col span { font-size: 2.05cqw; line-height: 1.35; }
.col.red { border-color: var(--red); } .col.red b { color: var(--red); }
.col.amber { border-color: var(--amber); } .col.amber b { color: var(--amber); }
.col.green { border-color: var(--green); } .col.green b { color: var(--green); }
.cols[style*="--n:5"] .col b { font-size: 2.1cqw; min-height: 2.3em; } .cols[style*="--n:5"] .col span { font-size: 1.75cqw; }

.bar { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; justify-content: center; font-size: 14px; }
.bar button, .bar a { font: inherit; color: var(--bar-ink); background: transparent; border: 1px solid #1C3A5C; border-radius: 4px; padding: 6px 12px; cursor: pointer; text-decoration: none; }
.bar button:hover, .bar a:hover { border-color: var(--gold); color: var(--white); }
.bar button:focus-visible, .bar a:focus-visible { outline: 2px solid #EAAA00; outline-offset: 2px; }
.bar .count { font-family: var(--f-mono); min-width: 6ch; text-align: center; font-variant-numeric: tabular-nums; }
.bar .sep { flex: 0 0 1px; height: 20px; background: #1C3A5C; }
.notes { max-width: 900px; justify-self: center; width: 100%; box-sizing: border-box; padding: 12px 16px; border: 1px solid #1C3A5C; border-radius: 4px; color: var(--bar-ink); font-size: 15px; line-height: 1.5; min-height: 3em; }
.notes b { color: var(--gold-light); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; display: block; margin-bottom: 4px; }
@media (max-width: 640px) { .slide, .notes-on .slide { width: 100%; } }
@media print {
  @page { size: 13.333in 7.5in; margin: 0; }
  body { background: #fff; }
  html, body { height: auto; }
  .deck, .viewport { display: block; padding: 0; min-height: 0; }
  .bar, .notes { display: none !important; }
  .slide { display: block; width: 13.333in; height: 7.5in; aspect-ratio: auto; border-radius: 0; box-shadow: none; break-after: page; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .slide:last-of-type { break-after: auto; }
}
"""

JS = """
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const count = document.getElementById('count');
  const note = document.getElementById('note-text');
  const deck = document.querySelector('.deck');
  const notesBox = document.getElementById('notes');
  let i = 0;
  const show = (n) => {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => s.classList.toggle('on', k === i));
    count.textContent = `${i + 1} / ${slides.length}`;
    note.textContent = slides[i].dataset.note || 'No notes for this slide.';
    if (location.hash !== `#${i + 1}`) history.replaceState(null, '', `#${i + 1}`);
  };
  const toggleNotes = () => {
    notesBox.hidden = !notesBox.hidden;
    deck.classList.toggle('notes-on', !notesBox.hidden);
    document.getElementById('notes-btn').setAttribute('aria-pressed', String(!notesBox.hidden));
  };
  document.getElementById('prev').onclick = () => show(i - 1);
  document.getElementById('next').onclick = () => show(i + 1);
  document.getElementById('notes-btn').onclick = toggleNotes;
  document.getElementById('full').onclick = () => document.documentElement.requestFullscreen?.().catch(() => {});
  document.addEventListener('keydown', (ev) => {
    if (ev.target.closest('input, textarea')) return;
    if (['ArrowRight', 'PageDown', ' '].includes(ev.key)) { ev.preventDefault(); show(i + 1); }
    else if (['ArrowLeft', 'PageUp'].includes(ev.key)) { ev.preventDefault(); show(i - 1); }
    else if (ev.key === 'Home') show(0);
    else if (ev.key === 'End') show(slides.length - 1);
    else if (ev.key.toLowerCase() === 'n') toggleNotes();
  });
  document.querySelector('.viewport').addEventListener('click', (ev) => {
    if (ev.target.closest('a, button')) return;
    const r = ev.currentTarget.getBoundingClientRect();
    show(ev.clientX > r.left + r.width / 2 ? i + 1 : i - 1);
  });
  const fromHash = () => show((parseInt(location.hash.slice(1), 10) || 1) - 1);
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
"""


def logo_symbol() -> str:
    """Return the GT logo as a reusable <symbol>, plus the markup that references it."""
    svg = (HERE / "logo.svg").read_text()
    paths = "".join(re.findall(r"<path[^>]*/>", svg)).replace(
        'class="cls-1"', 'fill="currentColor"'
    )
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="gt" viewBox="0 0 681.82346 121.32001">{paths}</symbol></svg>'


LOGO_USE = '<svg class="gt-logo" viewBox="0 0 681.82346 121.32001" role="img" aria-label="Georgia Tech"><use href="#gt"/></svg>'


def duration(note: str) -> str:
    """Return '15 min' from a note that starts with a duration, else ''."""
    m = re.match(r"(\d+) min", note)
    return m.group(0) if m else ""


def column(b: str) -> str:
    """Render one 'Head: body' bullet as a column."""
    head, _, body = b.partition(": ")
    tone = head.lower() if head in ("Red", "Amber", "Green") else ""
    return f'<div class="col {tone}"><b>{e(head)}</b><span>{e(body)}</span></div>'


def render(s: Slide, n: int, total: int, label: str) -> str:
    """Render one slide."""
    ty, title, bullets, note = s
    items = "".join(f"<li>{e(b)}</li>" for b in bullets)
    foot = f'<div class="foot">{LOGO_USE}<span>Applied AI at TIYA Services · {e(label)}</span><span class="n">{n} / {total}</span></div>'
    if ty == "title":
        meta = "".join(f"<span>{e(b)}</span>" for b in bullets)
        inner = f'{LOGO_USE}<div class="in"><span class="eyebrow">Applied AI at TIYA Services · {e(label)}</span><h1>{e(title)}</h1><div class="meta">{meta}</div></div>'
    elif ty == "section":
        name, _, when = title.partition(" · ")
        meta = "".join(f"<span>{e(b)}</span>" for b in bullets)
        inner = f'<div class="in"><span class="eyebrow">{e(when or label)}</span><h1>{e(name)}</h1><div class="meta">{meta}</div></div>'
    elif ty == "columns":
        cols = "".join(column(b) for b in bullets)
        inner = f'<div class="in"><h2>{e(title)}</h2><div class="cols" style="--n:{len(bullets)}">{cols}</div></div>{foot}'
    else:
        tag = ""
        if ty == "exercise":
            d = duration(note)
            tag = f'<span class="tag">Exercise{" · " + d if d else ""}</span>'
        elif ty == "demo":
            tag = '<span class="tag">Live demo</span>'
        inner = f'<div class="in">{tag}<h2>{e(title)}</h2><ul>{items}</ul></div>{foot}'
    return f'<section class="slide {ty}" data-note="{e(note)}" aria-label="Slide {n}: {e(title)}">{inner}</section>'


def build(key: str) -> None:
    """Write OUT/<key>-slides.html."""
    meta, slides = DECKS[key], SLIDES[key]
    label = f"{meta['label']} · {meta['title']}"
    body = "\n".join(render(s, i + 1, len(slides), label) for i, s in enumerate(slides))
    page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>TIYA AI {meta["label"]} Slides</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@500;600;700&family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@500&display=swap">
<style>{CSS}</style>
{logo_symbol()}
<div class="deck">
  <div class="viewport">
{body}
  </div>
  <div class="bar" role="toolbar" aria-label="Slide controls">
    <a href="index.html">← Course kit</a>
    <span class="sep"></span>
    <button id="prev" type="button" aria-label="Previous slide">←</button>
    <span class="count" id="count" aria-live="polite">1 / {len(slides)}</span>
    <button id="next" type="button" aria-label="Next slide">→</button>
    <span class="sep"></span>
    <button id="notes-btn" type="button" aria-pressed="false">Notes (N)</button>
    <button id="full" type="button">Full screen</button>
    <span class="sep"></span>
    <a href="downloads/{key}-slides.pptx" download>PowerPoint</a>
    <a href="downloads/{key}-slides.pdf" download>PDF</a>
  </div>
  <div class="notes" id="notes" hidden><b>Speaker notes</b><span id="note-text"></span></div>
</div>
<script>{JS}</script>
"""
    _ = (OUT / f"{key}-slides.html").write_text(page)
    print(f"{key}-slides.html  {len(slides)} slides  {len(page) // 1024} KB")


if __name__ == "__main__":
    for k in DECKS:
        build(k)
