"""Build the website into dist/.

python3 build.py
Reads content/ (exported from the private bank by portfolio/tools/export_site.py; never edit it by hand) and src/.
Writes:
  index.html        the cover: the record (the projects' ball), the masthead and now playing
  contents.html     目次: every public project as a volume spine on a shelf
  vol-<id>.html     one per file in content/chapters/: that project's cover, spine and story
  author.html       作者紹介: about, the years, contact, the CV per lens
  colophon.html     奥付: how this printing was made
"""
import hashlib, html, json, math, re, shutil, subprocess
from datetime import date
from pathlib import Path

import yaml

HERE = Path(__file__).parent
CONTENT, SRC, DIST = HERE / "content", HERE / "src", HERE / "dist"
HOME = "./"

esc = lambda s: html.escape(str(s or ""), quote=True)
STATUS = {"active": "running", "paused": "paused", "shipped": "completed", "archived": "archived", "idea": "pending", "learning": "pending"}
SHELVES = [("work", "仕事", "Work"), ("academic", "研究", "Academic"), ("side", "個人", "Side projects")]


def seed(s, k=0):
    """A stable number in [0, 1) from an id, so each spine's art is the same on every build."""
    return int(hashlib.sha1(f"{s}:{k}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


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
    flush = lambda: (out.append(f"<p>{inline_md(' '.join(para))}</p>") if para else None, para.clear())
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


def spine_art(n):
    """The band of art on a spine. The pattern says what kind of project it is; the id sets its details.
    Placeholder art: each one gets designed by hand, volume by volume."""
    kind, sid, W, H = n.get("kind"), n["id"], 52, 54
    a, b = seed(sid, 1), seed(sid, 2)
    g = []
    if kind == "job":  # a lattice, like racks
        s = 7 + a * 4
        for i in range(-1, int(W / s) + 2):
            for j in range(-1, int(H / s) + 2):
                if seed(sid, i * 31 + j) > 0.35:
                    g.append(f'<rect x="{i*s + b*s:.1f}" y="{j*s:.1f}" width="{s*0.62:.1f}" height="{s*0.62:.1f}"/>')
        return "".join(g), "fill"
    if kind == "research":  # rings about a point
        cx, cy = W * (0.2 + 0.6 * a), H * (0.2 + 0.6 * b)
        g = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>' for r in range(3, 70, 5)]
        return "".join(g), "stroke"
    if kind == "product":  # halftone dots growing down the band
        s = 5 + a * 2
        for i in range(int(W / s) + 1):
            for j in range(int(H / s) + 1):
                r = s * 0.48 * min(1, max(0.08, (j * s) / H + (b - 0.5) * 0.6))
                g.append(f'<circle cx="{i*s + (j % 2) * s/2:.1f}" cy="{j*s:.1f}" r="{r:.2f}"/>')
        return "".join(g), "fill"
    if kind == "model-from-scratch":  # crosshatch
        s, t = 5 + a * 3, 20 + b * 50
        g = [f'<line x1="{x}" y1="-10" x2="{x + t}" y2="{H + 10}"/><line x1="{x + t}" y1="-10" x2="{x}" y2="{H + 10}"/>' for x in range(-60, 80, int(s))]
        return "".join(g), "stroke"
    if kind == "trading":  # a price line, zig-zagging
        for row in range(3):
            pts, y = [], 12 + row * 15
            for k in range(9):
                pts.append(f"{k * 6.5:.1f},{y + (seed(sid, row * 10 + k) - 0.5) * 12:.1f}")
            g.append(f'<polyline points="{" ".join(pts)}"/>')
        return "".join(g), "stroke"
    if kind == "venture":  # rays from a corner
        g = [f'<line x1="0" y1="{H}" x2="{80 * math.cos(t):.1f}" y2="{H - 80 * math.sin(t):.1f}"/>' for t in [i * math.pi / 2 / 12 + a * 0.1 for i in range(13)]]
        return "".join(g), "stroke"
    if kind == "study":
        g = [f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(4, H, 6)]
        return "".join(g), "stroke"
    # tool and anything else: diagonal rules
    s = 5 + a * 4
    g = [f'<line x1="{x}" y1="0" x2="{x + H}" y2="{H}"/>' for x in range(-60, 60, int(s))]
    return "".join(g), "stroke"


def spine(n, vol, href=None, extra=""):
    big = n.get("size") == "big"
    h = 262 + seed(n["id"], 9) * 18 if big else 222 + seed(n["id"], 9) * 40
    art, mode = spine_art(n)
    paint = 'fill="currentColor"' if mode == "fill" else 'fill="none" stroke="currentColor" stroke-width="1.4"'
    live = " live" if n.get("status") == "active" else ""
    inner = (f'<span class="ser">KS</span><span class="vol">{vol}</span><span class="ttl">{esc(n["title"])}</span>'
             f'<svg class="art" viewBox="0 0 52 54" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g {paint}>{art}</g></svg>'
             f'<span class="obi{live}">{status_glyph(n.get("status"))}</span>')
    label = f'Vol. {vol}: {n["title"]}, {STATUS.get(n.get("status"), "")}'
    cls = "spine big" if big else "spine"
    if href:
        return f'<a class="{cls}" href="{href}" style="--h:{h:.0f}px" aria-label="{esc(label)}, read it" title="{esc(n["title"])}" {extra}>{inner}</a>'
    return f'<button type="button" class="{cls}" style="--h:{h:.0f}px" aria-label="{esc(label)}" aria-expanded="false" title="{esc(n["title"])}" {extra}>{inner}</button>'


# ---------- Wallet's art (hand-drawn, one volume) ----------
INK, PAPER, SPOT, ONSPOT = "fill:var(--ink)", "fill:var(--paper)", "fill:var(--spot)", "fill:var(--on-spot)"


def tone(x0, y0, x1, y1, step, rmax, fade_from_top=True):
    """Screentone: a dot grid whose dots grow across the area."""
    out = []
    y, row = y0, 0
    while y <= y1:
        x = x0 + (row % 2) * step / 2
        f = (y - y0) / max(1, y1 - y0) if fade_from_top else 1 - (y - y0) / max(1, y1 - y0)
        r = rmax * max(0, min(1, f)) ** 1.2
        while x <= x1 and r > 0.25:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.2f}"/>')
            x += step
        y += step * 0.87
        row += 1
    return f'<g style="{INK}">{"".join(out)}</g>'


def sheet(x, y, w, h, rot, rows=7):
    lines = "".join(f'<rect x="{x + 14}" y="{y + 30 + i * (h - 44) / rows:.0f}" width="{(w - 28) * (0.45 + 0.5 * seed("sheet", i + int(x))):.0f}" height="4" style="{INK}"/>' for i in range(rows))
    return (f'<g transform="rotate({rot} {x + w/2} {y + h/2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" style="{PAPER};stroke:var(--ink);stroke-width:4"/>'
            f'<rect x="{x + 14}" y="{y + 12}" width="{w * 0.4:.0f}" height="8" style="{INK}"/>{lines}</g>')


def phone(x, y, w, h, rot=0, screen=""):
    return (f'<g transform="rotate({rot} {x + w/2} {y + h/2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w*0.16:.0f}" style="{PAPER};stroke:var(--ink);stroke-width:7"/>'
            f'<rect x="{x + w*0.08:.0f}" y="{y + h*0.08:.0f}" width="{w*0.84:.0f}" height="{h*0.84:.0f}" rx="8" style="fill:none;stroke:var(--ink);stroke-width:3"/>'
            f'<rect x="{x + w*0.38:.0f}" y="{y + h*0.035:.0f}" width="{w*0.24:.0f}" height="7" rx="3.5" style="{INK}"/>{screen}</g>')


def ledger_rows(x, y, w, n, gap):
    out = []
    for i in range(n):
        yy = y + i * gap
        out.append(f'<rect x="{x}" y="{yy}" width="{w*0.32:.0f}" height="5" style="{INK}"/>')
        out.append(f'<rect x="{x + w - w*(0.16 + 0.2*seed("led", i)):.0f}" y="{yy}" width="{w*(0.16 + 0.2*seed("led", i)):.0f}" height="5" style="{INK}"/>')
    out.append(f'<rect x="{x}" y="{y + n*gap - 4}" width="{w}" height="3" style="{INK}"/><rect x="{x}" y="{y + n*gap + 2}" width="{w}" height="3" style="{INK}"/>')
    return "".join(out)


def cover_wallet(n, vol, kana, obi):
    W, H = 512, 728
    live = n.get("status") == "active"
    obi_fill, obi_text = (SPOT, ONSPOT) if live else (INK, PAPER)
    tag = n["tagline"]
    cut = tag.rfind(" ", 0, 48)
    tag1, tag2 = (tag[:cut], tag[cut + 1:]) if len(tag) > 48 else (tag, "")
    screen = ledger_rows(196, 330, 128, 9, 24)
    return f'''<svg class="cover" viewBox="0 0 {W} {H}" role="img" aria-label="Cover of volume {vol}, {esc(n['title'])}: statements slide into a phone that keeps its ledger to itself.">
<rect width="{W}" height="{H}" style="{PAPER}"/>
{tone(0, 200, W, 590, 13, 4.6)}
<rect width="{W}" height="44" style="{INK}"/>
<text x="20" y="30" style="{PAPER};font:400 17px var(--font-display);letter-spacing:.04em">TEOH KAI SHUN</text>
<text x="{W - 20}" y="30" text-anchor="end" style="{PAPER};font:500 13px var(--font-mono);letter-spacing:.12em">VOL. {vol}</text>
<text x="22" y="150" textLength="{W - 96}" lengthAdjust="spacingAndGlyphs" style="{INK};font:400 100px var(--font-display)">{esc(n['title']).upper()}</text>
<text x="{W - 34}" y="196" style="{INK};font:700 30px var(--font-body);writing-mode:vertical-rl">{esc(kana)}</text>
{sheet(118, 178, 150, 196, -16)}{sheet(214, 162, 150, 196, 7)}{sheet(166, 196, 150, 196, -3)}
{phone(150, 262, 212, 400, -6, screen)}
<g transform="rotate(-6 256 462)"><path d="M372 420 h58 m-16 -16 l16 16 l-16 16" style="fill:none;stroke:var(--ink);stroke-width:7;stroke-linecap:square"/>
<path d="M388 398 l44 44 m0 -44 l-44 44" style="fill:none;stroke:var(--paper);stroke-width:13"/><path d="M388 398 l44 44 m0 -44 l-44 44" style="fill:none;stroke:var(--ink);stroke-width:6"/></g>
<rect y="{H - 150}" width="{W}" height="150" style="{obi_fill}"/>
<text x="24" y="{H - 98}" style="{obi_text};font:400 31px var(--font-display)">{esc(obi)}</text>
<text x="24" y="{H - 64}" style="{obi_text};font:400 14px var(--font-body)">{esc(tag1)}</text>
<text x="24" y="{H - 44}" style="{obi_text};font:400 14px var(--font-body)">{esc(tag2)}</text>
<text x="{W - 22}" y="{H - 18}" text-anchor="end" style="{obi_text};font:700 14px var(--font-body)">第1話 収録</text>
</svg>'''


def panel_art(kind):
    if kind == "phone":
        cloud = ('<g style="fill:var(--paper);stroke:var(--ink);stroke-width:5">'
                 '<path d="M430 150 a34 34 0 0 1 64 -14 a40 40 0 0 1 72 26 a28 28 0 0 1 -6 56 h-124 a34 34 0 0 1 -6 -68z"/></g>'
                 '<path d="M455 118 l100 112 m0 -112 l-100 112" style="fill:none;stroke:var(--paper);stroke-width:16"/>'
                 '<path d="M455 118 l100 112 m0 -112 l-100 112" style="fill:none;stroke:var(--ink);stroke-width:7"/>')
        return (f'<svg viewBox="0 0 600 340" aria-hidden="true"><rect width="600" height="340" style="{PAPER}"/>{tone(0, 0, 600, 340, 12, 3.2, False)}'
                f'{sheet(60, 40, 120, 150, -12, 5)}{sheet(110, 30, 120, 150, 9, 5)}'
                f'{phone(150, 90, 150, 260, 0, ledger_rows(178, 150, 94, 6, 22))}'
                f'<path d="M318 190 q50 -10 96 -24" style="fill:none;stroke:var(--ink);stroke-width:4;stroke-dasharray:9 7"/>{cloud}</svg>')
    if kind == "sen":
        return (f'<svg viewBox="0 0 300 340" aria-hidden="true"><rect width="300" height="340" style="{PAPER}"/>'
                f'<text x="150" y="122" text-anchor="middle" style="{INK};font:400 52px var(--font-display)">RM 1.00</text>'
                f'<text x="150" y="182" text-anchor="middle" style="{INK};font:400 40px var(--font-display)">=</text>'
                f'<text x="150" y="250" text-anchor="middle" style="{INK};font:400 52px var(--font-display)">100 sen</text>'
                f'<text x="150" y="296" text-anchor="middle" style="fill:var(--muted);font:500 13px var(--font-mono)">Long, never Double</text></svg>')
    if kind == "ledger":
        rows = "".join(
            f'<g><rect x="{60 + i*86}" y="{150 - 50*seed("mv", i)}" width="54" height="{40 + 50*seed("mv", i):.0f}" style="{INK if i % 3 else PAPER};stroke:var(--ink);stroke-width:4"/>'
            f'<path d="M{87 + i*86} 214 v18" style="stroke:var(--ink);stroke-width:3"/></g>' for i in range(7))
        return (f'<svg viewBox="0 0 900 300" aria-hidden="true"><rect width="900" height="300" style="{PAPER}"/>'
                f'<text x="60" y="44" style="fill:var(--muted);font:500 14px var(--font-mono)">every movement, replayed</text>{rows}'
                f'<path d="M50 236 H660" style="stroke:var(--ink);stroke-width:5"/><path d="M640 220 l24 16 l-24 16" style="fill:none;stroke:var(--ink);stroke-width:5"/>'
                f'<rect x="690" y="186" width="160" height="96" style="{PAPER};stroke:var(--ink);stroke-width:5"/>'
                f'<text x="770" y="214" text-anchor="middle" style="fill:var(--muted);font:500 12px var(--font-mono)">statement says</text>'
                f'<rect x="716" y="236" width="108" height="8" style="{INK}"/><rect x="716" y="252" width="108" height="8" style="{INK}"/>'
                f'<g transform="rotate(-8 760 110)"><rect x="672" y="78" width="196" height="62" style="{PAPER};stroke:var(--ink);stroke-width:5"/>'
                f'<text x="770" y="118" text-anchor="middle" style="{INK};font:700 24px var(--font-body)">合わない</text></g>'
                f'<text x="770" y="166" text-anchor="middle" style="{INK};font:500 13px var(--font-mono)">doesn\'t reconcile</text></svg>')
    if kind == "wall":
        bricks = "".join(f'<rect x="{214 + (r % 2) * 11 - 11}" y="{40 + r*22}" width="22" height="20" style="{PAPER};stroke:var(--ink);stroke-width:3"/>'
                         f'<rect x="{214 + (r % 2) * 11 + 11}" y="{40 + r*22}" width="22" height="20" style="{PAPER};stroke:var(--ink);stroke-width:3"/>' for r in range(11))
        return (f'<svg viewBox="0 0 450 300" aria-hidden="true"><rect width="450" height="300" style="{PAPER}"/>'
                f'<rect x="40" y="110" width="130" height="80" style="{PAPER};stroke:var(--ink);stroke-width:5"/><text x="105" y="157" text-anchor="middle" style="{INK};font:400 18px var(--font-display)">phone</text>'
                f'<rect x="300" y="110" width="120" height="80" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-dasharray:10 6"/><text x="360" y="148" text-anchor="middle" style="{INK};font:500 13px var(--font-mono)">forbidden</text><text x="360" y="166" text-anchor="middle" style="{INK};font:500 13px var(--font-mono)">module</text>'
                f'<path d="M170 150 H206" style="stroke:var(--ink);stroke-width:5"/><path d="M262 150 H300" style="stroke:var(--ink);stroke-width:5;stroke-dasharray:6 6"/>{bricks}'
                f'<g transform="rotate(-6 225 268)"><rect x="128" y="246" width="194" height="40" style="{PAPER};stroke:var(--ink);stroke-width:4"/><text x="225" y="273" text-anchor="middle" style="{INK};font:400 17px var(--font-display)">BUILD FAILED</text></g></svg>')
    if kind == "month":
        cells = "".join(f'<rect x="{60 + (i % 7) * 46}" y="{70 + (i // 7) * 36}" width="40" height="30" style="{INK if i == 30 else PAPER};stroke:var(--ink);stroke-width:3"/>' for i in range(31))
        return (f'<svg viewBox="0 0 450 300" aria-hidden="true"><rect width="450" height="300" style="{PAPER}"/>{cells}'
                f'<path d="M318 64 C 300 38, 110 38, 76 58" style="fill:none;stroke:var(--ink);stroke-width:4;stroke-dasharray:9 7"/><path d="M68 44 l8 16 l16 -6" style="fill:none;stroke:var(--ink);stroke-width:4"/>'
                f'<text x="200" y="22" text-anchor="middle" style="fill:var(--muted);font:500 13px var(--font-mono)">one statement, looking back</text>'
                f'<text x="60" y="280" style="{INK};font:500 13px var(--font-mono)">statement day</text><path d="M170 276 H 330 V 262" style="fill:none;stroke:var(--ink);stroke-width:2.5"/></svg>')
    if kind == "live":
        banner = (f'<rect x="368" y="98" width="230" height="64" rx="14" style="{PAPER};stroke:var(--ink);stroke-width:5"/>'
                  f'<circle cx="398" cy="130" r="11" style="{SPOT}"/><rect x="420" y="116" width="120" height="7" style="{INK}"/><rect x="420" y="134" width="150" height="6" style="fill:var(--tone)"/>')
        lines = "".join(f'<path d="M{600 + i*14} {108 + i*12} h{60 - i*8}" style="stroke:var(--ink);stroke-width:2.5;opacity:{0.5 - i*0.08:.2f}"/>' for i in range(4))
        return (f'<svg viewBox="0 0 900 300" aria-hidden="true"><rect width="900" height="300" style="{PAPER}"/>{tone(0, 0, 900, 300, 12, 2.6)}'
                f'{phone(340, 40, 160, 300, 0)}{banner}{lines}'
                f'<text x="60" y="80" style="{INK};font:400 26px var(--font-display)">live</text><text x="60" y="104" style="fill:var(--muted);font:500 13px var(--font-mono)">bank notification → ledger</text></svg>')
    return ""


# What the music proxy will return (stage 3: a small worker holding Kai Shun's Spotify token). Until then the
# cover plays this sample, and a prototype-only switch shows the offline state.
MUSIC_API = ""   # the now-playing worker (worker/); empty: the cover plays SAMPLE_MUSIC
SAMPLE_MUSIC = {"sample": True, "is_playing": True, "title": "Sample track", "artist": "Sample artist", "url": None,
                "duration_ms": 214000, "progress_ms": 61000, "bpm": 96, "played_at": None}


def sample_playlists(nodes):
    """A stand-in playlist per project until Kai Shun names real ones (a `playlist:` link in the entry). Stage 3 reads
    each real playlist's name, cover and tracks (with a BPM per track) at build time and inlines the cover."""
    out = {}
    for n in nodes:
        tracks = [{"title": f"Sample track {k + 1}", "artist": "Sample artist", "bpm": int(78 + 54 * seed(n["id"], 20 + k)),
                   "duration_ms": int(180000 + 80000 * seed(n["id"], 30 + k))} for k in range(3)]
        out[n["id"]] = {"name": f"{n['title']}", "url": n.get("playlist"), "art": None, "sample": True, "tracks": tracks}
    return out


# ---------- pages ----------
TEMPLATE = (SRC / "page.html").read_text()
PAGES = []  # (file, short name, kana), in reading order; filled in main


def nav(current):
    items = [("index.html", "表紙", "cover"), ("contents.html", "目次", "contents"), ("author.html", "作者", "author & CV"), ("colophon.html", "奥付", "colophon")]
    return "".join(f'<a href="{HOME if f == "index.html" else f}"{" aria-current=page" if f == current else ""}><b>{k}</b>{e}</a>' for f, k, e in items)


def page(file, title, part, main, script=""):
    order = [p[0] for p in PAGES]
    i = order.index(file)
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    nxt_html = f'<a href="{nxt[0]}">next: {esc(nxt[2])} {esc(nxt[1])} →</a>' if nxt else f'<a href="{HOME}">back to the cover →</a>'
    out = TEMPLATE
    for k, v in {"title": title, "part": part, "nav": nav(file), "main": main, "folio": str(i + 1), "next": nxt_html, "script": script, "home": HOME}.items():
        out = out.replace("{{" + k + "}}", v)
    (DIST / file).write_text(out)


def chapter_files():
    return {yaml.safe_load(p.read_text())["entry"]: yaml.safe_load(p.read_text()) for p in sorted((CONTENT / "chapters").glob("*.yaml"))}


def contents_page(nodes, vols, chapters):
    shelves, pulls = [], {}
    for track, kana, name in SHELVES:
        items = sorted([n for n in nodes if n.get("track", "side") == track], key=lambda n: vols[n["id"]])
        if not items:
            continue
        books = []
        for n in items:
            mix = " ".join(k for k, w in n["mix"].items() if w >= 0.3)
            extra = f'data-id="{n["id"]}" data-status="{n.get("status")}" data-mix="{mix}"'
            href = f'vol-{n["id"]}.html' if n["id"] in chapters else None
            books.append(f'<div class="slot">{spine(n, vols[n["id"]], href, extra)}</div>')
            pulls[n["id"]] = {"title": n["title"], "vol": vols[n["id"]], "tagline": n["tagline"], "role": n.get("role"), "period": n["period"],
                              "status": STATUS.get(n.get("status"), ""), "live": n.get("status") == "active", "big": n.get("size") == "big",
                              "what": n["what"], "bullets": [inline_md(b) for b in n["bullets"]], "stack": n["stack"], "repo": n.get("repo")}
        shelves.append(f'<section aria-labelledby="sh-{track}"><div class="shelfname"><h2 id="sh-{track}"><span class="jp">{kana}</span> {name}</h2><span>{len(items)} volumes</span></div>'
                       f'<div class="shelf">{"".join(books)}</div><div class="pull" id="pull-{track}" hidden aria-live="polite"></div></section>')
    statuses = [("all", "all")] + [(k, v) for k, v in [("active", "running"), ("shipped", "completed"), ("paused", "paused"), ("archived", "archived"), ("idea", "pending")]]
    skills = [("all", "all"), ("ml", "ML"), ("backend", "Backend"), ("infra", "Infra"), ("product", "Product")]
    filt = (f'<div class="filters" role="group" aria-label="Filter the shelf"><div class="grp"><span class="lbl">status</span>'
            + "".join(f'<button type="button" class="chip" data-f="status" data-v="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in statuses)
            + '</div><div class="grp"><span class="lbl">skill</span>'
            + "".join(f'<button type="button" class="chip" data-f="mix" data-v="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in skills)
            + "</div></div>")
    main = (f'<div class="pt"><h1>目次</h1><p>Contents. Every project I\'ve built is a volume, numbered in the order I started it. '
            f'Thick spines are the big ones. A red band means it\'s still running. Pull one out.</p></div>{filt}{"".join(shelves)}')
    script = "<script>\nconst P = " + json.dumps(pulls, ensure_ascii=False) + r""";
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let open = null;
function show(btn) {
  const id = btn.dataset.id, n = P[id], pull = btn.closest("section").querySelector(".pull");
  document.querySelectorAll('.spine[aria-expanded="true"]').forEach(b => b.setAttribute("aria-expanded", "false"));
  document.querySelectorAll(".pull").forEach(p => { if (p !== pull) p.hidden = true; });
  if (open === id) { pull.hidden = true; open = null; return; }
  open = id; btn.setAttribute("aria-expanded", "true");
  pull.innerHTML = `<div><div class="meta">Vol. ${n.vol} · ${esc(n.period)}</div>
    <h3>${esc(n.title)}</h3><p class="tag">${esc(n.role ? n.role + " · " + n.tagline : n.tagline)}</p>
    ${n.what ? `<p>${esc(n.what)}</p>` : ""}
    ${n.bullets.length ? `<ul>${n.bullets.map(b => `<li>${b}</li>`).join("")}</ul>` : ""}
    ${n.stack.length ? `<div class="chips" style="margin-top:12px">${n.stack.map(s => `<span>${esc(s)}</span>`).join("")}</div>` : ""}
    ${n.big ? `<p class="meta" style="margin-top:12px">This is a big one; its chapter isn't written yet.</p>` : ""}</div>
    <div class="side"><button type="button" class="x" aria-label="Put it back">×</button>
      <span class="stamp${n.live ? " live" : ""}">${esc(n.status)}</span><span class="stamp draft">draft</span>
      <a href="./#${id}">find it on the ball →</a>${n.repo ? `<a href="${esc(n.repo)}" target="_blank" rel="noopener">repo →</a>` : ""}</div>`;
  pull.hidden = false;
  pull.querySelector(".x").onclick = () => show(btn);
}
document.querySelectorAll("button.spine").forEach(b => b.addEventListener("click", () => show(b)));
const want = { status: "all", mix: "all" };
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  want[c.dataset.f] = c.dataset.v;
  document.querySelectorAll(`.chip[data-f="${c.dataset.f}"]`).forEach(o => o.setAttribute("aria-pressed", String(o === c)));
  document.querySelectorAll(".spine").forEach(s => {
    const st = s.dataset.status === "learning" ? "idea" : s.dataset.status;
    const ok = (want.status === "all" || st === want.status) && (want.mix === "all" || s.dataset.mix.split(" ").includes(want.mix));
    s.classList.toggle("dim", !ok);
  });
}));
</script>"""
    page("contents.html", "目次 · Teoh Kai Shun", "目次 contents", main, script)


def volume_page(n, vol, ch, log):
    eps = []
    for ep in ch["episodes"]:
        panels = "".join(f'<figure class="panel s{p["span"]}" style="margin:0">{panel_art(p["art"])}<figcaption class="txt"><span class="cap">{esc(p["caption"])}</span><p>{esc(p["text"])}</p></figcaption></figure>' for p in ep["panels"])
        live = n.get("status") == "active"
        eps.append(f'''<section class="tobira" aria-labelledby="ep{ep["n"]}"><div class="ep jp">第{ep["n"]}話</div><h2 id="ep{ep["n"]}">{esc(ep["title"])}</h2>
<div class="stamps"><span class="stamp{" live" if live else ""}">{STATUS.get(n.get("status"))}</span><span class="stamp draft">draft</span></div></section>
<div class="page">{panels}</div>
<div class="tsuzuku"><span class="muted mono" style="font-size:12px">{"still being written" if live else "the end"}</span><span class="big">{"つづく" if live else "完"}</span></div>
{f'<div class="next"><span class="lbl jp">次回予告</span><span>Next time: {esc(ep["next"])}</span></div>' if ep.get("next") else ""}''')
    events = "".join(f"<li><time>{d}</time>{esc(msg)}</li>" for d, i, msg in sorted(log, reverse=True) if i == n["id"])
    blurb = (f'<div class="blurb"><h2>あらすじ · the story so far</h2><p>{inline_md(n["what"])}</p>'
             f'<dl><dt>period</dt><dd>{esc(n["period"])}</dd><dt>status</dt><dd>{STATUS.get(n.get("status"))}</dd><dt>repo</dt><dd>{"private" if not n.get("repo") else esc(n["repo"])}</dd></dl></div>')
    main = (f'<div class="book">{spine(n, vol)}{cover_wallet(n, vol, ch["kana"], ch["obi"])}{blurb}</div>'
            + "".join(eps)
            + f'<div class="back"><div><h3>stack</h3><div class="chips">{"".join(f"<span>{esc(s)}</span>" for s in n["stack"])}</div></div>'
            + (f'<div><h3>log</h3><ol>{events}</ol></div>' if events else "")
            + f'<div><h3>elsewhere</h3><ul><li><a href="./#{n["id"]}">find it on the ball →</a></li><li><a href="contents.html">back to the shelf →</a></li></ul>'
            + '<p class="muted" style="font-size:13px;margin-top:10px">Details are drafts until Kai Shun reviews this entry.</p></div></div>')
    page(f'vol-{n["id"]}.html', f'{n["title"]} · Vol. {vol}', f'Vol. {vol} · {esc(n["title"])}', main)


def author_page(data, groups):
    p = data["profile"]
    yrs = "".join(f"<li><time>{esc(re.sub(r' – present', '–', y['period']))}</time><span>{esc(y['what'])}</span></li>" for y in data["years"])
    tabs, sheets = [], []
    for i, (lens, label) in enumerate([("ml", "ML"), ("cloud", "Cloud"), ("backend", "Backend")]):
        f = CONTENT / "cv" / f"{lens}.md"
        if not f.exists():
            continue
        body = md_to_html(f.read_text())
        body = re.sub(r"(</h1>\n)<p>", r'\1<p class="head">', body, count=1)
        tabs.append(f'<button type="button" role="tab" id="tab-{lens}" aria-controls="cv-{lens}" aria-selected="{str(i == 0).lower()}">{label}</button>')
        sheets.append(f'<article class="cv" role="tabpanel" id="cv-{lens}" aria-labelledby="tab-{lens}"{"" if i == 0 else " hidden"}>{body}</article>')
    main = f'''<div class="pt"><h1>作者紹介</h1><p>About the author, and the CV. Pick the lens that fits the role.</p></div>
<div class="flap"><aside>
  <div class="seal" aria-hidden="true">KS</div>
  <div><h2 style="margin:0 0 4px;font-size:28px">{esc(p["name"])}</h2><p class="mono muted" style="margin:0;font-size:12px">ML Engineer · Tencent · Malaysia</p></div>
  <div class="comment"><span class="mono muted" style="font-size:11px">作者コメント · a word from the author</span><br>{esc(p["oneliner"])}</div>
  <div><h3>年譜 · the years</h3><ol class="years">{yrs}</ol></div>
  <div><h3>contact</h3><div class="contact">
    <div class="row"><span class="select" id="email">{esc(p["email"])}</span><button type="button" class="btn" id="copy">copy</button></div>
    <a href="{esc(p["github"])}" target="_blank" rel="noopener">github.com/BeanBois</a>
    <a href="{esc(p["linkedin"])}" target="_blank" rel="noopener">linkedin.com/in/kai-shun-teoh</a></div></div>
</aside>
<section aria-label="CV"><div class="tabs" role="tablist" aria-label="CV lens">{"".join(tabs)}<span class="note">PDFs come at deploy</span></div>{"".join(sheets)}</section></div>'''
    script = """<script>
const tabs = [...document.querySelectorAll('[role="tab"]')];
function pick(id) {
  tabs.forEach(t => { const on = t.id === "tab-" + id; t.setAttribute("aria-selected", String(on)); document.getElementById(t.getAttribute("aria-controls")).hidden = !on; });
}
tabs.forEach(t => t.addEventListener("click", () => pick(t.id.slice(4))));
const h = location.hash.replace("#cv-", "");
if (tabs.some(t => t.id === "tab-" + h)) pick(h);
const copy = document.getElementById("copy"), email = document.getElementById("email");
copy.onclick = () => {
  const fallback = () => { const r = document.createRange(); r.selectNodeContents(email); getSelection().removeAllRanges(); getSelection().addRange(r); };
  try { navigator.clipboard.writeText(email.textContent).then(() => { copy.textContent = "copied"; }, fallback); } catch { fallback(); }
};
</script>"""
    page("author.html", "作者紹介 · Teoh Kai Shun", "作者紹介 about the author", main, script)


def colophon_page(n_entries, n_public, n_vols):
    git = lambda *a: subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout.strip()
    count, short = git("rev-list", "--count", "HEAD") or "0", git("rev-parse", "--short", "HEAD") or "uncommitted"
    pages = "".join(f'<li><a href="{HOME if f == "index.html" else f}">{esc(k)} · {esc(e)}</a> <span class="muted mono" style="font-size:12px">p. {i + 1}</span></li>' for i, (f, e, k) in enumerate(PAGES))
    main = f'''<div class="okuzuke">
<h2>奥付</h2><p class="sub">Colophon. Japanese books end with this page: who made the book, and when it was printed.</p>
<dl>
<dt>書名<small>title</small></dt><dd>Teoh Kai Shun: every project, big or small</dd>
<dt>著者<small>author</small></dt><dd>Teoh Kai Shun</dd>
<dt>発行<small>printed</small></dt><dd>{date.today().isoformat()}</dd>
<dt>刷<small>printing</small></dt><dd>第{count}刷, the {count}th commit to the repo (<code>{esc(short)}</code>)</dd>
<dt>製本<small>binding</small></dt><dd>Every page is built from one private folder of Markdown, {n_entries} entries, {n_public} of them public. A page can't say something the folder doesn't.
  <div class="pipe"><span>bank/*.md</span><i>→</i><span>check + export</span><i>→</i><span>build.py</span><i>→</i><span>{len(PAGES)} pages</span><i>→</i><span>GitHub Pages</span></div></dd>
<dt>収録<small>contents</small></dt><dd>{n_vols} volumes on the shelf. <ul class="pages" style="margin-top:6px">{pages}</ul></dd>
<dt>書体<small>type</small></dt><dd>Dela Gothic One, Zen Kaku Gothic New, IBM Plex Mono</dd>
<dt>音<small>sound</small></dt><dd>The cover is a record: whatever Kai Shun is listening to on Spotify, or the playlist of the project you open. Here it plays sample data.</dd>
<dt>状態<small>state</small></dt><dd>A prototype. Details on most volumes are drafts until reviewed.</dd>
</dl></div>'''
    page("colophon.html", "奥付 · Teoh Kai Shun", "奥付 colophon", main)


def cover_page(data, vols, chapters):
    t = (SRC / "cover.html").read_text()
    data = dict(data, chapters={i: {"href": f"vol-{i}.html", "vol": vols[i]} for i in chapters}, vols=vols, musicApi=MUSIC_API or None,
                music=SAMPLE_MUSIC if not MUSIC_API else {"is_playing": False, "title": None},
                playlists=sample_playlists(data["nodes"]), topInset=110)
    music_js = """<script>
/* the line under the record: what's playing, or what played last */
const npEl = document.getElementById("np");
const ago = ms => { const m = Math.round(ms / 60000); return m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`; };
function renderNp() {
  if (!music || !music.title) { npEl.hidden = true; return; }
  npEl.hidden = false;
  const what = `<b>${esc(music.title)}</b> · ${esc(music.artist)}`;
  const line = music.playlist ? `from the ${esc(music.playlist)} playlist: ${what}${music.bpm ? ` · ${music.bpm} bpm` : ""}`
    : music.is_playing ? `<span class="dot" aria-hidden="true"></span>now playing ${what}${music.bpm ? ` · ${music.bpm} bpm` : ""}`
    : `last played ${ago(Date.now() - music.played_at)} ${what}`;
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

/* the real thing: ask the worker what's playing, every 20 s while the page is open and visible */
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
    if (rec.on === ME) { if (changed) rec.art = artFor(homeMusic); renderNp(); }
  } catch {}
}
poll();
setInterval(poll, 20000);
document.addEventListener("visibilitychange", poll);
</script>"""
    if t.count("/*__DATA__*/null") != 1:
        raise SystemExit("src/cover.html: the data placeholder is missing")
    t = t.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (DIST / "index.html").write_text(t.replace("</body>", music_js + "\n</body>"))


def main():
    data = json.loads((CONTENT / "site.json").read_text())
    nodes = data["nodes"]
    ordered = sorted(nodes, key=lambda n: (start(n["period"]), n["id"]))
    vols = {n["id"]: i + 1 for i, n in enumerate(ordered)}
    chapters = chapter_files()
    byid = {n["id"]: n for n in nodes}
    for i in chapters:
        if i not in byid:
            raise SystemExit(f"content/chapters/{i}.yaml: no public entry with that id")
    PAGES.clear()
    PAGES.extend([("index.html", "表紙", "cover"), ("contents.html", "目次", "contents")]
                 + [(f"vol-{i}.html", f"Vol. {vols[i]}", byid[i]["title"]) for i in chapters]
                 + [("author.html", "作者紹介", "about the author"), ("colophon.html", "奥付", "colophon")])
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    (DIST / ".nojekyll").write_text("")
    cover_page(data, vols, chapters)
    contents_page(nodes, vols, chapters)
    for i, ch in chapters.items():
        volume_page(byid[i], vols[i], ch, data["log"])
    groups = {k: dict(v, id=k) for k, v in data["groups"].items()}
    author_page(data, groups)
    colophon_page(data["counts"]["entries"], data["counts"]["public"], len(nodes))
    print(f"{len(PAGES)} pages, {len(nodes)} volumes, {len(chapters)} written -> dist/")


if __name__ == "__main__":
    main()
