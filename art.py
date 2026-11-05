"""The volumes' art: sleeves, records and panel pictures, drawn as SVG in the site's colour tokens. build.py calls
sleeve(), record() and panel(); a chapter script names its pictures by their keys in ART (or Wallet's own)."""
import hashlib, html, math

esc = lambda s: html.escape(str(s or ""), quote=True)


def seed(s, k=0):
    """A stable number in [0, 1) from an id, so each picture is the same on every build."""
    return int(hashlib.sha1(f"{s}:{k}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


# ---------- Wallet's art (hand-drawn, one volume) ----------
INK, PAPER, SPOT, ONSPOT = "fill:var(--ink)", "fill:var(--paper)", "fill:var(--live-red)", "fill:var(--live-on-red)"


_tone_ids = iter(range(10**9))   # pattern ids, unique across the build and so on any one page


def tone(x0, y0, x1, y1, step, rmax, fade_from_top=True):
    """Screentone: a dot grid whose dots grow across the area. Each row of dots is one rect filled with a
    one-dot pattern, not a circle per dot: the same picture, with a few dozen elements instead of thousands."""
    defs, rects = [], []
    y, row, h = y0, 0, step * 0.87
    while y <= y1:
        x = x0 + (row % 2) * step / 2
        f = (y - y0) / max(1, y1 - y0) if fade_from_top else 1 - (y - y0) / max(1, y1 - y0)
        r = rmax * max(0, min(1, f)) ** 1.2
        n = int((x1 - x) // step) + 1 if x <= x1 else 0
        if r > 0.25 and n:
            pid = f"tn{next(_tone_ids)}"
            # the tile is centred on the dot, so the row's rect runs half a step either side of its first and last dots
            defs.append(f'<pattern id="{pid}" x="{x - step / 2:g}" y="{y - h / 2:.2f}" width="{step:g}" height="{h:.2f}" patternUnits="userSpaceOnUse">'
                        f'<circle cx="{step / 2:g}" cy="{h / 2:.2f}" r="{r:.2f}"/></pattern>')
            rects.append(f'<rect x="{x - step / 2:g}" y="{y - h / 2:.2f}" width="{n * step:g}" height="{h:.2f}" fill="url(#{pid})"/>')
        y += h
        row += 1
    return f'<defs style="{INK}">{"".join(defs)}</defs><g>{"".join(rects)}</g>'


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
# screentone, and sleeve() puts the volume's chosen picture on its sleeve. Ink and paper only, one red accent at most.
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


PIECES = {   # outlines on a unit square centred on 0,0, drawn at a board's cell size
    "pawn": "M-.28 .36H.28L.16 .2L.08-.02H-.08L-.16 .2Z M0-.3A.13 .13 0 1 1 0-.04A.13 .13 0 1 1 0-.3Z",
    "rook": "M-.28 .36H.28V.24H.2L.16-.14H.24V-.34H.12V-.24H.04V-.34H-.04V-.24H-.12V-.34H-.24V-.14H-.16L-.2 .24H-.28Z",
    "king": "M-.28 .36H.28L.2 .1Q.3-.12 .06-.14V-.22H.14V-.3H.06V-.4H-.06V-.3H-.14V-.22H-.06V-.14Q-.3-.12-.2 .1Z",
    "knight": "M-.26 .36H.26L.2 .1Q.22-.2-.02-.36L-.08-.24Q-.24-.16-.28 0L-.18 .06L-.04-.04Q-.04 .12-.18 .24Z",
}


def piece(cx, cy, c, kind, side):
    """A chess piece on a square: white (1) in paper with an ink edge, black (0) in ink with a paper edge, red (2) for the one that moved."""
    fill, edge = {0: ("var(--ink)", "var(--paper)"), 1: ("var(--paper)", "var(--ink)"), 2: ("var(--live-red)", "var(--ink)")}[side]
    return (f'<path d="{PIECES[kind]}" transform="translate({cx:.1f} {cy:.1f}) scale({c * 1.3:.1f})" vector-effect="non-scaling-stroke" '
            f'style="fill:{fill};stroke:{edge};stroke-width:2.5;stroke-linejoin:round"/>')


def monkey(cx, cy, s=1.0, fill=PAPER, arm_up=True):
    """A monkey, sitting up: ears, head, a muzzle, one arm raised (or not)."""
    k = lambda v: v * s
    arm = (f"M{cx + k(22):.0f} {cy + k(42):.0f} L{cx + k(46):.0f} {cy + k(4):.0f}" if arm_up else f"M{cx + k(22):.0f} {cy + k(42):.0f} L{cx + k(38):.0f} {cy + k(82):.0f}")
    return (
            ring(cx - k(29), cy - k(4), k(11), 4, fill) + ring(cx + k(29), cy - k(4), k(11), 4, fill)
            + ln(f"M{cx + k(20):.0f} {cy + k(84):.0f} C{cx + k(60):.0f} {cy + k(90):.0f} {cx + k(64):.0f} {cy + k(50):.0f} {cx + k(48):.0f} {cy + k(56):.0f}", 4)
            + r(cx - k(24), cy + k(28), k(48), k(62), fill, 5, rx=k(20))
            + ln(f"M{cx - k(22):.0f} {cy + k(42):.0f} L{cx - k(38):.0f} {cy + k(82):.0f} " + arm, 6)
            + ln(f"M{cx - k(12):.0f} {cy + k(88):.0f} V{cy + k(108):.0f} M{cx + k(12):.0f} {cy + k(88):.0f} V{cy + k(108):.0f}", 6)
            + ring(cx, cy, k(27), 5, fill)
            + f'<ellipse cx="{cx:.0f}" cy="{cy + k(9):.0f}" rx="{k(16):.0f}" ry="{k(11):.0f}" style="{PAPER};stroke:var(--ink);stroke-width:3"/>'
            + dot(cx - k(9), cy - k(7), k(3.5)) + dot(cx + k(9), cy - k(7), k(3.5))
            + ln(f"M{cx - k(6):.0f} {cy + k(11):.0f} Q{cx:.0f} {cy + k(16):.0f} {cx + k(6):.0f} {cy + k(11):.0f}", 2.5))


def pix(x, y, p, rows, colours=None):
    """Pixel art: one string per row, a character per pixel (# ink, + tone, . paper, r red, space clear).
    Each run of one colour is one rect, so a sprite stays a few dozen elements."""
    colours = colours or {"#": INK, "+": "fill:var(--tone)", ".": PAPER, "r": SPOT}
    out = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            c, k = row[i], i
            while k < len(row) and row[k] == c:
                k += 1
            if c in colours:
                out.append(f'<rect x="{x + i * p:g}" y="{y + j * p:g}" width="{(k - i) * p:g}" height="{p:g}" style="{colours[c]}"/>')
            i = k
    return "".join(out)


HOUSE = ("     ##############     ", "    #++++++++++++++#    ", "   #++++++++++++++++#   ", "  #++++++++++++++++++#  ",
         " ###################### ", "  #..................#  ", "  #.####........####.#  ", "  #.#..#........#..#.#  ",
         "  #.####..####..####.#  ", "  #.......#..#.......#  ", "  #.......#..#.......#  ", "  ####################  ")
TREE = ("  ####  ", " #++++# ", "#++++++#", "#++#+++#", "#++++#+#", " #++++# ", "  ####  ", "   ##   ", "   ##   ", "  ####  ")
WALKER = ("  rrrr  ", " rrrrrr ", " #.##.# ", " #....# ", "  ####  ", " #+##+# ", "#.####.#", "  #..#  ", "  #  #  ", " ##  ## ")


def bubble(x, y, w, h, tail_x, tail_dir=1, fill=PAPER):
    """A speech bubble with its tail under it, pointing left (-1) or right (1)."""
    b = y + h
    return (f'<path d="M{x + 14} {y} H{x + w - 14} Q{x + w} {y} {x + w} {y + 14} V{b - 14} Q{x + w} {b} {x + w - 14} {b} '
            f'H{tail_x + 14} L{tail_x + 2 + 18 * tail_dir} {b + 26} L{tail_x - 4} {b} H{x + 14} Q{x} {b} {x} {b - 14} V{y + 14} Q{x} {y} {x + 14} {y}Z" '
            f'style="{fill};stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>')


def db(cx, y, w, h, fill=PAPER):
    """A database: a cylinder with two bands."""
    rx, ry = w / 2, w * 0.14
    side = f'<path d="M{cx - rx} {y} V{y + h} A{rx} {ry} 0 0 0 {cx + rx} {y + h} V{y}" style="{fill};stroke:var(--ink);stroke-width:5"/>'
    bands = "".join(f'<path d="M{cx - rx} {y + h * f:.0f} A{rx} {ry} 0 0 0 {cx + rx} {y + h * f:.0f}" style="fill:none;stroke:var(--ink);stroke-width:3"/>' for f in (0.33, 0.66))
    return side + bands + f'<ellipse cx="{cx}" cy="{y}" rx="{rx}" ry="{ry:.0f}" style="{fill};stroke:var(--ink);stroke-width:5"/>'


FIRE = ("   r   ", "  rr   ", "  rrr r", " rr.rrr", " r...rr", "rr...rr", "r.....r", " rrrrr ")


def commit_dots(mine, total, per, label, sub):
    """A share of commits: one dot per `per` commits, mine inked in, with the count under it."""
    n = math.ceil(total / per)
    cols = 10 if n <= 40 else 20
    gap = 380 / (cols - 1) if n > 40 else 38
    rad = min(13, gap * 0.36)
    return ("".join(dot(40 + (i % cols) * gap, 50 + (i // cols) * gap, rad) if i < round(mine / per) else ring(40 + (i % cols) * gap, 50 + (i // cols) * gap, rad * 0.8, 3) for i in range(n))
            + t(40, 250, label, 40, "display") + note(40, 284, sub))


def sr_tile(x, soft, label):
    """A crop of zigzag texture after 4× upscaling: blurred (as MSE leaves it) or crisp (as perceptual loss does)."""
    rows = "".join(ln(f"M{x + 8} {64 + k * 15} " + " ".join(f"l9 {-8 if q % 2 == 0 else 8}" for q in range(8)), 4) for k in range(5))
    blur = ' filter="url(#srgan-blur)"' if soft else ""
    return r(x, 50, 84, 84, PAPER, 4) + f"<g{blur}>{rows}</g>" + t(x + 42, 156, label, 14, "mono", "middle")


def envelope(x, y, w, h, fill=PAPER):
    return r(x, y, w, h, fill, 4, rx=3) + ln(f"M{x} {y} L{x + w / 2:.0f} {y + h * 0.6:.0f} L{x + w} {y}", 3)


def tick(x, y, s=1.0, colour="var(--art-win)"):
    return ln(f"M{x} {y} l{6 * s:.0f} {6 * s:.0f} l{12 * s:.0f} {-13 * s:.0f}", 4, colour=colour)


def key_icon(x, y, s=1.0, sw=5):
    k = lambda v: v * s
    return ring(x, y, k(16), sw) + ln(f"M{x + k(16):.0f} {y:.0f} H{x + k(70):.0f} M{x + k(50):.0f} {y:.0f} V{y + k(14):.0f} M{x + k(62):.0f} {y:.0f} V{y + k(12):.0f}", sw)


def drop(x, y, s=1.0, fill=SPOT):
    return f'<path d="M{x} {y} q{7 * s:.0f} {11 * s:.0f} 0 {16 * s:.0f} q{-7 * s:.0f} {-5 * s:.0f} 0 {-16 * s:.0f}Z" style="{fill};stroke:var(--ink);stroke-width:2"/>'


def branch(pts, w0, w1, fill="fill:var(--tone)"):
    """A tapering, crooked branch along a polyline: thick (w0) at the first point, thin (w1) at the last."""
    n = len(pts) - 1
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(0, i - 1)]
        bx, by = pts[min(n, i + 1)]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / n) / 2
        left.append((x - dy / d * w, y + dx / d * w))
        right.append((x + dy / d * w, y - dx / d * w))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left + right[::-1]) + "Z"
    return f'<path d="{d}" style="{fill};stroke:var(--ink);stroke-width:4;stroke-linejoin:round"/>'


def leaf(cx, cy, rot, s=1.0):
    return (f'<g transform="rotate({rot} {cx} {cy})"><path d="M{cx - 14 * s:.0f} {cy} Q{cx} {cy - 9 * s:.0f} {cx + 14 * s:.0f} {cy} Q{cx} {cy + 9 * s:.0f} {cx - 14 * s:.0f} {cy}Z" '
            f'style="fill:var(--paper);stroke:var(--ink);stroke-width:3"/>' + ln(f"M{cx - 12 * s:.0f} {cy} H{cx + 12 * s:.0f}", 1.5) + "</g>")


def pi_board(x, y, w=70, h=48, fill=PAPER, dash=None):
    """A small single-board computer: the board, its pin header, the chip."""
    return (r(x, y, w, h, fill, 4, dash=dash, rx=4) + "".join(dot(x + 8 + k * (w - 16) / 9, y + 7, 1.8) for k in range(10))
            + r(x + w * 0.38, y + h * 0.38, w * 0.26, h * 0.4, INK, 0))


def weather(cx, cy, kind):
    if kind == "sun":
        return ring(cx, cy, 9, 3) + "".join(ln(f"M{cx + 13 * math.cos(a):.0f} {cy + 13 * math.sin(a):.0f} L{cx + 18 * math.cos(a):.0f} {cy + 18 * math.sin(a):.0f}", 2.5) for a in [i * math.pi / 4 for i in range(8)])
    cloud = f'<path d="M{cx - 16} {cy + 6} a8 8 0 0 1 4 -14 a10 10 0 0 1 18 -2 a8 8 0 0 1 10 16z" style="fill:var(--paper);stroke:var(--ink);stroke-width:3"/>'
    if kind == "rain":
        return cloud + ln(f"M{cx - 8} {cy + 12} l-3 8 M{cx} {cy + 12} l-3 8 M{cx + 8} {cy + 12} l-3 8", 2.5)
    if kind == "snow":
        return cloud + "".join(dot(cx + d, cy + 16, 2.2) for d in (-8, 0, 8))
    return cloud


def disk(cx, cy, rad):
    return ring(cx, cy, rad, 5) + ring(cx, cy, rad * 0.66, 1.5, "fill:none", "4 5") + ring(cx, cy, rad * 0.33, 1.5, "fill:none", "4 5")


def vinyl(cx, cy, rad, grooves=4):
    """A record: grooves, a red label, the spindle hole."""
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rad * (0.48 + 0.44 * i / max(1, grooves - 1)):.1f}"/>' for i in range(grooves))
    return (ring(cx, cy, rad, 5, INK) + f'<g style="fill:none;stroke:var(--paper);stroke-width:1.5">{rings}</g>'
            + ring(cx, cy, rad * 0.32, 4, SPOT) + dot(cx, cy, max(2.5, rad * 0.05), PAPER))


def sleeve_sq(x, y, s, fill=PAPER):
    """A square record sleeve, with a band across the top like the site's sleeves."""
    return r(x, y, s, s, fill, 5) + f'<rect x="{x + 5:.0f}" y="{y + 5:.0f}" width="{s - 10:.0f}" height="{s * 0.14:.0f}" style="{INK}"/>'


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
    cur = (motion("@keyframes tm-c{0%,55%{opacity:1}56%,100%{opacity:0}}.tm-c{animation:tm-c 1.6s step-end infinite}")
           + f'<rect class="mv tm-c" x="{x + 16}" y="{y + 40 + len(lines) * 22}" width="10" height="16" style="{SPOT}"/>') if cursor else ""
    return r(x, y, w, h, INK, 5, rx=6) + ln(f"M{x} {y + 24} H{x + w}", 2, colour="var(--paper)") + dot(x + 14, y + 12, 4, PAPER) + dot(x + 28, y + 12, 4, PAPER) + body + cur



def arm2():
    """A two-joint arm reaching round an obstacle to the goal: the robot-learning coursework. A slow loop, still under reduced motion."""
    bx, by, l1, l2 = 110, 250, 120, 100
    # joint angles (degrees) at each keyframe, from inverse kinematics of the hand path drawn below
    keys = [(-100.3, 135.8), (-94.7, 97.4), (-70.5, 72.3), (-49.2, 64.2), (-34.7, 70.3)]
    times = [0, 22, 45, 68, 88]
    def frames(i):
        f = "".join(f"{t}%{{transform:rotate({k[i]}deg)}}" for t, k in zip(times, keys))
        return f + f"100%{{transform:rotate({keys[-1][i]}deg)}}"
    css = (f"@keyframes arm2a{{{frames(0)}}}@keyframes arm2b{{{frames(1)}}}"
           f".arm2-s{{transform-origin:{bx}px {by}px;transform:rotate({keys[-1][0]}deg);animation:arm2a 7s ease-in-out infinite alternate}}"
           f".arm2-e{{transform-origin:{bx + l1}px {by}px;transform:rotate({keys[-1][1]}deg);animation:arm2b 7s ease-in-out infinite alternate}}"
           "@media (prefers-reduced-motion: reduce){.arm2-s,.arm2-e{animation:none}}")
    path = ln("M170 190 C175 150 185 135 200 135 S240 132 250 140 S282 165 285 185 S290 225 290 240", 3, "5 8", "var(--muted)")
    return (f"<style>{css}</style>" + ln("M40 270 H410", 6) + r(178, 220, 34, 50, INK, 5)
            + ring(290, 240, 16, 5, SPOT) + path
            + r(bx - 40, by, 80, 20, INK, 5)
            + f'<g class="arm2-s">' + ln(f"M{bx} {by} H{bx + l1}", 14)
            + f'<g class="arm2-e">' + ln(f"M{bx + l1} {by} H{bx + l1 + l2}", 11) + dot(bx + l1 + l2, by, 9, SPOT) + "</g>"
            + ring(bx + l1, by, 10, 5) + "</g>" + ring(bx, by, 12, 5, INK))


ART = {
    # --- this website ---
    # the record's three stops: half out of its sleeve on the cover, one sleeve of many on the shelf (breaking into
    # screentone where it's clicked), and on the deck in the volume with the tonearm down
    "vinyl": lambda: (vinyl(118, 128, 54) + sleeve_sq(14, 76, 104) + t(66, 150, "♪", 30, "display", "middle")
                      + "".join(sleeve_sq(188 + (i % 2) * 56, 76 + (i // 2) * 56, 48) for i in range(3))
                      + "".join(dot(258 + 34 * seed("vy", i), 86 + 34 * seed("vy", i + 9), 1.5 + 3.5 * seed("vy", i + 30)) for i in range(26))
                      + turning_vinyl(362, 132, 60, 4, 16, "vy-spin") + ln("M432 52 L428 92 L392 148", 7) + r(420, 40, 24, 24, PAPER, 5, rx=12) + r(385, 141, 16, 12, INK, 0)
                      + note(66, 270, "cover", "middle") + note(240, 270, "contents", "middle") + note(362, 270, "volume", "middle")),
    # the record at the tempo of the song: a worker asks Spotify what's on and finds its beats per minute
    "nowplaying": lambda: (turning_vinyl(140, 150, 112, 5, 12, "np-spin") + ln("M140 22 A128 128 0 0 1 266 132", 4, "6 8", "var(--muted)") + arrow(258, 112, 266, 136, 4)
                           + t(345, 128, "118", 54, "display", "middle") + note(345, 156, "bpm", "middle")
                           + bars(296, 196, 100, 36, [0.5, 1, 0.5, 1, 0.5, 1, 0.5, 1], 5, hi=1)
                           + note(345, 270, "live, from Spotify", "middle")),
    # --- the model deployment platform (Tencent) ---
    "commits": lambda: ("".join(dot(52 + (i % 11) * 32, 70 + (i // 11) * 32, 11) if i < 45 else ring(52 + (i % 11) * 32, 70 + (i // 11) * 32, 9, 3) for i in range(55))
                        + t(40, 250, "450 / 550", 40, "display") + note(40, 284, "commits, Mar–Sep 2026")),
    "racks": lambda: (motion("@keyframes rk-g{0%,100%{opacity:0}50%{opacity:.45}}.rk-g{opacity:.2;animation:rk-g 4s ease-in-out infinite}")
                      + f'<circle class="mv rk-g" cx="122" cy="103" r="10" style="{SPOT}"/><circle class="mv rk-g" cx="257" cy="168" r="10" style="{SPOT};animation-delay:-2s"/>'
                      + server(40, 50, 100, 200, 6, (1,)) + server(175, 30, 100, 220, 7, (4,)) + server(310, 50, 100, 200, 6)
                      + ln("M20 262 H430", 6) + note(225, 290, "1,000+ GPUs' worth of serving", "middle")),
    "clock": lambda: (hands(120, 150, 92, 40, "ck")
                      + bars(240, 60, 180, 150, [0.2, 0.25, 0.6, 0.95, 1, 0.9, 0.5, 0.25], 6, hi=4) + ln("M232 214 H428", 4)
                      + note(330, 244, "replicas, by hour", "middle")),
    "lock": lambda: ("".join(r(30, 30 + i * 84, 110, 56, PAPER, 4) + t(85, 64 + i * 84, f"replica {i + 1}", 13, "mono", "middle") for i in range(3))
                     + arrow(146, 58, 268, 140) + arrow(146, 142, 268, 152, dash="8 7") + arrow(146, 226, 268, 164, dash="8 7")
                     + r(278, 110, 150, 84, PAPER, 5) + t(353, 140, "execution log", 13, "mono", "middle") + r(292, 154, 122, 22, SPOT, 3)
                     + t(353, 170, "UNIQUE", 13, "mono", "middle", ONSPOT) + stamp(200, 260, "duplicate key: skip", -4, 15, kind="mono")),
    "twostep": lambda: (motion("@keyframes ts-a{0%{transform:scaleX(0)}20%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
                               "@keyframes ts-b{0%,45%{transform:scaleX(0)}60%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}"
                               ".ts-a,.ts-b{transform-box:fill-box;transform-origin:left;animation:ts-a 11s ease-in-out infinite}.ts-b{animation-name:ts-b}")
                        + r(40, 70, 370, 50, PAPER, 5) + '<g class="mv ts-a">' + r(40, 70, 296, 50, INK, 5) + "</g>" + t(188, 104, "80%", 24, "display", "middle", PAPER)
                        + note(40, 52, "first: most of it, wait until ready")
                        + r(40, 190, 370, 50, INK, 5) + '<g class="mv ts-b">' + r(336, 190, 74, 50, SPOT, 5) + "</g>" + note(40, 172, "then: the rest")
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
                      + note(225, 220, "one ID, every call", "middle")
                      + motion("@keyframes tr-h{0%,16%{transform:translateX(0)}25%,41%{transform:translateX(110px)}50%,66%{transform:translateX(220px)}75%,91%{transform:translateX(330px)}100%{transform:translateX(0)}}"
                               ".tr-h{animation:tr-h 9s ease-in-out infinite}")
                      + f'<g class="mv tr-h">{dot(60, 110, 8, SPOT)}</g>'),
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
                       + motion("@keyframes sk-f{0%,100%{opacity:.4}8%{opacity:1}30%{opacity:.4}}.sk-f{animation:sk-f 5s ease-out infinite}")
                       + "".join(f'<g class="mv sk-f" style="animation-delay:{5 * seed("sw", j):.2f}s">' + ln(f"M{40 + 360 * seed('sw', j):.0f} {50 + 5 * 36} v20", 4, colour="var(--live-red)") + "</g>" for j in range(12))
                       + ln("M40 250 H410", 3) + note(40, 280, "winner takes all")),
    "motionface": lambda: ("".join(dot(225 + 95 * math.cos(a) * (0.8 + 0.2 * seed("f", k)), 150 + 120 * math.sin(a) * (0.8 + 0.2 * seed("g", k)), 3) for k, a in enumerate(i / 60 * 2 * math.pi for i in range(60)))
                           + "".join(dot(190 + 70 * (k % 2) + 10 * seed("e", k), 120 + 6 * seed("e2", k), 3) for k in range(14))
                           + "".join(dot(205 + 40 * seed("m", k), 200 + 5 * seed("m2", k), 3, SPOT) for k in range(10))
                           + note(225, 290, "only what moved", "middle")),
    "federated": lambda: (server(185, 30, 80, 110, 3) + "".join(laptop(30 + i * 150, 210, 90) + arrow(75 + i * 150, 200, 225 - (1 - i) * 30, 150, 4, "7 6") for i in range(3))),
    # --- KURF ---
    "arm2": arm2,
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
    # --- the FPS agent ---
    # imitation: the copy does what it saw, with no idea why
    "imitate": lambda: (monkey(110, 96) + monkey(340, 96, 1, SPOT) + arrow(170, 120, 276, 120, 4, "7 7") + note(223, 104, "copies the move", "middle")
                        + t(392, 52, "?", 30, "display", "middle") + note(110, 250, "monkey see", "middle") + note(340, 250, "monkey do", "middle")),
    # three laptops and the game: what each one hands on
    "split": lambda: (laptop(20, 50, 100) + laptop(175, 50, 100) + laptop(330, 50, 100)
                      + t(70, 92, "GSI", 16, "mono", "middle") + t(225, 96, "θ", 24, "display", "middle")
                      + ring(380, 81, 13, 3, "fill:none") + ln("M380 63 V99 M362 81 H398", 3, colour="var(--live-red)")
                      + t(70, 142, "SPECTATOR", 15, "display", "middle") + t(225, 142, "AGENT", 15, "display", "middle") + t(380, 142, "PLAYER", 15, "display", "middle")
                      + note(70, 160, "sees everything", "middle") + note(225, 160, "learns", "middle") + note(380, 160, "YOLOv5 enemies", "middle")
                      + arrow(124, 74, 171, 74, 4) + note(148, 38, "full state", "middle") + arrow(279, 74, 326, 74, 4) + note(302, 38, "actions", "middle")
                      + r(160, 210, 130, 60, INK, 5) + t(225, 248, "CS:GO", 22, "display", "middle", PAPER)
                      + arrow(160, 228, 92, 172, 4) + note(20, 215, "game state") + arrow(380, 172, 292, 228, 4) + note(430, 215, "mouse, keys", "end")),
    # the critic stands in the open and sees the sun; the actor's view is blocked by a hill
    "asymmetry": lambda: (ring(225, 82, 26, 5) + "".join(ln(f"M{225 + 34 * math.cos(a):.0f} {82 + 34 * math.sin(a):.0f} L{225 + 46 * math.cos(a):.0f} {82 + 46 * math.sin(a):.0f}", 4) for a in [i * math.pi / 4 for i in range(8)])
                          + '<path d="M250 270 C272 80 348 80 370 270" style="fill:var(--tone);stroke:var(--ink);stroke-width:5"/>' + ln("M10 270 H440", 6)
                          + person(75, 205, 1.3) + person(398, 205, 1.3, SPOT)
                          + ln("M86 196 L192 104", 3, "6 6") + ln("M388 198 L342 162", 3, "6 6") + cross(338, 158, 10, 5)
                          + t(20, 40, "critic", 20, "display") + note(20, 62, "sees it all")
                          + t(430, 40, "actor", 20, "display", "end") + note(430, 62, "a player's view", "end")),
    # a sparse reward: nothing for every step, then +1 for a win or −1 for a loss at the round's end
    "sparse": lambda: ("".join("".join(dot(40 + j * 16, 44 + i * 42, 2, MUTED) for j in range(int((e - 40) // 16)))
                               + dot(e, 44 + i * 42, 13, "fill:var(--art-win)" if w else "fill:var(--art-loss)") + t(e + 22, 49 + i * 42, "+1" if w else "−1", 15, "mono")
                               for i, (e, w) in enumerate(((330, 1), (260, 0), (380, 0), (300, 1), (220, 0))))
                       + note(40, 270, "0 every step, then +1 for a win or −1 for a loss")),
    # what it learnt: keep moving, so the bot's slow aim lands where it was, and fire now and then to make it wary
    "exploit": lambda: (ln("M170 240 L215 200 L195 160 L250 128 L282 176 L322 148", 4, "8 7", "var(--muted)")
                        + "".join(ring(x, y, 11, 3, "fill:none", "4 4") for x, y in ((215, 200), (195, 160), (250, 128), (282, 176)))
                        + ln("M80 170 L246 129", 3, "4 6") + ring(80, 170, 18, 5, INK) + ln("M80 170 L104 164", 7)
                        + "".join(ln(f"M{322 - 242 * f:.0f} {148 + 22 * f:.0f} L{322 - 242 * (f + 0.05):.0f} {148 + 22 * (f + 0.05):.0f}", 4, colour="var(--live-red)") for f in (0.14, 0.26, 0.38))
                        + ring(322, 148, 13, 5, SPOT) + clockface(392, 64, 30, 0, 50, 8)
                        + note(80, 210, "bot: slow aim", "middle") + note(330, 186, "keep moving") + note(392, 116, "run the clock", "middle")
                        + stamp(355, 255, "39 / 100", -6, 20, kind="display")),
    # --- BlockHub ---
    # the pitch: the team of six round a table, and me standing with the idea
    "pitch": lambda: ('<path d="M50 230 A150 30 0 0 1 350 230 A150 30 0 0 1 50 230Z" style="fill:var(--tone);stroke:var(--ink);stroke-width:5"/>'.join(
                          ["".join(person(90 + i * 60, 168, 1.0) for i in range(5)), ""])
                      + ln("M80 236 V278 M320 236 V278", 6)
                      + r(110, 128, 34, 22, PAPER, 3, rx=8) + t(127, 144, "…", 14, "mono", "middle") + r(266, 128, 34, 22, PAPER, 3, rx=8) + t(283, 144, "?", 14, "mono", "middle")
                      + ring(400, 108, 16, 5, SPOT) + r(386, 128, 28, 74, SPOT, 5, rx=10) + ln("M392 200 V276 M408 200 V276", 7) + ln("M388 140 L362 112 M412 140 L424 176", 6)
                      + ring(400, 52, 15, 4) + r(393, 66, 14, 10, INK, 0) + ln("M396 80 H404", 3)
                      + "".join(ln(f"M{400 + 22 * math.cos(a):.0f} {52 + 22 * math.sin(a):.0f} L{400 + 31 * math.cos(a):.0f} {52 + 31 * math.sin(a):.0f}", 3) for a in [math.pi * (1 + i / 4) for i in range(5)])),
    # --- carbon-coin ---
    # the demo, built in a day: a rough window taped up, placeholder boxes, a scanner that's only a concept
    "rough": lambda: ('<g transform="rotate(-2 225 150)">' + r(34, 34, 382, 224, PAPER, 5, rx=4) + ln("M34 60 H416", 4) + dot(50, 47, 4) + dot(64, 47, 4) + dot(78, 47, 4)
                      + "".join(r(52, 76 + i * 40, 26, 26, PAPER, 3) + ln(f"M52 {76 + i * 40} l26 26 M78 {76 + i * 40} l-26 26", 2)
                                + f'<rect x="90" y="{82 + i * 40}" width="{70 + 60 * seed("rough", i):.0f}" height="6" style="{INK}"/>'
                                + f'<rect x="90" y="{94 + i * 40}" width="{40 + 30 * seed("rough", i + 5):.0f}" height="4" style="{MUTED}"/>'
                                + r(214, 78 + i * 40, 40, 20, PAPER, 3) for i in range(4))
                      + r(282, 76, 116, 150, "fill:none", 4, dash="8 7") + ln("M310 120 H370 M310 120 V108 M370 120 V108 M310 180 H370 M310 180 V192 M370 180 V192", 4)
                      + ln("M300 150 H380", 3, colour="var(--live-red)") + t(340, 214, "concept", 12, "mono", "middle", MUTED) + "</g>"
                      + '<rect x="12" y="24" width="64" height="20" transform="rotate(-28 44 34)" style="fill:var(--tone);opacity:.85"/>'
                      + '<rect x="372" y="246" width="64" height="20" transform="rotate(-24 404 256)" style="fill:var(--tone);opacity:.85"/>'
                      + stamp(118, 270, "built in a day", -4, 15, kind="mono")),
    # --- this website, continued ---
    # the site before this one: a little black-and-white pixel town, walked round like an old handheld game
    "pixeltown": lambda: ('<rect x="207" y="96" width="36" height="128" style="fill:var(--tone)"/>'
                          + "".join(pix(30 + 400 * seed("grass", i), 20 + 190 * seed("grass", i + 50), 4, ("# #", " # ")) for i in range(28)
                                    if not (140 < 30 + 400 * seed("grass", i) < 300 and 20 + 190 * seed("grass", i + 50) < 110) and not (195 < 30 + 400 * seed("grass", i) < 250))
                          + pix(153, 24, 6, HOUSE) + pix(40, 40, 6, TREE) + pix(92, 108, 6, TREE) + pix(352, 30, 6, TREE) + pix(312, 120, 6, TREE)
                          + pix(201, 150, 6, WALKER)
                          + r(12, 226, 426, 64, PAPER, 5, rx=4) + r(19, 233, 412, 50, "fill:none", 2, rx=2)
                          + t(34, 264, "Welcome! Have a look around.", 16, "mono") + pix(408, 266, 3, ("#####", " ### ", "  #  "))),
    # its two rooms, as a house plan
    "houseplan": lambda: (ln("M180 262 H40 V38 H410 V262 H250", 7) + ln("M225 38 V120 M225 172 V262", 6)
                          + t(132, 84, "poems", 22, "mono", "middle") + "".join(f'<rect x="80" y="{110 + i * 22}" width="{60 + 40 * seed("poem", i):.0f}" height="5" style="{INK}"/>' for i in range(5))
                          + t(318, 84, "CS:GO", 22, "mono", "middle") + ring(318, 170, 34, 4, "fill:none") + ln("M318 124 V216 M272 170 H364", 4)
                          + arrow(215, 296, 215, 236, 5) + dot(215, 222, 10, SPOT)),
    # the series: four books, one per reader, the cover first
    "series": lambda: ("".join(r(50 + i * 92, 40 + (i % 2) * 6, 74, 204 - (i % 2) * 6, SPOT if i == 0 else PAPER, 5)
                               + f'<rect x="{56 + i * 92}" y="{48 + (i % 2) * 6}" width="62" height="18" style="{INK}"/>'
                               + "".join(t(87 + i * 92, 104 + j * 34, ch, 28, "body", "middle", ONSPOT if i == 0 else INK) for j, ch in enumerate(k))
                               + t(87 + i * 92, 226, str(i + 1), 18, "display", "middle", ONSPOT if i == 0 else INK)
                               + note(87 + i * 92, 274, w, "middle")
                               for i, (k, w) in enumerate(zip(("表紙", "作者", "目次", "奥付"), ("the hook", "the brief", "in depth", "the footnote"))))
                       + ln("M30 250 H420", 6)),
    # one source of truth: the bank held up high, and what it lights: the site and three CVs
    "truth": lambda: ("<style>@keyframes sot-tw{0%,100%{opacity:.25}50%{opacity:.9}}.sot-tw{animation:sot-tw 4s ease-in-out infinite}"
                      ".sot-tw:nth-of-type(2){animation-delay:1.3s}.sot-tw:nth-of-type(3){animation-delay:2.6s}"
                      "@media (prefers-reduced-motion: reduce){.sot-tw{animation:none;opacity:.7}}</style>"
                      + '<defs><radialGradient id="sot-glow"><stop offset="0" style="stop-color:var(--art-glow);stop-opacity:.75"/>'
                        '<stop offset=".45" style="stop-color:var(--art-glow);stop-opacity:.25"/><stop offset="1" style="stop-color:var(--art-glow);stop-opacity:0"/></radialGradient></defs>'
                      + '<circle cx="230" cy="60" r="70" fill="url(#sot-glow)"/>'
                      + "<g>" + "".join(f'<path class="sot-tw" d="M{x} {y - k} Q{x} {y} {x + k} {y} Q{x} {y} {x} {y + k} Q{x} {y} {x - k} {y} Q{x} {y} {x} {y - k}Z" style="fill:var(--art-glow)"/>'
                                        for x, y, k in ((196, 44, 9), (266, 30, 7), (258, 92, 6))) + "</g>"
                      + person(110, 190, 1.6) + branch(((146, 262), (160, 228), (174, 196), (178, 172), (194, 140), (204, 112), (216, 88), (230, 60)), 24, 7) + branch(((180, 166), (164, 146), (150, 128), (130, 116)), 9, 3) + branch(((152, 132), (146, 112), (140, 96)), 6, 2) + leaf(120, 112, 30) + leaf(138, 86, 70, 0.9) + '<ellipse cx="170" cy="210" rx="4" ry="8" transform="rotate(22 170 210)" style="fill:var(--ink)"/>' + ln("M160 246 l5 -12 M182 170 l4 -9 M208 106 l4 -10", 2) + ln("M124 222 L175 190", 6)
                      + note(180, 28, "the bank", "end")
                      + r(300, 36, 120, 44, PAPER, 4) + t(360, 64, "site", 16, "mono", "middle") + r(300, 104, 120, 44, PAPER, 4) + t(360, 132, "CV ×3", 16, "mono", "middle")
                      + arrow(270, 60, 294, 58, 3, "5 5") + arrow(262, 82, 294, 118, 3, "5 5")
                      + stamp(360, 214, "no leaks", -6, 18, kind="mono")),
    # ship it: a small, cheerful cargo ship carrying the site and the CVs
    "ship": lambda: ("<style>@keyframes puff{0%{transform:translate(0,0);opacity:1}100%{transform:translate(14px,-16px);opacity:0}}"
                     ".puff{animation:puff 3s ease-out infinite}.puff:nth-child(2){animation-delay:1s}.puff:nth-child(3){animation-delay:2s}"
                     "@media (prefers-reduced-motion: reduce){.puff{animation:none}}</style>"
                     + r(345, 112, 30, 78, PAPER, 5) + r(345, 112, 30, 14, SPOT, 5)
                     + "<g>" + "".join(f'<g class="puff">{ring(368 + 16 * i, 92 - 20 * i, 8 + 3 * i, 4)}</g>' for i in range(3)) + "</g>"
                     + r(90, 150, 80, 40, INK, 5) + t(130, 176, "site", 15, "mono", "middle", PAPER)
                     + "".join(r(175 + i * 55, 150, 50, 40, PAPER, 5) + t(200 + i * 55, 176, "CV", 15, "mono", "middle") for i in range(3))
                     + ln("M100 150 V108", 4) + '<path d="M100 108 L128 116 L100 124Z" style="fill:var(--live-red)"/>'
                     + '<path d="M54 190 H396 L362 244 H92Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>'
                     + dot(140, 210, 5) + dot(170, 210, 5) + ln("M146 222 Q155 230 164 222", 3) + dot(128, 222, 6, "fill:var(--live-edge);opacity:.6") + dot(182, 222, 6, "fill:var(--live-edge);opacity:.6")
                     + ln("M20 252 q20 -12 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0", 4)
                     + ln("M40 270 q20 -10 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0", 3, colour="var(--muted)")
                     + note(225, 294, "a push deploys", "middle")),
    # --- terminel ---
    # the idea: a terminal in the browser, and the first thing anyone runs in one
    "hello": lambda: (terminal(40, 20, 370, 180, ('> print("Hello World")', "Hello World")) + "".join(r(60 + i * 58, 220, 48, 44, PAPER, 4, rx=6) + t(84 + i * 58, 249, k, 15, "mono", "middle") for i, k in enumerate(("j", "k", "a", "d", "q", "↵")))),
    # the hard part: fine on my machine; live, the serverless function buckles under the Python
    "serverless": lambda: (laptop(30, 70, 150) + ln("M80 118 L98 136 L132 98", 7, colour="var(--art-win)") + note(105, 196, "my machine", "middle")
                           + r(262, 96, 160, 62, INK, 5) + t(342, 136, "python", 20, "mono", "middle", PAPER)
                           + '<path d="M290 160 H394 L388 212 H296Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>' + t(342, 198, "λ", 30, "display", "middle")
                           + ln("M282 176 l-12 -4 M282 194 l-14 2 M402 176 l12 -4 M402 194 l14 2", 3)
                           + '<path d="M410 228 q6 10 0 14 q-6 -4 0 -14Z" style="fill:var(--tone);stroke:var(--ink);stroke-width:2"/>'
                           + ln("M250 214 H440", 6) + note(342, 238, "live", "middle")
                           + stamp(225, 276, "fix5 · fix6", -3, 16, kind="mono")),
    # --- German Learning Hub ---
    # the same question twice, in English and in German
    "translate": lambda: (bubble(20, 40, 190, 92, 60, -1) + t(115, 82, "Where is the", 17, "mono", "middle") + t(115, 106, "station?", 17, "mono", "middle")
                          + bubble(240, 40, 190, 92, 390, 1, SPOT) + t(335, 82, "Wo ist der", 17, "mono", "middle", ONSPOT) + t(335, 106, "Bahnhof?", 17, "mono", "middle", ONSPOT)
                          + arrow(196, 160, 254, 160, 4) + t(60, 196, "EN", 22, "display", "middle") + t(390, 196, "DE", 22, "display", "middle")
                          + note(225, 262, "screenshot → OCR → lines → translation", "middle")),
    # --- 9Loop, continued ---
    # the database, before and after: a change designed in, in red
    "dbchange": lambda: (db(110, 100, 110, 120) + db(340, 100, 110, 120)
                         + '<path d="M285 60 V100 A55 15 0 0 0 395 100 V60" style="fill:var(--live-red);stroke:var(--ink);stroke-width:5"/>'
                         + '<ellipse cx="340" cy="60" rx="55" ry="15" style="fill:var(--live-red);stroke:var(--ink);stroke-width:5"/>'
                         + arrow(180, 160, 270, 160, 5) + note(225, 146, "redesigned", "middle") + note(410, 64, "new", "start")
                         + note(110, 270, "before", "middle") + note(340, 270, "after", "middle")),
    # --- the DGL coursework ---
    # from scratch: a sheet of paper with a graph sketched on it, a pencil, an eraser and its crumbs
    "scratch": lambda: ('<g transform="rotate(-4 170 150)">' + r(40, 30, 250, 240, PAPER, 5)
                        + "".join(ln(f"M{x1} {y1} L{x2} {y2}", 3) for x1, y1, x2, y2 in ((100, 90, 170, 70), (100, 90, 120, 170), (170, 70, 230, 120), (120, 170, 230, 120), (120, 170, 190, 220)))
                        + "".join(ring(x, y, 12, 4) for x, y in ((100, 90), (170, 70), (120, 170), (230, 120), (190, 220)))
                        + ln("M215 200 L262 228", 3, "3 5", "var(--muted)") + ring(262, 228, 12, 3, "fill:none", "3 5") + "</g>"
                        + '<g transform="rotate(38 360 150)">' + r(340, 20, 30, 200, "fill:var(--tone)", 5) + r(340, 20, 30, 24, SPOT, 5)
                        + '<path d="M340 220 L355 262 L370 220Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>' + dot(355, 254, 5) + "</g>"
                        + '<g transform="rotate(-14 352 244)">' + r(310, 222, 84, 40, PAPER, 5, rx=6) + r(310, 222, 30, 40, INK, 5, rx=6) + "</g>"
                        + "".join(dot(296 + 30 * seed("crumb", i), 270 + 18 * seed("crumb", i + 9), 2 + 2 * seed("crumb", i + 20), MUTED) for i in range(7))),
    # --- IC Hack 25 ---
    # the game: an office maze on fire, in pixels, and the act the LLM is writing
    "firegame": lambda: (r(14, 14, 422, 186, PAPER, 6) + ln("M120 14 V110 M220 74 V200 M320 14 V120 M14 150 H160 M270 160 H436", 6)
                         + motion("@keyframes fg-f{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}.fg-f{animation:fg-f 1.4s steps(1,end) infinite}")
                         + "".join(f'<g class="mv fg-f" style="animation-delay:-{d}s">{pix(x, y, 4, FIRE)}</g>' for x, y, d in ((240, 26, 0), (270, 40, .7), (356, 150, .35), (150, 160, 1.05), (388, 160, .5)))
                         + pix(56, 96, 4, WALKER) + r(370, 28, 56, 24, "fill:var(--art-win)", 4) + t(398, 46, "EXIT", 14, "mono", "middle", PAPER)
                         + r(14, 212, 422, 76, PAPER, 5, rx=4) + t(32, 240, "ACT 2", 14, "display") + t(32, 268, "Someone is calling for help.", 16, "mono")),
    # scoring you: your answer, embedded among reference actions with known Big Five levels; the nearest one counts
    "embed": lambda: (ring(225, 150, 120, 2, "fill:none", "4 7")
                      + "".join(ring(225 + 110 * math.cos(a), 150 + 100 * math.sin(a), 22, 4) + t(225 + 110 * math.cos(a), 157 + 100 * math.sin(a), k, 18, "display", "middle")
                                for k, a in zip("OCEAN", [math.pi * (-0.5 + 0.4 * i) for i in range(5)]))
                      + ln(f"M262 104 L{225 + 110 * math.cos(-0.1 * math.pi) - 18:.0f} {150 + 100 * math.sin(-0.1 * math.pi) + 6:.0f}", 4, "6 5") + dot(262, 104, 12, SPOT) + note(250, 84, "your answer", "end")
                      + note(225, 290, "nearest by similarity", "middle")),
    # the reading: the Big Five sheet, printed for the interviewer
    "bigfive": lambda: (r(110, 20, 230, 262, PAPER, 5) + t(130, 56, "Big Five", 20, "display") + r(282, 34, 44, 22, INK, 0) + t(304, 50, "PDF", 13, "mono", "middle", PAPER)
                        + "".join(t(134, 104 + i * 38, k, 18, "display", "middle") + r(152, 88 + i * 38, 168, 20, "fill:none", 3)
                                  + f'<rect x="152" y="{88 + i * 38}" width="{168 * v:.0f}" height="20" style="{SPOT if i == 2 else INK}"/>'
                                  for i, (k, v) in enumerate(zip("OCEAN", (0.7, 0.55, 0.85, 0.6, 0.4))))),
    "hackcommits": lambda: commit_dots(42, 97, 1, "42 / 97", "commits, Feb 2025: the most in the team"),
    # --- robot-learning coursework ---
    # the methods in the order the coursework took them: random play, a learnt model, replanning, cloning
    "methods": lambda: ("".join(r(x, y, 205, 128, PAPER, 4, rx=6) + t(x + 14, y + 26, str(i + 1), 18, "display") + note(x + 102, y + 116, lab, "middle")
                                for i, (x, y, lab) in enumerate(((15, 12, "random play"), (230, 12, "a learnt model"), (15, 158, "replan every step"), (230, 158, "copy the demos"))))
                        + "".join(ln(f"M100 66 L{100 + 52 * math.cos(a):.0f} {66 + 34 * math.sin(a):.0f}", 3, "3 4") + dot(100 + 52 * math.cos(a), 66 + 34 * math.sin(a), 4) for a in [6.283 * seed("rp", i) for i in range(9)]) + dot(100, 66, 7, SPOT)
                        + r(292, 40, 82, 46, INK, 4, rx=6) + t(333, 69, "f", 20, "display", "middle", PAPER) + note(282, 68, "s, a", "end") + arrow(376, 63, 404, 63, 3) + t(410, 68, "s′", 15, "mono")
                        + ring(176, 196, 10, 4, SPOT) + ln("M40 240 Q70 236 92 220 T150 204 L170 198", 4) + "".join(dot(x, y, 4) for x, y in ((66, 237), (92, 220), (122, 211), (150, 204)))
                        + ln("M40 240 Q90 232 130 236 T200 252", 3, "6 6", "var(--muted)")
                        + ln("M256 240 Q300 200 340 214 T408 186", 4, "8 7", "var(--muted)") + ln("M256 244 Q300 206 340 220 T408 192", 4) + person(392, 172, 0.6) ),
    # --- plate recognition ---
    # scarce data: three short stacks of images in a tray built for far more (each plate ≈ 20 images)
    "scarce": lambda: (r(20, 20, 410, 200, "fill:none", 3, dash="9 8") + note(225, 48, "room for a lot more", "middle")
                       + "".join(r(x0 + (i % 5) * 24, 196 - (i // 5) * 14, 20, 10, fill, 2) for x0, n, fill in ((40, 8, SPOT), (170, 20, PAPER), (310, 3, INK)) for i in range(n))
                       + note(100, 244, "168 Malaysian", "middle") + note(230, 244, "400+ foreign", "middle") + note(370, 244, "60 negatives", "middle")
                       + note(225, 282, "each plate ≈ 20 images", "middle")),
    # the weak stage: finding the plate gets you halfway across; reading it is where the bridge gives out
    "bridge": lambda: ('<path d="M0 160 H140 L150 300 H0Z" style="fill:var(--tone);stroke:var(--ink);stroke-width:5"/>'
                       + '<path d="M450 160 H310 L300 300 H450Z" style="fill:var(--tone);stroke:var(--ink);stroke-width:5"/>'
                       + '<path d="M140 160 H200 L192 168 L204 174 H140Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:4;stroke-linejoin:round"/>'
                       + '<path d="M310 160 H262 L270 167 L258 174 H310Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:4;stroke-linejoin:round"/>'
                       + ln("M140 128 L198 136 M310 128 L264 138", 3) + ln("M150 160 V128 M180 160 V132 M300 160 V128 M276 160 V134", 3)
                       + '<rect x="216" y="206" width="34" height="10" transform="rotate(28 233 211)" style="fill:var(--paper);stroke:var(--ink);stroke-width:3"/>'
                       + '<rect x="228" y="252" width="30" height="10" transform="rotate(-36 243 257)" style="fill:var(--paper);stroke:var(--ink);stroke-width:3"/>'
                       + t(70, 84, "find", 24, "display", "middle") + t(70, 124, "0.96", 26, "mono", "middle")
                       + t(380, 84, "read", 24, "display", "middle") + t(380, 124, "0.26", 26, "mono", "middle", SPOT)),
    # --- BlockHub, continued ---
    # the platform: projects ranked by contributors' on-chain votes; a major contributor gets a certificate
    "platform": lambda: ("".join(r(20, 30 + i * 62, 230, 50, SPOT if i == 0 else PAPER, 4, rx=6) + t(40, 62 + i * 62, f"#{i + 1}", 18, "display", fill=ONSPOT if i == 0 else INK)
                                 + "".join(f'<circle cx="{x}" cy="{y + i * 62}" r="4" style="fill:none;stroke:var({"--live-on-red" if i == 0 else "--ink"});stroke-width:2.5"/>' for x, y in ((92, 46), (92, 66), (110, 46)))
                                 + ln(f"M92 {50 + i * 62} V{62 + i * 62} M110 {50 + i * 62} Q110 {58 + i * 62} 96 {62 + i * 62}", 2.5, colour="var(--live-on-red)" if i == 0 else "var(--ink)")
                                 + "".join(dot(140 + k * 14, 55 + i * 62, 4.5, ONSPOT if i == 0 else INK) for k in range(6 - 2 * i))
                                 for i in range(3))
                         + note(135, 234, "ranked by votes", "middle")
                         + r(290, 50, 140, 110, PAPER, 5) + t(360, 84, "certificate", 13, "mono", "middle") + ln("M312 100 H408 M312 114 H380", 3)
                         + ring(400, 150, 20, 5, SPOT) + '<path d="M390 166 L384 194 L400 186 L416 194 L410 166" style="fill:var(--live-red);stroke:var(--ink);stroke-width:4;stroke-linejoin:round"/>'
                         + note(360, 234, "Polygon ID", "middle")),
    # --- task tracker ---
    # the brief: the team's requirements, turned into a design, built, and used by them
    "brief": lambda: (r(20, 46, 110, 150, PAPER, 5, rx=4) + r(52, 36, 46, 18, INK, 0, rx=4) + t(75, 80, "needs", 13, "mono", "middle")
                      + "".join(dot(38, 102 + i * 24, 3) + f'<rect x="48" y="{99 + i * 24}" width="{50 + 20 * seed("brief", i):.0f}" height="5" style="{INK}"/>' for i in range(4))
                      + arrow(140, 120, 176, 120, 4)
                      + r(186, 46, 120, 150, PAPER, 5, rx=4) + ln("M186 70 H306", 3) + r(198, 82, 44, 100, "fill:var(--tone)", 3) + r(250, 82, 44, 46, PAPER, 3) + r(250, 136, 44, 46, PAPER, 3)
                      + arrow(316, 120, 352, 120, 4)
                      + "".join(person(360 + i * 28, 104 + (i % 2) * 10, 0.8) for i in range(3)) + tick(380, 170, 1.4)
                      + note(75, 236, "their needs", "middle") + note(246, 236, "my design", "middle") + note(398, 236, "they used it", "middle")),
    # the app: a checklist filling up, and a late task that emails on its own
    "taskboard": lambda: (r(20, 30, 200, 220, PAPER, 5, rx=6) + t(36, 60, "checklist", 15, "mono")
                          + "".join(r(36, 78 + i * 30, 18, 18, PAPER, 3) + (tick(39, 86 + i * 30, 0.7, "var(--ink)") if i < 3 else "")
                                    + f'<rect x="64" y="{84 + i * 30}" width="{70 + 50 * seed("chk", i):.0f}" height="5" style="{INK if i < 3 else MUTED}"/>' for i in range(5))
                          + r(36, 228, 168, 10, "fill:none", 3) + f'<rect x="36" y="228" width="{168 * 0.6:.0f}" height="10" style="{INK}"/>'
                          + r(250, 60, 180, 110, SPOT, 5, rx=6) + t(266, 92, "task", 15, "mono", fill=ONSPOT) + t(414, 92, "LATE", 15, "display", "end", ONSPOT)
                          + f'<rect x="266" y="108" width="120" height="5" style="{ONSPOT}"/><rect x="266" y="122" width="80" height="5" style="{ONSPOT}"/>'
                          + clockface(290, 214, 26, 2, 0, 4) + note(290, 262, "cron", "middle")
                          + ln("M330 200 Q350 180 364 196", 3, "4 5", "var(--muted)") + envelope(370, 192, 56, 38) + note(398, 262, "email", "middle")),
    # --- the model platform, redrawn ---
    # the bill: GPU usage totalled per project and per service group; two API calls refactored into one
    "bill": lambda: (r(30, 24, 210, 252, PAPER, 5) + t(48, 58, "GPU usage", 17, "display")
                     + "".join(f'<rect x="48" y="{82 + i * 30}" width="{60 + 30 * seed("bill", i):.0f}" height="6" style="{INK}"/>'
                               + f'<rect x="{222 - 36 - 20 * seed("bill", i + 7):.0f}" y="{82 + i * 30}" width="{36 + 20 * seed("bill", i + 7):.0f}" height="6" style="{INK}"/>' for i in range(5))
                     + ln("M48 238 H222 M48 244 H222", 3) + t(48, 266, "total", 13, "mono") + f'<rect x="166" y="258" width="56" height="8" style="{SPOT}"/>'
                     + ln("M266 96 Q330 96 352 140 M266 184 Q330 184 352 140", 4, "6 6", "var(--muted)") + arrow(352, 140, 384, 140, 4)
                     + note(266, 86, "call 1") + note(266, 208, "call 2") + r(386, 116, 50, 48, INK, 4) + t(411, 146, "1", 22, "display", "middle", PAPER)),
    # the right versions: a service can only be updated to the model versions it's bound to
    "versions": lambda: (r(24, 110, 120, 80, INK, 5, rx=8) + t(84, 156, "service", 16, "mono", "middle", PAPER)
                         + "".join((ln(f"M144 150 L290 {60 + i * 90}", 4) if ok else ln(f"M144 150 L290 {60 + i * 90}", 3, "6 6", "var(--muted)"))
                                   + r(296, 36 + i * 90, 120, 48, PAPER if ok else "fill:none", 4, dash=None if ok else "6 5", rx=24) + t(356, 67 + i * 90, f"model v{v}", 15, "mono", "middle", INK if ok else MUTED)
                                   + (tick(426, 58 + i * 90) if ok else cross(430, 60 + i * 90, 9, 4)) for i, (v, ok) in enumerate(((1, True), (2, True), (3, False))))
                         + note(84, 230, "an update offers only", "middle") + note(84, 248, "the bound versions", "middle")),
    # where it lands: a GPU-type template, the cards it supports, then the cluster and namespace it deploys into;
    # and the fix: a refused call to the cluster manager no longer reads as "take it offline"
    "lands": lambda: (r(10, 70, 110, 130, PAPER, 5, rx=6) + t(65, 100, "template", 14, "mono", "middle") + ln("M28 124 H102 M28 142 H90 M28 160 H96", 3)
                      + note(65, 222, "GPU type", "middle") + arrow(126, 135, 156, 135, 4)
                      + "".join(r(166 + (i % 2) * 52, 78 + (i // 2) * 62, 44, 50, SPOT if i == 1 else PAPER, 4) + ln(f"M{172 + (i % 2) * 52} {128 + (i // 2) * 62} V{136 + (i // 2) * 62} M{204 + (i % 2) * 52} {128 + (i // 2) * 62} V{136 + (i // 2) * 62}", 3) for i in range(4))
                      + note(214, 222, "the cards it fits", "middle") + arrow(274, 135, 304, 135, 4)
                      + r(312, 56, 128, 156, PAPER, 5, rx=6) + t(376, 82, "cluster", 14, "mono", "middle") + r(326, 96, 100, 100, "fill:none", 3, dash="7 6") + t(376, 150, "namespace", 12, "mono", "middle", MUTED)
                      + dot(376, 176, 8, SPOT) + stamp(225, 270, "refused ≠ offline", -3, 15, kind="mono")),
    # three spare weeks: an audit from 9 July to 11 August, about thirty defects, merged to production on 17–19 August
    "weeks": lambda: ("".join(r(14 + i * 72, 40, 62, 170, SPOT if i == 5 else PAPER, 4, rx=4) + t(45 + i * 72, 64, d, 13, "mono", "middle", ONSPOT if i == 5 else INK)
                              + "".join(dot(30 + i * 72 + (k % 3) * 15, 92 + (k // 3) * 22, 5) for k in range(n))
                              for i, (d, n) in enumerate((("9 Jul", 6), ("16 Jul", 7), ("23 Jul", 6), ("30 Jul", 7), ("6 Aug", 4), ("17 Aug", 0))))
                      + t(405, 140, "prod", 16, "display", "middle", ONSPOT)
                      + note(160, 242, "≈30 defects, each with its cause and fix", "middle") + note(405, 242, "merged", "middle")),
    # offline, still running: two status constants copied the wrong way round, so "offline" got scaled back up
    "offline": lambda: (r(30, 30, 120, 40, PAPER, 4, rx=20) + t(90, 56, "ONLINE", 14, "mono", "middle") + r(300, 30, 120, 40, PAPER, 4, rx=20) + t(360, 56, "OFFLINE", 14, "mono", "middle")
                        + ln("M150 50 C220 50 230 110 300 110 M300 50 C230 50 220 110 150 110", 3, "6 5", "var(--live-red)") + note(225, 132, "copied the wrong way round", "middle")
                        + r(40, 186, 96, 46, PAPER, 5, rx=23) + dot(64, 209, 15) + t(88, 262, "off", 15, "mono", "middle")
                        + server(250, 160, 110, 110, 4, (0, 1, 2, 3)) + arrow(392, 260, 392, 166, 6) + note(392, 290, "scaled up", "middle")),
    # the clean-up that never ran: the rollback only deleted zero-replica deployments, so every real one kept its GPUs
    "nocleanup": lambda: (r(20, 50, 150, 110, PAPER, 5, rx=6) + t(95, 82, "deployment", 14, "mono", "middle") + t(95, 124, "replicas: 2", 16, "mono", "middle")
                          + chip(56, 196, 80, 44, "GPU") + drop(96, 252) + drop(118, 262, 0.8)
                          + arrow(380, 104, 250, 104, 5) + note(380, 92, "rollback", "end") + ln("M232 40 V170", 9) + stamp(330, 160, "only if 0", -4, 16, kind="mono")
                          + cross(232, 104, 14, 5) + note(300, 262, "the leak it was for, every time", "middle")),
    # ten models: a hard-coded LIMIT 10 cut the list off before the TTS model; and NULLs that never collide
    "limit10": lambda: ("".join(r(30, 16 + i * 20, 200, 16, PAPER, 2) + f'<rect x="40" y="{21 + i * 20}" width="{50 + 70 * seed("lim", i):.0f}" height="5" style="{INK}"/>' for i in range(10))
                        + ln("M16 220 H244", 4, "8 6", "var(--live-red)") + t(250, 225, "LIMIT 10", 15, "mono", fill=SPOT)
                        + r(30, 232, 200, 22, "fill:none", 2, dash="4 4") + t(40, 248, "TTS", 14, "mono", fill=MUTED)
                        + t(345, 110, "NULL ≠ NULL", 24, "display", "middle") + note(345, 140, "so a duplicate", "middle") + note(345, 158, "hid a service group", "middle")),
    # guards: an empty config push bounces off; the templates and credentials behind it stay; the client renews itself
    "guardrails": lambda: (r(14, 120, 80, 60, PAPER, 4, rx=8) + t(54, 158, "{ }", 22, "mono", "middle") + arrow(98, 150, 150, 150, 5)
                           + '<path d="M225 50 L290 74 V146 Q290 212 225 246 Q160 212 160 146 V74Z" style="fill:var(--live-red);stroke:var(--ink);stroke-width:6;stroke-linejoin:round"/>'
                           + tick(206, 150, 1.8, "var(--live-on-red)")
                           + doc(320, 70, 90, 70, 3, 4, False) + key_icon(326, 200, 0.9)
                           + note(366, 166, "templates", "middle") + note(366, 238, "credentials", "middle")),
    # keys out of the code: the keys leave the source for the config centre; the server won't start without them
    "keys": lambda: (r(16, 40, 140, 190, PAPER, 5) + t(30, 66, "source", 13, "mono", fill=MUTED)
                     + "".join(f'<rect x="30" y="{84 + i * 22}" width="{60 + 50 * seed("src", i):.0f}" height="5" style="{INK}"/>' for i in range(6) if i != 3)
                     + t(30, 156, "KEY = \u2026", 13, "mono", fill=SPOT) + ln("M28 152 H140", 3, colour="var(--live-red)")
                     + arrow(164, 135, 214, 135, 4) + key_icon(176, 112, 0.6, 4)
                     + r(222, 70, 110, 130, INK, 5, rx=8) + ring(277, 120, 22, 4, "fill:none") + ln("M277 98 V106 M277 134 V142 M255 120 H263 M291 120 H299", 3, colour="var(--paper)")
                     + t(277, 176, "config", 13, "mono", "middle", PAPER) + arrow(338, 135, 374, 135, 4) + server(378, 90, 60, 90, 3, (1,))
                     + stamp(250, 262, "old keys rotated", -3, 15, kind="mono")),
    # both ends: the deploy finishes its database write even past the deadline, and a sweep clears orphaned Deployments
    "bothends": lambda: (r(70, 110, 310, 44, "fill:var(--tone)", 5) + r(50, 98, 30, 68, SPOT, 5, rx=4) + r(370, 98, 30, 68, SPOT, 5, rx=4)
                         + chip(185, 104, 80, 56, "GPU") + note(65, 196, "the write", "middle") + note(65, 214, "always lands", "middle")
                         + note(385, 196, "a sweep for", "middle") + note(385, 214, "orphans", "middle")
                         + note(225, 262, "the leak, closed from both ends", "middle")),
    # --- KKP Wallet, redrawn ---
    # the statement is the judge: replay its rows; if they reproduce every balance it prints, it counts; if not, it's a claim
    "judge": lambda: (r(16, 24, 130, 250, PAPER, 5) + t(30, 52, "statement", 13, "mono", fill=MUTED)
                      + "".join(t(30, 84 + i * 26, "+" if seed("jd", i) > 0.45 else "−", 16, "mono") + f'<rect x="48" y="{74 + i * 26}" width="{40 + 40 * seed("jd", i + 3):.0f}" height="6" style="{INK}"/>' for i in range(6))
                      + ln("M30 244 H132", 3) + t(30, 264, "balance", 12, "mono") + f'<rect x="96" y="256" width="36" height="8" style="{INK}"/>'
                      + arrow(152, 150, 196, 150, 4) + note(174, 138, "replay", "middle") + ring(232, 150, 32, 5, INK) + t(232, 162, "Σ", 30, "display", "middle", PAPER)
                      + arrow(264, 132, 300, 84, 4) + arrow(264, 168, 300, 216, 4, "6 6")
                      + r(304, 50, 136, 66, PAPER, 5, rx=6) + t(372, 78, "matches", 14, "mono", "middle") + t(372, 100, "counts", 16, "display", "middle") + tick(410, 64, 1.1)
                      + r(304, 184, 136, 66, "fill:none", 4, dash="7 6", rx=6) + t(372, 212, "doesn't", 14, "mono", "middle", MUTED) + t(372, 234, "a claim", 16, "display", "middle", MUTED)
                      + note(372, 280, "used by nothing", "middle")),
    # the wall: thirteen Gradle modules, and a dependency that crosses one fails the build
    "modules": lambda: ("".join(r(24 + (i % 5) * 82, 24 + (i // 5) * 56, 70, 40, INK if i == 6 else PAPER, 4, rx=4) for i in range(13))
                        + '<path d="M101 64 Q150 140 260 136" style="fill:none;stroke:var(--live-red);stroke-width:4;stroke-dasharray:6 5"/>' + cross(186, 118, 11, 5)
                        + t(330, 164, "13", 30, "display", "middle") + note(330, 184, "modules", "middle")
                        + stamp(140, 236, "BUILD FAILED", -5, 18, spot=True, kind="display") + note(340, 248, "~1,200 tests", "middle")),
    # 26 times faster: the home screen's refresh before and after the log reads were cached
    "fast": lambda: (t(30, 60, "before", 14, "mono", fill=MUTED) + r(30, 72, 390, 34, INK, 4) + t(412, 96, "5.8 s", 16, "mono", "end", PAPER)
                     + t(30, 150, "after", 14, "mono", fill=MUTED) + r(30, 162, 15, 34, SPOT, 4) + t(56, 186, "221 ms", 16, "mono")
                     + t(330, 196, "26×", 54, "display", "middle") + note(225, 270, "once the log reads were cached", "middle")),
    # no passcodes: a figure is taken only word for word; a message that looks like it holds a passcode is dropped whole
    "nopasscode": lambda: (r(20, 24, 300, 66, PAPER, 4, rx=14) + dot(46, 57, 9, INK) + f'<rect x="66" y="44" width="110" height="6" style="{INK}"/>'
                           + r(184, 38, 80, 22, PAPER, 3) + t(224, 54, "RM 0.00", 13, "mono", "middle") + tick(282, 52) + note(170, 110, "every figure, word for word", "middle")
                           + r(20, 134, 300, 66, PAPER, 4, dash="8 6", rx=14) + dot(46, 167, 9, INK) + f'<rect x="66" y="154" width="90" height="6" style="{INK}"/>'
                           + t(66, 186, "code • • • • • •", 14, "mono", fill=SPOT)
                           + arrow(330, 168, 380, 168, 4) + r(386, 140, 52, 60, PAPER, 4) + ln("M386 152 H438", 3) + cross(412, 176, 12, 5) + note(412, 222, "dropped", "middle")
                           + r(20, 240, 300, 34, "fill:none", 3, dash="5 5") + t(36, 262, "refused · text not kept", 13, "mono", fill=MUTED)),
    # kept in order: three versioned docs, 22 dated decisions, and each doc pointing at the code it covers
    "docs": lambda: ("".join(r(20 + i * 18, 34 + i * 74, 150, 64, PAPER, 4) + t(34 + i * 18, 58 + i * 74, k, 14, "mono")
                             + r(134 + i * 18, 40 + i * 74, 28, 20, SPOT if i == 2 else INK, 0) + t(148 + i * 18, 55 + i * 74, "v", 13, "mono", "middle", PAPER)
                             + f'<rect x="{34 + i * 18}" y="{72 + i * 74}" width="100" height="5" style="{INK}"/><rect x="{34 + i * 18}" y="{84 + i * 74}" width="70" height="5" style="{INK}"/>'
                             for i, k in enumerate(("product", "design", "frontend")))
                     + ln("M232 34 V250", 4) + "".join(ln(f"M226 {40 + i * 9.6:.0f} H238", 2) for i in range(22)) + note(232, 274, "22 decisions, dated", "middle")
                     + r(330, 100, 100, 90, INK, 5, rx=6) + t(380, 154, "</>", 24, "mono", "middle", PAPER)
                     + ln("M170 66 C290 66 300 118 330 126 M188 140 C290 140 300 145 330 145 M206 214 C290 214 300 172 330 164", 3, "5 5", "var(--muted)")),
    # the face: an original UI, from a first sketch to the fourth frontend version
    "face": lambda: ("".join(phone(18 + i * 108, 30 + (0 if i == 3 else 10), 86, 170 - (0 if i == 3 else 10), 0,
                                   (ln(f"M{36 + i * 108} {70 + j * 22} H{80 + i * 108}", 3, "4 4" if i == 0 else None) for j in range(1)) and
                                   "".join((ln(f"M{34 + i * 108} {66 + j * 20} H{86 + i * 108}", 2 + i * 0.6, "4 5" if i == 0 else None) if i < 2 else
                                            r(34 + i * 108, 60 + j * 26, 54, 18, SPOT if (i == 3 and j == 0) else ("fill:var(--tone)" if i == 2 else INK), 2, rx=3 * i)) for j in range(4)))
                             + t(61 + i * 108, 232, f"v{i + 1}", 18, "display", "middle", SPOT if i == 3 else INK) for i in range(4))
                     + note(225, 274, "four frontend versions, from scratch", "middle")),
    # --- neuromorphic study ---
    # the case: memory and compute in the same place, sparse spikes out, and what that buys
    "neurocase": lambda: (ring(76, 120, 50, 5) + r(54, 98, 44, 44, INK, 0, rx=4) + ln("M60 110 H92 M60 120 H92 M60 130 H92", 3, colour="var(--paper)")
                          + note(76, 196, "stores and computes", "middle") + note(76, 212, "in one place", "middle")
                          + ln("M126 120 H200", 3) + "".join(ln(f"M{138 + x} 120 V98", 4) for x in (6, 30, 38)) + note(170, 150, "spikes", "middle")
                          + r(220, 20, 210, 74, PAPER, 4, rx=8) + r(238, 40, 44, 26, "fill:none", 4) + r(282, 46, 6, 14, INK, 0) + f'<rect x="242" y="44" width="12" height="18" style="{SPOT}"/>'
                          + t(300, 60, "frugal", 16, "display") + note(300, 80, "with energy")
                          + r(220, 112, 210, 74, PAPER, 4, rx=8) + "".join(f'<rect x="{238 + (k % 4) * 11}" y="{128 + (k // 4) * 11}" width="9" height="9" style="{INK};opacity:{0.15 + 0.6 * seed("priv", k):.2f}"/>' for k in range(16))
                          + t(300, 152, "private", 16, "display") + note(300, 172, "no inputs kept")
                          + r(220, 204, 210, 74, PAPER, 4, rx=8)
                          + ln("M244 224 L268 244 L244 262 M268 244 L288 226 M268 244 L288 262", 2.5) + "".join(dot(x, y, 5) for x, y in ((244, 224), (244, 262), (288, 226), (288, 262))) + dot(268, 244, 6, PAPER) + cross(268, 244, 7, 3)
                          + t(300, 244, "tolerant", 16, "display") + note(300, 264, "of faults")),
    # the ground the review covers, as layers of earth under a sprout
    "strata": lambda: (ln("M225 64 V40", 4) + leaf(210, 40, -30) + leaf(242, 34, 30)
                       + "".join(r(20, 64 + i * 56, 410, 56, f, 4) + t(40, 100 + i * 56, k, 20, "display", fill=tf)
                                 for i, (k, f, tf) in enumerate((("9 properties", PAPER, INK), ("hardware", "fill:var(--tone)", INK), ("software", PAPER, INK), ("learning rules", INK, PAPER))))
                       ),
    # the critique, in the report's own three limits: hard-coded mouse moves, no sound, too little training
    "critique": lambda: (r(70, 24, 46, 70, PAPER, 5, rx=22) + ln("M93 24 V48 M70 48 H116", 3) + "".join(arrow(128, 59, 128 + 46 * math.cos(a), 59 + 46 * math.sin(a), 3, "4 4") for a in (0, -0.75, 0.75))
                         + t(200, 52, "fixed", 20, "display") + t(200, 78, "mouse moves", 20, "display")
                         + '<path d="M70 132 H88 L112 112 V176 L88 156 H70Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>' + cross(140, 144, 12, 5)
                         + t(200, 140, "no sound,", 20, "display") + t(200, 166, "no \u201cfrom where\u201d", 20, "display")
                         + r(64, 204, 76, 66, PAPER, 5, rx=4) + ln("M64 222 H140", 4) + "".join(r(72 + (k % 5) * 13, 230 + (k // 5) * 14, 10, 10, SPOT if k < 5 else "fill:none", 2) for k in range(10))
                         + t(200, 234, "5 days,", 20, "display") + t(200, 260, "1 game", 20, "display")),
    # --- Wordle AI ---
    # three players: a letter-by-position table, a DQN, and an LSTM-DQN that reads the guesses so far, each playing a row
    "threeplayers": lambda: ('<g transform="translate(60 0)">' + "".join(
        (("".join(f'<rect x="{24 + (k % 4) * 15}" y="{y + 6 + (k // 4) * 15}" width="13" height="13" style="{INK};opacity:{0.15 + 0.85 * seed("tbl", k):.2f}"/>' for k in range(12))) if i == 0 else
         ("".join(ln(f"M{30} {y + 10 + a * 18} L{58} {y + 10 + b * 18} L{86} {y + 28}", 2) for a in range(3) for b in range(3))
          + "".join(dot(30, y + 10 + a * 18, 5) + dot(58, y + 10 + a * 18, 5) for a in range(3)) + dot(86, y + 28, 6, SPOT if i == 2 else INK)
          + (ln(f"M52 {y + 4} C52 {y - 14} 72 {y - 14} 66 {y + 2}", 3) + arrow(68, y - 4, 64, y + 4, 3) if i == 2 else "")))
        + t(112, y + 16, name, 18, "display")
        + "".join(r(112 + k * 38, y + 26, 32, 32, fill, 3) for k, fill in enumerate(row))
        for i, (y, name, row) in enumerate(((22, "table", ("fill:var(--art-glow)", PAPER, "fill:var(--art-win)", PAPER, PAPER)),
                                            (112, "DQN", (PAPER, "fill:var(--art-win)", PAPER, "fill:var(--art-glow)", PAPER)),
                                            (202, "LSTM-DQN", (PAPER, PAPER, "fill:var(--art-glow)", PAPER, "fill:var(--art-win)")))))
        + "</g>" + note(225, 292, "judged by average guesses", "middle")),
    # --- AKI predictor ---
    # the service: the model on Kubernetes, watched by Prometheus, rolled back when it degrades
    "aksvc": lambda: (r(20, 14, 410, 82, PAPER, 5, rx=8) + t(36, 40, "k8s", 16, "mono", fill=MUTED)
                      + "".join(r(110 + k * 104, 30, 88, 52, PAPER, 4, rx=10) + t(154 + k * 104, 62, "v2", 18, "display", "middle") for k in range(3))
                      + ln("M30 186 H330", 3) + ln("M30 150 H330", 2, "6 5", "var(--muted)") + note(30, 172, "threshold")
                      + ln("M30 128 L80 124 L130 132 L180 126 L222 140 L262 168 L300 176 L330 172", 4) + dot(234, 150, 8, SPOT)
                      + '<path d="M384 112 a22 22 0 0 1 22 22 v18 l8 10 h-60 l8 -10 v-18 a22 22 0 0 1 22 -22z" style="fill:var(--live-red);stroke:var(--ink);stroke-width:4;stroke-linejoin:round"/>' + dot(384, 168, 5)
                      + note(384, 196, "alert", "middle")
                      + r(250, 222, 80, 52, PAPER, 4, rx=10) + t(290, 255, "v2", 18, "display", "middle") + r(60, 222, 80, 52, INK, 4, rx=10) + t(100, 255, "v1", 18, "display", "middle", PAPER)
                      + ln("M250 236 C210 206 180 206 146 236", 4) + arrow(160, 226, 144, 238, 4) + note(195, 290, "rollback", "middle")),
    # the module: the hardware it reviewed, Intel's Lava, the learning rules from STDP to surrogate gradients; and a warning
    "neuromodule": lambda: ("".join(chip(44, 34 + k * 84, 64, 40) + t(138, 60 + k * 84, name, 15, "mono") for k, name in enumerate(("Loihi", "TrueNorth", "SpiNNaker 2")))
                            + '<path d="M362 30 L420 128 H304Z" style="fill:var(--live-red);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>'
                            + t(362, 116, "!", 46, "display", "middle", ONSPOT) + note(362, 150, "the one they", "middle") + note(362, 166, "warn you off", "middle")
                            + r(270, 186, 70, 34, INK, 4, rx=6) + t(305, 209, "Lava", 15, "mono", "middle", PAPER)
                            + ln("M250 250 H430", 4) + dot(250, 250, 6) + dot(430, 250, 6, SPOT) + note(250, 276, "STDP") + note(430, 276, "surrogate", "end") + note(430, 292, "gradients", "end")),
    # --- Instant Policy++ ---
    # the four tasks of the 2D game: reach the goal, eat all edibles, push and place, parking
    "fourtasks": lambda: ("".join(r(x, y, 205, 124, PAPER, 4, rx=4) + note(x + 102, y + 116, lab, "middle")
                                  for x, y, lab in ((15, 12, "reach the goal"), (230, 12, "eat all edibles"), (15, 162, "push and place"), (230, 162, "parking")))
                          + dot(46, 80, 10, SPOT) + ln("M58 76 Q110 30 170 52", 3, "5 6") + ring(180, 54, 14, 4) + dot(180, 54, 5)
                          + dot(262, 84, 10, SPOT) + ln("M272 80 L300 50 L340 80 L380 46 L410 82", 3, "5 6") + "".join(dot(x, y, 5) for x, y in ((300, 50), (340, 80), (380, 46), (410, 82)))
                          + dot(48, 232, 10, SPOT) + r(70, 214, 34, 34, INK, 3) + arrow(112, 231, 140, 231, 3) + r(150, 210, 42, 42, "fill:none", 3, dash="5 4")
                          + ln("M296 196 V256 M346 196 V256 M396 196 V256 M296 256 H396", 4) + r(306, 204, 30, 46, SPOT, 4, rx=7) + ln("M310 216 H332", 3) + r(356, 210, 30, 40, "fill:none", 2, dash="4 4") + arrow(262, 250, 296, 236, 3)),
    # the probe: can the frozen hyperbolic embeddings predict the next action? worse than a bigram
    "probe": lambda: (ln("M50 250 H400", 5) + r(90, 250 - 210 * 0.185 / 0.366, 110, 210 * 0.185 / 0.366, SPOT, 4) + r(250, 40, 110, 210, INK, 4)
                      + t(145, 236 - 210 * 0.185 / 0.366, "18.5%", 22, "display", "middle") + t(305, 30, "36.6%", 22, "display", "middle")
                      + t(145, 280, "probe", 18, "mono", "middle") + t(305, 280, "bigram", 18, "mono", "middle")),
    # my mistake: downsampling a demonstration evenly drops the frames that matter, and the policy oscillates
    "downsample": lambda: (ln("M30 70 H420", 3) + "".join(ln(f"M{30 + k * 26} 60 V80", 3 if k % 4 else 5, colour="var(--live-red)" if k in (3, 6, 9, 14) else "var(--ink)") for k in range(16))
                           + "".join(ring(30 + k * 26, 70, 11, 3, "fill:none") for k in range(0, 16, 4))
                           + note(30, 44, "kept: every 4th frame") + note(420, 108, "missed: the ones that matter", "end")
                           + ln("M30 220 " + " ".join(f"Q{45 + k * 30} {190 if k % 2 == 0 else 250} {60 + k * 30} 220" for k in range(12)), 4) + dot(420, 220, 9, SPOT)
                           + note(225, 284, "the policy oscillates", "middle")),
    # what breaks: federated learning on the edge, every client storing data and downloading a big model, a server in charge;
    # the ideal is a sparse, peer-to-peer mesh
    "fedbreaks": lambda: (server(94, 20, 60, 70, 3, (1,)) + note(162, 56, "the server")
                          + "".join(arrow(124, 96, x + 25, 170, 6) + r(x, 176, 50, 40, PAPER, 4, rx=4) + db(x + 25, 232, 30, 22) for x in (10, 70, 128, 186))
                          + note(124, 292, "store, download, train", "middle")
                          + "".join(ln(f"M{x1} {y1} L{x2} {y2}", 2.5, "5 5") for x1, y1, x2, y2 in ((300, 90, 380, 70), (380, 70, 420, 150), (300, 90, 330, 190), (330, 190, 420, 150), (300, 90, 420, 150)))
                          + "".join(ring(x, y, 12, 4) for x, y in ((300, 90), (380, 70), (420, 150), (330, 190)))
                          + note(360, 236, "the ideal:", "middle") + note(360, 254, "peer to peer", "middle")),
    # together: each device broadcasts its averaged weight changes every 100 updates, over HTTP, and the others merge them
    "together": lambda: ("".join(pi_board(x - 35, y - 24) for x, y in ((225, 52), (80, 220), (370, 220)))
                         + "".join(arrow(ax, ay, bx, by, 3, "6 5") for ax, ay, bx, by in ((190, 82, 116, 190), (128, 196, 202, 88), (260, 82, 334, 190), (322, 196, 248, 88), (122, 230, 328, 230)))
                         + t(140, 128, "Δw", 18, "display", "middle") + t(310, 128, "Δw", 18, "display", "middle") + t(225, 222, "Δw", 18, "display", "middle")
                         + note(225, 150, "every 100", "middle") + note(225, 166, "updates", "middle") + note(225, 284, "over HTTP", "middle")
                         + motion("".join(f"@keyframes tg{k}{{0%{{transform:translate(0,0);opacity:0}}10%,80%{{opacity:1}}90%,100%{{transform:translate({dx}px,{dy}px);opacity:0}}}}"
                                          f".tg{k}{{opacity:0;animation:tg{k} 6s ease-in-out {k * 2}s infinite}}" for k, (dx, dy) in enumerate(((-66, 96), (66, 96), (194, 0)))))
                         + "".join(f'<rect class="mv tg{k}" x="{x - 6}" y="{y - 6}" width="12" height="12" style="{SPOT}"/>' for k, (x, y) in enumerate(((188, 86), (262, 86), (126, 222))))),
    # the result: the plan (four Pi cameras, four kinds of weather) and what happened (out of memory; 12 hours, not converged)
    "piresult": lambda: ("".join(pi_board(16 + k * 108, 52, 84, 52, "fill:none", "6 5") + weather(58 + k * 108, 26, w) for k, w in enumerate(("sun", "rain", "cloud", "snow")))
                         + note(225, 126, "the plan", "middle")
                         + pi_board(40, 158, 110, 70) + r(40, 240, 110, 16, "fill:none", 3) + r(40, 240, 110, 16, SPOT, 0) + note(95, 280, "Pi 3B: out of memory", "middle")
                         + laptop(270, 158, 130) + curve(282, 168, 106, 60, lambda u: 0.9 - 0.5 * (1 - math.exp(-2 * u)) + 0.04 * math.sin(30 * u), 30, 3)
                         + note(335, 280, "12 h, not converged", "middle")),
    # less code: a monolith handler split, over four phases, into small packages, with the dead code taken out
    "lesscode": lambda: (r(20, 30, 110, 200, PAPER, 5) + "".join(f'<rect x="32" y="{44 + i * 14}" width="{50 + 36 * seed("mono", i):.0f}" height="5" style="{INK}"/>' for i in range(13))
                         + note(75, 254, "one handler", "middle")
                         + ln("M140 130 H262", 4) + arrow(250, 130, 268, 130, 4) + "".join(ring(158 + k * 30, 130, 11, 3, SPOT if k == 3 else PAPER) + t(158 + k * 30, 135, str(k + 1), 12, "mono", "middle", ONSPOT if k == 3 else INK) for k in range(4))
                         + note(204, 104, "four phases", "middle")
                         + "".join(r(282 + (k % 2) * 80, 30 + (k // 2) * 62, 68, 48, PAPER, 4, rx=4) + f'<rect x="{292 + (k % 2) * 80}" y="{46 + (k // 2) * 62}" width="40" height="5" style="{INK}"/><rect x="{292 + (k % 2) * 80}" y="{58 + (k // 2) * 62}" width="28" height="5" style="{INK}"/>' for k in range(5))
                         + note(356, 254, "packages", "middle")
                         + r(170, 196, 70, 40, "fill:none", 3, dash="5 5") + cross(205, 216, 12, 4) + note(205, 254, "dead code", "middle")),
    # signed rules: parsing rules ship as signed packs; a tampered or older pack is refused; secrets in the Keychain;
    # consent given purpose by purpose
    "signedrules": lambda: ("".join(r(16, 22 + k * 88, 120, 56, PAPER if k == 0 else "fill:none", 4, dash=None if k == 0 else "6 5", rx=4)
                                    + t(30, 46 + k * 88, "rules", 13, "mono", fill=INK if k == 0 else MUTED) + t(30, 66 + k * 88, lab, 12, "mono", fill=MUTED)
                                    + ring(112, 50 + k * 88, 13, 4, SPOT if k == 0 else "fill:none") + (tick(146, 50 + k * 88) if k == 0 else cross(156, 50 + k * 88, 9, 4))
                                    for k, lab in enumerate(("signed", "tampered", "older")))
                            + ln("M104 132 L120 146 M112 128 L108 150", 3)
                            + arrow(176, 50, 214, 70, 4) + phone(218, 30, 92, 180)
                            + "".join(r(330, 40 + k * 44, 50, 26, PAPER, 3, rx=13) + dot(343 + (24 if on else 0), 53 + k * 44, 9, "fill:var(--art-win)" if on else INK) for k, on in enumerate((True, False, True)))
                            + note(390, 176, "consent,", "middle") + note(390, 192, "per purpose", "middle")
                            + key_icon(232, 250, 0.7, 4) + note(300, 256, "Keychain")),
    # --- RE-News, redrawn ---
    # a flat score: most of the old salience weight barely moved, so turning the knob couldn't make range
    "flatscore": lambda: ("".join(r(20, 22 + k * 20, 150 if k < 8 else 150 + (40 if k == 8 else -60), 14, SPOT if k >= 8 else INK, 2) for k in range(10))
                          + t(30, 270, "85%", 34, "display") + note(118, 270, "near-constant")
                          + ring(320, 90, 40, 5) + ln("M320 90 L344 60", 5) + "".join(ln(f"M{320 + 46 * math.cos(a):.0f} {90 + 46 * math.sin(a):.0f} L{320 + 54 * math.cos(a):.0f} {90 + 54 * math.sin(a):.0f}", 3) for a in [math.pi * (0.75 + i * 0.25) for i in range(7)])
                          + note(320, 158, "retune", "middle") + arrow(320, 172, 320, 200, 3)
                          + ln("M240 226 H400", 4) + note(320, 250, "still flat", "middle")),
    # the new rule: rank by breadth (how many kinds of source back it); confidence gates, never multiplies;
    # trajectory is a badge; intensity is an honest null
    "breadth": lambda: (t(20, 34, "rank by breadth", 16, "display")
                        + "".join(t(20, 76 + k * 52, f"#{k + 1}", 16, "display") + "".join(dot(66 + j * 22, 70 + k * 52, 8, SPOT if k == 0 else INK) for j in range(n))
                                  + (r(66 + n * 22, 58 + k * 52, 30, 22, PAPER, 3, rx=11) + t(81 + n * 22, 74 + k * 52, "↗", 14, "mono", "middle") if k < 2 else "")
                                  for k, n in enumerate((5, 3, 2)))
                        + ln("M20 214 H250", 2, "4 5", "var(--muted)")
                        + t(290, 62, "× confidence", 15, "mono", fill=MUTED) + ln("M288 56 H408", 3, colour="var(--live-red)")
                        + r(290, 92, 130, 40, PAPER, 4, rx=4) + t(304, 117, "gate", 15, "mono") + tick(388, 112)
                        + t(290, 178, "intensity", 15, "mono") + t(290, 202, "null", 18, "display", fill=MUTED)
                        + note(20, 250, "dots: kinds of source") + note(20, 268, "↗: trajectory, a badge")),
    # --- Team Elk and Clucker ---
    # a chess game in progress: the board, a knight's move dashed in, the piece that moved in red
    "chess": lambda: (board(115, 20, 220)
                      + "".join(piece(115 + (i + 0.5) * 27.5, 20 + (j + 0.5) * 27.5, 27.5, k, w) for i, j, k, w in (
                          (0, 0, "rook", 0), (4, 0, "king", 0), (1, 1, "pawn", 0), (5, 1, "pawn", 0), (6, 1, "pawn", 0),
                          (0, 6, "pawn", 1), (3, 6, "pawn", 1), (6, 6, "pawn", 1), (5, 7, "rook", 1), (6, 7, "king", 1)))
                      + ln("M233.1 143.8 V88.8 H260.6", 3, "4 4", "var(--live-red)") + piece(260.6, 88.8, 27.5, "knight", 2)
                      + note(225, 270, "your move", "middle")),
    # the team of five, under the club they built the app for; the red one is me
    "elkteam": lambda: (r(120, 22, 210, 50, INK, 5) + t(225, 56, "CHESS CLUB", 22, "display", "middle", PAPER)
                     + ln("M225 72 V96 M55 96 H395 M55 96 V112 M140 96 V112 M225 96 V112 M310 96 V112 M395 96 V112", 3)
                     + "".join(person(55 + i * 85, 136, 1.4, SPOT if i == 1 else PAPER) for i in range(5))
                     + ln("M20 212 H430", 6) + note(225, 250, "a team of five", "middle")),
    # my share of the commits: one dot per ten, mine inked in
    "elkcommits": lambda: commit_dots(70, 400, 10, "~70 / 400", "commits, Nov–Dec 2021"),
    # --- RoboCup@Home ---
    # the receptionist task as a state machine: each box a state with what it holds, each arrow what moves it on.
    # LISTEN, the dialogue side, is the one inked in
    "statemachine": lambda: (
        r(10, 50, 110, 70, PAPER, 5, rx=10) + t(65, 80, "WAIT", 18, "display", "middle") + t(65, 104, "guest: none", 12, "mono", "middle", MUTED)
        + r(170, 50, 110, 70, INK, 5, rx=10) + t(225, 80, "LISTEN", 18, "display", "middle", PAPER) + t(225, 104, "name, drink", 12, "mono", "middle", PAPER)
        + dot(268, 110, 4, SPOT)
        + r(330, 50, 110, 70, PAPER, 5, rx=10) + t(385, 80, "GUIDE", 18, "display", "middle") + t(385, 104, "→ living room", 12, "mono", "middle", MUTED)
        + r(240, 200, 200, 66, PAPER, 5, rx=10) + t(340, 230, "INTRODUCE", 18, "display", "middle") + t(340, 252, "guest → host", 12, "mono", "middle", MUTED)
        + arrow(122, 85, 166, 85, 4) + note(145, 36, "person at door", "middle")
        + arrow(282, 85, 326, 85, 4) + note(305, 36, "intent filled", "middle")
        + ln("M205 122 C205 160 245 160 245 132", 3, "5 6") + arrow(245, 140, 245, 124, 3) + note(225, 176, "no match: ask again", "middle")
        + arrow(385, 122, 385, 196, 4) + note(378, 166, "arrived", "end")
        + ln("M238 236 H65 V128", 4) + arrow(65, 140, 65, 124, 4) + note(150, 228, "guest seated", "middle")),
    "switch": lambda: (server(40, 50, 120, 180, 5, (2,)) + note(100, 260, "home lab", "middle") + r(185, 120, 80, 40, PAPER, 5, rx=20) + dot(205, 140, 13, INK)
                       + r(300, 80, 120, 120, PAPER, 5, dash="10 7") + t(360, 148, "opt-in", 15, "mono", "middle")),
    "grey": lambda: ("".join(f'<polygon points="{60 + (i % 4) * 90},{50 + (i // 4) * 90} {130 + (i % 4) * 90},{60 + (i // 4) * 90} {140 + (i % 4) * 90},{130 + (i // 4) * 90} {70 + (i % 4) * 90},{125 + (i // 4) * 90}" style="{INK if seed("map", i) > 0.6 else "fill:var(--tone)"};stroke:var(--ink);stroke-width:3"/>' for i in range(8))
                     + stamp(225, 268, "grey is correct", -3, 18, kind="mono")),
    # --- the home lab ---
    "homelab": lambda: (r(170, 40, 110, 200, PAPER, 6) + r(186, 150, 78, 30, SPOT, 3) + "".join(ln(f"M186 {60 + i * 14} H264", 3) for i in range(5))
                        + laptop(20, 70, 90) + laptop(340, 70, 90) + laptop(340, 200, 70)
                        + motion("@keyframes hl-a{to{stroke-dashoffset:-26}}.hl-a path{animation:hl-a 2.6s linear infinite}")
                        + '<g class="mv hl-a">' + ln("M110 110 L170 140 M280 140 L340 110 M280 180 L340 220", 4, "6 7") + "</g>" + note(225, 284, "over Tailscale", "middle")),
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
    # the trade-off: pixel-wise MSE scores higher PSNR but comes out soft; perceptual loss scores lower but looks real.
    # Left, the two on the trade-off curve; right, the same texture upscaled each way
    "loss": lambda: (ln("M40 236 V26 M40 236 H236", 4) + ln("M34 34 L40 24 L46 34 M228 230 L238 236 L228 242", 4)
                     + t(46, 20, "looks real", 13, "mono", fill=MUTED) + t(236, 262, "PSNR", 13, "mono", "end", MUTED)
                     + ln("M66 60 Q196 70 206 204", 4, "7 6", "var(--muted)")
                     + dot(66, 60, 10, SPOT) + t(58, 90, "perceptual", 14, "mono") + dot(206, 204, 10) + t(194, 228, "MSE", 14, "mono", "end")
                     + '<defs><filter id="srgan-blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.6"/></filter></defs>'
                     + sr_tile(262, True, "MSE") + sr_tile(356, False, "perceptual")
                     + note(350, 190, "same image, 4× up", "middle")),
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
    "trophy": lambda: ('<g transform="translate(-62 0)">' + f'<path d="M160 50 h130 v40 a65 65 0 0 1 -130 0 z" style="fill:var(--live-red);stroke:var(--ink);stroke-width:6"/>'
                       + ln("M160 70 h-30 a30 30 0 0 0 40 50 M290 70 h30 a30 30 0 0 1 -40 50 M225 155 V200 M180 210 H270", 6) + r(170, 210, 110, 34, INK, 4)
                       + t(225, 108, "1st", 30, "display", "middle", ONSPOT) + note(225, 282, "of 50+ teams", "middle") + "</g>"
                       # the prize: a short stack of notes
                       + "".join(f'<g transform="rotate({-8 + 5 * k} 370 {214 - k * 12})">' + r(318, 192 - k * 12, 104, 46, PAPER, 4, rx=4)
                                 + ring(370, 215 - k * 12, 13, 3, "fill:none") + t(370, 221 - k * 12, "$", 16, "display", "middle") + "</g>" for k in range(3))
                       + t(370, 140, "$5,000", 26, "display", "middle") + note(370, 282, "the prize", "middle")),
    # --- CarDesigner ---
    "scan": lambda: scan(),
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
    "batch": lambda: (hands(110, 140, 70, 24, "bt") + "".join(dot(260, 60 + i * 44, 10, INK) + dot(400, 60 + i * 44, 10, PAPER) + ring(400, 60 + i * 44, 10, 4) + ln(f"M272 {60 + i * 44} Q330 {60 + i * 44 + (seed('pr', i) - 0.5) * 80:.0f} 388 {60 + ((i + 2) % 5) * 44}", 3) for i in range(5))
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
    # --- VIM4: kept generic on purpose (a client's line) ---
    "inspect": lambda: ("".join(r(70 + i * 105, 30, 70, 44, INK, 5) + ring(105 + i * 105, 82, 12, 5) + ln(f"M{105 + i * 105} 94 L200 168", 2, "6 6") for i in range(3))
                        + ln("M30 196 H250", 8) + ring(200, 178, 18, 5) + arrow(250, 196, 410, 150) + arrow(250, 196, 410, 250)
                        + note(416, 140, "pass", "end") + note(416, 284, "reject", "end")),
    "spec": lambda: (r(40, 30, 370, 240, PAPER, 5) + ln("M40 70 H410", 4) + t(60, 58, "check", 14) + t(250, 58, "limit", 14)
                     + "".join(f'<rect x="60" y="{88 + i * 36}" width="{70 + 80 * seed("spec", i):.0f}" height="6" style="{INK}"/>'
                               + t(250, 96 + i * 36, "≤ x", 14, "mono", "start", MUTED) for i in range(5))
                     + "".join(ln(f"M372 {90 + i * 36} l7 7 l14 -14", 4) for i in (0, 1, 3, 4)) + cross(382, 162, 9, 4)),
    "shadow": lambda: (r(40, 60, 150, 90, INK, 5) + t(115, 112, "current", 16, "mono", "middle", PAPER) + r(40, 170, 150, 90, PAPER, 5, dash="10 7") + t(115, 222, "new", 16, "mono", "middle")
                       + arrow(195, 105, 290, 150) + arrow(195, 215, 290, 170) + ring(330, 160, 34, 5) + t(330, 170, "=?", 24, "display", "middle") + note(330, 230, "same parts, compared", "middle")),
    # --- Pollector ---
    "tally": lambda: (person(70, 50, 0.9) + person(70, 170, 0.9) + doc(110, 40, 70, 80, 3, -3, False) + doc(110, 160, 70, 80, 3, 3, False)
                      + arrow(185, 80, 235, 135) + arrow(185, 200, 235, 155) + t(260, 154, "=", 30, "display", "middle")
                      + "".join(r(290 + i * 54, 125, 40, 40, INK if i < 2 else PAPER, 4) + (ln(f"M{330 + i * 54} 145 h14", 4) if i < 2 else "") for i in range(3))
                      + note(345, 200, "hash-chained", "middle")),
    # --- Envite ---
    "audience": lambda: ("".join(ring(90 + i * 135, 120, 40, 5, INK) + "".join(dot(90 + i * 135 + 70 * math.cos(a), 120 + 70 * math.sin(a), 7, PAPER if seed("env", i * 9 + k) > 0.4 else INK)
                                                                         + ring(90 + i * 135 + 70 * math.cos(a), 120 + 70 * math.sin(a), 7, 2, "fill:none")
                                                                         for k, a in enumerate(x * 0.9 + 0.3 for x in range(7))) for i in range(3))
                         + ln("M160 145 Q225 230 290 145 M295 145 Q360 230 425 145", 3, "6 6") + note(225, 270, "opted-in guests, no lists shared", "middle")),
    # --- London Cycle ---
    "docks": lambda: (ln("M20 210 C120 170 160 250 250 200 S380 120 430 150", 14, colour="var(--tone)") + ln("M60 60 L140 120 L230 90 L300 170 L390 110", 5, "12 8")
                      + "".join(r(x - 14, y - 14, 28, 28, PAPER if i not in (0, 4) else INK, 4) + t(x, y + 6, "P", 14, "mono", "middle", PAPER if i in (0, 4) else INK)
                                for i, (x, y) in enumerate([(60, 60), (140, 120), (230, 90), (300, 170), (390, 110)]))
                      + ring(100, 250, 22, 5) + ring(170, 250, 22, 5) + ln("M100 250 L130 224 L170 250 M130 224 L150 224 M116 230 H156", 4) + note(420, 280, "dock to dock", "end")),
    "team": lambda: ("".join(person(60 + i * 47, 150, 0.85, SPOT if i == 3 else PAPER) for i in range(8))
                     + r(140, 40, 170, 60, PAPER, 5) + t(225, 78, "screens → flow", 14, "mono", "middle") + ln("M225 100 L201 132", 3, "5 5") + note(225, 250, "a team of eight", "middle")),
    # --- Seall ---
    "erp": lambda: ("".join(r(30, 40 + i * 80, 110, 56, PAPER, 5) + t(85, 74 + i * 80, f"ERP {'ABC'[i]}", 15, "mono", "middle") + arrow(145, 68 + i * 80, 200, 150) for i in range(3))
                    + r(205, 110, 70, 80, INK, 5) + t(240, 156, "one", 15, "mono", "middle", PAPER) + arrow(280, 150, 300, 150)
                    + r(305, 70, 125, 160, PAPER, 5) + bars(320, 110, 95, 100, [0.4, 0.7, 0.55, 0.9], 6) + note(367, 260, "per department", "middle")),
    # --- Smart home app ---
    "devices": lambda: (phone(250, 30, 150, 250, 0) + curve(268, 110, 114, 90, lambda s: 0.5 + 0.35 * math.sin(6 * s) * (1 - s * 0.5), 24, 3)
                        + "".join(r(40, 40 + i * 78, 130, 56, PAPER, 4) + ring(66, 68 + i * 78, 12, 4, SPOT if i == 1 else PAPER) + t(90, 74 + i * 78, ("lamp", "sensor", "plug")[i], 14) + ln(f"M174 {68 + i * 78} H240", 3, "5 5") for i in range(3))),
    # --- Manunet ---
    "provenance": lambda: (chip(50, 90, 110, 110, "IC") + arrow(185, 145, 245, 145) + stamp(305, 100, "signed", -6, 18) + doc(260, 150, 100, 110, 4, 3, False)
                           + arrow(370, 205, 420, 205) + note(225, 40, "surplus → shortage", "middle")),
}


# ---------- soft motion ----------
# A picture that moves carries its own <style>: slow CSS keyframes on elements with class "mv", every one of them
# still under reduced motion, where each element rests in the pose it is drawn in. Keep it faint and slow.
def motion(css):
    return f"<style>{css}@media (prefers-reduced-motion: reduce){{.mv{{animation:none!important}}}}</style>"


def spin(inner, secs=14, cls="mv-spin"):
    """Turn a drawing slowly about its own centre (a record on its platter)."""
    return (motion(f"@keyframes {cls}{{to{{transform:rotate(360deg)}}}}.{cls}{{transform-box:fill-box;transform-origin:center;animation:{cls} {secs}s linear infinite}}")
            + f'<g class="mv {cls}">{inner}</g>')


def label_mark(cx, cy, rad):
    """A short paper stroke on a record's label, so a turning record visibly turns."""
    return ln(f"M{cx} {cy - rad * 0.12:.1f} V{cy - rad * 0.28:.1f}", max(2, rad * 0.05), colour="var(--paper)")


def turning_vinyl(cx, cy, rad, grooves=4, secs=14, cls="mv-spin"):
    return spin(vinyl(cx, cy, rad, grooves) + label_mark(cx, cy, rad), secs, cls)


def hands(cx, cy, rad, secs, cls):
    """A clock face whose hands go round, slowly: the minute hand once every `secs`, the hour hand twelve times slower."""
    face = clockface(cx, cy, rad, 0, 0)
    face = face[:face.rfind("<path")]   # drop the drawn hands: these turn instead
    face = face[:face.rfind("<path")]
    css = (f"@keyframes {cls}m{{to{{transform:rotate(360deg)}}}}@keyframes {cls}h{{from{{transform:rotate(300deg)}}to{{transform:rotate(660deg)}}}}"
           f".{cls}-m,.{cls}-h{{transform-origin:{cx}px {cy}px;animation:{cls}m {secs}s linear infinite}}"
           f".{cls}-h{{transform:rotate(300deg);animation-name:{cls}h;animation-duration:{secs * 12}s}}")
    return (motion(css) + face + f'<g class="mv {cls}-h">{ln(f"M{cx} {cy} V{cy - rad * 0.5:.0f}", 6)}</g>'
            + f'<g class="mv {cls}-m">{ln(f"M{cx} {cy} V{cy - rad * 0.78:.0f}", 4)}</g>' + dot(cx, cy, 6))


# ---------- pictures added 2026-11-05 (night): the last borrowed ones, and the ones repeated inside a volume ----------
def vonneumann():
    """Why it breaks: classical computing keeps memory apart from compute, so every value crosses one narrow bus."""
    css = ("@keyframes vn-r{0%{transform:translateX(0);opacity:0}12%,85%{opacity:1}100%{transform:translateX(104px);opacity:0}}"
           "@keyframes vn-l{0%{transform:translateX(0);opacity:0}12%,85%{opacity:1}100%{transform:translateX(-104px);opacity:0}}"
           ".vn-r{animation:vn-r 3.6s ease-in-out infinite}.vn-l{animation:vn-l 3.6s ease-in-out infinite}")
    packets = ("".join(f'<rect class="mv vn-r" x="166" y="120" width="18" height="12" style="{SPOT};animation-delay:{i * 1.2}s"/>' for i in range(3))
               + "".join(f'<rect class="mv vn-l" x="266" y="164" width="18" height="12" style="{INK};animation-delay:{0.6 + i * 1.2}s"/>' for i in range(3)))
    return (motion(css) + r(24, 70, 136, 160, INK, 5, rx=6) + t(92, 160, "compute", 20, "display", "middle", PAPER)
            + r(290, 70, 136, 160, PAPER, 5, rx=6) + "".join(ln(f"M306 {96 + i * 22} H410", 3) for i in range(6)) + t(358, 252 - 4, "", 1)
            + ln("M160 116 H290 M160 176 H290", 4) + packets
            + note(225, 100, "one narrow bus", "middle") + note(92, 256, "here", "middle") + note(358, 256, "there", "middle")
            + note(225, 288, "memory kept apart from compute", "middle"))


def failclosed():
    """Fail closed: 917 zero vectors had passed as a success; now a breaker trips and the job exits non-zero."""
    rows = "".join(r(20, 28 + i * 30, 170, 22, PAPER, 3) + t(30, 44 + i * 30, "0 0 0 0 0 0 0 0", 12, "mono", fill=MUTED) for i in range(6))
    return (rows + t(105, 232, "917 ×", 30, "display", "middle") + note(105, 256, "zero vectors", "middle")
            + arrow(200, 110, 236, 110, 4)
            + dot(250, 110, 7) + dot(330, 110, 7) + ln("M250 110 L320 74", 7) + note(290, 146, "breaker: open", "middle")
            + ln("M337 110 H352", 4) + terminal(352, 70, 84, 80, (), False) + t(394, 126, "exit 1", 15, "mono", "middle", SPOT.replace("fill", "fill"))
            + stamp(300, 228, "no quiet success", -5, 17, kind="mono"))


def perstage():
    """Whose model: each stage picks its own backend, the home-lab model by default and Claude only when asked."""
    css = ("@keyframes ps-k{0%,40%{transform:translateX(0)}50%,85%{transform:translateX(26px)}95%,100%{transform:translateX(0)}}"
           ".ps-k{animation:ps-k 12s ease-in-out infinite}")
    out = [motion(css), t(212, 34, "local", 14, "mono", "middle"), t(392, 34, "opt-in", 14, "mono", "middle", MUTED)]
    for k, name in enumerate(("encode", "fuse", "report")):
        y = 56 + k * 74
        knob = dot(208, y + 22, 11, PAPER)
        out += [r(16, y, 120, 44, PAPER, 4, rx=4), t(76, y + 28, name, 15, "mono", "middle"),
                ln(f"M140 {y + 22} H180", 3, "5 5"), r(180, y + 6, 66, 32, INK, 4, rx=16),
                f'<g class="mv ps-k">{knob}</g>' if k == 1 else knob,
                ln(f"M250 {y + 22} H330", 3, "5 5"),
                r(330, y + 2, 104, 40, "fill:none", 3, dash="7 6", rx=6)]
    out += [t(382, 84, "Claude", 15, "mono", "middle", MUTED), t(382, 158, "Claude", 15, "mono", "middle", MUTED), t(382, 232, "Claude", 15, "mono", "middle", MUTED),
            note(225, 290, "default: qwen3:32b on the home-lab GPU", "middle")]
    return "".join(out)


def coin(cx, cy, rad=16, fill=PAPER):
    return ring(cx, cy, rad, 4, fill) + ring(cx, cy, rad - 6, 2, "fill:none") + t(cx, cy + 5, "C", rad * 0.8, "display", "middle", INK if fill == PAPER else PAPER)


def carbon():
    """Carbon Coin: the companies along a supply chain, rewarded in coins on a chain for staying carbon-friendly."""
    firms = (("grower", True), ("factory", False), ("shop", True))
    out = []
    for i, (name, green) in enumerate(firms):
        x = 30 + i * 140
        out += [r(x, 40, 110, 70, PAPER, 5, rx=4), t(x + 55, 70, name, 14, "mono", "middle"),
                t(x + 55, 96, "CO₂ low" if green else "CO₂ high", 13, "mono", "middle", "fill:var(--art-win)" if green else SPOT)]
        if i < 2:
            out.append(arrow(x + 112, 75, x + 138, 75, 4))
        if green:
            out += [coin(x + 55, 146), ln(f"M{x + 55} 164 V196", 3, "5 5")]
    for i in range(5):
        x = 30 + i * 82
        out += [r(x, 200, 60, 48, INK if i % 2 else PAPER, 5, rx=4)]
        if i < 4:
            out.append(ln(f"M{x + 60} 224 H{x + 82}", 6))
    return "".join(out) + note(225, 284, "the record of every coin, on the chain", "middle")


def to2d():
    """From 3D to 2D: RLBench's 3D scenes, swapped within ten days for a 2D game made for the purpose."""
    cube = ('<path d="M70 120 L130 90 L190 120 L190 200 L130 230 L70 200Z" style="fill:var(--paper);stroke:var(--ink);stroke-width:5;stroke-linejoin:round"/>'
            '<path d="M70 120 L130 150 L190 120 M130 150 V230" style="fill:none;stroke:var(--ink);stroke-width:4"/>'
            '<path d="M130 150 L190 120 L190 200 L130 230Z" style="fill:var(--tone)"/>')
    grid = r(270, 80, 150, 150, PAPER, 5) + "".join(ln(f"M{270 + i * 30} 80 V230 M270 {80 + i * 30} H420", 1.5, colour="var(--muted)") for i in range(1, 5))
    return (cube + note(130, 266, "RLBench, 3D", "middle") + arrow(206, 155, 254, 155, 5) + note(230, 140, "10 days", "middle")
            + grid + dot(300, 200, 9, SPOT) + ring(390, 110, 11, 4) + r(330, 140, 30, 30, INK, 0) + note(345, 266, "a 2D game, made for it", "middle"))


def curvature():
    """Curvature: two tight clusters joined by one bridge; Ollivier–Ricci curvature is positive inside, negative on the bridge."""
    a = [(80, 90), (130, 60), (150, 130), (90, 170), (40, 130)]
    b = [(320, 110), (380, 70), (410, 140), (360, 190), (300, 180)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 4), (2, 4)]
    out = []
    for pts in (a, b):
        out += [ln(f"M{pts[i][0]} {pts[i][1]} L{pts[j][0]} {pts[j][1]}", 3) for i, j in edges]
    out.append(ln("M150 130 Q225 100 300 180", 6, colour="var(--live-red)"))
    for pts in (a, b):
        out += [dot(x, y, 9) for x, y in pts]
    out += [t(95, 124, "+", 26, "display", "middle", "fill:var(--art-win)"), t(355, 140, "+", 26, "display", "middle", "fill:var(--art-win)"),
            t(225, 104, "−", 30, "display", "middle", SPOT),
            note(225, 236, "positive inside, negative on the bridge", "middle"),
            note(225, 262, "the core: a Wasserstein distance", "middle"), note(225, 282, "between neighbourhoods", "middle")]
    return "".join(out)


def curious():
    """The question: an agent exploring for curiosity's sake, cells it has seen fading behind it, a question ahead."""
    path = [(0, 4), (1, 4), (1, 3), (2, 3), (3, 3), (3, 2), (4, 2), (4, 1), (5, 1), (6, 1), (6, 2), (7, 2)]
    seen = {(c, rr) for c, rr in path}
    cell, x0, y0 = 36, 63, 22
    out = []
    for c in range(9):
        for rr in range(6):
            if (c, rr) in seen:
                out.append(f'<rect x="{x0 + c * cell}" y="{y0 + rr * cell}" width="{cell}" height="{cell}" style="fill:var(--tone)"/>')
    out.append("".join(ln(f"M{x0 + i * cell} {y0} V{y0 + 6 * cell}", 1.5, colour="var(--muted)") for i in range(10))
               + "".join(ln(f"M{x0} {y0 + i * cell} H{x0 + 9 * cell}", 1.5, colour="var(--muted)") for i in range(7)))
    out.append(r(x0, y0, 9 * cell, 6 * cell, "fill:none", 5))
    n = len(path)
    frames = "".join(f"{k * 100 / (n - 1):.1f}%{{transform:translate({(c - path[-1][0]) * cell}px,{(rr - path[-1][1]) * cell}px)}}" for k, (c, rr) in enumerate(path))
    hx, hy = x0 + path[-1][0] * cell + cell / 2, y0 + path[-1][1] * cell + cell / 2
    out.append(motion(f"@keyframes cu-w{{{frames}}}.cu-w{{animation:cu-w 14s steps(1,end) infinite alternate}}"))
    out.append(f'<g class="mv cu-w">{dot(hx, hy, 11, SPOT)}</g>')
    out.append(t(x0 + 8.5 * cell, y0 + 4.7 * cell, "?", 44, "display", "middle"))
    out.append(note(225, 290, "how do you measure the wish to explore?", "middle"))
    return "".join(out)


def evidence():
    """Evidence, not examples: signals are fixed cards; how much each one weighs is worked out again every run."""
    ws = ((0.7, 0.4, 0.55), (0.35, 0.8, 0.5), (0.5, 0.3, 0.75), (0.2, 0.55, 0.35))
    css = []
    out = [t(30, 34, "signals, fixed", 14, "mono"), t(260, 34, "weight, every run", 14, "mono")]
    for i, w in enumerate(ws):
        y = 52 + i * 52
        css.append(f"@keyframes ev{i}{{0%,28%{{transform:scaleX({w[0]})}}36%,61%{{transform:scaleX({w[1]})}}69%,92%{{transform:scaleX({w[2]})}}100%{{transform:scaleX({w[0]})}}}}"
                   f".ev{i}{{transform-box:fill-box;transform-origin:left;transform:scaleX({w[0]});animation:ev{i} 15s ease-in-out infinite}}")
        out += [r(30, y, 150, 38, PAPER, 4, rx=4), f'<rect x="42" y="{y + 12}" width="{70 + 40 * seed("ev", i):.0f}" height="6" style="{MUTED}"/>',
                f'<rect x="42" y="{y + 24}" width="{40 + 50 * seed("ev2", i):.0f}" height="6" style="{MUTED}"/>',
                key_icon(160, y + 19, 0.5, 3) if False else ring(162, y + 19, 6, 3, INK),
                arrow(188, y + 19, 250, y + 19, 3, "5 5"), r(260, y + 6, 160, 26, "fill:none", 3),
                f'<rect class="mv ev{i}" x="263" y="{y + 9}" width="154" height="20" style="{SPOT if i == 1 else INK}"/>']
    out.insert(0, motion("".join(css)))
    return "".join(out) + note(225, 286, "retrieved and weighed, not shown as examples", "middle")


def wordle():
    """The reward: each guess's information gain, how far it narrows the possible answers."""
    guesses = (("crane", "_____"), ("solid", "y_y__"), ("blues", "ggg_y"))
    colours = {"g": "fill:var(--art-win)", "y": "fill:var(--art-glow)", "_": "fill:var(--tone)"}
    out = []
    for k, (word, marks) in enumerate(guesses):
        y = 30 + k * 64
        for j, (ch, m) in enumerate(zip(word, marks)):
            out += [r(24 + j * 50, y, 44, 52, colours[m], 4), t(46 + j * 50, y + 36, ch.upper(), 24, "display", "middle")]
    for k, w in enumerate((140, 84, 36, 6)):   # a picture of narrowing, not measured counts
        y = 44 + k * 64
        out += [f'<rect x="290" y="{y}" width="{w}" height="20" style="{SPOT if k == 3 else INK}"/>']
    out += [t(290, 30, "answers left", 13, "mono", fill=MUTED), t(304, 256, "1", 15, "mono")]
    out += [r(24, 222, 44, 52, "fill:none", 3, dash="6 5")] + [r(74 + j * 50, 222, 44, 52, "fill:none", 3, dash="6 5") for j in range(4)]
    return "".join(out) + note(225, 292, "reward: how much a guess narrows it", "middle")


def audit():
    """Auditing myself: the riskiest error was silent, upstream of the verifier; now each citation is graded by taking it out."""
    stages = ("ingest", "encode", "fuse", "verify")
    out = []
    for i, s in enumerate(stages):
        x = 16 + i * 108
        out += [r(x, 60, 92, 50, INK if s == "verify" else PAPER, 5, rx=4), t(x + 46, 90, s, 14, "mono", "middle", PAPER if s == "verify" else INK)]
        if i < 3:
            out.append(arrow(x + 94, 85, x + 106, 85, 3))
    out += [ring(170, 86, 46, 5, "fill:none"), ln("M204 118 L236 152", 9), dot(150, 74, 6, SPOT), note(20, 176, "silent error, upstream")]
    out += [r(240, 186, 190, 96, PAPER, 4), t(256, 212, "claim", 14, "display")]
    for k in range(3):
        y = 232 + k * 18
        out += [f'<rect x="256" y="{y - 8}" width="{80 + 30 * seed("au", k):.0f}" height="6" style="{MUTED}"/>', t(406, y, "−" if k == 1 else "✓", 14, "mono", "middle", SPOT if k == 1 else "fill:var(--art-win)")]
    return "".join(out) + note(20, 236, "each citation graded") + note(20, 254, "by removing it")


def nolinks():
    """Measure first: links between kinds of source, measured: none. Deferred on the evidence."""
    kinds = ("news", "gov", "econ", "opin")
    out = []
    for i, k in enumerate(kinds):
        out += [t(102 + i * 52, 40, k, 13, "mono", "middle"), t(70, 82 + i * 50, k, 13, "mono", "end")]
        for j in range(4):
            out += [r(78 + j * 52, 56 + i * 50, 48, 42, "fill:var(--tone)" if i == j else PAPER, 3),
                    t(102 + j * 52, 84 + i * 50, "" if i == j else "0", 18, "mono", "middle", MUTED)]
    return "".join(out) + stamp(370, 140, "deferred", -10, 20, spot=True, kind="display") + note(370, 190, "measured, not built", "middle")


def setaside():
    """Knowing when to stop: the campaign side boxed and set aside; what survived became RE-News."""
    out = [r(30, 50, 170, 130, PAPER, 5, dash="10 7"),
           t(115, 92, "campaign", 18, "display", "middle"), t(115, 116, "decision support", 13, "mono", "middle"),
           '<g transform="rotate(-6 115 150)">' + r(40, 136, 150, 26, "fill:var(--tone)", 3) + t(115, 154, "set aside", 14, "mono", "middle") + "</g>",
           note(115, 210, "profiling: legal and", "middle"), note(115, 226, "data-protection questions", "middle"),
           ln("M40 262 H90 M140 262 H190", 5), ln("M96 254 L104 270 M126 254 L134 270", 3, colour="var(--live-red)"),
           note(115, 290, "party attribution: too weak", "middle"),
           arrow(214, 115, 262, 115, 5), r(272, 65, 160, 100, INK, 5, rx=6), t(352, 124, "RE-News", 24, "display", "middle", PAPER),
           note(352, 192, "what survived", "middle")]
    return "".join(out)


def yolo():
    """Seeing: YOLOv5 boxes the enemy at about 60 fps on the player machine, against 16 for the first try."""
    return (ln("M0 300 L130 180 H320 L450 300 M0 0 L130 110 H320 L450 0 M130 110 V180 M320 110 V180", 3, colour="var(--muted)")
            + person(268, 118, 0.7) + r(246, 104, 46, 82, "fill:none", 4, dash=None).replace("var(--ink)", "var(--live-red)")
            + t(246, 98, "enemy", 12, "mono", fill=SPOT)
            + r(20, 20, 120, 56, INK, 4, rx=4) + t(80, 56, "60 fps", 22, "display", "middle", PAPER)
            + r(20, 90, 120, 40, PAPER, 3, rx=4, dash="6 5") + t(80, 116, "first try: 16", 13, "mono", "middle", MUTED)
            + note(225, 288, "YOLOv5, on the player machine", "middle"))


def lost():
    """It lost: successes out of ten, the hyperbolic policy against the rebuilt baseline, task by task."""
    tasks = (("reach goal", 2, 5), ("eat edibles", 1, 3), ("push, place", 0, 0), ("parking", 0, 0))
    out, base = [ln("M30 236 H430", 5)], 236
    for i, (name, mine, theirs) in enumerate(tasks):
        x = 46 + i * 100
        for k, (v, fill) in enumerate(((mine, SPOT), (theirs, INK))):
            h = v * 34
            if v:
                out.append(r(x + k * 38, base - h, 32, h, fill, 3))
            out.append(t(x + 16 + k * 38, base - h - 8, str(v), 15, "mono", "middle"))
        out.append(t(x + 35, 260, name, 12, "mono", "middle"))
    out += [r(250, 18, 14, 14, SPOT, 0), t(270, 30, "hyperbolic", 13, "mono"), r(250, 40, 14, 14, INK, 0), t(270, 52, "baseline", 13, "mono"),
            note(225, 290, "successes out of 10", "middle")]
    return "".join(out)


def institutional():
    """Its own limit: 94% of the corpus is institutional, so the ranker mostly ranks news volume."""
    return (r(30, 80, 390, 60, INK, 5) + r(30 + 390 * 0.94, 80, 390 * 0.06, 60, SPOT, 5)
            + t(200, 120, "94% institutional", 22, "display", "middle", PAPER) + note(420, 70, "social: 6%", "end")
            + t(225, 196, "ranks volume,", 20, "display", "middle") + t(225, 226, "not importance", 20, "display", "middle")
            + note(225, 270, "and the page says so", "middle"))


def archerloss():
    """The data: fourteen seasons of Archer subtitles; training loss from 7.5 to 4.4 over 200 epochs."""
    return (ln("M60 30 V240 H420", 4) + curve(64, 40, 350, 160, lambda s: 0.06 + 0.94 * (1 - (1 - math.exp(-5 * s)) / (1 - math.exp(-5))), 40, 5)
            + t(54, 46, "7.5", 14, "mono", "end") + t(54, 206, "4.4", 14, "mono", "end") + ln("M60 200 H420", 2, "4 6", "var(--muted)")
            + t(420, 262, "200 epochs", 13, "mono", "end") + t(320, 100, "S1–S14", 28, "display", "middle") + note(320, 126, "next line, given this one", "middle"))


def atlas():
    """Atlas: seven weeks, about 155 versions; a pipeline in a day, real data in a week, then six domains."""
    out = [ln("M30 150 H420", 5)]
    for w in range(8):
        out.append(ln(f"M{30 + w * 55.7:.0f} 138 V162", 4))
        if w < 7:
            out.append(t(58 + w * 55.7, 186, f"w{w + 1}", 12, "mono", "middle", MUTED))
    out += [ln(f"M{30 + 390 * seed('atl', i) ** 0.8:.0f} 118 v14", 2) for i in range(155)]
    out += [dot(36, 150, 9, SPOT), note(36, 100, "pipeline, day 1"), dot(86, 150, 9, SPOT), note(100, 72, "real data, week 1")]
    out += ["".join(r(30 + i * 66, 214, 58, 40, PAPER if i else INK, 4, rx=4) for i in range(6)), note(225, 282, "six domains, one citable shape", "middle")]
    return "".join(out)


def scan():
    """Scan: the LiDAR line sweeps the car and the points land behind it, then it sweeps back and takes them up again,
    a boomerang. Still, the sweep rests at the far end with every point showing."""
    cid = f"sc{next(_tone_ids)}"
    css = ("@keyframes sc-s{from{transform:translateX(0)}to{transform:translateX(320px)}}"
           ".sc-s{transform:translateX(320px);animation:sc-s 6s ease-in-out infinite alternate}")
    points = "".join(dot(70 + 310 * seed("lid", i), 80 + 100 * seed("lid2", i), 2.2, SPOT if i % 7 == 0 else INK) for i in range(120))
    return (motion(css) + f'<defs><clipPath id="{cid}"><rect class="mv sc-s" x="-252" y="0" width="320" height="300"/></clipPath></defs>'
            + car(60, 90, 330) + f'<g clip-path="url(#{cid})">{points}</g>'
            + ln("M40 40 L120 90 M40 40 L60 150", 2, "4 5") + r(20, 20, 30, 50, INK, 3, rx=5)
            + f'<g class="mv sc-s"><rect x="66" y="60" width="4" height="150" style="{SPOT};opacity:.55"/></g>')


ART.update({
    "vonneumann": vonneumann, "failclosed": failclosed, "perstage": perstage, "carbon": carbon, "to2d": to2d,
    "curvature": curvature, "curious": curious, "evidence": evidence, "wordle": wordle, "audit": audit,
    "nolinks": nolinks, "setaside": setaside, "yolo": yolo, "lost": lost, "institutional": institutional,
    "archerloss": archerloss, "atlas": atlas,
})


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


# ---------- the record and its sleeve (目次 and every volume page) ----------
def sleeve(n, vol, ch, name):
    """A volume as a record sleeve: square, the series band, the title and kana, the volume's picture on screentone,
    and the obi strip (red while the project runs)."""
    W, strip = 512, 62
    live = n.get("status") == "active"
    room = W - 24 - 58
    size, lines = fit_title(n["title"], room)
    size = min(size, 58 if len(lines) == 1 else 50)
    title = "".join(f'<text x="24" y="{46 + size * 0.95 * (i + 1):.0f}" textLength="{min(room, 0.86 * size * len(l)):.0f}" lengthAdjust="spacingAndGlyphs" '
                    f'style="{INK};font:400 {size:.0f}px var(--font-display)">{esc(l)}</text>' for i, l in enumerate(lines))
    top = 46 + size * 0.95 * len(lines) + 22
    pic_h = min(270, W - strip - 18 - top)
    pic_w = pic_h * 1.5
    pic = wallet_panel("phone") if ch.get("cover") == "wallet" else panel(ch["cover"], 3)
    pic = pic.replace("<svg ", f'<svg x="{(W - pic_w) / 2:.0f}" y="{top:.0f}" width="{pic_w:.0f}" height="{pic_h:.0f}" preserveAspectRatio="xMidYMid slice" ', 1)
    fill, text = (SPOT, ONSPOT) if live else (INK, PAPER)
    obi = ch.get("obi", "")
    return f"""<svg class="sleeve-art" viewBox="0 0 {W} {W}" role="img" aria-label="Sleeve of volume {vol}, {esc(n['title'])}.">
<rect width="{W}" height="{W}" style="{PAPER}"/>{tone_bands(n["id"], 0, top - 10, W, W - strip, 12, 3.6)}
<rect width="{W}" height="40" style="{INK}"/>
<text x="18" y="27" style="{PAPER};font:400 15px var(--font-display);letter-spacing:.04em">{esc(name)}</text>
<text x="{W - 18}" y="27" text-anchor="end" style="{PAPER};font:500 12px var(--font-mono);letter-spacing:.12em">VOL. {vol} · 33⅓</text>
{title}<text x="{W - 30}" y="64" style="{INK};font:700 24px var(--font-body);writing-mode:vertical-rl">{esc(ch.get("kana", ""))}</text>
<rect x="{(W - pic_w) / 2 - 5:.0f}" y="{top - 5:.0f}" width="{pic_w + 10:.0f}" height="{pic_h + 10:.0f}" style="{PAPER};stroke:var(--ink);stroke-width:5"/>{pic}
<rect y="{W - strip}" width="{W}" height="{strip}" style="{fill}"/>
<text x="20" y="{W - 24}" textLength="{min(W - 40, len(obi) * 15):.0f}" lengthAdjust="spacingAndGlyphs" style="{text};font:400 26px var(--font-display)">{esc(obi)}</text>
</svg>"""


def tone_bands(key, x0, y0, x1, y1, step, rmax, bands=8):
    """Screentone as tone() draws it, but as a few bands of repeating dot patterns instead of one circle per dot, so
    a page of twenty sleeves stays light. key keeps the pattern ids unique on the page."""
    defs, rects, h = [], [], (y1 - y0) / bands
    for i in range(bands):
        r = rmax * ((i + 0.5) / bands) ** 1.2
        pid = f"tb-{key}-{i}"
        defs.append(f'<pattern id="{pid}" width="{step}" height="{step * 0.87 * 2:.2f}" patternUnits="userSpaceOnUse">'
                    f'<circle cx="0" cy="0" r="{r:.2f}"/><circle cx="{step}" cy="0" r="{r:.2f}"/><circle cx="{step / 2}" cy="{step * 0.87:.2f}" r="{r:.2f}"/>'
                    f'<circle cx="0" cy="{step * 1.74:.2f}" r="{r:.2f}"/><circle cx="{step}" cy="{step * 1.74:.2f}" r="{r:.2f}"/></pattern>')
        rects.append(f'<rect x="{x0}" y="{y0 + i * h:.1f}" width="{x1 - x0}" height="{h + 0.5:.1f}" fill="url(#{pid})"/>')
    return f'<defs style="{INK}">{"".join(defs)}</defs><g>{"".join(rects)}</g>'


RECORD_GROOVES = (100, 242)   # the grooved band's inner and outer radius; the tonearm reads these (data-in, data-out)


def record(n, vol, ch):
    """The volume's record, centred on 0,0 with radius 250: one band of grooves per episode (the tracks), and a label
    that says which volume it is, red while the project runs. The label turns with the record, so a spin shows."""
    live = n.get("status") == "active"
    inner, outer = RECORD_GROOVES
    eps, gap = len(ch["episodes"]), 8
    span = (outer - inner - gap * (eps - 1)) / eps
    rings, r = [], outer
    for k in range(eps):
        end = r - span
        while r > end:
            rings.append(f'<circle r="{r:.1f}"/>')
            r -= 3.4
        r = end - gap
    label, on = ("var(--live-red)", "var(--live-on-red)") if live else ("var(--shelf-finished-band)", "var(--paper)")
    kana = esc(ch.get("kana", ""))
    return f"""<svg class="record" viewBox="-250 -250 500 500" aria-hidden="true" data-in="{inner}" data-out="{outer}">
<g class="spin"><circle r="248" style="fill:var(--paper);stroke:var(--record-edge);stroke-width:4"/>
<g style="fill:none;stroke:var(--record-grooves);stroke-width:1">{"".join(rings)}</g>
<circle r="90" style="fill:{label};stroke:var(--record-label-rim);stroke-width:3"/>
<text y="-46" text-anchor="middle" style="fill:{on};font:500 13px var(--font-mono);letter-spacing:.14em">VOL. {vol}</text>
<text y="10" text-anchor="middle" textLength="{min(140, 26 * len(ch.get("kana", "")))}" lengthAdjust="spacingAndGlyphs" style="fill:{on};font:700 26px var(--font-body)">{kana}</text>
<text y="56" text-anchor="middle" style="fill:{on};font:500 11px var(--font-mono);letter-spacing:.14em">33⅓ RPM</text>
<circle r="6" style="fill:var(--paper);stroke:var(--record-edge);stroke-width:2"/></g>
</svg>"""
