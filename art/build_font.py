"""dishme hand: a single-stroke, wobbly-pen display font drawn from scratch.

Each glyph is a set of pen strokes (centrelines) defined below in font units (1000/em,
x-height 470, ascender 700, descender -220). Strokes get a gentle, continuous wobble,
are expanded with a round pen, unioned, and written to OTF + WOFF2.
"""
import math, random
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

PEN = 44          # stroke width: light, never bold
SIDE = 36         # side bearing
WOBBLE = 11       # wobble amplitude

def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0) / 6))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def curve(pts, steps=8):
    """Catmull-Rom through points."""
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[i + 2] if i + 2 < len(pts) else p2
        for k in range(steps):
            t = k / steps; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out

def dot(x, y):
    return [(x - 3, y - 2), (x + 3, y + 3)]

L = lambda *p: list(p)

G = {}  # char -> (width, [strokes])
def g(ch, w, *strokes):
    G[ch] = (w, [s for s in strokes])

# ---- lowercase ----
g('a', 410, arc(198, 232, 182, 228, 22, 338), L((376, 470), (378, 0)))
g('b', 440, L((40, 700), (40, 0)), arc(236, 234, 196, 234, 150, -150))
g('c', 400, arc(212, 236, 198, 238, 48, 312))
g('d', 400, arc(196, 234, 190, 232, 32, 328), L((388, 700), (388, 0)))
g('e', 415, L((26, 246), (402, 246)) + arc(212, 236, 192, 236, 6, 318))
g('f', 300, L((118, 0), (118, 560)) + arc(228, 560, 110, 132, 180, 32), L((20, 458), (266, 462)))
g('g', 395, arc(196, 246, 180, 224, 22, 338), L((378, 470), (378, -70)) + arc(212, -70, 166, 140, 0, -158))
g('h', 400, L((40, 700), (40, 0)), arc(200, 296, 160, 172, 180, 0) + [(360, 0)])
g('i', 90, L((44, 470), (44, 0)), dot(46, 640))
g('j', 200, L((150, 470), (150, -110)) + arc(62, -110, 88, 100, 0, -158), dot(152, 640))
g('k', 360, L((40, 700), (40, 0)), L((322, 470), (40, 186)), L((150, 296), (344, 0)))
g('l', 110, L((48, 700), (44, 70)) + arc(96, 70, 52, 70, 180, 300))
g('m', 520, L((40, 470), (40, 0)), arc(150, 300, 110, 162, 180, 0) + [(260, 0)], arc(370, 300, 110, 162, 180, 0) + [(480, 0)])
g('n', 400, L((40, 470), (40, 0)), arc(200, 298, 160, 170, 180, 0) + [(360, 0)])
g('o', 420, arc(210, 236, 200, 240, 96, 96 + 368))
g('p', 440, L((40, 470), (40, -220)), arc(236, 236, 196, 236, 150, -150))
g('q', 430, arc(196, 236, 190, 236, 30, 330), L((388, 470), (388, -220), (428, -176)))
g('r', 300, L((40, 470), (40, 0)), arc(190, 278, 150, 184, 180, 58))
g('s', 380, curve([(334, 408), (252, 466), (148, 466), (68, 412), (74, 326), (166, 270), (296, 214), (352, 138), (330, 42), (228, 0), (118, 6), (28, 62)]))
g('t', 310, L((128, 640), (128, 92)) + arc(228, 92, 100, 92, 180, 300), L((22, 468), (280, 472)))
g('u', 400, L((40, 470), (40, 190)) + arc(200, 190, 160, 190, 180, 360) + [(360, 470)], L((362, 470), (366, 0)))
g('v', 390, L((10, 470), (195, 0), (380, 470)))
g('w', 540, L((10, 470), (140, 0), (270, 402), (400, 0), (530, 470)))
g('x', 380, L((22, 470), (360, 0)), L((358, 470), (22, 0)))
g('y', 390, L((10, 470), (196, 34)), L((380, 470), (120, -220)))
g('z', 400, L((40, 470), (352, 470), (32, 0), (372, 0)))

# ---- digits ----
g('0', 420, arc(210, 332, 200, 336, 96, 96 + 366))
g('1', 260, L((52, 520), (198, 662), (198, 0)))
g('2', 410, arc(200, 484, 168, 178, 162, -28) + [(30, 0), (382, 0)])
g('3', 400, arc(190, 500, 160, 160, 150, -90), arc(200, 180, 180, 180, 90, -150))
g('4', 420, L((302, 0), (302, 662), (20, 202), (402, 202)))
g('5', 400, L((352, 660), (92, 660), (70, 382)) + arc(200, 214, 180, 214, 140, -150))
g('6', 420, curve([(334, 640), (204, 560), (90, 400), (40, 220)]), arc(214, 210, 178, 210, 0, 360))
g('7', 410, L((30, 660), (380, 660), (150, 0)))
g('8', 400, arc(200, 500, 150, 160, 0, 360), arc(200, 182, 186, 184, 0, 360))
g('9', 410, arc(200, 452, 180, 210, 0, 360), L((380, 470), (330, 200), (250, 0)))

# ---- punctuation ----
g(' ', 230)
g('.', 110, dot(50, 28))
g(',', 120, L((62, 40), (26, -96)))
g(':', 110, dot(50, 28), dot(50, 360))
g(';', 120, dot(58, 360), L((62, 40), (26, -96)))
g('!', 120, L((58, 660), (52, 182)), dot(54, 28))
g('?', 340, arc(176, 502, 150, 160, 162, -62) + [(170, 200)], dot(170, 28))
g('-', 300, L((30, 252), (270, 248)))
g('–', 500, L((30, 252), (470, 248)))
g('—', 780, L((30, 252), (750, 248)))
for q in "'’‘":
    g(q, 110, L((60, 700), (44, 560)))
for q in '"“”':
    g(q, 190, L((60, 700), (44, 560)), L((150, 700), (134, 560)))
g('/', 320, L((20, -60), (300, 720)))
g('(', 230, arc(222, 280, 172, 420, 122, 238))
g(')', 230, arc(8, 280, 172, 420, 58, -58))
g('[', 210, L((170, 720), (50, 720), (50, -100), (170, -100)))
g(']', 210, L((40, 720), (160, 720), (160, -100), (40, -100)))
g('+', 400, L((40, 252), (360, 248)), L((200, 90), (202, 412)))
g('=', 380, L((40, 320), (340, 316)), L((40, 170), (340, 166)))
g('*', 300, L((150, 640), (150, 380)), L((40, 580), (260, 440)), L((260, 580), (40, 440)))
g('%', 420, arc(96, 560, 72, 92, 0, 360), arc(320, 100, 72, 92, 0, 360), L((40, 0), (380, 660)))
g('°', 220, arc(110, 600, 70, 80, 0, 360))
g('·', 120, dot(60, 250))
g('•', 140, arc(70, 250, 22, 22, 0, 360))
g('…', 360, dot(50, 28), dot(180, 28), dot(310, 28))
g('&', 430, curve([(392, 0), (126, 322), (82, 480), (150, 620), (244, 602), (254, 500), (62, 262), (52, 100), (152, 0), (282, 36), (384, 200)]))
g('#', 440, L((40, 440), (400, 440)), L((40, 220), (400, 220)), L((170, 640), (120, 0)), L((320, 640), (270, 0)))
g('$', 380, curve([(334, 520), (252, 576), (148, 576), (68, 520), (74, 420), (166, 360), (296, 290), (352, 200), (330, 90), (228, 50), (118, 56), (28, 112)]), L((190, 680), (192, -60)))
g('_', 420, L((10, -90), (410, -90)))
g('×', 320, L((40, 380), (280, 100)), L((280, 380), (40, 100)))
g('|', 120, L((60, 720), (60, -160)))
g('@', 640, arc(330, 250, 130, 150, 20, 340) + [(470, 380), (470, 140)] + arc(540, 140, 70, 80, 180, 360) + arc(330, 250, 310, 330, 0, 330))
g('>', 360, L((40, 440), (320, 250), (40, 60)))
g('<', 360, L((320, 440), (40, 250), (320, 60)))

# ---- accents on lowercase ----
ACC = {
    'acute': lambda x: [L((x - 40, 560), (x + 50, 660))],
    'grave': lambda x: [L((x - 50, 660), (x + 40, 560))],
    'circ': lambda x: [L((x - 70, 560), (x, 650), (x + 70, 560))],
    'uml': lambda x: [dot(x - 60, 600), dot(x + 60, 600)],
    'tilde': lambda x: [curve([(x - 90, 580), (x - 40, 630), (x + 30, 580), (x + 90, 630)])],
    'ring': lambda x: [arc(x, 610, 50, 50, 0, 360)],
}
def accented(ch, base, kind, x=None):
    w, strokes = G[base]
    if base == 'i': strokes = strokes[:1]
    G[ch] = (w, strokes + ACC[kind](x if x is not None else w / 2))
for ch, b, k in [('é', 'e', 'acute'), ('è', 'e', 'grave'), ('ê', 'e', 'circ'), ('ë', 'e', 'uml'),
                 ('á', 'a', 'acute'), ('à', 'a', 'grave'), ('â', 'a', 'circ'), ('ä', 'a', 'uml'), ('å', 'a', 'ring'), ('ã', 'a', 'tilde'),
                 ('ó', 'o', 'acute'), ('ò', 'o', 'grave'), ('ô', 'o', 'circ'), ('ö', 'o', 'uml'), ('õ', 'o', 'tilde'),
                 ('ú', 'u', 'acute'), ('ù', 'u', 'grave'), ('û', 'u', 'circ'), ('ü', 'u', 'uml'),
                 ('í', 'i', 'acute'), ('ì', 'i', 'grave'), ('î', 'i', 'circ'), ('ï', 'i', 'uml'), ('ñ', 'n', 'tilde')]:
    accented(ch, b, k, 46 if b == 'i' else None)
G['ç'] = (G['c'][0], G['c'][1] + [curve([(206, 0), (214, -60), (250, -90), (200, -150), (140, -150)])])

# ---- wobble, pen, outline ----
def resample(pts, step=9):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b); k = max(1, int(d / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out

def wobble(pts, rnd):
    pts = resample(pts)
    if len(pts) < 3: return pts
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    out, s = [], 0.0
    for i, p in enumerate(pts):
        if i: s += math.dist(pts[i - 1], p)
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        off = WOBBLE * (0.6 * math.sin(s / 82 + ph[0]) + 0.3 * math.sin(s / 27 + ph[1]) + 0.12 * math.sin(s / 10 + ph[2]))
        out.append((p[0] + nx * off, p[1] + ny * off))
    return out

def glyph_path(ch, strokes):
    rnd = random.Random(sum(map(ord, ch)) * 7919 + 11)
    rot = math.radians(rnd.uniform(-3.2, 3.2)); dy = rnd.uniform(-13, 13); sx = rnd.uniform(0.93, 1.07); sy = rnd.uniform(0.95, 1.05)
    acc = pathops.Path()
    for st in strokes:
        pts = wobble(st, rnd)
        pts = [(x * sx, (y - 235) * sy + 235) for x, y in pts]
        pts = [(x * math.cos(rot) - (y - 235) * math.sin(rot), x * math.sin(rot) + (y - 235) * math.cos(rot) + 235 + dy) for x, y in pts]
        p = pathops.Path()
        p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.stroke(PEN, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        p.convertConicsToQuads(0.5)
        acc = pathops.op(acc, p, pathops.PathOp.UNION)
    acc.simplify()
    return acc

order = ['.notdef', 'space']
cmap = {32: 'space'}
names = {}
for ch in G:
    if ch == ' ': continue
    nm = 'uni%04X' % ord(ch)
    names[ch] = nm; order.append(nm); cmap[ord(ch)] = nm
    if ch.isalpha() and ch.upper() != ch and len(ch.upper()) == 1:
        cmap[ord(ch.upper())] = nm          # capitals draw as lowercase: the house style is lowercase

charstrings, metrics = {}, {}
def build(nm, w, path):
    adv = int(w + 2 * SIDE)
    pen = T2CharStringPen(adv, None)
    if path is not None:
        tp = pathops.Path(); path.draw(tp.getPen()) if False else None
        # shift by side bearing
        shifted = pathops.Path()
        class Shift:
            def __init__(s, pen): s.pen = pen
            def moveTo(s, p): s.pen.moveTo((p[0] + SIDE, p[1]))
            def lineTo(s, p): s.pen.lineTo((p[0] + SIDE, p[1]))
            def curveTo(s, *ps): s.pen.curveTo(*[(p[0] + SIDE, p[1]) for p in ps])
            def qCurveTo(s, *ps): s.pen.qCurveTo(*[(p[0] + SIDE, p[1]) if p else None for p in ps])
            def closePath(s): s.pen.closePath()
            def endPath(s): s.pen.endPath()
        from fontTools.pens.basePen import BasePen
        class Fwd(BasePen):
            def __init__(s, out): super().__init__(None); s.out = out
            def _moveTo(s, p): s.out.moveTo((p[0] + SIDE, p[1]))
            def _lineTo(s, p): s.out.lineTo((p[0] + SIDE, p[1]))
            def _curveToOne(s, a, b, c): s.out.curveTo((a[0] + SIDE, a[1]), (b[0] + SIDE, b[1]), (c[0] + SIDE, c[1]))
            def _closePath(s): s.out.closePath()
            def _endPath(s): s.out.endPath()
        bp = BoundsPen(None)
        fwd = Fwd(pen); path.draw(fwd)
        path.draw(Fwd(bp))
        lsb = int(bp.bounds[0]) if bp.bounds else 0
    else:
        lsb = 0
    charstrings[nm] = pen.getCharString()
    metrics[nm] = (adv, lsb)

build('.notdef', 300, None)
build('space', G[' '][0] - 2 * SIDE, None)
for ch, nm in names.items():
    w, strokes = G[ch]
    build(nm, w, glyph_path(ch, strokes))

fb = FontBuilder(1000, isTTF=False)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(cmap)
fb.setupCFF('DishmeHand-Regular', {'FullName': 'dishme hand', 'FamilyName': 'dishme hand', 'Weight': 'Regular'}, charstrings, {})
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=880, descent=-280)
fb.setupNameTable({'familyName': 'dishme hand', 'styleName': 'Regular', 'uniqueFontIdentifier': 'dishme hand 1.0', 'fullName': 'dishme hand', 'psName': 'DishmeHand-Regular', 'version': 'Version 1.000'})
fb.setupOS2(sTypoAscender=760, sTypoDescender=-240, sTypoLineGap=200, usWinAscent=880, usWinDescent=280, sxHeight=470, sCapHeight=470, usWeightClass=400)
fb.setupPost()
fb.save('dishme-hand.otf')
f = TTFont('dishme-hand.otf'); f.flavor = 'woff2'; f.save('dishme-hand.woff2')
print('glyphs', len(order))
