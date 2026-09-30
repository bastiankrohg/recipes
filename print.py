"""Print-ready recipes: writes utskrift.html, opens it in your browser, then Ctrl+P / Cmd+P.

    python print.py                    the whole collection as a cookbook: contents, then one recipe per page
    python print.py pannekaker         just these (drafts too: drafts/fiskesuppe)

Standard library only, so it runs anywhere Python does. Recipe format: see _mal.md.
"""
import html
import re
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).parent
INGREDIENTS = {"ingredienser", "ingredients"}


def parse(text):
    """-> (meta, title, intro lines, [(section, [(kind, text)])]) with kind in sub | item | step | p."""
    lines = text.splitlines()
    meta = {}
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), 0) if lines[:1] == ["---"] else 0
    for l in lines[1:end]:
        if ":" in l:
            k, v = l.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    title, intro, sections = "", [], []
    for l in (l.strip() for l in lines[end + 1 if end else 0:]):
        if not l:
            continue
        if l.startswith("# ") and not title:
            title = l[2:]
        elif l.startswith("## "):
            sections.append((l[3:], []))
        elif not sections:
            intro.append(l)
        elif l.startswith("### "):
            sections[-1][1].append(("sub", l[4:]))
        elif m := re.match(r"[-*]\s+(.*)", l):
            sections[-1][1].append(("item", m[1]))
        elif m := re.match(r"\d+[.)]\s+(.*)", l):
            sections[-1][1].append(("step", m[1]))
        else:
            sections[-1][1].append(("p", l))
    return meta, title, intro, sections


def inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(s))


def blocks(items):
    out, open_tag = [], None
    for kind, text in items:
        tag = {"item": "ul", "step": "ol"}.get(kind)
        if tag != open_tag:
            if open_tag:
                out.append(f"</{open_tag}>")
            if tag:
                out.append(f"<{tag}>")
            open_tag = tag
        out.append(f"<h3>{inline(text)}</h3>" if kind == "sub" else
                   f"<p>{inline(text)}</p>" if kind == "p" else f"<li>{inline(text)}</li>")
    return "".join(out + ([f"</{open_tag}>"] if open_tag else []))


def facts(meta):
    return " · ".join(x for x in (meta.get("porsjoner") and f"{meta['porsjoner']} porsjoner", meta.get("tid")) if x)


def card(path):
    meta, title, intro, sections = parse(path.read_text(encoding="utf-8"))
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    if path.parent.name == "drafts":
        tags.insert(0, "utkast")
    side = "".join(f"<h2>{inline(n)}</h2>{blocks(b)}" for n, b in sections if n.lower() in INGREDIENTS)
    main = "".join(f"<h2>{inline(n)}</h2>{blocks(b)}" for n, b in sections if n.lower() not in INGREDIENTS)
    src = meta.get("kilde", "")
    if src.startswith("http"):
        src = f'<a href="{html.escape(src)}">{html.escape(urlparse(src).netloc.removeprefix("www."))}</a>'
    else:
        src = html.escape(src)
    return f"""<article class="recipe" id="{html.escape(path.stem)}">
<header><p class="tags">{html.escape(" · ".join(tags))}</p><h1>{inline(title or path.stem)}</h1>
{"".join(f'<p class="intro">{inline(p)}</p>' for p in intro)}<p class="facts">{html.escape(facts(meta))}</p></header>
<div class="body"><aside>{side}</aside><main>{main}</main></div>
{f'<footer>Kilde: {src}</footer>' if src else ''}</article>"""


CSS = """
:root { --ink: #1f1c18; --muted: #6f685d; --rule: #dcd5c8; --paper: #fdfbf6; --accent: #9c3f1d; }
* { box-sizing: border-box; }
body { margin: 0; background: #ebe6dc; color: var(--ink);
  font: 11.5pt/1.5 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.recipe, .toc { background: var(--paper); max-width: 210mm; margin: 24px auto; padding: 18mm 18mm 14mm;
  box-shadow: 0 1px 3px rgb(0 0 0 / .12); }
.tags, h2, .facts, footer, .toc li span { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.tags { font-size: 8pt; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: var(--accent);
  margin: 0 0 4px; min-height: 1em; }
h1 { font-size: 30pt; line-height: 1.08; font-weight: 600; margin: 0 0 8px; }
.intro { font-style: italic; font-size: 12.5pt; color: var(--muted); max-width: 34em; margin: 0 0 4px; }
.facts { font-size: 9.5pt; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 6px; margin: 10px 0 0; }
.body { display: grid; grid-template-columns: 60mm 1fr; gap: 11mm; margin-top: 9mm; }
h2 { font-size: 8.5pt; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--accent);
  margin: 0 0 8px; }
main h2:not(:first-child) { margin-top: 8mm; }
h3 { font-size: 11pt; font-style: italic; font-weight: 400; margin: 12px 0 2px; }
ul, ol { list-style: none; margin: 0; padding: 0; }
aside li { position: relative; padding: 4px 0 4px 20px; border-bottom: 1px dotted var(--rule); }
aside li::before { content: ""; position: absolute; left: 0; top: .62em; width: 9px; height: 9px;
  border: 1.2px solid var(--ink); border-radius: 2px; }
main ul li { position: relative; padding-left: 16px; margin-bottom: 4px; }
main ul li::before { content: "–"; position: absolute; left: 0; color: var(--muted); }
ol { counter-reset: step; }
ol li { counter-increment: step; position: relative; padding-left: 36px; margin-bottom: 11px; break-inside: avoid; }
ol li::before { content: counter(step); position: absolute; left: 0; top: .05em; width: 23px; height: 23px;
  border-radius: 50%; background: var(--ink); color: var(--paper); text-align: center;
  font: 700 9.5pt/23px system-ui, sans-serif; }
main p { margin: 0 0 8px; }
footer { margin-top: 10mm; padding-top: 6px; border-top: 1px solid var(--rule); font-size: 8.5pt; color: var(--muted); }
a { color: inherit; }
.toc h1 { margin-bottom: 8mm; }
.toc ol li { break-inside: avoid; padding-left: 0; margin-bottom: 6px; display: flex; gap: 12px; align-items: baseline; }
.toc ol li::before { display: none; }
.toc a { text-decoration: none; font-size: 13pt; }
.toc li span { font-size: 8.5pt; color: var(--muted); margin-left: auto; }
@media (max-width: 640px) { .body { grid-template-columns: 1fr; } .recipe, .toc { padding: 24px 16px; margin: 0; } }
@page { size: A4; margin: 15mm 16mm; }
@media print {
  body { background: none; }
  .recipe, .toc { background: none; box-shadow: none; margin: 0; padding: 0; max-width: none; break-after: page; }
  a { text-decoration: none; }
}
"""


def main(names):
    if names:
        paths = [(HERE / n).with_suffix(".md") for n in names]
    else:  # the cookbook: everything except drafts, the template and the README
        paths = sorted(p for p in HERE.glob("*.md") if p.name.lower() != "readme.md" and not p.name.startswith("_"))
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        sys.exit(f"not found: {', '.join(missing)}")
    toc = ""
    if not names and len(paths) > 1:
        rows = []
        for p in paths:
            meta, title, _, _ = parse(p.read_text(encoding="utf-8"))
            rows.append(f'<li><a href="#{html.escape(p.stem)}">{inline(title or p.stem)}</a>'
                        f'<span>{html.escape(meta.get("tags", ""))}</span></li>')
        toc = f'<section class="toc"><p class="tags">Oppskrifter</p><h1>Kokebok</h1><ol>{"".join(rows)}</ol></section>'
    title = "Kokebok" if not names else parse(paths[0].read_text(encoding="utf-8"))[1]
    out = HERE / "utskrift.html"
    out.write_text(f"""<!doctype html><html lang="no"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body>{toc}{"".join(card(p) for p in paths)}</body></html>""", encoding="utf-8")
    print(out)
    webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main(sys.argv[1:])
