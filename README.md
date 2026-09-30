# Oppskrifter

My recipe collection, one Markdown file per dish. Weatherboy (the phone on the hallway wall) reads it. When a dish isn't here, it drafts one from the web into `drafts/` for me to try and fix.

## Add a recipe

Copy [`_mal.md`](_mal.md), fill it in, and name the file after the dish (`fiskesuppe.md`).

| Part | Notes |
|---|---|
| Front matter | `porsjoner`, `tid`, `tags` (comma-separated), `kilde` (a name or a URL) |
| `# Tittel` | then an optional sentence about the dish |
| `## Ingredienser` | `- ` lines; group with `### Til sausen` |
| `## Slik gjør du` | `1. ` one step per line |
| `## Tips` | optional, like any other `##` section |

Drafts graduate with `git mv drafts/fiskesuppe.md .` once they've been cooked and corrected.

## Print

```sh
python print.py               # the whole collection: contents page, then one recipe per page
python print.py pannekaker    # one or more recipes, drafts too: drafts/fiskesuppe
```

This writes `utskrift.html` and opens it in the browser; print from there on A4. Python 3.9+, standard library only.

On the receipt printer, ask Weatherboy for the recipe and say "skriv ut".
