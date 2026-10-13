"""Генератор иллюстраций для уроков в духе книг Usborne начала 80-х
(«Understanding the Micro»): пухлые металлические роботы с красными глазами
изображают понятия программирования.

Картинки не содержат текста на человеческом языке — только код,
поэтому одни и те же SVG используются во всех языковых версиях.
Запуск: python3 tools/make_illustrations.py  →  assets/illustrations/*.svg
"""
import html
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "illustrations")
MONO = "DejaVu Sans Mono, Menlo, Consolas, monospace"
INK = "#1b1b1b"

# light, mid, dark
COLORS = {
    "steel": ("#eef7fc", "#93b6ca", "#34566a"),
    "cyan": ("#d4f6ff", "#49bfe3", "#155a74"),
    "purple": ("#c9b8ff", "#7b5cd6", "#352273"),
    "green": ("#c8f59a", "#5fbf3a", "#22631f"),
    "orange": ("#ffd9a0", "#ff9a2e", "#a84a0c"),
    "blue": ("#b5dbff", "#4c97f0", "#173f8f"),
    "red": ("#ffbcb5", "#ef5a4f", "#8a1f1a"),
    "yellow": ("#fff6b0", "#ffd43b", "#a87700"),
    "wood": ("#ffe08a", "#f0a92e", "#9c5a10"),
}


def defs(*extra):
    out = ["<defs>"]
    for name, (light, mid, dark) in COLORS.items():
        # "airbrushed" metal: dark edges, bright highlight left of centre
        out.append(
            f'<linearGradient id="m-{name}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{dark}"/><stop offset="0.22" stop-color="{mid}"/>'
            f'<stop offset="0.4" stop-color="{light}"/><stop offset="0.7" stop-color="{mid}"/>'
            f'<stop offset="1" stop-color="{dark}"/></linearGradient>'
        )
        out.append(
            f'<linearGradient id="v-{name}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{light}"/><stop offset="1" stop-color="{mid}"/></linearGradient>'
        )
    out.append(
        '<radialGradient id="eye" cx="0.38" cy="0.35" r="0.75">'
        '<stop offset="0" stop-color="#ffffff"/><stop offset="0.22" stop-color="#ff8a80"/>'
        '<stop offset="0.6" stop-color="#e01b1b"/><stop offset="1" stop-color="#7a0000"/></radialGradient>'
        '<linearGradient id="visor" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#4a5468"/><stop offset="1" stop-color="#1a1f2b"/></linearGradient>'
        '<linearGradient id="card" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#ece6d2"/></linearGradient>'
        '<linearGradient id="slot" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#5a8f1f"/><stop offset="1" stop-color="#d7ef6a"/></linearGradient>'
    )
    out.extend(extra)
    out.append("</defs>")
    return "".join(out)


def ik(sx, sy, tx, ty, l1, l2, outward):
    """Two-segment arm: elbow position so that the hand reaches (tx, ty), elbow bent outwards."""
    dx, dy = tx - sx, ty - sy
    d = min(math.hypot(dx, dy), l1 + l2 - 0.01)
    d = max(d, abs(l1 - l2) + 0.01)
    base = math.atan2(dy, dx)
    a = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    cands = [(sx + l1 * math.cos(base + s * a), sy + l1 * math.sin(base + s * a)) for s in (1, -1)]
    return max(cands, key=lambda p: p[0] * outward)


def limb(x1, y1, x2, y2, color, width):
    """A ribbed, spring-like limb segment."""
    light, mid, dark = COLORS[color]
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="{width + 3}"/>'
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{mid}" stroke-width="{width}"/>'
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{light}" stroke-width="{width - 2}" stroke-dasharray="2.5 3"/>'
    )


def arm(sx, sy, hand, color, outward):
    l1, l2 = 24, 24
    ex, ey = ik(sx, sy, hand[0], hand[1], l1, l2, outward)
    ang = math.atan2(hand[1] - ey, hand[0] - ex)
    hx, hy = ex + l2 * math.cos(ang), ey + l2 * math.sin(ang)
    light, mid, dark = COLORS[color]
    deg = math.degrees(ang)
    return (
        '<g stroke-linecap="round">'
        + limb(sx, sy, ex, ey, color, 8)
        + limb(ex, ey, hx, hy, color, 7)
        + f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5.5" fill="{dark}" stroke="{INK}" stroke-width="1.5"/>'
        # claw hand
        + f'<g transform="translate({hx:.1f},{hy:.1f}) rotate({deg:.0f})">'
        f'<circle r="6.5" fill="url(#m-{color})" stroke="{INK}" stroke-width="1.5"/>'
        f'<path d="M4,-6 q9,-1 9,5 M4,6 q9,1 9,-5" stroke="{INK}" stroke-width="3.5" fill="none"/>'
        f'<path d="M4,-6 q9,-1 9,5 M4,6 q9,1 9,-5" stroke="{mid}" stroke-width="1.8" fill="none"/></g>'
        "</g>"
    ), (hx, hy)


def robot(x, y, s, color, left=(-34, 62), right=(34, 62), look=0, chest=None):
    """A friendly robot. (x, y) is the point between its feet; hands are given in local coords
    (origin at the neck, y down, body ~52 wide, feet at y=90). Returns (svg, to_world)."""
    light, mid, dark = COLORS[color]
    oy = -90
    st = f'stroke="{INK}" stroke-width="1.6"'
    p = [f'<g transform="translate({x},{y}) scale({s}) translate(0,{oy})">']
    p.append('<ellipse cx="0" cy="92" rx="36" ry="7" fill="#000" opacity="0.2"/>')
    # legs: ribbed, with round feet
    for lx in (-14, 14):
        p.append(f'<g stroke-linecap="round">{limb(lx, 60, lx, 82, color, 9)}</g>')
        p.append(f'<path d="M{lx - 14},92 q0,-13 14,-13 q14,0 14,13 z" fill="url(#m-{color})" {st}/>')
    # body: a short cylinder
    p.append(f'<path d="M-27,14 v42 a27,9 0 0 0 54,0 v-42 z" fill="url(#m-{color})" {st}/>')
    p.append(f'<ellipse cx="0" cy="14" rx="27" ry="9" fill="url(#v-{color})" {st}/>')
    if chest:
        p.append(chest)
    else:
        p.append(f'<rect x="-15" y="28" width="30" height="18" rx="4" fill="url(#visor)" {st}/>')
        for i, c in enumerate(("#ff5d5d", "#ffd43b", "#5ce07a")):
            p.append(f'<circle cx="{-8 + i * 8}" cy="37" r="3" fill="{c}"/>')
    # neck
    p.append(f'<rect x="-6" y="0" width="12" height="9" fill="{dark}" {st}/>')
    # antenna
    p.append(f'<path d="M0,-44 q{look * 3},-8 {look * 6},-14" stroke="{INK}" stroke-width="2.5" fill="none"/>')
    p.append(f'<circle cx="{look * 6}" cy="-59" r="5" fill="url(#eye)" {st}/>')
    # ears
    for ex in (-26, 26):
        p.append(f'<rect x="{ex - 5}" y="-26" width="10" height="16" rx="4" fill="url(#m-{color})" {st}/>')
    # domed head
    p.append(f'<path d="M-24,2 v-22 a24,22 0 0 1 48,0 v22 q0,4 -4,4 h-40 q-4,0 -4,-4 z" fill="url(#m-{color})" {st}/>')
    p.append(f'<rect x="-20" y="-26" width="40" height="18" rx="9" fill="url(#visor)" {st}/>')
    for ex in (-9, 9):
        p.append(f'<circle cx="{ex + look * 2}" cy="-17" r="6.5" fill="url(#eye)" stroke="{INK}" stroke-width="1"/>')
    for gx in (-6, 0, 6):
        p.append(f'<line x1="{gx}" y1="-3" x2="{gx}" y2="1" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    # arms
    left_svg, left_hand = arm(-27, 20, left, color, -1)
    right_svg, right_hand = arm(27, 20, right, color, 1)
    p.append(left_svg)
    p.append(right_svg)
    p.append("</g>")

    def world(pt):
        return (x + pt[0] * s, y + (pt[1] + oy) * s)

    world.left = world(left_hand)
    world.right = world(right_hand)
    return "".join(p), world


def card(cx, cy, text, w=None, rot=0, size=20, color="#1d2140"):
    text = html.escape(text, quote=False)
    w = w or max(34, 12.5 * len(text) + 16)
    h = size + 14
    return (
        f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot})">'
        f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="url(#card)" stroke="{INK}" stroke-width="1.5"/>'
        f'<text x="0" y="{size * 0.35:.1f}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="{size}" fill="{color}">{text}</text>'
        f"</g>"
    )


def bubble(x, y, w, h, code, tail=(-30, 30), size=18):
    code = html.escape(code, quote=False)
    """A cloud-like speech bubble with a line of code. (x, y) is its centre."""
    bumps = []
    n = 7
    for i in range(n):
        a = 2 * math.pi * i / n
        bumps.append(f'<ellipse cx="{x + math.cos(a) * w * 0.36:.1f}" cy="{y + math.sin(a) * h * 0.3:.1f}" rx="{w * 0.28:.1f}" ry="{h * 0.36:.1f}"/>')
    tx, ty = tail
    return (
        f'<g fill="#fff59d" stroke="{INK}" stroke-width="2">'
        f'<path d="M{x + tx * 0.3:.1f},{y + h * 0.3:.1f} L{x + tx:.1f},{y + ty + h * 0.3:.1f} L{x + tx * 0.3 + 18:.1f},{y + h * 0.3:.1f} z"/>'
        + "".join(bumps)
        + f'</g><g fill="#fff59d">'
        + f'<ellipse cx="{x}" cy="{y}" rx="{w * 0.5:.1f}" ry="{h * 0.4:.1f}"/></g>'
        f'<text x="{x}" y="{y + size * 0.35:.1f}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="{size}" fill="#1d2140">{code}</text>'
    )


def scene(w, h, bg, body):
    top, bottom = bg
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        + defs(
            f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient>'
        )
        + f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" fill="url(#bg)" stroke="{INK}" stroke-width="3"/>'
        + body
        + "</svg>"
    )


def cells_floor(x, y, n, size):
    """A strip of the dark game field with a grid, top-left at (x, y)."""
    out = [f'<rect x="{x - 8}" y="{y - 8}" width="{n * size + 16}" height="{size + 16}" rx="10" fill="#1e1f29" stroke="{INK}" stroke-width="2"/>']
    for i in range(n):
        out.append(f'<rect x="{x + i * size + 1}" y="{y + 1}" width="{size - 2}" height="{size - 2}" rx="3" fill="#2a2c3a"/>')
    return "".join(out)


def block(x, y, size, color, opacity=1):
    light, mid, dark = COLORS[color]
    return (
        f'<g opacity="{opacity}"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="5" fill="url(#v-{color})" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{x + 5}" y="{y + 4}" width="{size - 10}" height="6" rx="3" fill="#fff" opacity="0.5"/></g>'
    )


def apple(cx, cy, r=24):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ef3b3b" stroke="{INK}" stroke-width="2"/>'
        f'<ellipse cx="{cx - r * 0.38}" cy="{cy - r * 0.4}" rx="{r * 0.28}" ry="{r * 0.2}" fill="#fff" opacity="0.55"/>'
        f'<path d="M{cx},{cy - r + 2} q2,-12 10,-16" stroke="#6b3d12" stroke-width="4" fill="none"/>'
        f'<path d="M{cx + 4},{cy - r - 6} q16,-10 24,2 q-14,8 -24,-2z" fill="#5fbf3a" stroke="{INK}" stroke-width="1.5"/>'
    )


def pigeonholes(x, y, cols, rows, cw, ch, labels):
    """A wooden pigeon-hole cabinet like in the book; labels[r][c] -> (name, value or None)."""
    w, h = cols * cw, rows * ch
    d = 22
    light, mid, dark = COLORS["wood"]
    out = [
        f'<ellipse cx="{x + w / 2 + 10}" cy="{y + h + 4}" rx="{w / 2 + 30}" ry="9" fill="#000" opacity="0.18"/>',
        f'<path d="M{x},{y} l{d},{-d} h{w} l{-d},{d} z" fill="{light}" stroke="{INK}" stroke-width="2"/>',
        f'<path d="M{x + w},{y} l{d},{-d} v{h} l{-d},{d} z" fill="{dark}" stroke="{INK}" stroke-width="2"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{mid}" stroke="{INK}" stroke-width="2"/>',
    ]
    for r in range(rows):
        for c in range(cols):
            sx, sy = x + c * cw + 7, y + r * ch + 7
            out.append(f'<rect x="{sx}" y="{sy}" width="{cw - 14}" height="{ch - 14}" fill="url(#slot)" stroke="{INK}" stroke-width="1.5"/>')
            name, value = labels[r][c]
            if value is not None:
                out.append(card(sx + (cw - 14) / 2 + 4, sy + ch * 0.42, value, rot=-4 + 6 * ((r + c) % 2), size=18))
            out.append(
                f'<rect x="{sx + 6}" y="{sy + ch - 34}" width="{cw - 26}" height="22" rx="3" fill="#fffdf3" stroke="{INK}" stroke-width="1.5"/>'
                f'<text x="{sx + (cw - 14) / 2}" y="{sy + ch - 18}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="15" fill="#1d2140">{name}</text>'
            )
    return "".join(out)


# ---------------------------------------------------------------- scenes

def variables():
    w, h = 680, 380
    floor = 352
    body = []
    labels = [
        [("score", None), ("lives", "3"), ("speed", "200")],
        [("apples", "5"), ("size", "20"), ("year", "2026")],
    ]
    body.append(pigeonholes(300, 120, 3, 2, 112, 112, labels))
    # the robot puts "10" into the empty score slot
    svg, world = robot(185, floor, 1.3, "steel", left=(-40, 58), right=(62, -18), look=1)
    body.append(svg)
    hx, hy = world.right
    body.append(card(hx + 20, hy - 8, "10", rot=10))
    body.append(f'<path d="M{hx + 44},{hy - 14} Q{hx + 80},{hy - 70} 352,148" stroke="#5b6b7a" stroke-width="3" fill="none" stroke-dasharray="6 6"/>')
    body.append(bubble(140, 72, 220, 80, "score = 10;", tail=(30, 46)))
    return scene(w, h, ("#fff7b8", "#ffd44f"), "".join(body))


def array_snake():
    w, h = 680, 380
    size = 112
    x0, y0 = 62, 250
    body = [cells_floor(x0, y0, 5, size)]
    body.append(f'<g transform="translate(30,24)"><rect width="282" height="44" rx="8" fill="#123d16" stroke="{INK}" stroke-width="2"/>'
                f'<text x="16" y="29" font-family="{MONO}" font-size="20" font-weight="700" fill="#7CFC7C">let snake = [ … ];</text></g>')
    body.append(apple(x0 + 4 * size + size / 2, y0 + 66))
    data = [("yellow", "[0]", "10,10"), ("green", "[1]", "9,10"), ("green", "[2]", "8,10")]
    for i, (color, idx, xy) in enumerate(data):
        cx = x0 + (3 - i) * size + size / 2 - size
        chest = (f'<rect x="-19" y="25" width="38" height="22" rx="4" fill="url(#visor)" stroke="{INK}" stroke-width="1.5"/>'
                 f'<text x="0" y="41" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="#7CFC7C">{xy}</text>')
        svg, world = robot(cx, y0 + size * 0.86, 1.0, color, left=(-24, -76), right=(24, -76), look=1, chest=chest)
        body.append(svg)
        lx, ly = world((0, -84))
        body.append(card(lx, ly - 4, idx, w=62, size=22, color="#c2410c"))
    return scene(w, h, ("#dff4ff", "#86c9f5"), "".join(body))


def unshift_pop():
    w, h = 680, 380
    size = 70
    x0, y0 = 165, 262
    body = [cells_floor(x0, y0, 5, size)]
    for i in (1, 2):
        body.append(block(x0 + i * size + 4, y0 + 4, size - 8, "green"))
    body.append(f'<rect x="{x0 + 6}" y="{y0 + 6}" width="{size - 12}" height="{size - 12}" rx="5" fill="none" stroke="#ff8a80" stroke-width="2.5" stroke-dasharray="6 5"/>')
    for i, xy in enumerate(("8,10", "9,10", "10,10", "11,10")):
        body.append(f'<text x="{x0 + i * size + size / 2}" y="{y0 + size + 28}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="#5a3a1a">{xy}</text>')
    body.append(f'<rect x="{x0 + 3 * size + 6}" y="{y0 + 6}" width="{size - 12}" height="{size - 12}" rx="5" fill="none" stroke="#ffd43b" stroke-width="2.5" stroke-dasharray="6 5"/>')
    # red robot carries the tail away
    svg, world = robot(66, y0 + 56, 0.95, "red", left=(-22, -74), right=(22, -74), look=-1)
    body.append(svg)
    tx, ty = world((0, -90))
    body.append(block(tx - 28, ty - 28, 56, "green", opacity=0.8))
    body.append(card(84, 42, "snake.pop()", size=17, color="#b42318"))
    # cyan robot brings the new head
    svg, world = robot(610, y0 + 56, 0.95, "cyan", left=(-22, -74), right=(22, -74), look=-1)
    body.append(svg)
    hx, hy = world((0, -90))
    body.append(block(hx - 28, hy - 28, 56, "yellow"))
    body.append(card(530, 42, "snake.unshift(head)", size=17, color="#1d4ed8"))
    body.append(f'<path d="M{x0 + size / 2},{y0 - 8} C{x0 + 20},{y0 - 110} 120,{ty + 50} 98,{ty + 30}" stroke="#d63b2f" stroke-width="3" fill="none" stroke-dasharray="7 6"/>')
    body.append(f'<path d="M{hx - 34},{hy + 10} C530,{y0 - 130} {x0 + 3 * size + 60},{y0 - 80} {x0 + 3 * size + size / 2},{y0 - 8}" stroke="#b07d00" stroke-width="3" fill="none" stroke-dasharray="7 6"/>')
    return scene(w, h, ("#ffe9d6", "#ffb27a"), "".join(body))


# ---------------------------------------------------------------- more props

def keycap(x, y, w, h, label, pressed=False, size=22, face="#f6f1e2"):
    label = html.escape(label, quote=False)
    """A chunky 3D keyboard key; (x, y) is the top-left of its top face."""
    depth = 4 if pressed else 12
    dy = 8 if pressed else 0
    return (
        f'<g transform="translate(0,{dy})">'
        f'<rect x="{x}" y="{y + depth}" width="{w}" height="{h}" rx="9" fill="#9a927c" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{face}" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{x + 6}" y="{y + 5}" width="{w - 12}" height="{h - 14}" rx="6" fill="#ffffff" opacity="0.55"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + size * 0.35}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="{size}" fill="#1d2140">{label}</text>'
        "</g>"
    )


def label(x, y, text, size=17, color="#1d2140", bg="#fffdf3", rot=0):
    text = html.escape(text, quote=False)
    """A code label on a plate; (x, y) is its centre."""
    w = 10.5 * len(text) * size / 17 + 22
    h = size + 14
    return (
        f'<g transform="translate({x},{y}) rotate({rot})">'
        f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h}" rx="7" fill="{bg}" stroke="{INK}" stroke-width="2"/>'
        f'<text x="0" y="{size * 0.36:.1f}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="{size}" fill="{color}">{text}</text>'
        "</g>"
    )


def screen_lines(x, y, lines, size=13, gap=19):
    out = []
    for i, parts in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i * gap}" font-family="{MONO}" font-size="{size}" font-weight="700">')
        for text, color in parts:
            out.append(f'<tspan fill="{color}">{text}</tspan>')
        out.append("</text>")
    return "".join(out)


def bug(cx, cy, s=1.0, rot=0):
    """A ladybird-like computer bug."""
    legs = "".join(
        f'<path d="M{sx * 8},{ly} q{sx * 12},{-4} {sx * 18},{ly / 2 + 6}" stroke="{INK}" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        for sx in (-1, 1) for ly in (-6, 2, 10)
    )
    return (
        f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">{legs}'
        f'<path d="M-5,-18 q-6,-10 -12,-12 M5,-18 q6,-10 12,-12" stroke="{INK}" stroke-width="2" fill="none"/>'
        f'<circle cx="-17" cy="-30" r="2.5" fill="{INK}"/><circle cx="17" cy="-30" r="2.5" fill="{INK}"/>'
        f'<circle cx="0" cy="-15" r="8" fill="#222"/>'
        f'<ellipse cx="0" cy="2" rx="15" ry="17" fill="#e8322b" stroke="{INK}" stroke-width="2"/>'
        f'<line x1="0" y1="-14" x2="0" y2="19" stroke="{INK}" stroke-width="2"/>'
        f'<circle cx="-7" cy="-2" r="3.2" fill="{INK}"/><circle cx="7" cy="5" r="3.2" fill="{INK}"/><circle cx="-6" cy="10" r="2.6" fill="{INK}"/><circle cx="8" cy="-6" r="2.6" fill="{INK}"/>'
        f'<circle cx="-3" cy="-17" r="2" fill="#fff"/><circle cx="3" cy="-17" r="2" fill="#fff"/>'
        "</g>"
    )


def star(cx, cy, r, color="#ffd43b", rot=0):
    pts = []
    for i in range(10):
        a = math.pi / 5 * i - math.pi / 2 + math.radians(rot)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'


def hat_beret(color="#c0392b"):
    return f'<ellipse cx="4" cy="-44" rx="26" ry="9" fill="{color}" stroke="{INK}" stroke-width="1.6"/><circle cx="4" cy="-54" r="3" fill="{color}" stroke="{INK}" stroke-width="1.2"/>'


def stopwatch(cx, cy, r, hand_deg=40, face="#fffdf3"):
    a = math.radians(hand_deg - 90)
    ticks = "".join(
        f'<line x1="{cx + (r - 6) * math.cos(math.radians(t * 30)):.1f}" y1="{cy + (r - 6) * math.sin(math.radians(t * 30)):.1f}" '
        f'x2="{cx + (r - 14) * math.cos(math.radians(t * 30)):.1f}" y2="{cy + (r - 14) * math.sin(math.radians(t * 30)):.1f}" stroke="{INK}" stroke-width="2"/>'
        for t in range(12)
    )
    return (
        f'<rect x="{cx - 9}" y="{cy - r - 22}" width="18" height="14" rx="3" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{cx - 16}" y="{cy - r - 30}" width="32" height="10" rx="4" fill="url(#m-red)" stroke="{INK}" stroke-width="2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{face}" stroke="{INK}" stroke-width="2"/>{ticks}'
        f'<line x1="{cx}" y1="{cy}" x2="{cx + (r - 14) * math.cos(a):.1f}" y2="{cy + (r - 14) * math.sin(a):.1f}" stroke="#d63b2f" stroke-width="4" stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{cy}" r="5" fill="{INK}"/>'
    )


def browser_window(x, y, w, h, inner=""):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fbfbfd" stroke="{INK}" stroke-width="2"/>'
        f'<path d="M{x},{y + 22} h{w}" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="21" rx="7" fill="#e3e6ee"/>'
        + "".join(f'<circle cx="{x + 14 + i * 14}" cy="{y + 11}" r="4.5" fill="{c}" stroke="{INK}" stroke-width="1"/>' for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")))
        + inner
    )


def mini_game(x, y, cell, cols, rows, snake_cells, apple_cell=None, bg="#111"):
    out = [f'<rect x="{x}" y="{y}" width="{cols * cell}" height="{rows * cell}" fill="{bg}"/>']
    for i, (cx, cy) in enumerate(snake_cells):
        out.append(f'<rect x="{x + cx * cell + 1}" y="{y + cy * cell + 1}" width="{cell - 2}" height="{cell - 2}" fill="{"#ffd43b" if i == 0 else "#32cd32"}"/>')
    if apple_cell:
        out.append(f'<circle cx="{x + apple_cell[0] * cell + cell / 2}" cy="{y + apple_cell[1] * cell + cell / 2}" r="{cell / 2 - 1}" fill="#ef3b3b"/>')
    return "".join(out)


# ---------------------------------------------------------------- scenes for every lesson

def setup():
    w, h = 680, 380
    body = []
    # desk
    body.append(f'<rect x="30" y="252" width="500" height="20" rx="4" fill="url(#v-wood)" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="50" y="272" width="16" height="92" fill="url(#m-wood)" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="494" y="272" width="16" height="92" fill="url(#m-wood)" stroke="{INK}" stroke-width="2"/>')
    # monitor
    body.append(f'<rect x="250" y="226" width="60" height="28" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="210" y="246" width="140" height="10" rx="4" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="80" y="36" width="400" height="196" rx="14" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="96" y="50" width="368" height="166" rx="6" fill="#1e1f29" stroke="{INK}" stroke-width="2"/>')
    # Geany on the left half
    body.append(f'<rect x="100" y="54" width="178" height="18" fill="#5fbf3a"/>'
                f'<text x="108" y="68" font-family="{MONO}" font-size="12" font-weight="700" fill="#fff">Geany</text>')
    body.append(screen_lines(104, 92, [
        [("1 ", "#6c6f85"), ("&lt;canvas&gt;", "#8be9fd")],
        [("2 ", "#6c6f85"), ("let ", "#ff79c6"), ("size = 20;", "#ecebe8")],
        [("3 ", "#6c6f85"), ("function ", "#ff79c6"), ("draw", "#50fa7b"), ("() {", "#ecebe8")],
        [("4 ", "#6c6f85"), ("  drawCell(", "#ecebe8"), ("10", "#bd93f9"), (",…", "#ecebe8")],
        [("5 ", "#6c6f85"), ("}", "#ecebe8")],
        [("6 ", "#6c6f85"), ("draw();", "#ecebe8")],
    ], size=11, gap=19))
    # browser on the right half
    body.append(browser_window(286, 56, 172, 154, mini_game(312, 90, 12, 10, 9, [(5, 4), (4, 4), (3, 4)], (8, 2))))
    # keyboard with programmer keys
    body.append(f'<rect x="104" y="272" width="320" height="70" rx="10" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>')
    body.append(keycap(118, 280, 52, 46, "{"))
    body.append(keycap(178, 280, 52, 46, "}"))
    body.append(keycap(238, 280, 52, 46, ";"))
    body.append(keycap(298, 280, 52, 46, "("))
    body.append(keycap(358, 280, 52, 46, ")"))
    # Raspberry Pi board
    body.append(f'<rect x="420" y="232" width="92" height="20" rx="3" fill="#1f8a4c" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="436" y="226" width="22" height="10" fill="#2b2b2b" stroke="{INK}" stroke-width="1.5"/>'
                f'<rect x="466" y="228" width="16" height="8" fill="url(#m-steel)" stroke="{INK}" stroke-width="1.5"/>'
                f'<circle cx="500" cy="238" r="5" fill="#d6336c" stroke="{INK}" stroke-width="1.5"/>')
    svg, world = robot(600, 360, 1.15, "steel", left=(-70, -20), right=(36, 60), look=-1)
    body.append(svg)
    return scene(w, h, ("#e3f3ff", "#a8d8ff"), "".join(body))


def save_refresh():
    w, h = 680, 380
    body = []
    body.append(keycap(40, 250, 120, 74, "Ctrl", size=26))
    body.append(f'<text x="182" y="300" font-family="{MONO}" font-size="40" font-weight="700" fill="#1d2140">+</text>')
    body.append(keycap(218, 250, 92, 74, "S", pressed=True, size=32))
    body.append(f'<path d="M340,290 h60" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M392,276 l18,14 l-18,14" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(keycap(440, 250, 110, 74, "F5", size=30))
    # robot jumping on S
    svg, world = robot(264, 250, 0.95, "purple", left=(-60, -40), right=(60, -40), look=0)
    body.append(svg)
    for dx in (-48, 48):
        body.append(f'<path d="M{264 + dx},{262} l{dx * 0.25},10" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    # floppy disk above S
    body.append(f'<g transform="translate(150,40)"><rect width="64" height="64" rx="6" fill="#3b5bdb" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="14" y="4" width="36" height="20" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/><rect x="36" y="8" width="8" height="12" fill="#3b5bdb"/>'
                f'<rect x="10" y="34" width="44" height="26" rx="2" fill="#fffdf3" stroke="{INK}" stroke-width="2"/></g>')
    # second robot pressing F5, a refresh symbol above
    svg, world = robot(610, 360, 1.0, "green", left=(-62, 16), right=(40, 60), look=-1)
    body.append(svg)
    body.append(f'<g transform="translate(495,82)"><circle r="34" fill="#fffdf3" stroke="{INK}" stroke-width="2.5"/>'
                f'<path d="M18,-12 A22,22 0 1 0 22,6" fill="none" stroke="#1d4ed8" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M8,-20 L26,-16 L20,2 z" fill="#1d4ed8"/></g>')
    return scene(w, h, ("#fff7b8", "#ffd44f"), "".join(body))


def console_bug():
    w, h = 680, 380
    body = []
    body.append(f'<rect x="34" y="40" width="440" height="270" rx="12" fill="#1e1f29" stroke="{INK}" stroke-width="3"/>'
                f'<rect x="34" y="40" width="440" height="30" rx="12" fill="#3a3d4f"/>'
                f'<rect x="34" y="58" width="440" height="12" fill="#3a3d4f"/>'
                f'<text x="52" y="61" font-family="{MONO}" font-size="14" font-weight="700" fill="#e3e6ee">Console</text>')
    body.append(screen_lines(52, 104, [
        [("&gt;&gt; ", "#8a93b2"), ("2 + 2", "#ecebe8")],
        [("4", "#bd93f9")],
        [("&gt;&gt; ", "#8a93b2"), ("console.log(", "#ecebe8"), ("\"OK\"", "#f1fa8c"), (")", "#ecebe8")],
        [("OK", "#ecebe8")],
    ], size=15, gap=28))
    body.append(f'<rect x="44" y="214" width="420" height="58" rx="6" fill="#4a1d1f" stroke="#ff6b6b" stroke-width="2"/>')
    body.append(screen_lines(56, 238, [
        [("✖ ReferenceError:", "#ff6b6b")],
        [("consol is not defined   :10", "#ffb3b3")],
    ], size=15, gap=24))
    body.append(bug(372, 244, 0.9, rot=20))
    # detective robot with a magnifying glass
    hat = (f'<path d="M-26,-38 q26,-26 52,0 z" fill="#8a5a2b" stroke="{INK}" stroke-width="1.6"/>'
           f'<path d="M-30,-38 h60" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    svg, world = robot(570, 360, 1.25, "steel", left=(-72, -12), right=(40, 58), look=-1)
    body.append(svg)
    body.append(f'<g transform="translate(570,360) scale(1.25) translate(0,-90)">{hat}</g>')
    hx, hy = world.left
    lx, ly = 372, 240
    body.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{lx + 40}" y2="{ly + 18}" stroke="#6b3d12" stroke-width="9" stroke-linecap="round"/>'
                f'<circle cx="{lx}" cy="{ly}" r="44" fill="#bfe9ff" fill-opacity="0.15" stroke="{INK}" stroke-width="7"/>'
                f'<circle cx="{lx}" cy="{ly}" r="44" fill="none" stroke="url(#m-yellow)" stroke-width="4"/>'
                f'<path d="M{lx - 26},{ly - 18} q10,-14 26,-16" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.8"/>')
    return scene(w, h, ("#e5fff2", "#9fe6c4"), "".join(body))


def canvas_paint():
    w, h = 680, 380
    body = []
    # easel
    body.append(f'<path d="M300,330 L360,40 M560,330 L500,40 M430,40 V360" stroke="#9c5a10" stroke-width="12" stroke-linecap="round"/>'
                f'<path d="M300,330 L360,40 M560,330 L500,40 M430,40 V360" stroke="#f0a92e" stroke-width="6" stroke-linecap="round"/>')
    cx0, cy0, cw = 300, 40, 280
    body.append(f'<rect x="{cx0 - 6}" y="{cy0 - 6}" width="{cw + 12}" height="{cw + 12}" fill="url(#v-wood)" stroke="{INK}" stroke-width="2"/>'
                f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{cw}" fill="#111" stroke="{INK}" stroke-width="2"/>')
    for i in range(1, 7):
        body.append(f'<line x1="{cx0 + i * 40}" y1="{cy0}" x2="{cx0 + i * 40}" y2="{cy0 + cw}" stroke="#2c2f3d"/>'
                    f'<line x1="{cx0}" y1="{cy0 + i * 40}" x2="{cx0 + cw}" y2="{cy0 + i * 40}" stroke="#2c2f3d"/>')
    body.append(f'<path d="M{cx0 + 8},{cy0 + 14} h80" stroke="#ff9a2e" stroke-width="4"/><path d="M{cx0 + 84},{cy0 + 7} l10,7 l-10,7" fill="#ff9a2e"/>'
                f'<text x="{cx0 + 100}" y="{cy0 + 20}" font-family="{MONO}" font-size="18" font-weight="700" fill="#ff9a2e">x</text>'
                f'<path d="M{cx0 + 14},{cy0 + 8} v80" stroke="#ff9a2e" stroke-width="4"/><path d="M{cx0 + 7},{cy0 + 84} l7,10 l7,-10" fill="#ff9a2e"/>'
                f'<text x="{cx0 + 8}" y="{cy0 + 114}" font-family="{MONO}" font-size="18" font-weight="700" fill="#ff9a2e">y</text>')
    k = cw / 400  # the lesson's canvas is 400 px wide: head at (200, 200), apple at (300, 100)
    body.append(f'<rect x="{cx0 + 200 * k:.1f}" y="{cy0 + 200 * k:.1f}" width="{20 * k * 1.6:.1f}" height="{20 * k * 1.6:.1f}" fill="#32cd32"/>'
                f'<rect x="{cx0 + 300 * k:.1f}" y="{cy0 + 100 * k:.1f}" width="{20 * k * 1.6:.1f}" height="{20 * k * 1.6:.1f}" fill="#ef3b3b"/>')
    # painter robot
    svg, world = robot(150, 360, 1.25, "orange", left=(-50, 20), right=(56, -36), look=1)
    body.append(svg)
    body.append(f'<g transform="translate(150,360) scale(1.25) translate(0,-90)">{hat_beret()}</g>')
    hx, hy = world.right
    tx, ty = cx0 + 200 * cw / 400, cy0 + 200 * cw / 400 + 10
    body.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{tx}" y2="{ty}" stroke="#9c5a10" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M{tx - 6},{ty - 8} l14,4 l-6,16 q-14,-2 -8,-20z" fill="#32cd32" stroke="{INK}" stroke-width="1.5"/>')
    lx, ly = world.left
    body.append(f'<path d="M{lx - 40},{ly + 6} q0,-30 40,-30 q40,0 40,24 q0,14 -18,10 q-12,-2 -12,10 q0,10 -14,10 q-36,0 -36,-24z" fill="url(#v-wood)" stroke="{INK}" stroke-width="2"/>'
                + "".join(f'<circle cx="{lx - 24 + i * 14}" cy="{ly - 12 + (i % 2) * 8}" r="5" fill="{c}" stroke="{INK}" stroke-width="1"/>' for i, c in enumerate(("#ef3b3b", "#32cd32", "#4c97f0", "#ffd43b"))))
    body.append(label(150, 40, "ctx.fillRect(x, y, 20, 20)", size=15))
    return scene(w, h, ("#fff0e0", "#ffc89a"), "".join(body))


def function_machine():
    w, h = 680, 380
    body = []
    # machine body
    body.append(f'<path d="M290,60 h120 l-30,50 h-60 z" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="230" y="108" width="240" height="190" rx="18" fill="url(#m-purple)" stroke="{INK}" stroke-width="3"/>'
                f'<rect x="252" y="128" width="196" height="40" rx="8" fill="#fffdf3" stroke="{INK}" stroke-width="2"/>'
                f'<text x="350" y="155" text-anchor="middle" font-family="{MONO}" font-size="18" font-weight="700" fill="#1d2140">drawCell</text>')
    for gx, gy, r in ((290, 220, 30), (352, 240, 22), (410, 214, 26)):
        teeth = "".join(f'<rect x="{gx - 5}" y="{gy - r - 8}" width="10" height="12" fill="url(#m-yellow)" stroke="{INK}" stroke-width="1.5" transform="rotate({k * 45} {gx} {gy})"/>' for k in range(8))
        body.append(teeth + f'<circle cx="{gx}" cy="{gy}" r="{r}" fill="url(#m-yellow)" stroke="{INK}" stroke-width="2"/><circle cx="{gx}" cy="{gy}" r="{r * 0.3:.0f}" fill="{INK}"/>')
    # chute and output
    body.append(f'<path d="M470,250 h70 l20,30 h-90 z" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="470" y="300" width="190" height="16" rx="8" fill="#444" stroke="{INK}" stroke-width="2"/>')
    body.append(block(590, 252, 48, "green"))
    # inputs falling into the hopper
    body.append(card(300, 34, "10", rot=-12, size=18))
    body.append(card(350, 26, "10", rot=6, size=18))
    body.append(card(420, 36, '"lime"', rot=14, size=18))
    # lever robot
    body.append(f'<path d="M230,190 l-40,-60" stroke="{INK}" stroke-width="8" stroke-linecap="round"/><circle cx="190" cy="130" r="11" fill="url(#m-red)" stroke="{INK}" stroke-width="2"/>')
    svg, world = robot(110, 360, 1.15, "steel", left=(-40, 50), right=(66, -50), look=1)
    body.append(svg)
    body.append(label(120, 46, "drawCell(10, 10, \"lime\")", size=14))
    return scene(w, h, ("#f1e9ff", "#c6b3ff"), "".join(body))


def loop_track():
    w, h = 680, 380
    body = []
    cx, cy, rx, ry = 340, 200, 270, 140
    body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="44"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#e8673c" stroke-width="38"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="14 12"/>')
    # inside: a row of cells being drawn
    for i in range(5):
        fill = "#9a9a9a" if i < 3 else "#2a2c3a"
        body.append(f'<rect x="{220 + i * 48}" y="182" width="44" height="44" rx="4" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
                    f'<text x="{242 + i * 48}" y="246" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="#5a3a1a">{i}</text>')
    body.append(label(340, 150, "drawCell(i, 0, \"gray\");", size=15))
    # checkpoints
    body.append(label(98, 116, "let i = 0", size=16, bg="#e7ffe0"))
    body.append(label(340, 40, "i < 5 ?", size=18, bg="#fff3b0"))
    body.append(label(590, 116, "i++", size=18, bg="#dff1ff"))
    # running robot with a counter on its chest
    chest = (f'<rect x="-19" y="25" width="38" height="22" rx="4" fill="url(#visor)" stroke="{INK}" stroke-width="1.5"/>'
             f'<text x="0" y="41" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="#7CFC7C">i=3</text>')
    svg, world = robot(470, 352, 0.85, "green", left=(-50, 0), right=(50, 50), look=1, chest=chest)
    body.append(svg)
    body.append(f'<path d="M390,330 h-26 M396,312 h-20 M392,296 h-14" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    return scene(w, h, ("#f4ffd6", "#c4ec7a"), "".join(body))


def if_fork():
    w, h = 680, 380
    body = []
    body.append(f'<path d="M290,380 C300,300 330,250 340,220 C350,180 200,150 90,110 M340,220 C350,180 480,150 590,110" fill="none" stroke="{INK}" stroke-width="64" stroke-linecap="round"/>'
                f'<path d="M290,380 C300,300 330,250 340,220 C350,180 200,150 90,110 M340,220 C350,180 480,150 590,110" fill="none" stroke="#c9b48a" stroke-width="58" stroke-linecap="round"/>'
                f'<path d="M290,380 C300,300 330,250 340,220 C350,180 200,150 90,110 M340,220 C350,180 480,150 590,110" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="14 14"/>')
    # signpost
    body.append(f'<rect x="420" y="170" width="10" height="150" fill="url(#m-wood)" stroke="{INK}" stroke-width="2"/>')
    body.append(label(426, 160, "if (score > 10)", size=19, bg="#fff3b0"))
    body.append(f'<g transform="translate(150,60)"><path d="M-62,-20 h104 l20,20 l-20,20 h-104 z" transform="scale(-1,1)" fill="#5ce07a" stroke="{INK}" stroke-width="2"/>'
                f'<text x="0" y="7" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" fill="#14532d">true</text></g>')
    body.append(f'<g transform="translate(540,60)"><path d="M-62,-20 h104 l20,20 l-20,20 h-104 z" fill="#ff8a80" stroke="{INK}" stroke-width="2"/>'
                f'<text x="-10" y="7" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" fill="#7f1d1d">false</text></g>')
    body.append(star(66, 110, 24))
    # thinking robot at the fork
    svg, world = robot(300, 356, 1.05, "cyan", left=(-40, 50), right=(12, -6), look=0)
    body.append(svg)
    body.append(f'<text x="350" y="232" font-family="{MONO}" font-size="40" font-weight="700" fill="#1d2140">?</text>')
    return scene(w, h, ("#e3f6ff", "#b6f0b0"), "".join(body))


def key_events():
    w, h = 680, 380
    body = []
    body.append(keycap(110, 170, 74, 66, "↑", pressed=True, size=34))
    body.append(keycap(30, 248, 74, 66, "←", size=34))
    body.append(keycap(110, 248, 74, 66, "↓", size=34))
    body.append(keycap(190, 248, 74, 66, "→", size=34))
    body.append(f'<path d="M100,170 l-16,-14 M150,160 v-20 M196,170 l16,-14" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    # flying envelope
    body.append(f'<path d="M190,170 C260,60 340,60 400,110" stroke="#4c97f0" stroke-width="3" fill="none" stroke-dasharray="8 7"/>')
    body.append(f'<g transform="translate(300,64) rotate(-8)"><rect x="-70" y="-30" width="140" height="64" rx="5" fill="#fffdf3" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M-70,-30 l70,36 l70,-36" fill="none" stroke="{INK}" stroke-width="2"/>'
                f'<text x="0" y="26" text-anchor="middle" font-family="{MONO}" font-size="16" font-weight="700" fill="#c2410c">"ArrowUp"</text></g>')
    # listener robot
    svg, world = robot(520, 352, 1.2, "blue", left=(-64, -40), right=(46, 40), look=-1)
    body.append(svg)
    body.append(label(520, 40, "onKey(event)", size=18))
    hx, hy = world.left
    body.append(card(hx - 10, hy - 30, "dy = -1", rot=-6, size=17))
    return scene(w, h, ("#eaffea", "#a8e6a0"), "".join(body))


def random_die():
    w, h = 680, 380
    body = []
    # small field with possible apple places
    fx, fy, c = 410, 120, 44
    body.append(f'<rect x="{fx - 6}" y="{fy - 6}" width="{5 * c + 12}" height="{4 * c + 12}" rx="8" fill="#1e1f29" stroke="{INK}" stroke-width="2"/>')
    for i in range(5):
        for j in range(4):
            body.append(f'<rect x="{fx + i * c + 2}" y="{fy + j * c + 2}" width="{c - 4}" height="{c - 4}" rx="3" fill="#2a2c3a"/>')
    for (i, j) in ((0, 0), (4, 1), (1, 3), (3, 3)):
        body.append(f'<text x="{fx + i * c + c / 2}" y="{fy + j * c + c / 2 + 9}" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="700" fill="#8a93b2">?</text>')
    body.append(apple(fx + 2 * c + c / 2, fy + 2 * c + c / 2 + 2, r=16))
    # the die
    body.append(f'<g transform="translate(300,170) rotate(-18)"><path d="M-40,-40 l20,-20 h80 l-20,20 z" fill="#ffe0e0" stroke="{INK}" stroke-width="2.5"/>'
                f'<path d="M40,-40 l20,-20 v80 l-20,20 z" fill="#c92a2a" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="-40" y="-40" width="80" height="80" rx="6" fill="url(#v-red)" stroke="{INK}" stroke-width="2.5"/>'
                f'<text x="0" y="14" text-anchor="middle" font-family="{MONO}" font-size="38" font-weight="700" fill="#fff">13</text></g>')
    body.append(f'<path d="M210,250 q40,-80 80,-90 M226,272 q50,-70 92,-84" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="2 10"/>')
    svg, world = robot(140, 356, 1.2, "yellow", left=(-46, 50), right=(60, -30), look=1)
    body.append(svg)
    body.append(label(340, 40, "Math.floor(Math.random() * 20)", size=16))
    return scene(w, h, ("#fff4d6", "#ffc96b"), "".join(body))


def crash_wall():
    w, h = 680, 380
    body = []
    # brick wall
    body.append(f'<rect x="560" y="2" width="116" height="376" fill="#b5462e"/>')
    for row in range(12):
        off = 0 if row % 2 == 0 else 28
        for k in range(-1, 3):
            body.append(f'<rect x="{560 + off + k * 56}" y="{4 + row * 31}" width="54" height="29" fill="#c95a3d" stroke="#7a2a17" stroke-width="2"/>')
    body.append(f'<line x1="560" y1="2" x2="560" y2="378" stroke="{INK}" stroke-width="3"/>')
    # crashed robot, tilted
    svg, world = robot(0, 0, 1.15, "steel", left=(-58, -10), right=(40, -50), look=1)
    body.append(f'<g transform="translate(470,356) rotate(-14)">{svg}</g>')
    for (sx, sy, r) in ((540, 120, 16), (500, 84, 11), (548, 172, 10), (470, 110, 9)):
        body.append(star(sx, sy, r))
    body.append(f'<path d="M520,150 l24,-8 M522,174 l26,4 M514,128 l20,-18" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    # the stopped timer
    body.append(stopwatch(150, 200, 70, hand_deg=110))
    body.append(f'<path d="M90,140 L210,260 M210,140 L90,260" stroke="#d63b2f" stroke-width="12" stroke-linecap="round" opacity="0.85"/>')
    body.append(label(150, 320, "clearInterval(timer)", size=16))
    body.append(label(330, 46, "endGame();", size=24, bg="#fff3b0"))
    return scene(w, h, ("#ffe6e6", "#ff9f9f"), "".join(body))


def restart_space():
    w, h = 680, 380
    body = []
    body.append(keycap(150, 270, 400, 60, "", pressed=True))
    body.append(f'<path d="M150,262 l-20,-12 M550,262 l20,-12 M350,250 v-14" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    svg, world = robot(350, 278, 1.0, "green", left=(-56, -50), right=(56, -50), look=0)
    body.append(svg)
    # flag robot
    svg, world = robot(90, 356, 1.0, "red", left=(-40, 50), right=(44, -20), look=1)
    body.append(svg)
    hx, hy = world.right
    body.append(f'<line x1="{hx:.1f}" y1="{hy + 40:.1f}" x2="{hx:.1f}" y2="40" stroke="#6b3d12" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M{hx:.1f},44 q60,-14 120,6 v56 q-60,-20 -120,-6 z" fill="#fffdf3" stroke="{INK}" stroke-width="2"/>'
                f'<text x="{hx + 60:.1f}" y="76" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="#b42318">gameOver</text>'
                f'<text x="{hx + 60:.1f}" y="96" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="#1d4ed8">= true</text>')
    # a fresh game appears
    body.append(browser_window(470, 40, 180, 150, mini_game(500, 72, 12, 10, 9, [(5, 4), (4, 4), (3, 4)], (8, 6))))
    body.append(label(560, 216, "startGame();", size=17, bg="#e7ffe0"))
    return scene(w, h, ("#e6f0ff", "#9fc0ff"), "".join(body))


def speed_record():
    w, h = 680, 380
    body = []
    body.append(stopwatch(130, 190, 80, hand_deg=300))
    for k, t in enumerate(("200", "150", "100", "60")):
        body.append(f'<text x="{60 + k * 46}" y="318" font-family="{MONO}" font-size="16" font-weight="700" fill="#7a4a00">{t}</text>')
    body.append(f'<path d="M64,330 h190" stroke="#7a4a00" stroke-width="3"/><path d="M248,323 l10,7 l-10,7" fill="#7a4a00"/>')
    body.append(label(130, 46, "speed = speed - 10", size=15))
    # notebook + trophy
    body.append(f'<g transform="translate(300,120)"><path d="M0,0 q60,-16 120,0 v150 q-60,-16 -120,0 z" fill="#fffdf3" stroke="{INK}" stroke-width="2.5"/>'
                f'<path d="M120,0 q60,-16 120,0 v150 q-60,-16 -120,0 z" fill="#f4efe0" stroke="{INK}" stroke-width="2.5"/>'
                + "".join(f'<line x1="14" y1="{30 + i * 22}" x2="106" y2="{30 + i * 22 - 3}" stroke="#a5c8ff"/>' for i in range(5))
                + f'<text x="14" y="58" font-family="{MONO}" font-size="13" font-weight="700" fill="#1d2140">snakeBest</text>'
                f'<text x="40" y="96" font-family="{MONO}" font-size="30" font-weight="700" fill="#c2410c">25</text></g>')
    body.append(f'<g transform="translate(470,218)"><path d="M-30,-40 h60 v20 q0,36 -30,40 q-30,-4 -30,-40 z" fill="url(#m-yellow)" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M-30,-32 q-22,0 -18,16 q4,12 18,10 M30,-32 q22,0 18,16 q-4,12 -18,10" fill="none" stroke="{INK}" stroke-width="3"/>'
                f'<rect x="-8" y="20" width="16" height="16" fill="url(#m-yellow)" stroke="{INK}" stroke-width="2"/><rect x="-22" y="36" width="44" height="12" rx="3" fill="url(#m-wood)" stroke="{INK}" stroke-width="2"/></g>')
    svg, world = robot(600, 356, 1.05, "purple", left=(-60, 6), right=(40, 50), look=-1)
    body.append(svg)
    hx, hy = world.left
    body.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{hx - 34:.1f}" y2="{hy + 22:.1f}" stroke="#1d4ed8" stroke-width="6" stroke-linecap="round"/>')
    body.append(label(470, 46, "localStorage", size=18, bg="#fff3b0"))
    return scene(w, h, ("#fff8d6", "#ffd27a"), "".join(body))


def bug_hunt():
    w, h = 680, 380
    body = []
    body.append(keycap(300, 250, 70, 60, "↑", size=30))
    body.append(keycap(390, 250, 70, 60, "←", size=30))
    body.append(bug(480, 150, 1.5, rot=-20))
    for (x1, y1, x2, y2) in ((440, 120, 420, 108), (520, 120, 540, 104), (520, 186, 544, 196)):
        body.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    svg, world = robot(150, 356, 1.2, "orange", left=(-40, 50), right=(64, -44), look=1)
    body.append(svg)
    hx, hy = world.right
    nx, ny = 448, 130
    body.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{nx - 50}" y2="{ny + 30}" stroke="#9c5a10" stroke-width="7" stroke-linecap="round"/>'
                f'<ellipse cx="{nx}" cy="{ny}" rx="58" ry="40" fill="#fff" fill-opacity="0.35" stroke="{INK}" stroke-width="4" transform="rotate(-25 {nx} {ny})"/>'
                + "".join(f'<line x1="{nx - 50 + k * 20}" y1="{ny - 40}" x2="{nx - 40 + k * 20}" y2="{ny + 40}" stroke="{INK}" stroke-width="1" opacity="0.5" transform="rotate(-25 {nx} {ny})"/>' for k in range(6)))
    body.append(label(500, 46, "nextDx, nextDy", size=18, bg="#fff3b0"))
    return scene(w, h, ("#efffe6", "#b5e88a"), "".join(body))


def css_paint():
    w, h = 680, 380
    body = []
    # a page: left half already styled, right half plain
    px, py, pw, ph = 250, 40, 390, 300
    body.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="#f2f2f2" stroke="{INK}" stroke-width="2.5"/>')
    body.append(f'<clipPath id="half"><rect x="{px}" y="{py}" width="{pw * 0.55}" height="{ph}"/></clipPath>')
    styled = (f'<g clip-path="url(#half)"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="#10241a"/>'
              f'<rect x="{px + 115}" y="{py + 30}" width="160" height="20" rx="6" fill="#7ee081"/>'
              f'<rect x="{px + 95}" y="{py + 80}" width="200" height="190" rx="10" fill="#000" stroke="#3fa34d" stroke-width="8"/>'
              + mini_game(px + 120, py + 110, 14, 10, 9, [(5, 4), (4, 4), (3, 4)], (8, 2)) + "</g>")
    plain = (f'<rect x="{px + 115}" y="{py + 30}" width="160" height="20" rx="2" fill="#bbb"/>'
             f'<rect x="{px + 95}" y="{py + 80}" width="200" height="190" fill="#000"/>')
    body.append(plain + styled)
    body.append(f'<path d="M{px + pw * 0.55},{py} v{ph}" stroke="#7ee081" stroke-width="10"/>'
                f'<path d="M{px + pw * 0.55 - 4},{py + ph} q4,16 8,0" fill="#7ee081"/>')
    # roller
    svg, world = robot(120, 356, 1.2, "steel", left=(-40, 50), right=(70, -60), look=1)
    body.append(svg)
    hx, hy = world.right
    rx_, ry_ = px + pw * 0.55, py + 120
    body.append(f'<path d="M{hx:.1f},{hy:.1f} L{rx_ - 30},{ry_ + 40} L{rx_ - 10},{ry_}" fill="none" stroke="#555" stroke-width="6" stroke-linejoin="round"/>'
                f'<rect x="{rx_ - 14}" y="{ry_ - 50}" width="26" height="100" rx="10" fill="#7ee081" stroke="{INK}" stroke-width="2"/>')
    # paint buckets with CSS properties
    for i, (prop, col) in enumerate((("color", "#7ee081"), ("border", "#3fa34d"), ("background", "#10241a"))):
        bx = 30 + i * 0
        by = 24 + i * 48
        body.append(f'<g transform="translate({bx},{by})"><path d="M0,0 h44 l-5,40 h-34 z" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/>'
                    f'<ellipse cx="22" cy="0" rx="22" ry="6" fill="{col}" stroke="{INK}" stroke-width="2"/>'
                    f'<text x="54" y="26" font-family="{MONO}" font-size="16" font-weight="700" fill="#1d2140">{prop}</text></g>')
    return scene(w, h, ("#ffe8f3", "#ffb3d4"), "".join(body))


def publish():
    w, h = 680, 380
    body = []
    for (sx, sy) in ((60, 50), (140, 120), (230, 40), (600, 200), (520, 300), (90, 240), (300, 300)):
        body.append(star(sx, sy, 6, color="#fff59d"))
    # cloud with the address
    body.append(f'<g fill="#ffffff" stroke="{INK}" stroke-width="2.5"><ellipse cx="520" cy="80" rx="70" ry="38"/><ellipse cx="460" cy="96" rx="50" ry="30"/><ellipse cx="590" cy="98" rx="52" ry="30"/></g>'
                f'<g fill="#ffffff"><ellipse cx="520" cy="86" rx="66" ry="32"/><ellipse cx="462" cy="98" rx="46" ry="25"/><ellipse cx="588" cy="100" rx="48" ry="25"/></g>'
                f'<text x="524" y="102" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" fill="#1d4ed8">github.io</text>')
    # rocket carrying index.html
    body.append(f'<g transform="translate(330,190) rotate(40)">'
                f'<path d="M-22,40 q-4,30 22,52 q26,-22 22,-52 z" fill="#ffb347" stroke="{INK}" stroke-width="2"/>'
                f'<path d="M-14,40 q-2,20 14,34 q16,-14 14,-34 z" fill="#ffe066"/>'
                f'<path d="M-26,-30 q26,-70 52,0 v70 h-52 z" fill="url(#m-steel)" stroke="{INK}" stroke-width="2.5"/>'
                f'<path d="M-26,10 l-20,34 l20,-4 z M26,10 l20,34 l-20,-4 z" fill="url(#m-red)" stroke="{INK}" stroke-width="2"/>'
                f'<circle cx="0" cy="-16" r="11" fill="#bfe9ff" stroke="{INK}" stroke-width="2.5"/></g>')
    body.append(card(300, 260, "index.html", rot=-8, size=16))
    body.append(f'<path d="M240,330 q40,-40 70,-90" stroke="#ffe066" stroke-width="3" fill="none" stroke-dasharray="6 8"/>')
    # waving robot at the launch pad
    svg, world = robot(140, 356, 1.1, "cyan", left=(-40, 50), right=(60, -60), look=1)
    body.append(svg)
    # a phone and a laptop playing the game
    body.append(f'<g transform="translate(560,190)"><rect x="-32" y="0" width="64" height="112" rx="10" fill="#2b2b2b" stroke="{INK}" stroke-width="2"/>'
                + mini_game(-26, 12, 6, 9, 14, [(4, 7), (3, 7), (2, 7)], (6, 3)) + "</g>")
    body.append(f'<g transform="translate(450,250)"><rect x="-60" y="0" width="120" height="76" rx="6" fill="#2b2b2b" stroke="{INK}" stroke-width="2"/>'
                + mini_game(-54, 6, 8, 13, 8, [(6, 4), (5, 4), (4, 4)], (10, 2))
                + f'<path d="M-76,76 h152 l-12,14 h-128 z" fill="url(#m-steel)" stroke="{INK}" stroke-width="2"/></g>')
    return scene(w, h, ("#1b2a5c", "#4b3b8f"), "".join(body))


SCENES = {
    "l00-setup.svg": setup,
    "l01-save-refresh.svg": save_refresh,
    "l02-console-bug.svg": console_bug,
    "l03-variables.svg": variables,
    "l04-canvas.svg": canvas_paint,
    "l05-function.svg": function_machine,
    "l06-loop.svg": loop_track,
    "l07-array.svg": array_snake,
    "l08-unshift-pop.svg": unshift_pop,
    "l09-if.svg": if_fork,
    "l10-events.svg": key_events,
    "l11-random.svg": random_die,
    "l12-crash.svg": crash_wall,
    "l13-restart.svg": restart_space,
    "l14-speed-record.svg": speed_record,
    "l14-bug-hunt.svg": bug_hunt,
    "l15-css.svg": css_paint,
    "l16-publish.svg": publish,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in SCENES.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", name)
