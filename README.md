# 資料庫系統 考前講義

A static exam-prep notes site for 資料庫系統 (NYCU), following Silberschatz, Korth & Sudarshan, *Database System Concepts*. Each concept gets one page, and each exam-style problem gets one walkthrough page.

The writing and design rules live in [`CLAUDE.md`](CLAUDE.md). Read them before adding a page.

## Preview

```sh
python3 -m http.server 8000
# open http://localhost:8000/
```

Opening the HTML files directly (`file://`) won't work, because the sidebar, index and glossary are built from `data/*.json` with `fetch`.

## Adding a page

1. Pick a slug and chapter (CLAUDE.md §3). Look for a `planned` entry in `data/pages.json` first.
2. Copy `templates/concept.html` into `concepts/`, or `templates/problem.html` into `problems/`.
3. Fill the sections in order (CLAUDE.md §5–§10).
4. Set the entry's `status` to `"published"` in `data/pages.json`, and add new terms to `data/glossary.json`.
5. Run `python3 scripts/check.py` until it prints `OK`.

The sidebar, index, glossary page, coverage counters and prev/next links all update from the JSON files.

## Changing the exam range

Edit `data/syllabus.json` only.

## Design credits

- Visual design follows [Material Design 3](https://m3.material.io/) baseline tokens, reimplemented in plain CSS. The color roles were generated from seed `#3F6FA8` with [`@material/material-color-utilities`](https://github.com/material-foundation/material-color-utilities) (SchemeTonalSpot, 2021 spec) and pasted into `assets/style.css`. No M3 code, text or assets are included.
- Layout and interaction decisions are guided by [Laws of UX](https://lawsofux.com/) by Jon Yablonski. No text or illustrations are copied.

## Content

All explanations and examples are original. Course PDFs go in `sources/`, which is gitignored and used for reference only (CLAUDE.md §10).
