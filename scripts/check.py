#!/usr/bin/env python3
"""Enforce CLAUDE.md §14. Python stdlib only.

Prints one line per problem and exits non-zero; on success prints
`OK: N pages, M terms`.
"""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems = []


def err(where, msg):
    problems.append(f"{where}: {msg}")


# ---------------------------------------------------------------- HTML tree
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []   # Node or str
        self.line = 0

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def iter(self):
        for c in self.elements():
            yield c
            yield from c.iter()

    def find_all(self, tag=None, cls=None, id=None):
        return [n for n in self.iter()
                if (tag is None or n.tag == tag)
                and (cls is None or cls in n.classes)
                and (id is None or n.attrs.get("id") == id)]

    def is_empty(self):
        return not self.elements() and not "".join(c for c in self.children if isinstance(c, str)).strip()


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", {})
        self.cur = self.root
        self.style_attrs = []
        self.style_blocks = 0

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        node.line = self.getpos()[0]
        if any(k == "style" for k, _ in attrs):
            self.style_attrs.append(node.line)
        if tag == "style":
            self.style_blocks += 1
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.cur = self.cur.parent

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse_html(path):
    tb = TreeBuilder()
    tb.feed(path.read_text(encoding="utf-8"))
    tb.close()
    return tb


# ---------------------------------------------------------------- data
def load_json(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(rel, "missing")
    except json.JSONDecodeError as e:
        err(rel, f"invalid JSON: {e}")
    return None


syllabus = load_json("data/syllabus.json") or {"chapters": []}
pages = load_json("data/pages.json") or []
glossary = load_json("data/glossary.json") or []

chapter_ids = {c["id"] for c in syllabus.get("chapters", [])}
by_id = {}
for p in pages:
    pid = p.get("id", "?")
    if pid in by_id:
        err("data/pages.json", f"duplicate id {pid}")
    by_id[pid] = p

SECTIONS = {
    ("concept", "full"): ["motivate", "build-up", "definition", "examples", "summary", "exam-link", "check"],
    ("problem", None): ["problem", "identify", "refresh", "solve", "trap", "check"],
}
SHORT_ORDER = ["motivate", "build-up", "definition", "examples", "exam-note", "check"]
HEADINGS = {
    "motivate": "動機", "build-up": "從已知出發", "definition": "正式定義", "examples": "例子",
    "summary": "重點整理", "exam-link": "考試怎麼考", "check": "自我檢測", "exam-note": "考試提醒",
    "problem": "題目", "identify": "這題在考什麼", "refresh": "先複習", "solve": "解題", "trap": "陷阱",
}

# ---------------------------------------------------------------- 1. registry vs files
files = {}
for folder, ptype in (("concepts", "concept"), ("problems", "problem")):
    for f in sorted((ROOT / folder).glob("*.html")):
        files[f.stem] = (f, ptype)

for p in pages:
    pid = p.get("id", "?")
    where = f"data/pages.json[{pid}]"
    if p.get("type") not in ("concept", "problem"):
        err(where, f"type must be concept or problem, got {p.get('type')!r}")
    if p.get("type") == "concept" and p.get("form") not in ("full", "short"):
        err(where, "concept needs form full or short")
    if p.get("type") == "problem" and "form" in p and p["form"] is not None:
        err(where, "form applies to concepts only")
    if p.get("chapter") not in chapter_ids:
        err(where, f"chapter {p.get('chapter')!r} not in syllabus.json")
    for pre in p.get("prerequisites", []):
        if pre not in by_id:
            err(where, f"prerequisite {pre!r} not in pages.json")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pid):
        err(where, "slug must be lowercase, hyphen-separated")
    status = p.get("status")
    if status not in ("published", "planned"):
        err(where, f"status must be published or planned, got {status!r}")
    folder = "problems" if p.get("type") == "problem" else "concepts"
    exists = (ROOT / folder / f"{pid}.html").exists()
    if status == "published" and not exists:
        err(where, f"published but {folder}/{pid}.html does not exist")
    if status == "planned" and exists:
        err(where, f"planned but {folder}/{pid}.html exists")
    if p.get("type") == "problem":
        if not p.get("source"):
            err(where, "problem needs source")
        if not re.fullmatch(r"(nycu-\d{4}-(midterm|final)-q\d+|gov-\d{4}-[a-z0-9-]+-q\d+|practice-[a-z0-9-]+-\d+)", pid):
            err(where, "problem slug must be nycu-<year>-<midterm|final>-q<n>, gov-<year>-<exam>-q<n> or practice-<concept>-<n>")
    elif p.get("source") is not None:
        err(where, "source applies to problems only")

for stem, (f, ptype) in files.items():
    if stem not in by_id:
        err(f.relative_to(ROOT), "no entry in data/pages.json")
    elif by_id[stem].get("type") != ptype:
        err(f.relative_to(ROOT), f"folder says {ptype}, pages.json says {by_id[stem].get('type')}")


# ---------------------------------------------------------------- 3/4/8: page structure
def check_structure(path, ptype, form, tb, where):
    doc = tb.root
    # 8. no inline styles
    for line in tb.style_attrs:
        err(where, f"line {line}: style= attribute")
    if tb.style_blocks:
        err(where, "<style> block")

    body = doc.find_all("body")
    if len(body) != 1:
        err(where, "needs exactly one <body>")
        return None
    body = body[0]

    # 3. skeleton
    bars = [n for n in body.find_all("header") if "top-bar" in n.classes]
    if len(bars) != 1 or not bars[0].is_empty():
        err(where, "needs exactly one empty header.top-bar")
    shells = [n for n in body.find_all("div") if "shell" in n.classes]
    if len(shells) != 1:
        err(where, "needs exactly one div.shell")
        return None
    kids = shells[0].elements()
    if len(kids) != 2 or kids[0].tag != "aside" or "sidebar" not in kids[0].classes or kids[1].tag != "main":
        err(where, "div.shell must contain aside.sidebar then main")
        return None
    if not kids[0].is_empty():
        err(where, "aside.sidebar must be empty (site.js fills it)")
    if len([n for n in body.find_all("aside") if "sidebar" in n.classes]) != 1:
        err(where, "needs exactly one aside.sidebar")
    main = kids[1]
    pagers = [n for n in body.find_all("nav") if "pager" in n.classes]
    mk = main.elements()
    if len(pagers) != 1 or not mk or mk[-1] is not pagers[0] or not pagers[0].is_empty():
        err(where, "needs one empty nav.pager as the last child of main")
    if len(main.find_all("h1")) != 1:
        err(where, "main needs exactly one <h1>")

    # 4. sections
    steps = [n for n in main.elements() if n.tag == "section" and "step" in n.classes]
    ids = [s.attrs.get("id") for s in steps]
    for s in steps:
        sid = s.attrs.get("id")
        h2 = [c for c in s.elements() if c.tag == "h2"]
        if not h2:
            err(where, f"section#{sid} has no <h2>")
        elif sid in HEADINGS:
            want = "變化題" if (sid == "check" and ptype == "problem") else HEADINGS[sid]
            text = "".join(t for t in h2[0].children if isinstance(t, str)).strip()
            if text != want:
                err(where, f"section#{sid} heading should be {want!r}, got {text!r}")
    if ptype == "concept" and form == "short":
        required = ["motivate", "build-up", "definition", "examples"]
        if ids[:4] != required or any(i not in SHORT_ORDER for i in ids) or \
                [i for i in SHORT_ORDER if i in ids] != ids:
            err(where, f"short-form sections must be {' → '.join(required)} → [exam-note] → [check], got {ids}")
        ex = main.find_all("section", id="examples")
        if ex and len([d for d in ex[0].find_all("div") if "example" in d.classes]) != 1:
            err(where, "short form needs exactly one div.example in #examples")
    elif ptype == "concept":
        if ids != SECTIONS[("concept", "full")]:
            err(where, f"full-form sections must be {SECTIONS[('concept', 'full')]}, got {ids}")
    else:
        want = [i for i in SECTIONS[("problem", None)] if i != "refresh" or "refresh" in ids]
        if ids != want:
            err(where, f"walkthrough sections must be {want}, got {ids}")
        # 5. source line
        prob = main.find_all("section", id="problem")
        if not prob or not [n for n in prob[0].find_all("p") if "source" in n.classes]:
            err(where, "section#problem needs p.source")
    if "check" in ids:
        if ids[-1] != "check":
            err(where, "#check must be the last section")
        chk = steps[ids.index("check")]
        last = chk.elements()[-1] if chk.elements() else None
        if last is None or last.tag != "details" or "answer" not in last.classes:
            err(where, "details.answer must be the last element of #check")
    elif not (ptype == "concept" and form == "short"):
        err(where, "#check is required")
    # Never refer to the FD abbreviation in prose
    text = " ".join(t for n in main.iter() for t in n.children if isinstance(t, str))
    if re.search(r"\bFDs?\b", text):
        mentions = len(re.findall(r"\bFDs?\b", text))
        if mentions > 1 or "本站一律寫全名" not in text:
            err(where, "uses the abbreviation FD in prose (mention it once with 本站一律寫全名, then never)")
    return main


published_count = 0
dfn_index = {}  # term id -> page id
for stem, (f, ptype) in files.items():
    where = str(f.relative_to(ROOT))
    entry = by_id.get(stem, {})
    tb = parse_html(f)
    # 2. ids agree
    bodies = tb.root.find_all("body")
    if bodies and bodies[0].attrs.get("data-page-id") != stem:
        err(where, f"<body data-page-id> must be {stem!r}, got {bodies[0].attrs.get('data-page-id')!r}")
    main = check_structure(f, ptype, entry.get("form"), tb, where)
    if entry.get("status") == "published":
        published_count += 1
    # 6. dfn → glossary
    for d in tb.root.find_all("dfn"):
        did = d.attrs.get("id", "")
        if not did.startswith("term-"):
            err(where, f"line {d.line}: <dfn> needs id=\"term-<slug>\"")
            continue
        dfn_index.setdefault(did[5:], []).append(stem)
    # 7. no links into sources/
    for n in tb.root.iter():
        for attr in ("href", "src"):
            v = n.attrs.get(attr) or ""
            if re.search(r"(^|/)sources/", v):
                err(where, f"line {n.line}: {attr} points into sources/")

# Templates must keep a valid skeleton too
for tpl, ptype, form in (("templates/concept.html", "concept", "full"), ("templates/problem.html", "problem", None)):
    path = ROOT / tpl
    if not path.exists():
        err(tpl, "missing")
        continue
    check_structure(path, ptype, form, parse_html(path), tpl)

# Index and glossary pages: no inline styles, no links into sources/
for extra in ("index.html", "glossary.html"):
    path = ROOT / extra
    if not path.exists():
        err(extra, "missing")
        continue
    tb = parse_html(path)
    for line in tb.style_attrs:
        err(extra, f"line {line}: style= attribute")
    if tb.style_blocks:
        err(extra, "<style> block")
    for n in tb.root.iter():
        for attr in ("href", "src"):
            if re.search(r"(^|/)sources/", n.attrs.get(attr) or ""):
                err(extra, f"line {n.line}: {attr} points into sources/")

# ---------------------------------------------------------------- 6. glossary
gl_ids = {}
for g in glossary:
    gid = g.get("id", "?")
    where = f"data/glossary.json[{gid}]"
    for k in ("id", "term", "alt", "plain", "definition", "page"):
        if not g.get(k):
            err(where, f"missing {k}")
    if gid in gl_ids:
        err(where, "duplicate id")
    gl_ids[gid] = g
    page = by_id.get(g.get("page"))
    if not page or page.get("status") != "published":
        err(where, f"page {g.get('page')!r} is not a published page")
    elif g.get("page") not in dfn_index.get(gid, []):
        err(where, f"no <dfn id=\"term-{gid}\"> on page {g.get('page')}")

for tid, stems in dfn_index.items():
    if len(stems) > 1:
        err("pages", f"term-{tid} is defined on more than one page: {stems}")
    g = gl_ids.get(tid)
    if not g:
        err(stems[0], f"<dfn id=\"term-{tid}\"> has no glossary entry")
    elif g.get("page") not in stems:
        err(stems[0], f"glossary entry {tid} points to {g.get('page')}, not this page")

# ---------------------------------------------------------------- 7. sources/ never tracked
try:
    out = subprocess.run(["git", "ls-files", "sources/"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip():
        err("git", "files under sources/ are tracked: " + ", ".join(out.stdout.split()))
except FileNotFoundError:
    pass
gi = ROOT / ".gitignore"
if not gi.exists() or "sources/" not in gi.read_text(encoding="utf-8").split():
    err(".gitignore", "must ignore sources/")

# ---------------------------------------------------------------- 9/10/11: stylesheet
css_path = ROOT / "assets/style.css"
css = re.sub(r"/\*.*?\*/", "", css_path.read_text(encoding="utf-8"), flags=re.S)


def split_blocks(text):
    """Yield (prelude, body, start) for top-level blocks; nested blocks are returned raw."""
    i, depth, start, pre_start = 0, 0, 0, 0
    out = []
    while i < len(text):
        ch = text[i]
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append((text[pre_start:start].strip(), text[start + 1:i], start))
                pre_start = i + 1
        i += 1
    return out


light_tokens, dark_tokens = {}, {}
non_token_rules = []  # (selector, body)
for prelude, body, _ in split_blocks(css):
    if prelude == ":root":
        light_tokens.update(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body))
        continue
    if prelude.startswith("@media"):
        inner = split_blocks(body)
        for ip, ib, _ in inner:
            if ip == ":root" and "prefers-color-scheme: dark" in prelude.replace("  ", " "):
                dark_tokens.update(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", ib))
            elif ip == ":root":
                # layout-only token overrides (e.g. page margin) still count as token blocks
                if re.search(r"#[0-9a-fA-F]{3,8}\b|\b(rgb|hsl)a?\(", ib):
                    err("assets/style.css", f"color literal in {prelude} :root block")
            else:
                non_token_rules.append((ip, ib))
        continue
    non_token_rules.append((prelude, body))

for sel, body in non_token_rules:
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b|\b(rgb|hsl)a?\(", body):
        err("assets/style.css", f"color literal {m.group(0)!r} in rule {sel!r}")
    for m in re.finditer(r"font-size\s*:\s*([^;]+)", body):
        if not m.group(1).strip().startswith("var("):
            err("assets/style.css", f"raw font-size {m.group(1).strip()!r} in rule {sel!r}")
    if re.search(r"\bfont\s*:", body):
        err("assets/style.css", f"font shorthand in rule {sel!r}; use the typescale tokens")
    # 11. tertiary only in the Check card rule
    if "tertiary" in body and sel.strip() != ".step#check":
        err("assets/style.css", f"tertiary used outside the Check card rule: {sel!r}")

REQUIRED_ROLES = ["primary", "on-primary", "primary-container", "on-primary-container", "secondary-container",
                  "on-secondary-container", "tertiary-container", "on-tertiary-container", "error", "on-error",
                  "surface", "on-surface", "on-surface-variant", "surface-container-low", "surface-container",
                  "surface-container-high", "surface-container-highest", "outline", "outline-variant"]


def hex_to_rgb(v):
    v = v.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(rgb):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(hex_to_rgb(a)), luminance(hex_to_rgb(b))), reverse=True)
    return (la + 0.05) / (lb + 0.05)


for theme, tokens in (("light", light_tokens), ("dark", dark_tokens)):
    roles = {k[len("--md-sys-color-"):]: v.strip() for k, v in tokens.items() if k.startswith("--md-sys-color-")}
    for r in REQUIRED_ROLES:
        if r not in roles:
            err("assets/style.css", f"{theme}: missing --md-sys-color-{r}")
    pairs = [(r, r[3:]) for r in roles if r.startswith("on-") and r[3:] in roles]
    surfaces = ["surface"] + [r for r in roles if r.startswith("surface-container")]
    for fg in ("on-surface", "on-surface-variant", "primary"):  # primary = prose link color
        pairs += [(fg, s) for s in surfaces if fg in roles]
    for fg, bg in sorted(set(pairs)):
        try:
            c = contrast(roles[fg], roles[bg])
        except ValueError:
            err("assets/style.css", f"{theme}: {fg}/{bg} is not a hex color")
            continue
        if c < 4.5:
            err("assets/style.css", f"{theme}: contrast {fg} on {bg} is {c:.2f}:1 (< 4.5:1)")

# ---------------------------------------------------------------- report
if problems:
    for p in problems:
        print(p)
    sys.exit(1)
print(f"OK: {published_count} pages, {len(glossary)} terms")
