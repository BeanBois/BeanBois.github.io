"""The volumes' art: covers and panel pictures, drawn as SVG in the site's colour tokens. build.py calls cover(),
cover_wallet() and panel(); a chapter script names its pictures by their keys in ART (or Wallet's own)."""
import hashlib, html, math

esc = lambda s: html.escape(str(s or ""), quote=True)


def seed(s, k=0):
    """A stable number in [0, 1) from an id, so each picture is the same on every build."""
    return int(hashlib.sha1(f"{s}:{k}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


# ---------- Wallet's art (hand-drawn, one volume) ----------
INK, PAPER, SPOT, ONSPOT = "fill:var(--ink)", "fill:var(--paper)", "fill:var(--live-red)", "fill:var(--live-on-red)"


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


def cover_wallet(n, vol, kana, obi, name):
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
<text x="20" y="30" style="{PAPER};font:400 17px var(--font-display);letter-spacing:.04em">{esc(name)}</text>
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


def wallet_panel(kind):
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


WALLET_PANELS = ("phone", "sen", "ledger", "wall", "month", "live")


# ---------- every other volume's art ----------
# Each picture is drawn on a 450 x 300 stage; panel() fits the stage to the panel's width and fills the rest with
# screentone, and cover() puts the volume's chosen picture on its cover. Ink and paper only, one red accent at most.
MUTED = "fill:var(--muted)"


def r(x, y, w, h, fill=PAPER, sw=5, dash=None, rx=0):
    d = f";stroke-dasharray:{dash}" if dash else ""
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" style="{fill};stroke:var(--ink);stroke-width:{sw}{d}"/>'


def ln(d, sw=5, dash=None, colour="var(--ink)"):
    da = f";stroke-dasharray:{dash}" if dash else ""
    return f'<path d="{d}" style="fill:none;stroke:{colour};stroke-width:{sw};stroke-linecap:square;stroke-linejoin:round{da}"/>'


def t(x, y, s, size=13, kind="mono", anchor="start", fill=INK):
    font = {"mono": f"500 {size}px var(--font-mono)", "display": f"400 {size}px var(--font-display)", "body": f"700 {size}px var(--font-body)"}[kind]
    return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" style="{fill};font:{font}">{esc(s)}</text>'


def note(x, y, s, anchor="start"):
    return t(x, y, s, 13, "mono", anchor, MUTED)


def dot(x, y, rad, fill=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" style="{fill}"/>'


def ring(x, y, rad, sw=5, fill=PAPER, dash=None):
    d = f";stroke-dasharray:{dash}" if dash else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" style="{fill};stroke:var(--ink);stroke-width:{sw}{d}"/>'


def arrow(x1, y1, x2, y2, sw=5, dash=None):
    a = math.atan2(y2 - y1, x2 - x1)
    h = lambda s: (x2 - 14 * math.cos(a + s), y2 - 14 * math.sin(a + s))
    (ax, ay), (bx, by) = h(0.5), h(-0.5)
    return ln(f"M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}", sw, dash) + ln(f"M{ax:.0f} {ay:.0f} L{x2:.0f} {y2:.0f} L{bx:.0f} {by:.0f}", sw)


def stamp(cx, cy, s, rot=-8, size=22, spot=False, kind="body"):
    w = max(80, len(s) * size * (0.95 if kind == "body" and not s.isascii() else 0.86 if kind == "display" else 0.66) + 36)
    fill, txt = (SPOT, ONSPOT) if spot else (PAPER, INK)
    return (f'<g transform="rotate({rot} {cx} {cy})">{r(cx - w/2, cy - size - 6, w, size * 2 + 12, fill, 5)}'
            f'{t(cx, cy + size * 0.36, s, size, kind, "middle", txt)}</g>')


def cross(x, y, s=22, sw=7):
    """A big X, drawn over whatever is under it, with a paper halo."""
    d = f"M{x - s} {y - s} L{x + s} {y + s} M{x + s} {y - s} L{x - s} {y + s}"
    return ln(d, sw + 8, colour="var(--paper)") + ln(d, sw)


def doc(x, y, w, h, rows=5, rot=0, title=True):
    lines = "".join(f'<rect x="{x + 12}" y="{y + (30 if title else 16) + i * (h - (42 if title else 28)) / rows:.0f}" width="{(w - 24) * (0.45 + 0.5 * seed("doc", i + int(x))):.0f}" height="4" style="{INK}"/>' for i in range(rows))
    head = f'<rect x="{x + 12}" y="{y + 12}" width="{w * 0.45:.0f}" height="7" style="{INK}"/>' if title else ""
    return f'<g transform="rotate({rot} {x + w/2} {y + h/2})">{r(x, y, w, h, PAPER, 4)}{head}{lines}</g>'


def server(x, y, w, h, slots=5, lit=()):
    out = [r(x, y, w, h, PAPER, 5)]
    for i in range(slots):
        yy = y + 10 + i * (h - 16) / slots
        out.append(r(x + 8, yy, w - 16, (h - 16) / slots - 6, PAPER, 3))
        out.append(dot(x + w - 18, yy + ((h - 16) / slots - 6) / 2, 3.5, SPOT if i in lit else INK))
    return "".join(out)


def laptop(x, y, w):
    h = w * 0.62
    return r(x, y, w, h, PAPER, 4, rx=4) + r(x + 6, y + 6, w - 12, h - 12, "fill:var(--tone)", 0) + ln(f"M{x - 10} {y + h + 6} H{x + w + 10}", 6)


def clockface(cx, cy, rad, hh=10, mm=0, ticks=12):
    out = [ring(cx, cy, rad, 5)]
    for i in range(ticks):
        a = i / ticks * 2 * math.pi
        out.append(ln(f"M{cx + (rad - 10) * math.sin(a):.0f} {cy - (rad - 10) * math.cos(a):.0f} L{cx + (rad - 3) * math.sin(a):.0f} {cy - (rad - 3) * math.cos(a):.0f}", 3))
    ha, ma = (hh % 12 + mm / 60) / 12 * 2 * math.pi, mm / 60 * 2 * math.pi
    out.append(ln(f"M{cx} {cy} L{cx + rad * 0.5 * math.sin(ha):.0f} {cy - rad * 0.5 * math.cos(ha):.0f}", 6))
    out.append(ln(f"M{cx} {cy} L{cx + rad * 0.78 * math.sin(ma):.0f} {cy - rad * 0.78 * math.cos(ma):.0f}", 4))
    return "".join(out) + dot(cx, cy, 5)


def bars(x, y, w, h, vals, gap=4, fill=INK, hi=None):
    bw = (w - gap * (len(vals) - 1)) / len(vals)
    return "".join(r(x + i * (bw + gap), y + h - h * v, bw, h * v, SPOT if i == hi else fill, 2) for i, v in enumerate(vals))


def curve(x, y, w, h, fn, n=40, sw=4, dash=None):
    pts = " L".join(f"{x + w * i / n:.1f} {y + h - h * fn(i / n):.1f}" for i in range(n + 1))
    return ln("M" + pts, sw, dash)


def person(x, y, s=1.0, fill=PAPER):
    return ring(x, y, 13 * s, 4, fill) + ln(f"M{x - 22 * s:.0f} {y + 48 * s:.0f} Q{x} {y + 6 * s:.0f} {x + 22 * s:.0f} {y + 48 * s:.0f}", 4)


def chip(x, y, w, h, label=""):
    pins = "".join(ln(f"M{x + w * (i + 1) / 7:.0f} {y - 12} V{y} M{x + w * (i + 1) / 7:.0f} {y + h} V{y + h + 12}", 4) for i in range(6))
    pins += "".join(ln(f"M{x - 12} {y + h * (i + 1) / 5:.0f} H{x} M{x + w} {y + h * (i + 1) / 5:.0f} H{x + w + 12}", 4) for i in range(4))
    return pins + r(x, y, w, h, INK, 0) + r(x + 10, y + 10, w - 20, h - 20, PAPER, 3) + t(x + w / 2, y + h / 2 + 8, label, 20, "display", "middle")


def car(x, y, w, fill=PAPER):
    k = w / 300
    body = (f"M{x} {y + 70*k} L{x + 20*k} {y + 40*k} L{x + 85*k} {y + 34*k} L{x + 125*k} {y} L{x + 215*k} {y} L{x + 255*k} {y + 34*k} "
            f"L{x + 292*k} {y + 44*k} L{x + 300*k} {y + 70*k} Z")
    return (f'<path d="{body}" style="{fill};stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>'
            + ln(f"M{x + 132*k} {y + 8*k} L{x + 100*k} {y + 34*k} H{x + 165*k} V{y + 8*k} Z M{x + 175*k} {y + 8*k} V{y + 34*k} H{x + 240*k} L{x + 210*k} {y + 8*k} Z", 3)
            + ring(x + 70*k, y + 72*k, 20*k, 5, INK) + ring(x + 235*k, y + 72*k, 20*k, 5, INK) + dot(x + 70*k, y + 72*k, 6*k, PAPER) + dot(x + 235*k, y + 72*k, 6*k, PAPER))


def board(x, y, s, n=8, pieces=()):
    c = s / n
    sq = "".join(f'<rect x="{x + i * c:.1f}" y="{y + j * c:.1f}" width="{c:.1f}" height="{c:.1f}" style="{INK}"/>' for i in range(n) for j in range(n) if (i + j) % 2)
    return r(x, y, s, s, PAPER, 4) + sq + "".join(ring(x + (i + 0.5) * c, y + (j + 0.5) * c, c * 0.3, 3, SPOT if red else PAPER) for i, j, red in pieces) + r(x, y, s, s, "fill:none", 5)


def disk(cx, cy, rad):
    return ring(cx, cy, rad, 5) + ring(cx, cy, rad * 0.66, 1.5, "fill:none", "4 5") + ring(cx, cy, rad * 0.33, 1.5, "fill:none", "4 5")


def tree_in_disk(cx, cy, rad, depth=4, red_leaf=None):
    """A tree embedded in a Poincaré disk: each level halfway to the rim, children spreading out."""
    out, k = [], 0
    def go(x, y, a, spread, lvl):
        nonlocal k
        if lvl == depth:
            out.append(dot(x, y, 4, SPOT if k == red_leaf else INK)); k += 1
            return
        for s in (-1, 1):
            rr = rad * (1 - 0.5 ** (lvl + 1))
            b = a + s * spread
            nx, ny = cx + rr * math.cos(b), cy + rr * math.sin(b)
            out.append(ln(f"M{x:.1f} {y:.1f} Q{(x + nx) / 2 + (cx - (x + nx) / 2) * 0.25:.1f} {(y + ny) / 2 + (cy - (y + ny) / 2) * 0.25:.1f} {nx:.1f} {ny:.1f}", 2.5))
            go(nx, ny, b, spread / 2, lvl + 1)
        out.append(dot(x, y, 4.5 - lvl * 0.6))
    for a in (0, 2 * math.pi / 3, 4 * math.pi / 3):
        go(cx, cy, a - math.pi / 2, math.pi / 6, 0)
    return disk(cx, cy, rad) + "".join(out)


def terminal(x, y, w, h, lines=(), cursor=True):
    body = "".join(t(x + 16, y + 52 + i * 22, s, 14, "mono", fill=PAPER) for i, s in enumerate(lines))
    cur = f'<rect x="{x + 16}" y="{y + 40 + len(lines) * 22}" width="10" height="16" style="{SPOT}"/>' if cursor else ""
    return r(x, y, w, h, INK, 5, rx=6) + ln(f"M{x} {y + 24} H{x + w}", 2, colour="var(--paper)") + dot(x + 14, y + 12, 4, PAPER) + dot(x + 28, y + 12, 4, PAPER) + body + cur


ART = {
    # --- the model deployment platform (Tencent) ---
    "commits": lambda: ("".join(dot(52 + (i % 11) * 32, 70 + (i // 11) * 32, 11) if i < 45 else ring(52 + (i % 11) * 32, 70 + (i // 11) * 32, 9, 3) for i in range(55))
                        + t(40, 250, "450 / 550", 40, "display") + note(40, 284, "commits, Mar–Sep 2026")),
    "racks": lambda: (server(40, 50, 100, 200, 6, (1,)) + server(175, 30, 100, 220, 7, (4,)) + server(310, 50, 100, 200, 6)
                      + ln("M20 262 H430", 6) + note(225, 290, "1,000+ GPUs' worth of serving", "middle")),
    "clock": lambda: (clockface(120, 150, 92, 8, 0)
                      + bars(240, 60, 180, 150, [0.2, 0.25, 0.6, 0.95, 1, 0.9, 0.5, 0.25], 6, hi=4) + ln("M232 214 H428", 4)
                      + note(330, 244, "replicas, by hour", "middle")),
    "lock": lambda: ("".join(r(30, 30 + i * 84, 110, 56, PAPER, 4) + t(85, 64 + i * 84, f"replica {i + 1}", 13, "mono", "middle") for i in range(3))
                     + arrow(146, 58, 268, 140) + arrow(146, 142, 268, 152, dash="8 7") + arrow(146, 226, 268, 164, dash="8 7")
                     + r(278, 110, 150, 84, PAPER, 5) + t(353, 140, "execution log", 13, "mono", "middle") + r(292, 154, 122, 22, SPOT, 3)
                     + t(353, 170, "UNIQUE", 13, "mono", "middle", ONSPOT) + stamp(200, 260, "duplicate key: skip", -4, 15, kind="mono")),
    "twostep": lambda: (r(40, 70, 370, 50, PAPER, 5) + r(40, 70, 296, 50, INK, 5) + t(188, 104, "80%", 24, "display", "middle", PAPER)
                        + note(40, 52, "first: most of it, wait until ready")
                        + r(40, 190, 370, 50, INK, 5) + r(336, 190, 74, 50, SPOT, 5) + note(40, 172, "then: the rest")
                        + t(373, 272, "100%", 18, "display", "middle")),
    "reconcile": lambda: (r(50, 60, 200, 170, PAPER, 5) + t(70, 96, "schedule", 18, "display") + note(70, 130, "service: gone") + note(70, 156, "up / down by the clock")
                          + cross(210, 128, 16, 6) + arrow(262, 145, 320, 145)
                          + r(335, 115, 80, 40, PAPER, 5, rx=20) + dot(355, 135, 13, INK) + t(375, 188, "off", 18, "display", "middle")),
    "history": lambda: (bars(40, 60, 370, 170, [0.3 + 0.6 * abs(math.sin(i / 5)) * seed("gpu", i) + 0.1 for i in range(24)], 4)
                        + ln("M34 236 H416", 4) + note(40, 270, "a snapshot every 30 minutes")),
    "tenants": lambda: ("".join(r(30 + i * 140, 70, 110, 130, PAPER, 5) + t(85 + i * 140, 112, "BU", 22, "display", "middle") + doc(52 + i * 140, 126, 66, 60, 3, 0, False) for i in range(3))
                        + ln("M155 60 V215 M295 60 V215", 7, "2 10") + note(225, 250, "every query scoped, every owner checked", "middle")),
    "missingdir": lambda: (r(30, 80, 80, 44, PAPER, 4) + t(70, 108, "app", 14, "mono", "middle") + t(130, 110, "+", 26, "display", "middle")
                           + r(150, 80, 80, 44, PAPER, 4) + t(190, 108, "env", 14, "mono", "middle") + arrow(240, 102, 290, 102)
                           + f'<path d="M300 70 h46 l12 12 h62 v84 h-120 z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-dasharray:10 8"/>'
                           + t(360, 140, "?", 40, "display", "middle") + stamp(220, 238, "no such directory", -5, 18, kind="mono")),
    "table": lambda: (r(40, 40, 370, 200, PAPER, 5) + ln("M40 82 H410 M230 40 V240", 4)
                      + t(60, 68, "ID pair", 15, "mono") + t(250, 68, "tenant", 15, "mono")
                      + "".join(f'<rect x="60" y="{100 + i * 34}" width="{90 + 50 * seed("tab", i):.0f}" height="8" style="{INK}"/><rect x="250" y="{100 + i * 34}" width="{60 + 40 * seed("tbt", i):.0f}" height="8" style="{INK}"/>' for i in range(3))
                      + note(60, 210, "undeclared") + stamp(320, 210, "refused", -6, 18, spot=True)),
    "pin": lambda: (r(150, 30, 150, 60, INK, 5) + t(225, 68, "shared base", 15, "mono", "middle", PAPER)
                    + "".join(arrow(225, 96, 75 + i * 150, 168) + r(30 + i * 150, 176, 90, 70, PAPER, 5) for i in range(3))
                    + ring(345, 168, 12, 4, SPOT) + ln("M345 180 V206", 5) + note(225, 286, "each tenant can pin a known-good version", "middle")),
    "copy": lambda: (r(20, 70, 140, 160, PAPER, 5) + t(90, 100, "env A", 16, "display", "middle") + doc(40, 118, 100, 90, 4, -3, False)
                     + arrow(170, 150, 270, 150, dash="10 8") + note(220, 132, "replay", "middle")
                     + r(290, 70, 140, 160, PAPER, 5) + t(360, 100, "env B", 16, "display", "middle") + doc(310, 118, 100, 90, 4, 2, False)
                     + r(186, 186, 68, 52, PAPER, 4) + t(220, 218, "model", 12, "mono", "middle") + cross(220, 212, 26, 5)),
    "revert": lambda: (r(30, 40, 160, 150, PAPER, 5) + t(110, 104, "24 h", 40, "display", "middle") + note(110, 140, "every real copy", "middle") + note(110, 160, "broke", "middle")
                       + stamp(310, 90, "REFUSED", 6, 22, kind="display") + ln("M226 92 H396", 7) + stamp(310, 210, "REPORTED", -5, 22, spot=True, kind="display")),
    "trace": lambda: ("".join(r(20 + i * 110, 110, 80, 60, PAPER, 5) + t(60 + i * 110, 146, "rpc", 14, "mono", "middle") for i in range(4))
                      + "".join(arrow(100 + i * 110, 140, 128 + i * 110, 140, 4) for i in range(3))
                      + ln("M60 110 V78 H390 V110", 3, "6 6") + r(150, 60, 150, 34, SPOT, 4) + t(225, 83, "request-id", 14, "mono", "middle", ONSPOT)
                      + note(225, 220, "one ID, every call", "middle")),
    "token": lambda: (ring(110, 140, 34, 6) + ln("M144 140 H260 M220 140 v24 M246 140 v18", 8) + clockface(330, 140, 60, 11, 55)
                      + ln("M80 236 A160 70 0 0 0 380 236", 4, "9 7") + arrow(370, 246, 384, 228, 4) + note(225, 280, "expired: rebuild the client", "middle")),
    "guards": lambda: (r(290, 60, 140, 180, PAPER, 5, dash="12 7") + t(360, 92, "namespace", 13, "mono", "middle")
                       + ln("M240 40 V260", 10) + "".join(ln(f"M226 {60 + i * 40} H254", 6) for i in range(6))
                       + doc(40, 90, 110, 120, 5, -4) + arrow(160, 150, 222, 150) + stamp(120, 262, "checked first", -4, 15, kind="mono")),
    "handover": lambda: (doc(40, 50, 150, 200, 8, -6) + doc(170, 40, 150, 200, 8, 5) + t(115, 150, "EN", 34, "display", "middle") + t(245, 140, "中文", 34, "body", "middle")
                         + r(330, 70, 100, 110, INK, 5) + t(380, 132, "11", 44, "display", "middle", PAPER) + note(380, 210, "decisions", "middle") + note(380, 228, "recorded", "middle")),
    # --- the conversation query service ---
    "newservice": lambda: (r(40, 50, 180, 200, PAPER, 5) + t(130, 84, ".proto", 18, "mono", "middle") + "".join(f'<rect x="60" y="{104 + i * 22}" width="{80 + 60 * seed("pb", i):.0f}" height="6" style="{INK}"/>' for i in range(6))
                           + arrow(230, 150, 290, 150) + r(300, 90, 120, 120, INK, 5) + t(360, 158, "query", 18, "display", "middle", PAPER)
                           + stamp(330, 250, "No. 2", -6, 18, spot=True, kind="display")),
    "tz": lambda: (clockface(120, 130, 80, 9, 0) + clockface(330, 130, 80, 1, 0) + t(120, 248, "written", 16, "mono", "middle") + t(330, 248, "read back", 16, "mono", "middle")
                   + t(225, 140, "≠", 44, "display", "middle") + note(225, 286, "DATETIME, timezone-wrong", "middle")),
    "timeout": lambda: (r(40, 70, 160, 140, INK, 5) + t(120, 148, "LLM", 30, "display", "middle", PAPER) + note(120, 236, "worker", "middle")
                        + f'<path d="M280 50 h110 l-46 100 l46 100 h-110 l46 -100 z" style="fill:var(--paper);stroke:var(--ink);stroke-width:6;stroke-linejoin:round"/>'
                        + f'<path d="M300 228 h70 l-35 -30 z" style="{INK}"/>' + dot(335, 180, 4)),
    # --- 9Loop ---
    "week": lambda: ("".join(r(30 + i * 56, 60, 48, 60, PAPER if i < 6 else SPOT, 4) + t(54 + i * 56, 98, "MTWTFSS"[i], 18, "display", "middle", ONSPOT if i == 6 else INK) for i in range(7))
                     + r(30, 150, 120, 110, INK, 5) + t(90, 222, "TS", 44, "display", "middle", PAPER)
                     + "".join(r(180 + (i % 3) * 82, 150 + (i // 3) * 58, 70, 48, PAPER, 4) for i in range(6))),
    "coverage": lambda: (t(40, 60, "test coverage", 15, "mono") + r(40, 80, 370, 44, PAPER, 5) + r(40, 80, 148, 44, INK, 5) + t(206, 112, "40%", 20, "display")
                         + arrow(225, 136, 225, 168) + r(40, 178, 370, 44, PAPER, 5) + r(40, 178, 315, 44, SPOT, 5) + t(56, 210, "85%", 20, "display", fill=ONSPOT)
                         + note(40, 266, "an automated integration suite")),
    "latency": lambda: (bars(80, 50, 120, 190, [1.0], 0) + bars(250, 50, 120, 190, [0.7], 0, hi=0) + ln("M40 244 H410", 5)
                        + t(140, 276, "before", 15, "mono", "middle") + t(310, 276, "after", 15, "mono", "middle") + t(310, 90, "−30%", 28, "display", "middle")),
    # --- in-context imitation learning ---
    "demos": lambda: ("".join(r(20, 30 + i * 84, 150, 66, PAPER, 4) + curve(30, 38 + i * 84, 130, 50, lambda s, i=i: 0.5 + 0.4 * math.sin(3 * s + i), 20, 3) for i in range(3))
                      + arrow(182, 150, 236, 150) + ln("M300 250 V190 L340 130 L400 120", 12) + ring(300, 250, 18, 5, INK) + ring(340, 130, 9, 4)
                      + ln("M400 108 l18 -10 M400 132 l18 10", 6) + r(404, 112, 18, 18, SPOT, 3) + note(300, 290, "a few demonstrations, then the task", "middle")),
    "poincare": lambda: tree_in_disk(225, 150, 130, 4, red_leaf=9),
    "dual": lambda: (r(30, 60, 390, 64, PAPER, 5) + t(50, 99, "actions", 16, "mono") + "".join(arrow(170 + i * 60, 92, 214 + i * 60, 92, 4) for i in range(4))
                     + r(30, 176, 390, 64, PAPER, 5) + t(50, 215, "observations", 16, "mono") + "".join(dot(220 + i * 46, 208, 9, INK) for i in range(5))
                     + note(225, 280, "two channels, embedded apart", "middle")),
    "product": lambda: ("".join(ln(f"M{40 + i * 30} 70 V230 M40 {70 + i * 32} H160", 2) for i in range(5)) + r(40, 70, 120, 160, "fill:none", 5)
                        + t(200, 168, "×", 48, "display", "middle") + disk(330, 150, 85) + tree_in_disk(330, 150, 85, 3)
                        + t(100, 268, "E", 22, "display", "middle") + t(330, 268, "H", 22, "display", "middle")),
    "sarkar": lambda: (tree_in_disk(150, 150, 120, 4) + stamp(340, 110, "no training", -8, 18, kind="mono") + note(340, 190, "the embedding", "middle") + note(340, 210, "is constructed", "middle")),
    "versus": lambda: (bars(90, 40, 110, 200, [0.86], 0) + bars(250, 40, 110, 200, [0.64], 0, hi=0) + ln("M50 244 H400", 5)
                       + t(145, 276, "Instant Policy", 14, "mono", "middle") + t(305, 276, "hyperbolic", 14, "mono", "middle")),
    "feasible": lambda: (doc(60, 30, 220, 240, 9, -3) + stamp(300, 200, "feasible", -10, 24, spot=True, kind="display") + note(80, 22, "the write-up says so")),
    # --- acute kidney injury ---
    "blood": lambda: (r(60, 40, 52, 200, PAPER, 5, rx=24) + r(64, 130, 44, 108, SPOT, 0, rx=20) + r(60, 40, 52, 200, "fill:none", 5, rx=24)
                      + curve(170, 60, 240, 160, lambda s: 0.2 + 0.7 * s ** 3, 30, 5) + ln("M170 60 V220 H410", 4) + note(170, 252, "creatinine, over time")
                      + t(360, 100, "AUC 87%", 18, "display", "end")),
    "k8s": lambda: ("".join(f'<polygon points="{x},{y - 34} {x + 30},{y - 17} {x + 30},{y + 17} {x},{y + 34} {x - 30},{y + 17} {x - 30},{y - 17}" style="fill:var(--paper);stroke:var(--ink);stroke-width:5"/>' for x, y in ((80, 90), (150, 90), (115, 150)))
                    + ring(320, 120, 70, 5) + ln("M270 120 A50 50 0 0 1 370 120", 10, "4 6") + ln("M320 120 L356 84", 5) + dot(320, 120, 6)
                    + arrow(150, 240, 70, 240) + note(160, 246, "rollback on degradation")),
    "postmortem": lambda: (r(70, 20, 310, 260, PAPER, 5) + t(90, 60, "POSTMORTEM", 22, "display")
                           + "".join(t(90, 104 + i * 58, h, 13, "mono") + f'<rect x="90" y="{114 + i * 58}" width="{180 + 80 * seed("pm", i):.0f}" height="6" style="{INK}"/>' for i, h in enumerate(("impact", "root cause", "resolution")))
                           + stamp(340, 250, "live", -10, 16, spot=True, kind="mono")),
    # --- neuromorphic ---
    "chip": lambda: chip(150, 70, 150, 150, "Loihi 2") + note(225, 286, "for the edge", "middle"),
    "spikes": lambda: ("".join(ln(f"M{40 + 360 * seed('sp', i * 13 + j):.0f} {50 + i * 36} v20", 3) for i in range(5) for j in range(8))
                       + "".join(ln(f"M{40 + 360 * seed('sw', j):.0f} {50 + 5 * 36} v20", 4, colour="var(--live-red)") for j in range(12))
                       + ln("M40 250 H410", 3) + note(40, 280, "winner takes all")),
    "motionface": lambda: ("".join(dot(225 + 95 * math.cos(a) * (0.8 + 0.2 * seed("f", k)), 150 + 120 * math.sin(a) * (0.8 + 0.2 * seed("g", k)), 3) for k, a in enumerate(i / 60 * 2 * math.pi for i in range(60)))
                           + "".join(dot(190 + 70 * (k % 2) + 10 * seed("e", k), 120 + 6 * seed("e2", k), 3) for k in range(14))
                           + "".join(dot(205 + 40 * seed("m", k), 200 + 5 * seed("m2", k), 3, SPOT) for k in range(10))
                           + note(225, 290, "only what moved", "middle")),
    "federated": lambda: (server(185, 30, 80, 110, 3) + "".join(laptop(30 + i * 150, 210, 90) + arrow(75 + i * 150, 200, 225 - (1 - i) * 30, 150, 4, "7 6") for i in range(3))),
    # --- KURF ---
    "arm": lambda: (ln("M40 260 H410", 6) + r(90, 230, 80, 30, INK, 5) + ln("M130 230 L170 130 L270 90", 16) + ring(170, 130, 12, 5) + ring(130, 230, 12, 5, INK)
                    + ln("M270 78 l26 -6 M270 102 l26 6", 7) + r(300, 196, 64, 64, SPOT, 5) + arrow(300, 86, 330, 186, 3, "6 6")),
    "ablate": lambda: ("".join(r(30 + (i % 3) * 136, 30 + (i // 3) * 130, 120, 110, PAPER, 4) + curve(40 + (i % 3) * 136, 40 + (i // 3) * 130, 100, 86, lambda s, i=i: (1 - math.exp(-4 * s)) * (0.5 + 0.5 * seed("ab", i)), 20, 3) for i in range(6))),
    # --- TradingJoe ---
    "strategies": lambda: ("".join(r(20, 20 + i * 54, 150, 42, PAPER, 4) + t(30, 47 + i * 54, s, 13, "mono") + arrow(176, 41 + i * 54, 266, 150, 3) for i, s in enumerate(("Black-Litterman", "Fama-French", "momentum", "mean-reversion", "views")))
                           + r(274, 100, 156, 100, INK, 5) + t(352, 158, "meta", 26, "display", "middle", PAPER)),
    "views": lambda: (doc(30, 50, 140, 180, 6, -5) + r(52, 120, 96, 30, PAPER, 0) + t(100, 142, "Form 4", 18, "display", "middle") + note(100, 260, "insider buys", "middle")
                      + ln("M210 200 L260 140 L300 160 L380 70", 6) + arrow(330, 110, 384, 66) + note(320, 260, "analyst targets", "middle")),
    "walkforward": lambda: ("".join(r(30 + i * 60, 40 + i * 46, 200, 30, INK, 3) + r(230 + i * 60, 40 + i * 46, 60, 30, SPOT, 3) for i in range(4))
                            + arrow(30, 250, 420, 250, 4) + note(30, 285, "train, then test on what comes after")),
    "claim": lambda: (r(30, 60, 390, 140, PAPER, 6) + t(225, 130, "5/5 beats", 46, "display", "middle") + t(225, 180, "MinVar", 34, "display", "middle")
                      + note(225, 250, "what the backtest said", "middle")),
    "redteam": lambda: ("".join(person(55 + i * 85, 70, 1.2, SPOT if i == 0 else PAPER) + t(55 + i * 85, 160, s, 13, "mono", "middle") for i, s in enumerate(("leakage", "finance", "ML", "LLM", "execution")))
                        + note(225, 240, "five agents, against my own results", "middle")),
    "ghost": lambda: (r(30, 70, 180, 150, PAPER, 5) + t(50, 104, "LLM view", 16, "mono") + "".join(f'<rect x="50" y="{124 + i * 22}" width="{100 + 30 * seed("gh", i):.0f}" height="6" style="{INK}"/>' for i in range(3)) + t(176, 196, "[1]", 16, "mono")
                      + arrow(210, 190, 280, 150, 4, "7 6") + f'<path d="M290 60 h100 l30 30 v150 h-130 z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-dasharray:4 9"/>'
                      + note(355, 268, "never ingested", "middle")),
    "retract": lambda: (doc(60, 30, 250, 240, 9, 2) + "".join(ln(f"M80 {80 + i * 22} H280", 4) for i in range(6)) + stamp(300, 150, "RETRACTED", -12, 26, spot=True, kind="display")),
    # --- RE-News ---
    "sources": lambda: ("".join(r(20, 26 + i * 52, 110, 40, PAPER, 4) + t(30, 51 + i * 52, s, 12, "mono") + arrow(136, 46 + i * 52, 210, 46 + i * 52, 3) for i, s in enumerate(("news", "government", "CPI / OPR", "opinion", "search")))
                        + "".join(r(222, 30 + i * 52, 200, 34, INK if i != 2 else SPOT, 3) for i in range(5)) + note(322, 296, "one citable signal schema", "middle")),
    "fusion": lambda: ("".join(r(20 + i * 10, 40 + i * 52, 120, 34, INK, 3) for i in range(3)) + doc(40, 210, 70, 80, 3, -8) + cross(75, 250, 26, 6)
                       + arrow(170, 120, 240, 150) + r(250, 90, 170, 120, PAPER, 6) + t(335, 160, "LLM", 30, "display", "middle") + note(335, 250, "signals in, never documents", "middle")),
    "switch": lambda: (server(40, 50, 120, 180, 5, (2,)) + note(100, 260, "home lab", "middle") + r(185, 120, 80, 40, PAPER, 5, rx=20) + dot(205, 140, 13, INK)
                       + r(300, 80, 120, 120, PAPER, 5, dash="10 7") + t(360, 148, "opt-in", 15, "mono", "middle")),
    "grey": lambda: ("".join(f'<polygon points="{60 + (i % 4) * 90},{50 + (i // 4) * 90} {130 + (i % 4) * 90},{60 + (i // 4) * 90} {140 + (i % 4) * 90},{130 + (i // 4) * 90} {70 + (i % 4) * 90},{125 + (i // 4) * 90}" style="{INK if seed("map", i) > 0.6 else "fill:var(--tone)"};stroke:var(--ink);stroke-width:3"/>' for i in range(8))
                     + stamp(225, 268, "grey is correct", -3, 18, kind="mono")),
    # --- the home lab ---
    "homelab": lambda: (r(170, 40, 110, 200, PAPER, 6) + r(186, 150, 78, 30, SPOT, 3) + "".join(ln(f"M186 {60 + i * 14} H264", 3) for i in range(5))
                        + laptop(20, 70, 90) + laptop(340, 70, 90) + laptop(340, 200, 70)
                        + ln("M110 110 L170 140 M280 140 L340 110 M280 180 L340 220", 4, "6 7") + note(225, 284, "over Tailscale", "middle")),
    # --- chess ---
    "board": lambda: board(40, 40, 220, 8, ((2, 3, False), (5, 4, True), (4, 6, False))) + "".join(r(300 + i * 8, 60 + i * 30, 100, 100, PAPER, 4) for i in range(3)) + note(350, 270, "CNN", "middle"),
    "mcts": lambda: (ring(225, 40, 16, 5, INK) + "".join(ln(f"M225 56 L{90 + i * 135} 120", 4) + ring(90 + i * 135, 130, 13, 4) for i in range(3))
                     + "".join(ln(f"M{90 + (i // 3) * 135} 143 L{50 + i * 45} 200", 3) + ring(50 + i * 45, 208, 9, 3, SPOT if i == 4 else PAPER) for i in range(9))
                     + note(225, 270, "search, guided by the net", "middle")),
    "selfplay": lambda: (board(30, 70, 150, 8, ((3, 3, False),)) + board(270, 70, 150, 8, ((4, 4, True),)) + ln("M195 110 Q225 70 255 110", 5) + ln("M255 190 Q225 230 195 190", 5)
                         + arrow(240, 98, 256, 112, 4) + arrow(210, 202, 194, 188, 4) + note(225, 270, "it plays itself, on the GPU", "middle")),
    # --- the Transformer ---
    "subtitles": lambda: (r(60, 30, 330, 210, INK, 6, rx=10) + r(80, 50, 290, 170, "fill:var(--tone)", 0) + r(110, 178, 230, 12, PAPER, 0) + r(150, 196, 150, 12, PAPER, 0)
                          + ln("M180 240 L160 268 M270 240 L290 268", 6) + t(225, 120, "S1–S14", 34, "display", "middle", PAPER)),
    "attention": lambda: ("".join(f'<rect x="{110 + i * 28}" y="{30 + j * 28}" width="26" height="26" style="{INK};opacity:{0.1 + 0.9 * (1 if i == j else seed("at", i * 9 + j) ** 3):.2f}"/>' for i in range(8) for j in range(8))
                          + r(110, 30, 224, 224, "fill:none", 4) + note(222, 284, "Q · Kᵀ", "middle")),
    # --- SRGAN ---
    "pixels": lambda: ("".join(f'<rect x="{30 + i * 36}" y="{60 + j * 36}" width="36" height="36" style="{INK};opacity:{0.15 + 0.85 * seed("px", i * 5 + j):.2f}"/>' for i in range(5) for j in range(5))
                       + t(225, 160, "4×", 34, "display", "middle") + ring(350, 150, 82, 5) + f'<circle cx="350" cy="150" r="62" style="fill:var(--tone)"/>' + ring(330, 128, 18, 0, INK)),
    "loss": lambda: (r(30, 50, 160, 160, "fill:var(--tone)", 5) + t(110, 240, "MSE", 18, "display", "middle") + r(260, 50, 160, 160, PAPER, 5)
                     + "".join(ln(f"M{270 + i * 14} 200 L{290 + i * 14} 60", 2) for i in range(10)) + t(340, 240, "perceptual", 18, "display", "middle") + t(225, 140, "vs", 22, "display", "middle")),
    "gpu": lambda: (r(40, 80, 370, 130, PAPER, 6, rx=6) + "".join(ring(120 + i * 150, 145, 46, 5) + "".join(ln(f"M{120 + i * 150} 145 L{120 + i * 150 + 40 * math.cos(k * 1.05 + i):.0f} {145 + 40 * math.sin(k * 1.05 + i):.0f}", 4) for k in range(6)) for i in range(2))
                    + "".join(r(70 + i * 22, 210, 14, 22, INK, 0) for i in range(14)) + note(225, 276, "Windows, through DirectML", "middle")),
    # --- licence plates ---
    "plate": lambda: (car(60, 70, 330) + r(170, 190, 110, 32, PAPER, 4) + t(225, 213, "ABC 1234", 15, "mono", "middle") + r(160, 182, 130, 48, "fill:none", 4, dash="8 6")
                      + note(225, 280, "YOLOv8 finds it", "middle")),
    "chars": lambda: ("".join(r(30 + i * 52, 80, 44, 64, PAPER, 4) + t(52 + i * 52, 124, c, 24, "display", "middle") for i, c in enumerate("ABC1234"))
                      + "".join(arrow(52 + i * 52, 154, 52 + i * 52, 190, 3) for i in range(7)) + bars(30, 196, 356, 40, [1] * 7, 8)
                      + note(30, 272, "a small CNN reads each one")),
    # --- the FPS agent ---
    "fps": lambda: (ln("M0 300 L160 170 H290 L450 300 M0 0 L160 120 H290 L450 0 M160 120 V170 M290 120 V170", 4) + r(196, 128, 58, 34, "fill:var(--tone)", 3)
                    + ring(225, 145, 34, 4, "fill:none") + ln("M225 96 V126 M225 164 V194 M176 145 H206 M244 145 H274", 4, colour="var(--live-red)")),
    "machines": lambda: ("".join(server(30 + i * 140, 160, 110, 110, 3) + arrow(85 + i * 140, 150, 225, 90, 4, "7 6") for i in range(3)) + ring(225, 60, 34, 6, INK) + t(225, 67, "θ", 22, "display", "middle", PAPER)),
    # --- BlockHub ---
    "vote": lambda: ("".join(r(30 + i * 100, 200, 80, 44, PAPER, 5, rx=22) + (ln(f"M{110 + i * 100} 222 H{130 + i * 100}", 8) if i < 3 else "") for i in range(4))
                     + r(160, 50, 130, 110, PAPER, 6) + ln("M190 80 H260", 8) + doc(186, 22, 78, 70, 3, 6, False) + note(225, 286, "every vote on-chain", "middle")),
    "trophy": lambda: (f'<path d="M160 50 h130 v40 a65 65 0 0 1 -130 0 z" style="fill:var(--live-red);stroke:var(--ink);stroke-width:6"/>'
                       + ln("M160 70 h-30 a30 30 0 0 0 40 50 M290 70 h30 a30 30 0 0 1 -40 50 M225 155 V200 M180 210 H270", 6) + r(170, 210, 110, 34, INK, 4)
                       + t(225, 108, "1st", 30, "display", "middle", ONSPOT) + note(225, 282, "of 50+ teams", "middle")),
    # --- CarDesigner ---
    "scan": lambda: (car(60, 90, 330) + "".join(dot(70 + 310 * seed("lid", i), 80 + 100 * seed("lid2", i), 2.2, SPOT if i % 7 == 0 else INK) for i in range(120))
                     + ln("M40 40 L120 90 M40 40 L60 150", 2, "4 5") + r(20, 20, 30, 50, INK, 3, rx=5)),
    "driveway": lambda: (phone(150, 20, 150, 270, 0, ln("M170 200 L280 200 M180 250 L270 250", 2, "5 6") + car(166, 150, 118, "fill:var(--live-red)"))),
    # --- the data terminal ---
    "ticks": lambda: ("".join(ln(f"M{30 + i * 16} {130 - 70 * seed('tk', i):.0f} v{10 + 50 * seed('tk2', i):.0f}", 6) for i in range(10))
                      + arrow(200, 110, 250, 110) + r(258, 80, 70, 60, INK, 4) + t(293, 116, "TCP", 13, "mono", "middle", PAPER) + arrow(336, 110, 360, 110)
                      + r(366, 70, 70, 80, PAPER, 4) + curve(370, 76, 62, 68, lambda s: 0.5 + 0.4 * math.sin(7 * s) * s, 20, 3)
                      + note(30, 200, "C++ in, Python plots") + terminal(30, 216, 390, 76, (), False)),
    # --- expense tracker ---
    "tui": lambda: (terminal(40, 20, 370, 180, ("> new month", "budgets carried forward")) + "".join(r(60 + i * 58, 220, 48, 44, PAPER, 4, rx=6) + t(84 + i * 58, 249, k, 15, "mono", "middle") for i, k in enumerate(("j", "k", "a", "d", "q", "↵")))),
    # --- myBudiXc ---
    "book": lambda: ("".join(r(130, 20 + i * 26, 60 + 120 * seed("ask", i), 20, PAPER, 3) for i in range(5)) + ln("M100 155 H350", 5, colour="var(--live-red)")
                     + "".join(r(130, 168 + i * 26, 60 + 120 * seed("bid", i), 20, INK, 3) for i in range(5)) + t(110, 74, "asks", 14, "mono", "end") + t(110, 222, "bids", 14, "mono", "end")),
    "batch": lambda: (clockface(110, 140, 70, 12, 15) + "".join(dot(260, 60 + i * 44, 10, INK) + dot(400, 60 + i * 44, 10, PAPER) + ring(400, 60 + i * 44, 10, 4) + ln(f"M272 {60 + i * 44} Q330 {60 + i * 44 + (seed('pr', i) - 0.5) * 80:.0f} 388 {60 + ((i + 2) % 5) * 44}", 3) for i in range(5))
                      + note(110, 250, "every N minutes", "middle")),
    # --- polyarb ---
    "set": lambda: (r(30, 70, 120, 140, PAPER, 5) + t(90, 130, "YES", 26, "display", "middle") + t(90, 172, "a", 18, "mono", "middle")
                    + t(175, 150, "+", 30, "display", "middle") + r(200, 70, 120, 140, PAPER, 5) + t(260, 130, "NO", 26, "display", "middle") + t(260, 172, "b", 18, "mono", "middle")
                    + t(385, 150, "a+b<1", 22, "display", "middle") + note(225, 260, "buy every outcome under a dollar", "middle")),
    "legs": lambda: (r(40, 60, 160, 60, INK, 5) + t(120, 98, "leg 1: filled", 14, "mono", "middle", PAPER) + r(40, 160, 160, 60, PAPER, 5, dash="10 7") + t(120, 198, "leg 2: ?", 14, "mono", "middle")
                     + r(270, 90, 140, 100, PAPER, 5) + ln("M300 110 V170 M300 110 h60 l-12 14 l12 14 h-60", 5) + note(340, 220, "live: behind a flag", "middle")),
    # --- sales signatures ---
    "signatures": lambda: ("".join(curve(30, 40 + i * 8, 260, 160, lambda s, i=i: 0.2 + 0.6 * s ** (1 + i * 0.4) + 0.06 * math.sin(9 * s + i), 30, 3) for i in range(4))
                           + curve(300, 40, 120, 160, lambda s: 0.55 + 0.35 * s, 10, 4, "8 7") + ln("M30 220 H420", 4) + note(30, 256, "products that behave alike")),
    # --- RoboCup ---
    "robot": lambda: (r(170, 120, 110, 130, PAPER, 6, rx=10) + ring(225, 80, 40, 6) + dot(210, 78, 6) + dot(240, 78, 6) + ring(195, 260, 16, 5, INK) + ring(255, 260, 16, 5, INK)
                      + f'<path d="M290 40 h130 v60 h-90 l-20 20 v-20 h-20 z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5"/>' + t(355, 78, "bring me…", 13, "mono", "middle")),
    "rooms": lambda: (r(30, 30, 390, 240, PAPER, 6) + ln("M200 30 V140 M200 190 V270 M30 150 H120 M160 150 H200 M200 120 H420", 5)
                      + person(320, 200, 0.9, SPOT) + note(110, 100, "kitchen", "middle") + note(310, 80, "living room", "middle")),
}


def panel(kind, span):
    """A panel's picture: Wallet's own, or a library picture on a stage fitted to the panel's width."""
    if kind in WALLET_PANELS:
        return wallet_panel(kind)
    if kind not in ART:
        raise SystemExit(f"chapters: there is no picture called '{kind}' (art.py ART)")
    W, H = {6: (900, 300), 4: (600, 340), 3: (450, 300), 2: (300, 340)}[span]
    k = min(W / 450, H / 300)
    x, y = (W - 450 * k) / 2, (H - 300 * k) / 2
    tone_ = tone(0, 0, W, H, 12, 2.6, False) if W > 450 * k + 1 or H > 300 * k + 1 else ""
    stage = f'<rect x="{x:.0f}" y="{y:.0f}" width="{450 * k:.0f}" height="{300 * k:.0f}" style="{PAPER}"/>' if tone_ else ""
    return (f'<svg viewBox="0 0 {W} {H}" aria-hidden="true"><rect width="{W}" height="{H}" style="{PAPER}"/>{tone_}{stage}'
            f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">{ART[kind]()}</g></svg>')


def fit_title(title, room):
    """The cover title in up to three lines, as big as fits the room beside the kana and above the picture."""
    words, best = title.upper().split(), None
    for a in range(1, len(words) + 1):
        for b in range(a, len(words) + 1):
            lines = [" ".join(w) for w in (words[:a], words[a:b], words[b:]) if w]
            size = min(100, 160 / (0.95 * len(lines)), min(room / (0.86 * len(l)) for l in lines))
            if not best or size > best[0]:
                best = (size, lines)
    return best


def cover(n, vol, ch, name):
    """Any volume's cover but Wallet's: the band, the title, the volume's picture on screentone, and the obi."""
    W, H = 512, 728
    live = n.get("status") == "active"
    obi_fill, obi_text = (SPOT, ONSPOT) if live else (INK, PAPER)
    room = W - 22 - 64
    size, lines = fit_title(n["title"], room)
    title = "".join(f'<text x="22" y="{58 + size * 0.95 * (i + 1):.0f}" textLength="{min(room, 0.86 * size * len(l)):.0f}" lengthAdjust="spacingAndGlyphs" '
                    f'style="{INK};font:400 {size:.0f}px var(--font-display)">{esc(l)}</text>' for i, l in enumerate(lines))
    top = 58 + size * 0.95 * len(lines) + 30
    words, tag = n["tagline"].split(), [""]
    for w in words:
        if len(tag[-1]) + len(w) > 50 and len(tag) < 2:
            tag.append("")
        tag[-1] = (tag[-1] + " " + w).strip()
    eps = ch["episodes"]
    shown = f"第{eps[0]['n']}話 収録" if len(eps) == 1 else f"第{eps[0]['n']}–{eps[-1]['n']}話 収録"
    kana = ch["kana"]
    return f'''<svg class="cover" viewBox="0 0 {W} {H}" role="img" aria-label="Cover of volume {vol}, {esc(n['title'])}.">
<rect width="{W}" height="{H}" style="{PAPER}"/>
{tone(0, top, W, H - 150, 13, 4.6)}
<rect width="{W}" height="44" style="{INK}"/>
<text x="20" y="30" style="{PAPER};font:400 17px var(--font-display);letter-spacing:.04em">{esc(name)}</text>
<text x="{W - 20}" y="30" text-anchor="end" style="{PAPER};font:500 13px var(--font-mono);letter-spacing:.12em">VOL. {vol}</text>
{title}
<g transform="translate(31 {max(top, 252):.0f})"><rect x="-6" y="-6" width="462" height="312" style="{PAPER};stroke:var(--ink);stroke-width:5"/>{ART[ch["cover"]]()}</g>
<text x="{W - 34}" y="70" style="{INK};font:700 28px var(--font-body);writing-mode:vertical-rl">{esc(kana)}</text>
<rect y="{H - 150}" width="{W}" height="150" style="{obi_fill}"/>
<text x="24" y="{H - 98}" textLength="{min(W - 48, len(ch['obi']) * 17):.0f}" lengthAdjust="spacingAndGlyphs" style="{obi_text};font:400 31px var(--font-display)">{esc(ch["obi"])}</text>
{"".join(f'<text x="24" y="{H - 64 + i * 20}" style="{obi_text};font:400 14px var(--font-body)">{esc(l)}</text>' for i, l in enumerate(tag))}
<text x="{W - 22}" y="{H - 18}" text-anchor="end" style="{obi_text};font:700 14px var(--font-body)">{shown}</text>
</svg>'''
