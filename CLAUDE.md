# CLAUDE.md: 資料庫系統 考前講義

These are the rules for this repo. Read the whole file before changing anything. If the repo and this file disagree, the repo is wrong: bring it in line with this file.

## 1. What this project is

A static exam-prep notes site for 資料庫系統 (NYCU), textbook Silberschatz, Korth & Sudarshan, *Database System Concepts*. Every page is one of two types:

- **Concept page**: explains one course concept.
- **Walkthrough page**: solves one exam-style problem.

Every page of a type has the same fixed sections in the same order, so a new page can be added by following this file alone.

- **Audience:** students in the course reviewing for the exam.
- **Reader baseline:** basic programming, set and logic notation (⊆, ⇒, ∀), plus whatever a page lists as `prerequisites`.
- **Language:** prose in 繁體中文. Technical terms are in English, as on the exam, with the Chinese term once in parentheses at first mention (§7).
- **Scope:** the current exam range in `data/syllabus.json`. Nothing outside it gets a page.
- **Hosting:** GitHub Pages from `main`, repo root. No build step, no frameworks, no external dependencies (fonts, CDNs, images).

## 2. Repository layout

```
/
├── CLAUDE.md                 the rules (this file)
├── README.md                 intro and how-to for humans
├── index.html                home: chapters, coverage, page cards
├── glossary.html             all defined terms
├── concepts/<slug>.html      concept pages
├── problems/<slug>.html      walkthrough pages
├── templates/concept.html    copy to start a concept page
├── templates/problem.html    copy to start a walkthrough page
├── data/syllabus.json        exam range: chapter order, titles, slide ranges
├── data/pages.json           registry of every page, the single source of truth for navigation
├── data/glossary.json        every term defined anywhere on the site
├── assets/style.css          the only stylesheet; all design tokens live here
├── assets/site.js            the only script: sidebar, index, glossary, pager
├── scripts/check.py          enforces this file (§14)
├── sources/                  course PDFs: GITIGNORED, reference only
└── .nojekyll
```

Do not add top-level folders, stylesheets or scripts. A new kind of content needs a change to this file first.

## 3. Naming

- Slugs are lowercase English, hyphen-separated, named the way the exam names the concept: `functional-dependency`, `bcnf`, `outer-join`.
- Walkthrough slugs: `nycu-<year>-<midterm|final>-q<n>` for real NYCU exams, `gov-<year>-<exam>-q<n>` for 高普考, `practice-<concept-slug>-<n>` for original problems.
- A page's file name, its `id` in `pages.json`, and `<body data-page-id="…">` are the same slug.

## 4. Data files

### `data/syllabus.json`: the exam range

Update only this file when the range is announced or changed.

```json
{
  "exam": "期中考",
  "note": "課本投影片及相關補充教材；Web Application 不在筆試範圍",
  "slides_url": "https://www.db-book.com/slides-dir/index.html",
  "slide_numbering": "Slide numbers are the numbers printed in each slide's footer (ch3 slide 26 = 3.26), not PDF page numbers.",
  "chapters": [
    { "id": "ch2", "title": "Introduction to the Relational Model", "slides": "3–21" },
    { "id": "ch3", "title": "Introduction to SQL", "slides": "6–28, 30–33, 49" },
    { "id": "ch4", "title": "Intermediate SQL", "slides": "3–21, 34–42" },
    { "id": "ch6", "title": "Database Design Using the E-R Model", "slides": "9–17, 21–31, 35–37, 45–51" },
    { "id": "ch7", "title": "Relational Database Design", "slides": "3–32, 36–54, 62–64, 68, 70–72" }
  ]
}
```

### `data/pages.json`: every page, published or planned

```json
{
  "id": "functional-dependency",
  "type": "concept",
  "form": "full",
  "chapter": "ch7",
  "title": "functional dependency（函數相依）",
  "prerequisites": ["superkey"],
  "summary": "One line for the index.",
  "source": null,
  "status": "published"
}
```

- `type`: `"concept"` or `"problem"`. `form` applies to concepts only: `"full"` or `"short"`.
- `chapter` must exist in `syllabus.json`.
- `source` applies to problems only, e.g. `"NYCU 2025 期中考 Q3"` or `"原創練習題"`.
- `status`: `"published"` (file exists) or `"planned"` (no file yet). Planned entries make coverage visible and tell the next session what to write.
- Order within a chapter = reading order. The sidebar, index and pager all follow it.
- `prerequisites` replaces asking the reader what they know: it sets the page's baseline for Build up and Terms (§6, §7).

### `data/glossary.json`

See §7.

## 5. Page skeleton and types

Start every page from its template. Never hand-build the skeleton.

```html
<body data-page-id="SLUG">
  <header class="top-bar"></header>                 <!-- filled by site.js -->
  <div class="shell">
    <aside class="sidebar" aria-label="目錄"></aside>   <!-- empty; filled by site.js -->
    <main>
      <h1>…</h1>
      <section class="step" id="motivate"><h2>動機</h2> … </section>
      …
      <nav class="pager"></nav>                     <!-- empty; filled by site.js -->
    </main>
  </div>
  <footer class="site-footer">說明與例子皆為原創；<a href="https://github.com/…/blob/main/CLAUDE.md">撰寫規則</a></footer>
</body>
```

Each step is a `<section class="step" id="<id>">` whose `<h2>` is the heading below. Sections appear in exactly this order.

### 5.1 Concept page, full form

| # | id | heading |
|---|---|---|
| 1 | `motivate` | 動機 |
| 2 | `build-up` | 從已知出發 |
| 3 | `definition` | 正式定義 |
| 4 | `examples` | 例子 |
| 5 | `summary` | 重點整理 |
| 6 | `exam-link` | 考試怎麼考 |
| 7 | `check` | 自我檢測 (always last) |

### 5.2 Concept page, short form

For minor concepts and sub-ideas (e.g. trivial functional dependency, natural join vs. inner join). Order: `motivate` → `build-up` → `definition` → `examples` (exactly one example) → optional `exam-note` (考試提醒, one line) → optional `check`. Include the Check when the concept is likely to be tested on its own. Build up is usually most of a short page.

### 5.3 Walkthrough page

| # | id | heading | required |
|---|---|---|---|
| 0 | `problem` | 題目 | yes: statement + `<p class="source">題目來源：…</p>` |
| 1 | `identify` | 這題在考什麼 | yes |
| 2 | `refresh` | 先複習 | only if the solution needs one |
| 3 | `solve` | 解題 | yes |
| 4 | `trap` | 陷阱 | yes |
| 5 | `check` | 變化題 | yes (always last) |

If the concept a problem tests has no published page, write a short-form concept page first, then link it from `identify`.

### 5.4 Content markup (use these, nothing else)

| Content | Markup |
|---|---|
| Relation instance | `<div class="table-wrap"><table class="relation"><caption>schema(attr, …)</caption>…</table></div>`; row labels (t₁, t₂ …) are `<th scope="row">` |
| Highlighted rows | `<tr class="hl">`. The text must also name the rows ("1001 和 1003 兩列"); never refer to them by color alone |
| Empty relation | one row: `<td class="empty" colspan="n">（沒有任何 tuple）</td>` |
| Inline math / attribute sets | `<span class="math">α → β</span>` |
| Display formula | `<p class="math">t₁[α] = t₂[α] ⇒ t₁[β] = t₂[β]</p>` |
| SQL | `<pre class="sql"><code>…</code></pre>`, keywords in lowercase as in the textbook |
| Example | `<div class="example"><p class="example-label">例 n：…</p>…</div>` |
| Non-example | same, labeled `非例：…`, saying exactly which condition fails (e.g. "satisfy 了，卻不 hold") |
| Sub-topic inside a step | `<h3>` |

## 6. Writing rules

### Motivate
- Start with the problem that forced the concept to exist, in its smallest form, before any definition.
- Where possible, show the naive approach failing (e.g. storing a shop's phone on every order lets two rows contradict each other).
- Include history only when it explains a design choice that otherwise looks arbitrary.
- For pure conventions: say what having a convention makes easier, and state that the specific choice is a convention, not a fact.

### Build up
- Derive the concept from the closest concept the reader already knows.
- **Stopping rule:** go back to the most recent concept in the page's `prerequisites` (or the baseline), and no further.
- State the mapping explicitly. ("A superkey is the special case where the right-hand side is all of R.")

### Definition
- The precise definition and notation the textbook and exam use.
- Introduce notation only after the reader knows what it stands for.
- Several definitions in one step: give each its own `<h3>`.

### Examples
- **No spurious features**: properties all examples share that the concept doesn't depend on. Vary whatever a learner would mistake for a rule: single vs. multi-attribute sides, adjacent vs. non-adjacent counterexample rows, holds vs. merely satisfied.
- One trivial example first, then non-trivial ones.
- At least one edge case: empty relation, one tuple, nulls, duplicates, a self-referencing relationship, etc.
- A non-example when the concept's boundary is unclear.
- Every example and every value in it is invented for this site (§10). Don't reuse the textbook's university database.

### Summary
A `<dl class="summary">` with exactly these entries:
- **問題 Problem**: what forced the concept to exist (for a convention: what it makes easier).
- **核心 Key idea**: the one-sentence core.
- **來自 Built from**: the earlier concept it came from.
- **差別 Difference**: what makes it different from that concept.

Omit the last two if there's no clear predecessor. Never restate the page as bullet points.

### Exam link
- Say which question types the concept appears in, and the step students most often get wrong.
- Tag every claim with its basis:
  - `<span class="basis course">課程依據：Ch.7</span>`: grounded in course material, named by chapter or title only, never quoted;
  - `<span class="basis general">一般經驗</span>`: general experience.
- A later concept (e.g. BCNF before its page exists) may be named only with a few-word gloss and a link or "（規劃中頁面）" note, e.g. "BCNF（之後的正規化形式，規劃中頁面）".

### Check
- One question set (≤ 3 parts), matched to how the exam tests the concept. It must differ from every worked example in at least one feature that matters.
- It's the last section on the page.
- The answer goes in `<details class="answer"><summary>看答案</summary>…</details>` as the last element of the section. The answer names the step most likely to fail and how to avoid it. Nothing outside `<details>` reveals the answer.

### Walkthrough sections
- `identify`: name the concept and the exact cue in the problem statement that gives it away.
- `refresh`: only what the solution needs (§8).
- `solve`: explain *why* each step is taken, not just what it does. Spend the most space where people get stuck.
- `trap`: the step most likely to go wrong, and what the wrong answer looks like.
- `check`: a variant that differs in at least one feature that matters; answer in `<details class="answer">`.

### Readability
- Paragraphs ≤ 4 sentences, one idea per paragraph.
- Lists ≤ 7 items; split or group beyond that.

## 7. Terms and the glossary

- **Define before use.** No technical term before it's defined, unless it's in the baseline or a prerequisite page. This includes Exam link (§6).
- **One name per concept:** the exam's name. Mention an abbreviation or alternative once (e.g. "縮寫 FD；本站一律寫全名"), then never use it.
- **Bilingual:** English term first, Chinese once in parentheses at first mention: functional dependency（函數相依）.
- **Three passes for standard terms:**
  1. plain-language version first;
  2. formal definition once, marked `<dfn id="term-<slug>">`;
  3. short reminders in parentheses, `<span class="reminder">（…）</span>`, for the next few mentions.
- A reminder must match the formal definition. If it simplifies, say so ("簡化版").
- Every term the page's argument depends on gets a `<dfn>`, including verbs like **holds** and **satisfy**.
- **Before writing:** read `data/glossary.json` and use existing names exactly.
- **After writing:** add every new `<dfn>` to the glossary:

```json
{ "id": "legal-instance", "term": "legal instance", "alt": "合法實例",
  "plain": "遵守全部現實規則的資料。",
  "definition": "滿足 R 所有現實世界限制的 instance r(R)。",
  "page": "functional-dependency" }
```

## 8. Refresh

- **Within a page:** if two or more other concepts have been introduced since a concept was last mentioned, refresh it in a phrase before reusing it.
- **Across pages:** a concept from a prerequisite page that Build up or a solution depends on gets an `<aside class="refresh">`. It contains only the facts the next step needs, plus a link to the page if it's published.

## 9. Accuracy

- When saying a DBMS enforces something, name the mechanism: primary key, unique, foreign key, `check`, assertion, trigger. Never imply SQL can declare a functional dependency directly. Functional dependencies become enforceable by decomposing the table so they turn into keys.
- Keep these pairs distinct and use them correctly: holds / satisfy, schema / instance, superkey / candidate key / primary key, relation / table (use relation).
- Before publishing, verify every worked example and every Check answer by recomputing it, not by rereading it.

## 10. Source material and copyright

- The official textbook slides are listed at `slides_url` in `syllabus.json`. Download the PDFs for the in-range chapters into `sources/` (never into a tracked folder). Read only the slides inside each chapter's range: a topic outside the range gets no page, even if it's in the same chapter.
- The site may link to the public slide index at `slides_url` (e.g. on the index page). It never links to, or hosts, the slide files themselves.
- `sources/` holds the course PDFs for reference only. It's gitignored. Never commit, quote, embed or link anything in it.
- From `sources/` you may take: the topic list, terminology and notation, and what the course emphasizes (for Exam link, cited by chapter or title only).
- Never take: wording, figures, worked examples, example values, sample databases, or the order of slides. Every explanation follows this file's flow, and every example is newly invented.
- If a page can't be written without leaning on one specific slide, **stop and tell the user** instead of paraphrasing it.
- Walkthrough problems may come from NYCU midterms/finals or 高普考 (exam questions are not copyrighted under 著作權法 §9(1)(5)), always with a source line. Official answer keys are never copied; solutions are written fresh.
- Never use 補習班 materials, prep books, foreign university problem sets, or verbatim textbook exercises. Original problems are labeled `題目來源：原創練習題`.
- Design references (Material Design 3, Laws of UX) are credited in the README. Their text, illustrations and assets are not copied.

## 11. Visual design

References: [Material Design 3](https://m3.material.io/) is the design system; [Laws of UX](https://lawsofux.com/) decides how we apply it. We use **M3 baseline** tokens in plain CSS. M3 Expressive (shape morphing, springs, hover scaling) is deliberately left out: this is a reading site, and motion competes with content.

### 11.1 Tokens: the only source of visual values

All visual values are CSS custom properties in `:root` of `assets/style.css`, using M3 names. Everything else uses `var(--…)`.

- **Color roles**, generated from seed `#3F6FA8` in light and dark sets (dark under `prefers-color-scheme: dark`): `--md-sys-color-{primary, on-primary, primary-container, on-primary-container, secondary-container, on-secondary-container, tertiary-container, on-tertiary-container, error, on-error, surface, on-surface, on-surface-variant, surface-container-low, surface-container, surface-container-high, surface-container-highest, outline, outline-variant}`. Every text/background pair has contrast ≥ 4.5:1 in both themes.
- **Type scale** (M3 baseline), as `--md-sys-typescale-<role>-<size>-{size, line-height, weight}`:

  | Element | Token |
  |---|---|
  | `<h1>` | headline-large (32/40) |
  | Step `<h2>` | title-large (22/28) |
  | `<h3>` | title-medium (16/24, 500) |
  | Body | body-large (16 px), line-height **1.75**: a deliberate deviation from M3's 24 px, because Chinese text needs more leading |
  | Chips, buttons, step numbers, sidebar labels | label-large / label-small |
  | Tables, SQL, math | body-medium, monospace |
  | Captions, source lines | body-small (12/16) |

- **Shape:** `--md-sys-shape-corner-{extra-small: 4px, small: 8px, medium: 12px, large: 16px, extra-large: 28px, full: 9999px}`. Step cards use large; tables and code use medium; chips use small; buttons, badges and the sidebar's active indicator use full.
- **Elevation:** depth comes from tonal surfaces, not shadows. Page = `surface`, step card = `surface-container-low`, refresh aside = `surface-container-high`. No `box-shadow` except under the top bar once scrolled.
- **State layers:** hover 8%, focus 10%, pressed 10% overlay of the content color (`color-mix()`). Keyboard focus shows a 3 px `secondary` outline with 2 px offset. Never remove focus outlines.
- **Spacing:** 4 px grid: `--space-{1:4, 2:8, 3:12, 4:16, 6:24, 8:32, 12:48}` px.
- **Motion:** only for state changes, 150–250 ms, `cubic-bezier(0.2, 0, 0, 1)`. Off under `prefers-reduced-motion`.
- **Fonts:** body `system-ui, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif`; mono `ui-monospace, "Cascadia Code", "JetBrains Mono", monospace`. No web fonts.

### 11.2 Layout (M3 window size classes)

| Class | Width | Layout |
|---|---|---|
| Compact | < 600 px | One column, 16 px margins. A sticky `<details class="toc-compact">` sits under the top bar; its summary reads `目錄 · Ch 7 · 第 3 / 7 步` and it opens the same tree as the sidebar. |
| Medium | 600–839 px | Same as compact, 24 px margins. |
| Expanded | ≥ 840 px | `.shell` grid `248px minmax(0, 1fr)`, gap `--space-8`. Sidebar sticky under the top bar, with `max-height: calc(100dvh - top bar)` and its own scroll. Content `max-width: 72ch`. |

### 11.3 Sidebar (generated by `site.js`; never hand-written)

```
開始
  首頁
  詞彙表
期中範圍
  Ch 2  Introduction to the Relational Model   1/4
  Ch 7  Relational Database Design             2/6    ← current chapter: expanded
     ● 概  functional dependency                       ← current page
          1 動機
          2 從已知出發                                  ← current step
     ○ 概  attribute closure                           ← planned: muted, not a link
```

- Built from `syllabus.json` (chapters, in order) and `pages.json` (pages, in order). The step sub-list comes from the current page's `section.step > h2`, numbered to match the CSS counter.
- Group labels: label-small, `on-surface-variant`.
- Chapter rows: monospace number · title · published/total.
- Page rows: type badge (概 / 題) · title · status dot.
- Only the current page's chapter is expanded; others are collapsed `<details>`. On the index and glossary, all chapters start collapsed.
- Published pages get a filled dot. Planned pages get a hollow dot, muted text, no link, and `aria-disabled="true"` with the visually hidden text 規劃中. Status never relies on color alone.
- Current page: `aria-current="page"`, `secondary-container` active indicator, corner full, weight 600. Current step: highlighted via IntersectionObserver, `aria-current="location"`.
- Every row is ≥ 48 px tall and clickable across its full width.

### 11.4 Components (plain-CSS versions of M3 components; nothing else)

| Component | M3 basis | Used for |
|---|---|---|
| Top bar | Small top app bar | Site title (links home); right side: `期中範圍 已發布 n / m` with a 96 px linear progress indicator. ≤ 3 links. |
| Sidebar | Standard navigation drawer / expanded navigation rail | §11.3 |
| Compact TOC | Disclosure | §11.2 |
| Step card | Filled card | Every `section.step`; `<h2>` carries a step-number badge from a CSS counter |
| **Check card** | Filled card, **`tertiary-container`** | `#check`: the only tertiary surface on a page |
| Refresh aside | Tonal container with `outline-variant` left border | `aside.refresh` |
| Basis chip | Outlined assist chip | `.basis.course` / `.basis.general`; the text carries the meaning |
| Answer button | Filled tonal button, min-height 48 px, full width on compact | `details.answer > summary` |
| Highlighted row | `secondary-container` background **plus** a ▸ marker in the first cell | `tr.hl` |
| Pager | Text buttons | `← 上一頁` / `下一頁 →` in sidebar order, published pages only |
| Index card | Filled card (published) / outlined and muted (planned) | Index, grouped by chapter with coverage; ≤ 7 visible per chapter, then 顯示更多 |

Not used: FABs, snackbars, dialogs, bottom navigation, tabs, carousels, shadows, gradients, decorative images.

### 11.5 Laws of UX: how each one shows up

| Law | Rule on this site | Enforced in |
|---|---|---|
| Jakob's Law | Documentation-site layout: title top-left links home, tree sidebar left, prev/next at the bottom, prose links underlined | templates, `site.js` |
| Mental Model | Every page of a type has the same steps, names and order | templates, checker |
| Law of Common Region | Each step is its own card; the current page's steps nest under it in the sidebar | CSS |
| Law of Proximity | Space inside a group < space between groups: heading→body `--space-2`, paragraph→paragraph `--space-4`, card→card `--space-8` | CSS tokens |
| Law of Similarity | Same role, same look: headings, chips, tables, SQL are each styled once, site-wide | CSS; no inline styles (checker) |
| Von Restorff Effect | Exactly one element per page stands out: the Check card (tertiary) | CSS, checker |
| Serial Position + Peak-End | Pages open with Motivate and end with Summary → Check → pager | templates |
| Chunking / Miller's Law / Cognitive Load | Paragraphs ≤ 4 sentences, lists ≤ 7 items, one `<h3>` per definition, wide tables scroll inside their own wrapper | §6, CSS |
| Hick's Law / Choice Overload | Top bar ≤ 3 links; only the current chapter expanded; ≤ 7 index cards per chapter before 顯示更多 | `site.js`, checker |
| Fitts's Law | Interactive targets ≥ 48 × 48 px (prose links excepted); full-row sidebar targets; full-width answer button on compact | CSS |
| Goal-Gradient Effect | Coverage in top bar and chapter rows; 第 n / N 步 in the compact TOC | `site.js` |
| Doherty Threshold | Content is static HTML; only navigation reads small JSON files; no spinners or entrance animations | architecture |
| Tesler's Law | Visual complexity lives in tokens, templates and `site.js`, so a new page needs no design decisions | this section |

## 12. Workflow: adding a page

1. Choose the type (and form for concepts), chapter and slug (§3).
2. Read `data/glossary.json` and the Summary sections of the prerequisite pages.
3. Copy the template into `concepts/` or `problems/`.
4. Fill the sections in order, following §6–§10.
5. Add or update the `pages.json` entry (`status: "published"`, correct `chapter` and position). The sidebar, index and pager update themselves.
6. Add new terms to `data/glossary.json`.
7. Run `python3 scripts/check.py` and fix everything until it prints OK.
8. Preview with `python3 -m http.server 8000` at 375 px and 1280 px, light and dark.
9. Commit `add: concept <slug>` or `add: problem <slug>`.

## 13. Editing existing pages

- Change only what was asked. Don't reorder sections, remove the Check, or restyle a page locally.
- Renaming a term: update the glossary and every page that uses it, in one commit.
- Design changes go into `style.css` tokens/components and this file together, never into one page.
- If a rule here blocks a good page, propose the change to this file to the user. Don't silently deviate.

## 14. What `scripts/check.py` enforces

Python stdlib only. It prints one line per problem and exits non-zero; on success it prints `OK: N pages, M terms`.

1. Every file in `concepts/` and `problems/` has a `pages.json` entry and vice versa; planned entries have no file; every `chapter` exists in `syllabus.json`; every prerequisite exists in `pages.json`.
2. `data-page-id` = file slug = entry `id`.
3. The skeleton (§5) is present: one empty `header.top-bar`, a `div.shell` containing one **empty** `aside.sidebar` then `main`, and one empty `nav.pager` as the last child of `main`.
4. Required section ids are present, in order, for the type and form; `check` is last where required; `details.answer` is the last element of `#check`.
5. Problem pages have `p.source`, and `pages.json` `source` is set.
6. Every `<dfn id="term-x">` has a glossary entry pointing to that page; every glossary `page` is published.
7. No `href` or `src` points into `sources/`; `git ls-files sources/` is empty.
8. Pages have no `style=` attributes and no `<style>` blocks.
9. `style.css` has no color literals (hex, `rgb()`, `hsl()`) and no raw `font-size` values outside the `:root` token blocks.
10. Contrast ≥ 4.5:1 for every `on-X` / `X` pair, and for `on-surface` and `on-surface-variant` on `surface` and every `surface-container-*`, in both themes.
11. `tertiary` is used only by the Check card rule.

## 15. Per-page done checklist

- [ ] Sections present and in order; Check last with its answer inside `details.answer`.
- [ ] Every term defined before use (including Exam link); new terms in the glossary; reminders match definitions.
- [ ] Examples: trivial first, at least one edge case, varied features, all invented; non-examples say which condition fails.
- [ ] Every example and Check answer recomputed (§9).
- [ ] Exam link claims tagged `course` or `general`.
- [ ] Highlighted rows also named in the text.
- [ ] Paragraphs ≤ 4 sentences, lists ≤ 7 items.
- [ ] Nothing from `sources/` quoted, embedded or linked.
- [ ] `pages.json` entry correct; checker prints OK; viewed at 375 and 1280 px, light and dark.

## 16. Never

- Commit anything under `sources/`, or a student ID or legal name.
- Copy wording, examples, figures or sample databases from course materials or the textbook.
- Add frameworks, CDNs, web fonts, external images, or a build step.
- Hand-write sidebar, index or prev/next links in a page.
- Put the Check answer anywhere outside `details.answer`.
- Use two names for one concept, or "FD" in prose.
- Add shadows, gradients, decorative images, or M3 Expressive motion.
