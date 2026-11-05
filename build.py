"""Build the website into dist/.

python3 build.py
python3 build.py --watch     also serves dist/ on http://127.0.0.1:8765 and rebuilds whenever a source file changes
Reads site.yaml (words, colours, music: the file to edit), content/ (exported from the private bank by
portfolio/tools/export_site.py; never edit it by hand) and src/.
Writes:
Four parts, each for a different reader:
  index.html        the hook. The cover: the record (the projects' ball), now playing, and a blurb written like
                    the back of a book that sends you on to the brief or the projects
  author.html       the brief (作者紹介): thirty seconds on who, the highlights, the years, contact, the CV per lens
  contents.html     the projects, in depth (目次): every volume as a record in its sleeve
  vol-<id>.html     one per file in content/chapters/: a volume's sleeve, its record playing, and its story. A volume is one entry, or
                    several folded together (a chapter script's `members:`), led by an entry or by a job
  <name>-cv-<lens>.pdf   each CV as an A4 PDF, printed by headless Chrome (the deploy has it; locally it's skipped
                         with a note if Chrome isn't found)
  colophon.html     the footnote (奥付): when the site was last updated and how this printing was made
"""
import html, json, math, os, re, shutil, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

import yaml

from art import panel, record, seed, sleeve

HERE = Path(__file__).parent
CONTENT, SRC, DIST = HERE / "content", HERE / "src", HERE / "dist"
CFG = {}   # site.yaml, loaded by main()
HOME = "./"
PREVIEW = os.environ.get("PREVIEW")   # set by the deploy for design/* branches: shown as a stamp

esc = lambda s: html.escape(str(s or ""), quote=True)
STATUS = {"active": "running", "paused": "paused", "shipped": "completed", "archived": "archived", "idea": "pending", "learning": "pending"}
SHELVES = [("work", "仕事", "Work"), ("academic", "研究", "Academic"), ("side", "個人", "Side projects")]


def start(period):
    m = re.search(r"(\d{4})(?:-(\d{2}))?", period or "")
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (9999, 0)


def inline_md(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)


def md_to_html(text):
    """Enough Markdown for the CVs: headings, bullets, paragraphs, bold, italics, links."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out, para, items = [], [], []
    flush = lambda: (out.append(f"<p>{'<br>'.join(inline_md(l) for l in para)}</p>") if para else None, para.clear())   # a line break in the source stays one
    close = lambda: (out.append("<ul>" + "".join(f"<li>{inline_md(i)}</li>" for i in items) + "</ul>") if items else None, items.clear())
    for line in text.splitlines():
        if not line.strip():
            flush(); close(); continue
        if m := re.match(r"^(#{1,3}) (.*)$", line):
            flush(); close(); n = len(m.group(1)); out.append(f"<h{n}>{inline_md(m.group(2))}</h{n}>"); continue
        if m := re.match(r"^- (.*)$", line):
            flush(); items.append(m.group(1)); continue
        if para and line.startswith("**"):
            flush()
        para.append(line.strip())
    flush(); close()
    return "\n".join(out)


# ---------- glyphs and art ----------
def status_glyph(status):
    style = {"active": "solid", "paused": "tone", "shipped": "outline", "archived": "faint"}.get(status, "dashed")
    body = {
        "solid": '<circle cx="6" cy="6" r="5" fill="currentColor"/>',
        "tone": '<circle cx="6" cy="6" r="4.4" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="4.5" cy="5" r="0.9" fill="currentColor"/><circle cx="7.5" cy="5" r="0.9" fill="currentColor"/><circle cx="6" cy="7.6" r="0.9" fill="currentColor"/>',
        "outline": '<circle cx="6" cy="6" r="4.4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="6" cy="6" r="1.6" fill="currentColor"/>',
        "faint": '<circle cx="6" cy="6" r="4.4" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>',
        "dashed": '<circle cx="6" cy="6" r="4.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>',
    }[style]
    return f'<svg viewBox="0 0 12 12" aria-hidden="true">{body}</svg>'


# What the music proxy will return (stage 3: a small worker holding Kai Shun's Spotify token). Until then the
# cover plays this sample, and a prototype-only switch shows the offline state.
MUSIC_API = "https://kaishun-now-playing.beanbois.workers.dev"   # the now-playing worker (worker/); empty: the cover plays SAMPLE_MUSIC
SAMPLE_MUSIC = {"sample": True, "is_playing": True, "title": "Sample track", "artist": "Sample artist", "url": None,
                "duration_ms": 214000, "progress_ms": 61000, "bpm": 96, "played_at": None}


# ---------- site.yaml ----------
def load_config():
    cfg = yaml.safe_load((HERE / "site.yaml").read_text()) or {}
    for key in ("you", "nav", "cover", "pages", "colophon", "colours"):
        if not isinstance(cfg.get(key), dict):
            raise SystemExit(f"site.yaml: the '{key}' section is missing or not a list of settings")
    cfg.setdefault("music", {})
    cfg["music"] = {k: v for k, v in (cfg["music"] or {}).items()}
    return cfg


def cfg(path):
    """A setting by its dotted path, e.g. cfg("you.name"); a missing one stops the build with its name."""
    v = CFG
    for k in path.split("."):
        if not isinstance(v, dict) or k not in v:
            raise SystemExit(f"site.yaml: '{path}' is missing")
        v = v[k]
    return str(v)


def fill(t):
    """{{you.name}} and the like in a template, from site.yaml (HTML-escaped)."""
    return re.sub(r"\{\{([a-z_]+(?:\.[a-z_]+)+)\}\}", lambda m: esc(cfg(m.group(1))), t)


# Colours by part of the site. Each part's colour falls back to a base colour, so site.yaml only sets what differs.
# The page is the base itself (paper, ink, muted).
PARTS = {
    "record": {"grooves": "tone", "edge": "ink", "label_rim": "ink"},
    "rim_player": {"track_text": "music", "level_bars": "music"},
    "tonearm": {"arm": "music"},
    "points": {"fallback": "ink"},
    "sleeve": {"paper": "paper", "border": "ink", "text": "ink"},
    "shadows": {"shadow": "ink", "blot": "ink"},
    "corners": {"triangles": "archive", "labels": "ink", "current": "spot"},
    "live": {"red": "spot", "edge": "spot_edge", "text": "spot", "on_red": "on_spot"},
    "shelf": {"running_band": "archive", "finished_band": "archive"},
    "panels": {"border": "archive", "caption_box": "mark", "caption_text": "on_mark"},
    "cv": {"paper": "paper", "border": "archive", "tabs": "archive"},
}
BASE = ("paper", "ink", "tone", "soft", "muted", "music", "archive", "mark", "on_mark", "spot", "spot_edge", "on_spot")


def colours_css():
    """The palette as CSS tokens: light on :root, dark for a dark system setting or an explicit dark theme.
    Base colours become --paper etc.; each part's colour becomes --<part>-<name>, resolved here to a value."""
    def block(name):
        pal = CFG["colours"].get(name) or {}
        for k in BASE:
            if k not in pal:
                raise SystemExit(f"site.yaml: colours.{name}.{k} is missing")
        for k, v in pal.items():
            if k not in BASE and k not in PARTS:
                raise SystemExit(f"site.yaml: colours.{name}.{k} is not a colour or a part of the site")
            if k in PARTS:
                for n in v or {}:
                    if n not in PARTS[k]:
                        raise SystemExit(f"site.yaml: colours.{name}.{k}.{n} is not one of: {', '.join(PARTS[k])}")
        out = [f"--{k.replace('_', '-')}: {pal[k]};" for k in BASE]
        for part, names in PARTS.items():
            own = pal.get(part) or {}
            out += [f"--{part}-{n}: {own.get(n, pal[base])};".replace("_", "-") for n, base in names.items()]
        return " ".join(out)
    dark = block("dark") + " color-scheme: dark;"
    return (f":root {{ {block('light')} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ {dark} }} }}\n"
            f":root[data-theme=\"dark\"] {{ {dark} }}")


def spotify_id(link, kind):
    m = re.search(rf"{kind}/([A-Za-z0-9]{{22}})", str(link or "")) or re.fullmatch(r"([A-Za-z0-9]{22})", str(link or ""))
    return m.group(1) if m else None


def music_settings(node_ids):
    """Playlists per project for the page; hidden artists and your own tempos for the worker."""
    music = CFG["music"]
    lists = {}
    for pid, link in (music.get("playlists") or {}).items():
        if pid not in node_ids:
            raise SystemExit(f"site.yaml: music.playlists has '{pid}', which is not a project id (GUIDE.md lists them)")
        if not spotify_id(link, "playlist"):
            raise SystemExit(f"site.yaml: music.playlists.{pid} is not a Spotify playlist link")
        lists[pid] = spotify_id(link, "playlist")
    bpm = {}
    for link, n in (music.get("bpm") or {}).items():
        tid = spotify_id(link, "track")
        if not tid or not isinstance(n, (int, float)) or not 30 < n < 300:
            raise SystemExit(f"site.yaml: music.bpm entry '{link}: {n}' needs a Spotify track link and a tempo between 30 and 300")
        bpm[tid] = round(n)
    worker = {"hide_artists": [str(a) for a in (music.get("hide_artists") or [])], "bpm": bpm}
    out = HERE / "worker" / "src" / "config.json"
    text = json.dumps(worker, indent=1, ensure_ascii=False) + "\n"
    if not out.exists() or out.read_text() != text:
        out.write_text(text)
        print("music: hidden artists or tempos changed; publish them with `npm run deploy` in worker/")
    return lists


# ---------- pages ----------
TEMPLATE = (SRC / "page.html").read_text()
PAGES = []  # (file, short name, kana), in reading order; filled in main
PDFS = set()  # the lenses whose CV was printed to PDF this build
UPDATED = []  # the date of the last commit: when the site last changed (filled in main)


def git(*a):
    return subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout.strip()


def nav(current, part):
    """The four corners, as on the cover: triangles point the way to each page; the page you're on is red."""
    cur = lambda f: ' aria-current="page"' if f == current else ""
    corner = lambda pos, f, k, e: f'<div class="c {pos}"><a href="{f}"{cur(f)}><i aria-hidden="true"></i><b>{k}</b>{e}</a></div>'
    return (f'<div class="c tl"><a class="home" href="{HOME}"><i aria-hidden="true"></i>{esc(cfg("you.name"))}</a><span class="part">{part}</span></div>'
            + corner("tr", "contents.html", "目次", esc(cfg("nav.projects"))) + corner("bl", "author.html", "作者", esc(cfg("nav.brief")))
            + corner("br", "colophon.html", "奥付", esc(cfg("nav.colophon"))))


def turn_html():
    """The page turn shared by the cover and every page (src/turn.html), told where the music worker is."""
    return (SRC / "turn.html").read_text().replace("__MUSIC_API__", MUSIC_API or "")


def page(file, title, part, main, script=""):
    order = [p[0] for p in PAGES]
    i = order.index(file)
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    nxt_html = f'<a href="{nxt[0]}">next: {esc(nxt[2])} {esc(nxt[1])} →</a>' if nxt else f'<a href="{HOME}">back to the cover →</a>'
    out = TEMPLATE
    if PREVIEW:
        part += f' <span class="stamp draft">preview: {esc(PREVIEW)}</span>'
    updated = f'<a class="upd" href="colophon.html">{esc(cfg("pages.updated").replace("{date}", UPDATED[0]))}</a>'
    for k, v in {"title": title, "part": part, "nav": nav(file, part), "main": main, "folio": str(i + 1), "next": nxt_html, "script": script, "home": HOME, "updated": updated}.items():
        out = out.replace("{{" + k + "}}", v)
    out = out.replace("<!--TURN-->", turn_html())
    (DIST / file).write_text(fill(out.replace("/*__COLOURS__*/", colours_css())))


def split(main, rail, rail_first=True):
    """7-3: the page's main thing on the left, a sticky rail of what supports it on the right.
    On a phone the two stack, the rail first unless the main thing should be seen first (a volume's cover)."""
    return f'<div class="split{"" if rail_first else " main-first"}"><div class="main">{main}</div><aside class="rail">{rail}</aside></div>'


def chapter_files():
    """Each chapter script, by its volume's id: `id:` if it sets one, else its entry's."""
    out = {}
    for p in sorted((CONTENT / "chapters").glob("*.yaml")):
        ch = yaml.safe_load(p.read_text())
        out[ch.get("id", ch["entry"])] = ch
    return out


LIVENESS = ["active", "paused", "shipped", "archived", "idea", "learning"]   # a volume takes its liveliest entry's status


def volumes(nodes, groups, chapters):
    """The shelf: one spine per volume, and one per entry no volume holds yet. Also returns, for each entry in a
    volume, that volume's id. A volume of several entries takes its title and tagline from the chapter script, its
    period across all of them, and its words from the entry or job it's led by."""
    byid = {n["id"]: n for n in nodes}
    shelf, home = [], {}
    for vid, ch in chapters.items():
        lead = ch["entry"]
        if lead not in byid and lead not in groups:
            raise SystemExit(f"content/chapters: {vid} is led by '{lead}', which is neither a public entry nor a job")
        ids = ([lead] if lead in byid else []) + list(ch.get("members") or [])
        for i in ids:
            if i not in byid:
                raise SystemExit(f"content/chapters: {vid} holds '{i}', which is not a public entry")
            if i in home:
                raise SystemExit(f"content/chapters: '{i}' is in both {home[i]} and {vid}")
            home[i] = vid
        ms = [byid[i] for i in ids]
        head = byid.get(lead) or dict(groups[lead], kind="job", track=ms[0]["track"], tagline="", bullets=[], stack=[])
        dates = [d for m in ms for d in re.findall(r"\d{4}(?:-\d{2})?", m["period"])]
        end = "present" if any("present" in m["period"] for m in ms) else max(dates)
        period = head["period"] if len(ms) == 1 else min(dates) + ("" if end == min(dates) else f" – {end}")
        keys = {k for m in ms for k in m["mix"]}
        shelf.append(dict(head, id=vid, members=ids, title=ch.get("title", head["title"]), tagline=ch.get("tagline", head.get("tagline", "")),
                          period=period, status=min((m.get("status") for m in ms), key=LIVENESS.index),
                          stack=list(dict.fromkeys(x for m in [head] + ms for x in m.get("stack", []))),
                          mix={k: sum(m["mix"].get(k, 0) for m in ms) / len(ms) for k in keys},
                          size="big" if len(ms) > 1 else head.get("size"), verified=all(m.get("verified") for m in ms)))
    return shelf + [n for n in nodes if n["id"] not in home], home


def blot(cls="blot"):
    """The page's one organic shape: an ink blot in screentone, behind everything else."""
    pts = []
    for i in range(73):
        a = i / 72 * 2 * math.pi
        r = 120 * (1 + 0.13 * math.sin(3 * a + 0.6) + 0.07 * math.sin(5 * a + 2.1) + 0.04 * math.sin(9 * a))
        pts.append(f"{200 + r * math.cos(a) * 1.3:.1f},{150 + r * math.sin(a) * 0.95:.1f}")
    return (f'<svg class="{cls}" viewBox="0 0 400 300" aria-hidden="true"><defs><pattern id="bd" width="5" height="5" patternUnits="userSpaceOnUse">'
            f'<circle cx="2.5" cy="2.5" r="1" fill="currentColor"/></pattern></defs><path d="M{" L".join(pts)} Z" fill="url(#bd)"/></svg>')


def contents_page(nodes, vols, chapters):
    """The projects, in depth: every volume as a record in its sleeve, a grid per shelf. Hovering pulls the record half
    out; clicking pulls it all the way and the volume page opens with the record carried over (see the transition
    in src/page.html)."""
    secs, sleeves = [], {}
    for track, kana, name in SHELVES:
        items = sorted([n for n in nodes if n.get("track", "side") == track], key=lambda n: vols[n["id"]])
        if not items:
            continue
        cards = []
        for n in items:
            ch, vid = chapters.get(n["id"]), n["id"]
            if not ch:
                continue
            mix = " ".join(k for k, w in n["mix"].items() if w >= 0.3)
            live = n.get("status") == "active"
            cards.append(f'<a class="lp-card{" live" if live else ""}" href="vol-{vid}.html" data-vt="{vid}" data-status="{n.get("status")}" data-mix="{mix}">'
                         f'<div class="lp"><div class="disc">{record(n, vols[vid], ch)}</div><div class="obj sl">{sleeves.setdefault(vid, sleeve(n, vols[vid], ch, cfg("you.name")))}</div></div>'
                         f'<div class="cap"><span class="mono muted">Vol. {vols[vid]} · {esc(n["period"])}{" · " if live else ""}<span class="livetxt">{"running" if live else ""}</span></span>'
                         f'<b>{esc(n["title"])}</b><small>{esc(n.get("tagline") or "")}</small></div></a>')
        secs.append(f'<section aria-labelledby="sh-{track}" id="sh-{track}"><h2 class="gh" id="sh-{track}-h"><span class="jp">{kana}</span> {name} '
                    f'<span class="mono muted">{len(items)}</span></h2><div class="lp-grid">{"".join(cards)}</div></section>')
    statuses = [("all", "all"), ("active", "running"), ("shipped", "completed"), ("paused", "paused"), ("archived", "archived"), ("idea", "pending")]
    skills = [("all", "all"), ("ml", "ML"), ("backend", "Backend"), ("infra", "Infra"), ("product", "Product")]
    chips = lambda f, opts: "".join(f'<button type="button" class="chip" data-f="{f}" data-v="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in opts)
    filt = (f'<div class="filters" role="group" aria-label="Filter the projects"><div class="grp"><span class="lbl">status</span>{chips("status", statuses)}</div>'
            f'<div class="grp"><span class="lbl">skill</span>{chips("mix", skills)}</div></div>')
    main = (f'<div class="pt"><h1>目次</h1><p>{esc(cfg("pages.contents_intro"))}</p></div>{filt}' + "".join(secs))
    script = r"""<script>
/* click: pull the record all the way out, then open its volume; the browser carries record and sleeve across */
// no pull without a turn to carry the record on: reduced motion, and iPhones, where pages don't turn (src/turn.html)
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches || CSS.supports("-webkit-touch-callout", "none");
document.querySelectorAll(".lp-card").forEach(card => card.addEventListener("click", e => {
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
  card.querySelector(".disc").style.viewTransitionName = "rec";
  card.querySelector(".sl").style.viewTransitionName = "sleeve";
  if (reduce) return;
  e.preventDefault();
  const pull = () => { card.classList.add("pulling"); setTimeout(() => { location.href = card.href; }, 420); };  // out, clear, a beat at rest, then the turn
  /* first the shelf breaks into dots round the chosen card, then the record comes out */
  const s = card.querySelector(".lp").getBoundingClientRect();
  card.classList.add("chosen");
  toneDots(toneVeil(), s.left + s.width / 2, s.top + s.height / 2, 640);
  setTimeout(pull, 600);
}));
/* fetch a volume as soon as a card is pointed at, so the turn doesn't wait on the network */
const got = new Set();
document.querySelectorAll(".lp-card").forEach(card => ["pointerenter", "focus", "touchstart"].forEach(ev => card.addEventListener(ev, () => {
  if (got.has(card.href)) return; got.add(card.href);
  const l = document.createElement("link"); l.rel = "prefetch"; l.href = card.href; document.head.append(l);
}, { passive: true })));
/* back from a volume: hand the record back to its own sleeve. Only for a shelf restored from the page cache, as it was
   left: a fresh load has nothing to tidy, and its pageshow comes when the fonts are in, partway through the turn home,
   where taking the veil away cut the turn short and the shelf just appeared */
addEventListener("pageshow", e => {
  if (!e.persisted) return;
  document.querySelectorAll(".pulling, .chosen").forEach(c => c.classList.remove("pulling", "chosen"));
  document.querySelectorAll(".tone-veil").forEach(v => v.remove());
});
const want = { status: "all", mix: "all" };
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  want[c.dataset.f] = c.dataset.v;
  document.querySelectorAll(`.chip[data-f="${c.dataset.f}"]`).forEach(o => o.setAttribute("aria-pressed", String(o === c)));
  document.querySelectorAll(".lp-card").forEach(s => {
    const st = s.dataset.status === "learning" ? "idea" : s.dataset.status;
    s.classList.toggle("dim", !((want.status === "all" || st === want.status) && (want.mix === "all" || s.dataset.mix.split(" ").includes(want.mix))));
  });
}));
</script>"""
    page("contents.html", "目次 · Teoh Kai Shun", f'目次 {esc(cfg("nav.projects"))}', main, script)


VOLUME_JS = r"""<script>
/* The record plays. When it lands (after the transition from the shelf, or on a plain load) it spins at 33⅓ for a
   few seconds and slows to a stop; after that it turns as you scroll. The tonearm drops onto the outer groove and
   follows how far through the volume you've read, and lifts at the end. Reduced motion: no spin, the arm just sits. */
(() => {
  /* on a phone the rail comes after the story, so the turntable moves up beside the sleeve (before the first paint) */
  if (matchMedia("(max-width: 860px)").matches) document.querySelector(".vtop").append(document.querySelector(".deck"));
  const svg = document.querySelector(".deck .record"), spin = svg.querySelector(".spin"), arm = document.getElementById("arm");
  const IN = +svg.dataset.in, OUT = +svg.dataset.out, PX = 300, PY = -200, L = 312;   // pivot and arm length, in the record's units
  const D = Math.hypot(PX, PY), BASE = Math.atan2(-PY, -PX) * 180 / Math.PI;
  const armAt = r => BASE - Math.acos((D * D + L * L - r * r) / (2 * D * L)) * 180 / Math.PI;
  const PARK = armAt(296) - 22, reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let angle = 0, omega = 0, hold = 0, armA = PARK, armTo = PARK, dropped = false, lastY = scrollY, last = 0, raf = 0;
  const progress = () => { const max = document.documentElement.scrollHeight - innerHeight; return max > 0 ? Math.min(1, scrollY / max) : 0; };
  const target = () => !dropped ? PARK : progress() > 0.985 ? PARK : armAt(OUT - 4 - progress() * (OUT - IN - 8));
  const draw = () => { spin.setAttribute("transform", `rotate(${angle.toFixed(2)})`); arm.setAttribute("transform", `translate(${PX} ${PY}) rotate(${armA.toFixed(2)})`); };
  function tick(now) {
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    angle = (angle + omega * dt) % 360;
    if (hold > 0) hold -= dt; else omega *= Math.exp(-dt / 0.9);       // 33⅓ for a while, then friction
    armA += (armTo - armA) * (1 - Math.exp(-dt * 5));
    draw();
    if (Math.abs(omega) > 0.5 || Math.abs(armTo - armA) > 0.05) raf = requestAnimationFrame(tick); else { raf = 0; last = 0; }
  }
  const kick = () => { if (!raf) raf = requestAnimationFrame(tick); };
  function play() {
    dropped = true;
    if (reduce) { armA = armTo = target(); draw(); return; }
    omega = 200; hold = 2.6; kick();                                    // 33⅓ rpm is 200 degrees a second
    setTimeout(() => { armTo = target(); kick(); }, 350);                // the platter first, then the needle
  }
  addEventListener("scroll", () => {
    const dy = scrollY - lastY; lastY = scrollY;
    if (!dropped) return;
    armTo = target();
    if (reduce) { armA = armTo; draw(); return; }
    angle += dy * 0.35; kick();
  }, { passive: true });
  draw();
  if ("onpagereveal" in window) addEventListener("pagereveal", e => (e.viewTransition ? e.viewTransition.finished : Promise.resolve()).then(play, play), { once: true });
  else setTimeout(play, 150);
})();
</script>"""


def volume_page(n, vol, ch, log, byid, prev=None, nxt=None):
    """A project in depth. prev and nxt are the volumes either side on the shelf, as (book, number)."""
    eps = []
    for k, ep in enumerate(ch["episodes"]):
        last = k == len(ch["episodes"]) - 1
        e = byid.get(ep.get("entry"), n)   # an episode about one of the volume's entries carries that entry's stamps
        panels = "".join(f'<figure class="panel s{p["span"]}" style="margin:0">{panel(p["art"], p["span"])}<figcaption class="txt"><span class="cap">{esc(p["caption"])}</span><p>{esc(p["text"])}</p></figcaption></figure>' for p in ep["panels"])
        live = e.get("status") == "active"
        eps.append(f'''<section class="tobira" aria-labelledby="ep{ep["n"]}"><div class="ep jp">第{ep["n"]}話</div><h2 id="ep{ep["n"]}">{esc(ep["title"])}</h2>
<div class="stamps"><span class="stamp{" live" if live else ""}">{STATUS.get(e.get("status"))}</span>{"" if e.get("verified") else '<span class="stamp draft">draft</span>'}</div></section>
<div class="page">{panels}</div>
<div class="tsuzuku"><span class="muted mono" style="font-size:12px">{"the end" if last and not live else "to be continued" if last else "continued"}</span><span class="big">{"完" if last and not live else "つづく"}</span></div>
{f'<div class="next"><span class="lbl jp">次回予告</span><span>Next time: {esc(ep["next"])}</span></div>' if ep.get("next") else ""}''')
    events = "".join(f"<li><time>{d}</time>{esc(msg)}</li>" for d, i, msg in sorted(log, reverse=True) if i in n["members"])
    repo = f'<a href="{esc(n["repo"])}" target="_blank" rel="noopener">{esc(n["repo"].split("github.com/")[-1])}</a>' if n.get("repo") else "private"
    toc = "".join(f'<li><a href="#ep{ep["n"]}"><span class="jp">第{ep["n"]}話</span> {esc(ep["title"])}</a></li>' for ep in ch["episodes"])
    link = lambda b, arrow: f'<a href="vol-{b[0]["id"]}.html">' + (f'← Vol. {b[1]} · {esc(b[0]["title"])}' if arrow == "←" else f'Vol. {b[1]} · {esc(b[0]["title"])} →') + "</a>"
    side = "".join(f"<li>{link(b, a)}</li>" for b, a in ((prev, "←"), (nxt, "→")) if b)
    volnav = ('<nav class="volnav" aria-label="Other volumes">'
              + (f'<a class="vn-prev" href="vol-{prev[0]["id"]}.html"><span>← Vol. {prev[1]}</span><b>{esc(prev[0]["title"])}</b></a>' if prev else "<span></span>")
              + '<a class="vn-all" href="contents.html"><span class="jp">目次</span></a>'
              + (f'<a class="vn-next" href="vol-{nxt[0]["id"]}.html"><span>Vol. {nxt[1]} →</span><b>{esc(nxt[0]["title"])}</b></a>' if nxt else "<span></span>")
              + "</nav>")
    blurb = (f'<div class="blurb"><h2>あらすじ · the story so far</h2><p>{inline_md(n["what"] or n["tagline"])}</p>'
             f'<dl><dt>period</dt><dd>{esc(n["period"])}</dd><dt>status</dt><dd>{STATUS.get(n.get("status"))}</dd><dt>repo</dt><dd>{repo}</dd></dl></div>')
    rail = (blurb
            + f'<div class="back"><div><h3>stack</h3><div class="chips">{"".join(f"<span>{esc(s)}</span>" for s in n["stack"])}</div></div>'
            + (f'<div><h3>log</h3><ol>{events}</ol></div>' if events else "")
            + (f'<div><h3>in this volume</h3><ol>{toc}</ol></div>' if len(ch["episodes"]) > 1 else "")
            + f'<div><h3>elsewhere</h3><ul>{side}<li><a href="contents.html">all the projects →</a></li><li><a href="./#{n["id"]}">find it on the record →</a></li></ul>'
            + ("" if n.get("verified") else f'<p class="muted" style="font-size:13px;margin-top:10px">{esc(cfg("pages.draft_note"))}</p>') + '</div></div>')
    deck = (f'<div class="deck"><div class="rec-wrap">{record(n, vol, ch)}</div>'
            '<svg class="arm" viewBox="-250 -250 600 500" aria-hidden="true"><g id="arm" transform="translate(300 -200) rotate(95)">'
            '<circle r="24" style="fill:var(--paper);stroke:var(--tonearm-arm);stroke-width:5"/><rect x="-62" y="-13" width="30" height="26" style="fill:var(--tonearm-arm)"/>'
            '<path d="M0 0 H294" style="stroke:var(--tonearm-arm);stroke-width:7;stroke-linecap:round"/>'
            '<rect x="290" y="-15" width="44" height="30" rx="3" style="fill:var(--tonearm-arm)"/><circle cx="312" r="5" style="fill:var(--paper)"/>'
            '<circle r="7" style="fill:var(--tonearm-arm)"/></g></svg></div>')   # the stylus is the paper dot at the arm's length, 312
    main = split(f'<div class="vtop"><div class="vsleeve obj">{sleeve(n, vol, ch, cfg("you.name"))}</div></div>' + "".join(eps) + volnav, deck + rail, rail_first=False)
    page(f'vol-{n["id"]}.html', f'{n["title"]} · Vol. {vol}', f'Vol. {vol} · {esc(n["title"])}', main, VOLUME_JS)


def author_page(data, books, vols, pdfs):
    """The brief: what a busy reader needs in thirty seconds. Who, the highlights (site.yaml picks them), the years,
    contact and the CV, as PDFs beside it and in full below."""
    p = data["profile"]
    yrs = "".join(f"<li><time>{esc(re.sub(r' – present', '–', y['period']))}</time><span>{esc(y['what'])}</span></li>" for y in data["years"])
    hl = []
    for vid in CFG["pages"].get("highlights") or []:
        if vid not in books:
            raise SystemExit(f"site.yaml: pages.highlights has '{vid}', which is not a volume (GUIDE.md lists the ids)")
        b, live = books[vid], books[vid].get("status") == "active"
        hl.append(f'<li><a href="vol-{vid}.html"><span class="no">Vol. {vols[vid]}</span><b>{esc(b["title"])}</b>'
                  f'<span class="tag">{esc(b.get("tagline") or "")}</span>'
                  f'<span class="meta">{esc(b["period"])} · <span class="{"live" if live else ""}">{STATUS.get(b.get("status"), "")}</span></span></a></li>')
    tabs, sheets, gets = [], [], []
    for i, (lens, label) in enumerate(LENSES):
        f = CONTENT / "cv" / f"{lens}.md"
        if not f.exists():
            continue
        body = md_to_html(f.read_text())
        body = re.sub(r"(</h1>\n)<p>", r'\1<p class="head">', body, count=1)
        if lens in pdfs:
            body = f'<a class="btn pdf" href="{pdf_name(lens)}" download>{esc(cfg("pages.cv_pdf_link"))}</a>' + body
        gets.append(f'<a class="btn" href="{pdf_name(lens)}" download>{label} · PDF</a>' if lens in pdfs else f'<a class="btn" href="#cv-{lens}" data-lens="{lens}">{label}</a>')
        tabs.append(f'<button type="button" role="tab" id="tab-{lens}" aria-controls="cv-{lens}" aria-selected="{str(i == 0).lower()}">{label}</button>')
        sheets.append(f'<article class="cv obj" role="tabpanel" id="cv-{lens}" aria-labelledby="tab-{lens}"{"" if i == 0 else " hidden"}>{body}</article>')
    rail = f"""<div class="pt"><h1>作者紹介</h1><p>{esc(cfg("pages.author_intro"))}</p></div>
<div class="flap">
  <div class="seal" aria-hidden="true">KS</div>
  <div><h2 style="margin:0 0 4px;font-size:28px">{esc(p["name"])}</h2><p class="mono muted" style="margin:0;font-size:12px">{esc(cfg("you.role_short"))}</p></div>
  <div class="comment"><span class="mono muted" style="font-size:11px">{esc(cfg("pages.author_comment_label"))}</span><br>{esc(cfg("you.one_liner"))}</div>
  <div><h3>{esc(cfg("pages.cv_get"))}</h3><div class="row">{"".join(gets)}</div></div>
  <div><h3>contact</h3><div class="contact">
    <div class="row"><span class="select" id="email">{esc(p["email"])}</span><button type="button" class="btn" id="copy">copy</button></div>
    <a href="{esc(p["github"])}" target="_blank" rel="noopener">github.com/BeanBois</a>
    <a href="{esc(p["linkedin"])}" target="_blank" rel="noopener">linkedin.com/in/kai-shun-teoh</a></div></div>
  <div><h3>{esc(cfg("pages.years_heading"))}</h3><ol class="years">{yrs}</ol></div>
</div>"""
    brief = (f'<section class="brief" aria-labelledby="b-sum"><h2 class="kicker" id="b-sum">{esc(cfg("pages.brief_summary"))}</h2><p class="sum">{inline_md(p.get("summary") or "")}</p></section>'
             # the projects and the CV share one place, as two tabs
             + '<section class="brief"><div class="btabs" role="tablist" aria-label="The brief">'
             + f'<button type="button" role="tab" id="bt-hl" aria-controls="bp-hl" aria-selected="true">{esc(cfg("pages.highlights_heading"))}</button>'
             + f'<button type="button" role="tab" id="bt-cv" aria-controls="bp-cv" aria-selected="false">{esc(cfg("pages.cv_heading"))}</button></div>'
             + f'<div role="tabpanel" id="bp-hl" aria-labelledby="bt-hl"><ol class="hl">{"".join(hl)}</ol></div>'
             + f'<div role="tabpanel" id="bp-cv" aria-labelledby="bt-cv" hidden><div class="tabs" role="tablist" aria-label="CV lens">{"".join(tabs)}</div>{"".join(sheets)}</div></section>')
    main = split(brief, rail)
    script = """<script>
/* two tab sets: the brief's (highlights | the CV) and, inside the CV, the lens (ML | Cloud | Backend) */
const set = sel => {
  const tabs = [...document.querySelectorAll(sel)];
  const pick = id => tabs.forEach(t => { const on = t.id === id; t.setAttribute("aria-selected", String(on)); t.tabIndex = on ? 0 : -1; document.getElementById(t.getAttribute("aria-controls")).hidden = !on; });
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => pick(t.id));
    t.addEventListener("keydown", e => {   // arrow keys move between tabs
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (!d) return;
      const n = tabs[(i + d + tabs.length) % tabs.length]; pick(n.id); n.focus();
    });
  });
  pick(tabs.find(t => t.getAttribute("aria-selected") === "true").id);
  return pick;
};
const brief = set(".btabs [role=tab]"), lens = set(".tabs [role=tab]");
const showCv = l => { brief("bt-cv"); if (l) lens("tab-" + l); };
document.querySelectorAll("[data-lens]").forEach(a => a.addEventListener("click", () => showCv(a.dataset.lens)));
const h = location.hash;   // author.html#cv opens the CV; #cv-ml opens it on that lens
// after the browser's own jump to the anchor, so the tabs are in view rather than the sheet's top
const land = () => addEventListener("load", () => setTimeout(() => document.querySelector(".btabs").scrollIntoView({ block: "start" }), 0));
if (h === "#cv") { showCv(); land(); }
else if (h.startsWith("#cv-") && document.getElementById("tab-" + h.slice(4))) { showCv(h.slice(4)); land(); }
const copy = document.getElementById("copy"), email = document.getElementById("email");
copy.onclick = () => {
  const fallback = () => { const r = document.createRange(); r.selectNodeContents(email); getSelection().removeAllRanges(); getSelection().addRange(r); };
  try { navigator.clipboard.writeText(email.textContent).then(() => { copy.textContent = "copied"; }, fallback); } catch { fallback(); }
};
</script>"""
    page("author.html", "作者紹介 · Teoh Kai Shun", f'作者紹介 {esc(cfg("nav.brief"))}', main, script)


# ---------- the CVs as PDFs ----------
LENSES = [("ml", "ML"), ("cloud", "Cloud"), ("backend", "Backend")]
PRINT_CSS = """@page { size: A4; margin: 12mm 14mm 11mm; }
body { margin: 0; color: #1d1d1f; font: var(--pt)/1.38 "Inter", "Zen Kaku Gothic New", "Hiragino Sans", sans-serif; }   /* Inter: only + and ×, which Zen draws full-width */
h1 { font: 400 22pt/1.1 "Dela Gothic One", sans-serif; letter-spacing: 0.02em; margin: 0 0 3pt; }
h1 + p { font: 8.4pt "IBM Plex Mono", monospace; margin: 0 0 8pt; }
h2 { font: 500 8.4pt "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: 0.12em; margin: 9pt 0 4pt; padding-bottom: 2pt; border-bottom: 1.2pt solid #1d1d1f; break-after: avoid; }
p { margin: 0 0 4pt; } ul { margin: 0 0 6pt; padding-left: 12pt; } li { margin-bottom: 1pt; break-inside: avoid; }
p:has(+ ul) { break-after: avoid; }
a { color: inherit; text-decoration: none; }"""


def find_chrome():
    for c in (os.environ.get("CHROME"), shutil.which("google-chrome"), shutil.which("google-chrome-stable"), shutil.which("chromium"),
              shutil.which("chromium-browser"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if c and Path(c).exists():
            return c


def pdf_name(lens):
    return re.sub(r"[^a-z]+", "-", cfg("you.name").lower()).strip("-") + f"-cv-{lens}.pdf"


def pdf_pages(path):
    return len(re.findall(rb"/Type\s*/Page[^s]", path.read_bytes()))


def cv_pdfs():
    """Print each CV to dist/ as a PDF, on one A4 page if a slightly smaller type size gets it there. Returns the
    lenses that got one. On the deploy (CI) a failure stops the build, so the site never links a PDF that isn't there."""
    chrome, ci = find_chrome(), os.environ.get("CI") == "true"
    if not chrome:
        if ci:
            raise SystemExit("CV PDFs: no Chrome found on the deploy")
        print("CV PDFs: skipped, no Chrome found (set CHROME to its path); the author page shows no PDF links")
        return set()
    made = set()
    with tempfile.TemporaryDirectory() as tmp:
        for lens, label in LENSES:
            f = CONTENT / "cv" / f"{lens}.md"
            if not f.exists():
                continue
            out = DIST / pdf_name(lens)
            for pt in ("9.4pt", "9.1pt", "8.8pt"):    # the body size: smaller until the CV fits one page
                page_ = Path(tmp) / f"{lens}.html"
                page_.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(cfg("you.name"))}, CV ({label})</title>'
                                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=IBM+Plex+Mono:wght@400;500&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=block">'
                                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&text=%2B%C3%97&display=block">'
                                 f'<style>:root {{ --pt: {pt}; }}\n{PRINT_CSS}</style></head><body>{md_to_html(f.read_text())}</body></html>')
                for attempt in (1, 2):   # headless Chrome now and then hangs; a second go nearly always works
                    try:
                        r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                                            f"--user-data-dir={tmp}/profile-{lens}-{pt}-{attempt}", *(["--no-sandbox"] if ci else []),
                                            f"--print-to-pdf={out}", page_.as_uri()], capture_output=True, text=True, timeout=45)
                        err = r.stderr.strip()[-300:] if r.returncode or not out.exists() else None
                    except subprocess.TimeoutExpired:
                        err = "timed out"
                    if not err:
                        break
                if err or pdf_pages(out) == 1:
                    break
            if err:
                if ci:
                    raise SystemExit(f"CV PDFs: Chrome failed on {lens}: {err}")
                print(f"CV PDFs: Chrome failed on {lens} ({err}), skipped")
                continue
            if pdf_pages(out) > 1:
                print(f"CV PDFs: the {label} CV runs to {pdf_pages(out)} pages even at {pt}")
            made.add(lens)
    return made


def ordinal(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def colophon_page(n_entries, n_public, n_vols, log, titles):
    """The footnote: when the site last changed, what changed in the projects lately, and how it's made."""
    count, short = git("rev-list", "--count", "HEAD") or "0", git("rev-parse", "--short", "HEAD") or "uncommitted"
    pages = "".join(f'<li><a href="{HOME if f == "index.html" else f}">{esc(k)} · {esc(e)}</a> <span class="muted mono" style="font-size:12px">p. {i + 1}</span></li>' for i, (f, e, k) in enumerate(PAGES))
    box = f'''<div class="okuzuke obj"><div class="seal-c" aria-hidden="true"><b>第{count}刷</b><small>printing</small></div>
<h2>奥付</h2><p class="sub">Colophon. Japanese books end with this page: who made the book, and when it was printed.</p>
<p class="upd-big"><span class="mono muted">{esc(cfg("colophon.updated"))}</span><b>{UPDATED[0]}</b></p>
<dl>
<dt>書名<small>title</small></dt><dd>{esc(cfg("colophon.title"))}</dd>
<dt>著者<small>author</small></dt><dd>Teoh Kai Shun</dd>
<dt>刷<small>printing</small></dt><dd>第{count}刷, the {ordinal(count)} commit to the repo (<code>{esc(short)}</code>)</dd>
<dt>製本<small>binding</small></dt><dd>Every page is built from one private folder of Markdown, {n_entries} entries, {n_public} of them public. A page can't say something the folder doesn't.
  <div class="pipe"><span>bank/*.md</span><i>→</i><span>check + export</span><i>→</i><span>build.py</span><i>→</i><span>{len(PAGES)} pages</span><i>→</i><span>GitHub Pages</span></div></dd>
<dt>収録<small>contents</small></dt><dd>{n_vols} volumes on the shelf, {len(PAGES)} pages in this printing.</dd>
<dt>書体<small>type</small></dt><dd>Dela Gothic One, Zen Kaku Gothic New, IBM Plex Mono</dd>
<dt>音<small>sound</small></dt><dd>{esc(cfg("colophon.sound"))}</dd>
<dt>状態<small>state</small></dt><dd>{esc(cfg("colophon.state"))}</dd>
</dl></div>'''
    recent = ""
    for d, i, msg in sorted(log, reverse=True)[:8]:
        title, vid = titles.get(i, (i, None))
        name = f'<a href="vol-{vid}.html">{esc(title)}</a>' if vid else esc(title)
        recent += f"<li><time>{d}</time>{name}: {esc(msg)}</li>"
    main = split(box, f'<div class="back">{f"<div><h3>更新履歴 · lately</h3><ol>{recent}</ol></div>" if recent else ""}'
                      f'<div><h3>収録 · in this printing</h3><ul class="pages">{pages}</ul></div></div>', rail_first=False)   # phones: the colophon itself first
    page("colophon.html", "奥付 · Teoh Kai Shun", f'奥付 {esc(cfg("nav.colophon"))}', main)


def barcode(text):
    """The back cover's barcode, drawn from the date the site last changed: a different printing, different bars."""
    import hashlib
    bits = "".join(f"{b:08b}" for b in hashlib.sha256(text.encode()).digest()[:12])
    x, bars = 6, []
    for i in range(0, len(bits), 3):
        w = 1 + int(bits[i:i + 2], 2) % 3
        if bits[i + 2:i + 3] == "1" or i % 9 == 0:
            bars.append(f'<rect x="{x}" y="0" width="{w}" height="{30 if i % 24 else 34}"/>')
        x += w + 1
    return f'<svg class="bars" viewBox="0 0 {x + 6} 34" aria-hidden="true"><g fill="currentColor">{"".join(bars)}</g></svg>'


def cover_page(data, vols, chapters, home):
    t = (SRC / "cover.html").read_text().replace("<!--TURN-->", turn_html())
    ep = lambda i, ch: next((e["n"] for e in ch["episodes"] if e.get("entry") == i), ch["episodes"][0]["n"])
    data = dict(data, chapters={i: {"href": f"vol-{v}.html", "vol": vols[v], "ep": ep(i, chapters[v])} for i, v in home.items()},
                vols={n["id"]: vols[home.get(n["id"], n["id"])] for n in data["nodes"]}, musicApi=MUSIC_API or None,
                profile=dict(data["profile"], oneliner=cfg("you.one_liner")), playlistIds=music_settings({n["id"] for n in data["nodes"]}),
                text={"intro": cfg("cover.intro"), "labelRim": cfg("cover.label_rim"), "blurbHead": cfg("cover.blurb_head"), "blurb": cfg("cover.blurb"),
                      "doorBrief": cfg("cover.door_brief"), "doorBriefNote": cfg("cover.door_brief_note"),
                      "doorProjects": cfg("cover.door_projects"), "doorProjectsNote": cfg("cover.door_projects_note").replace("{count}", str(len(vols))),
                      "directoryProjects": cfg("cover.directory.projects").replace("{count}", str(len(vols))),
                      "updated": cfg("cover.updated").replace("{date}", UPDATED[0]), "readMore": cfg("cover.read_more")},
                barcode=barcode(UPDATED[0]),
                music=SAMPLE_MUSIC if not MUSIC_API else {"is_playing": False, "title": None},
                playlists={})   # per-project playlists: not yet (see README)
    music_js = """<script>
/* the line under the record: what's playing, or what played last */
const npEl = document.getElementById("np");
const ago = ms => { const m = Math.round(ms / 60000); return m < 1 ? "just now" : m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`; };
function renderNp() {
  if (!music || !music.title) { npEl.hidden = true; return; }
  npEl.hidden = false;
  // one block: what this is, the title, who, and the tempo; laid out inline on phones, stacked in the rail
  const label = music.playlist ? `from the ${esc(music.playlist)} playlist`
    : music.is_playing ? `<span class="dot" aria-hidden="true"></span>now playing` : `last played ${ago(Date.now() - music.played_at)}`;
  const line = `<span class="lbl">${label}</span> <b>${esc(music.title)}</b> <span class="by">${esc(music.artist)}</span>`
    + (music.bpm ? ` <span class="bpm">${music.bpm} bpm${music.bpm_source ? ` · ${esc(music.bpm_source)}` : ""}</span>` : "");
  npEl.innerHTML = (music.url ? `<a href="${esc(music.url)}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none">${line}</a>` : line)
    + (music.sample ? `<br>sample data, not live${music === homeMusic ? `<button type="button" id="npdemo">${music.is_playing ? "stop the music" : "play it"}</button>` : ""}` : "");
  const b = document.getElementById("npdemo");
  if (b) b.onclick = () => {
    const now = performance.now();
    if (music.is_playing) Object.assign(music, { is_playing: false, progress_ms: songAt(now) * 1000, played_at: Date.now() - 2 * 3600e3 });
    else Object.assign(music, { is_playing: true, at: now });
    rec.art = artFor(music); renderNp();
  };
}
renderNp();
window.addEventListener("record", renderNp);

/* the real thing: ask the worker what's playing every 5 s while the page is visible, and again the moment the song
   should end, so a change shows within a few seconds */
let endTimer = 0;
async function poll() {
  if (!D.musicApi || document.hidden) return;
  try {
    const r = await fetch(D.musicApi + "/now", { cache: "no-store" });
    if (!r.ok) return;
    const j = await r.json();
    if (!j.title) return;
    const changed = j.title !== homeMusic.title || j.is_playing !== homeMusic.is_playing || j.art !== homeMusic.art;
    const late = j.is_playing ? Math.max(0, Date.now() - j.fetched_at) : 0;   // the worker's answer can be up to 15 s old
    Object.assign(homeMusic, j, { key: "me", progress_ms: (j.progress_ms || 0) + late, at: performance.now(), sample: false });
    if (music === homeMusic) {
      if (changed) { rec.art = artFor(homeMusic); rec.revealAt = performance.now(); }   // a new song: its cover spreads out again
      renderNp();
    }
    clearTimeout(endTimer);
    if (j.is_playing && j.duration_ms) endTimer = setTimeout(poll, Math.max(1000, j.duration_ms - homeMusic.progress_ms + 800));
  } catch {}
}
poll();
setInterval(poll, 5000);
/* each project's playlist (site.yaml music.playlists), fetched once; until one arrives, that project plays the current song */
for (const [pid, plid] of Object.entries(D.playlistIds || {})) {
  if (!D.musicApi) break;
  fetch(D.musicApi + "/playlist?id=" + plid).then(r => r.json()).then(j => { if (j.tracks && j.tracks.length) D.playlists[pid] = j; }).catch(() => {});
}
document.addEventListener("visibilitychange", poll);
</script>"""
    if t.count("/*__DATA__*/null") != 1:
        raise SystemExit("src/cover.html: the data placeholder is missing")
    t = fill(t.replace("/*__COLOURS__*/", colours_css())).replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (DIST / "index.html").write_text(t.replace("</body>", music_js + "\n</body>"))


FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=IBM+Plex+Mono:wght@400;500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">'


def subset_fonts():
    """Ask Google Fonts for only the characters the site uses. The Japanese families otherwise come with a 115 KB
    stylesheet of character ranges that blocks the first paint. Text that arrives later (a song title in Japanese,
    say) falls back to the system's Japanese font."""
    pages = sorted(DIST.glob("*.html"))
    chars = set(map(chr, range(32, 127))) | set("·–—…→←↑↓×’“”")
    for f in pages:
        chars |= {c for c in html.unescape(f.read_text()) if c.isprintable() and not c.isspace()}
    text = "".join(sorted(chars))
    from urllib.parse import quote
    link = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap">\n'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Zen+Kaku+Gothic+New:wght@400;500;700&text={quote(text)}&display=swap">')
    for f in pages:
        s = f.read_text()
        if FONTS not in s:
            raise SystemExit(f"{f.name}: the Google Fonts link has changed; update FONTS in build.py")
        f.write_text(s.replace(FONTS, link))


def main():
    CFG.clear(); CFG.update(load_config())
    data = json.loads((CONTENT / "site.json").read_text())
    nodes = data["nodes"]
    chapters = chapter_files()
    shelf, home = volumes(nodes, data["groups"], chapters)
    ordered = sorted(shelf, key=lambda n: (start(n["period"]), n["id"]))
    vols = {n["id"]: i + 1 for i, n in enumerate(ordered)}
    byid = {n["id"]: n for n in nodes}
    books = {n["id"]: n for n in shelf}
    PAGES.clear()
    PAGES.extend([("index.html", "表紙", "cover"), ("author.html", "作者紹介", cfg("nav.brief")), ("contents.html", "目次", cfg("nav.projects"))]
                 + [(f"vol-{i}.html", f"Vol. {vols[i]}", books[i]["title"]) for i in sorted(chapters, key=vols.get)]
                 + [("colophon.html", "奥付", cfg("nav.colophon"))])
    UPDATED[:] = [git("log", "-1", "--format=%cs") or date.today().isoformat()]
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    (DIST / ".nojekyll").write_text("")
    PDFS.clear(); PDFS.update(cv_pdfs())
    cover_page(data, vols, chapters, home)
    contents_page(shelf, vols, chapters)
    order = sorted(chapters, key=vols.get)
    for k, i in enumerate(order):
        prev = order[k - 1] if k > 0 else None
        nxt = order[k + 1] if k + 1 < len(order) else None
        volume_page(books[i], vols[i], chapters[i], data["log"], byid, prev and (books[prev], vols[prev]), nxt and (books[nxt], vols[nxt]))
    author_page(data, books, vols, PDFS)
    titles = {i: (byid[i]["title"], home.get(i) or (i if i in chapters else None)) for i in byid}   # entry -> its title and its volume
    colophon_page(data["counts"]["entries"], data["counts"]["public"], len(shelf), data["log"], titles)
    subset_fonts()
    print(f"{len(PAGES)} pages, {len(shelf)} volumes, {len(chapters)} written -> dist/")


def watch(port=8765):
    """Serve dist/ and rebuild whenever site.yaml, src/ or content/ changes. 127.0.0.1:8765 is a page the
    now-playing worker answers, so the record plays live locally too."""
    import functools, http.server, sys, threading, time
    watched = lambda: [HERE / "site.yaml", HERE / "build.py", HERE / "art.py"] + [p for d in (SRC, CONTENT) for p in d.rglob("*") if p.is_file()]
    stamp = lambda: max(p.stat().st_mtime for p in watched())
    def build():
        try:
            main()
        except SystemExit as e:        # a mistake in site.yaml: say so and keep serving the last good build
            print(f"not rebuilt: {e}", file=sys.stderr)
    sys.stdout.reconfigure(line_buffering=True)
    build()

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(DIST))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"serving http://127.0.0.1:{port}/  (rebuilds when you save; Ctrl+C stops)")
    last = stamp()
    try:
        while True:
            time.sleep(0.7)
            if stamp() != last:
                last = stamp()
                print(time.strftime("%H:%M:%S"), "rebuilding")
                build()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    import sys
    watch() if "--watch" in sys.argv else main()
