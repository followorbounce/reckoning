"""SVG drawings generated from the flag designs in data/signals.py and the weather symbols.

Flags are drawn on a 90 x 60 field, then clipped to their outline: rectangle, swallowtail
(A and B), tapered pennant (numerals, answering pennant) or triangle (substitutes)."""
import hashlib
import math
from signals import C

W, H = 90, 60
SHAPES = {
    'flag': 'M0 0H90V60H0Z',
    'swallow': 'M0 0H90L66 30L90 60H0Z',
    'pennant': 'M0 0L90 21V39L0 60Z',
    'triangle': 'M0 0L90 30L0 60Z',
}


def _rect(x, y, w, h, c):
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x, y, w, h, C[c])


def field(kind, cols):
    k = kind
    c = list(cols)
    o = []
    if k in ('plain', 'swallow'):
        o.append(_rect(0, 0, W, H, c[0]))
    elif k == 'swallow-pale' or k == 'pale2':
        o += [_rect(0, 0, W / 2, H, c[0]), _rect(W / 2, 0, W / 2, H, c[1])]
    elif k == 'pale3':
        o += [_rect(i * W / 3, 0, W / 3 + 0.2, H, c[i]) for i in range(3)]
    elif k == 'pale5':
        o += [_rect(i * W / 5, 0, W / 5 + 0.2, H, c[i]) for i in range(5)]
    elif k == 'paly6':
        o += [_rect(i * W / 6, 0, W / 6 + 0.2, H, c[i % 2]) for i in range(6)]
    elif k == 'fess2':
        o += [_rect(0, 0, W, H / 2, c[0]), _rect(0, H / 2, W, H / 2, c[1])]
    elif k == 'fess3':
        o += [_rect(0, i * H / 3, W, H / 3 + 0.2, c[i]) for i in range(3)]
    elif k == 'fess5':
        o += [_rect(0, i * H / 5, W, H / 5 + 0.2, c[i]) for i in range(5)]
    elif k == 'fess121':   # a Spanish fess: middle band twice the others
        o += [_rect(0, 0, W, H, c[0]), _rect(0, H / 4, W, H / 2, c[1])]
    elif k == 'lozenge':
        o += [_rect(0, 0, W, H, c[0]), '<path d="M45 0L90 30L45 60L0 30Z" fill="%s"/>' % C[c[1]]]
    elif k == 'disc':
        o += [_rect(0, 0, W, H, c[0]), '<circle cx="45" cy="30" r="16" fill="%s"/>' % C[c[1]]]
    elif k == 'quarterly':   # order: top hoist, top fly, bottom hoist, bottom fly
        o += [_rect(0, 0, W / 2, H / 2, c[0]), _rect(W / 2, 0, W / 2, H / 2, c[1]), _rect(0, H / 2, W / 2, H / 2, c[2]), _rect(W / 2, H / 2, W / 2, H / 2, c[3])]
    elif k == 'saltire':
        o += [_rect(0, 0, W, H, c[0]), '<path d="M0 0L90 60M90 0L0 60" stroke="%s" stroke-width="13"/>' % C[c[1]]]
    elif k == 'cross':
        o += [_rect(0, 0, W, H, c[0]), _rect(0, H / 2 - 7, W, 14, c[1]), _rect(W / 2 - 7, 0, 14, H, c[1])]
    elif k == 'chequy':
        for i in range(4):
            for j in range(4):
                o.append(_rect(i * W / 4, j * H / 4, W / 4 + 0.2, H / 4 + 0.2, c[(i + j) % 2]))
    elif k == 'perbend':     # line from top hoist to bottom fly; first colour above it (fly side)
        o += [_rect(0, 0, W, H, c[1]), '<path d="M0 0H90V60Z" fill="%s"/>' % C[c[0]]]
    elif k == 'square':
        o += [_rect(0, 0, W, H, c[0]), _rect(W / 2 - 15, H / 2 - 15, 30, 30, c[1])]
    elif k == 'square2':
        o += [_rect(0, 0, W, H, c[0]), _rect(W / 2 - 27, H / 2 - 18, 54, 36, c[1]), _rect(W / 2 - 15, H / 2 - 9, 30, 18, c[2])]
    elif k == 'bendy':       # ten diagonal stripes rising toward the fly
        o.append(_rect(0, 0, W, H, c[0]))
        step = (W + H) / 10
        for i in range(1, 10, 2):
            a, b = i * step, (i + 1) * step
            o.append('<path d="M%g 60L%g 60L%g 0L%g 0Z" fill="%s"/>' % (a - H, b - H, b, a, C[c[1]]))
    elif k == 'persaltire':  # top, hoist, bottom, fly
        o += ['<path d="M0 0H90L45 30Z" fill="%s"/>' % C[c[0]], '<path d="M0 0L45 30L0 60Z" fill="%s"/>' % C[c[1]],
              '<path d="M0 60L45 30L90 60Z" fill="%s"/>' % C[c[2]], '<path d="M90 0L45 30L90 60Z" fill="%s"/>' % C[c[3]]]
    elif k == 'border':      # first substitute: yellow with a blue border that leaves the hoist edge open
        o += ['<rect width="90" height="60" fill="%s"/>' % C[c[1]], '<path d="M0 9L64 30L0 51Z" fill="%s"/>' % C[c[0]]]
    else:
        raise KeyError(k)
    return ''.join(o)


def flag_svg(design, outline='flag', title='', cls='flag'):
    kind, cols = design
    if kind.startswith('swallow'):
        outline = 'swallow'
    cid = 'c' + hashlib.md5(repr((kind, cols, outline)).encode()).hexdigest()[:8]
    return ('<svg class="%s" viewBox="-1 -1 92 62" role="img" aria-label="%s"><defs><clipPath id="%s"><path d="%s"/></clipPath></defs>'
            '<g clip-path="url(#%s)">%s</g><path d="%s" fill="none" stroke="#14212b" stroke-opacity=".35" stroke-width="1"/></svg>') % (
        cls, title, cid, SHAPES[outline], cid, field(kind, cols), SHAPES[outline])


# ---------------------------------------------------------------- weather symbols (WMO present weather, ww)
INK = 'currentColor'


def _dot(x, y, r=4.2):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s"/>' % (x, y, r, INK)


def _comma(x, y):
    return ('<circle cx="%g" cy="%g" r="3.8" fill="%s"/><path d="M%g %g q2 6 -4 10" stroke="%s" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            % (x, y, INK, x + 3.2, y + 1, INK))


def _star(x, y, s=6):
    p = []
    for i in range(3):
        a = math.pi / 2 + i * math.pi / 3
        dx, dy = s * math.cos(a), s * math.sin(a)
        p.append('M%.1f %.1fL%.1f %.1f' % (x - dx, y - dy, x + dx, y + dy))
    return '<path d="%s" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>' % (''.join(p), INK)


def _pattern(fn, n, cont):
    """Intensity patterns used for drizzle, rain and snow: intermittent forms stack
    vertically, continuous forms spread sideways (1, 2, 3 or 4 elements)."""
    if cont:
        pos = {1: [(30, 30)], 2: [(20, 30), (40, 30)], 3: [(30, 20), (20, 38), (40, 38)], 4: [(30, 14), (18, 30), (42, 30), (30, 46)]}[n]
    else:
        pos = {1: [(30, 30)], 2: [(30, 20), (30, 40)], 3: [(30, 12), (30, 30), (30, 48)]}[n]
    return ''.join(fn(x, y) for x, y in pos)


def _shower(top):
    return top + '<path d="M18 34H42L30 54Z" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % INK


def _storm():
    # the thunderstorm sign: a right angle with a lightning stroke ending in an arrowhead
    return ('<path d="M14 12V50M14 12H40L28 32L46 32L30 52" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
            '<path d="M30 52L29 42L37 47Z" fill="%s"/>' % (INK, INK))


WX = [
    ('05', 'Haze', '<path d="M8 30c6-12 16-12 22 0s16 12 22 0c-6-12-16-12-22 0s-16 12-22 0" fill="none" stroke="%s" stroke-width="2.6"/>' % INK),
    ('10', 'Mist', '<path d="M12 24H48M12 36H48" stroke="%s" stroke-width="2.8"/>' % INK),
    ('45', 'Fog, sky invisible', '<path d="M12 20H48M12 30H48M12 40H48" stroke="%s" stroke-width="2.8"/>' % INK),
    ('13', 'Lightning visible, no thunder heard', '<path d="M40 10L22 32H36L18 52" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/><path d="M18 52L20 41L27 46Z" fill="%s"/>' % (INK, INK)),
    ('50', 'Drizzle, intermittent, slight', _pattern(_comma, 1, False)),
    ('51', 'Drizzle, continuous, slight', _pattern(_comma, 2, True)),
    ('53', 'Drizzle, continuous, moderate', _pattern(_comma, 3, True)),
    ('60', 'Rain, intermittent, slight', _pattern(_dot, 1, False)),
    ('61', 'Rain, continuous, slight', _pattern(_dot, 2, True)),
    ('62', 'Rain, intermittent, moderate', _pattern(_dot, 2, False)),
    ('63', 'Rain, continuous, moderate', _pattern(_dot, 3, True)),
    ('64', 'Rain, intermittent, heavy', _pattern(_dot, 3, False)),
    ('65', 'Rain, continuous, heavy', _pattern(_dot, 4, True)),
    ('71', 'Snow, continuous, slight', _pattern(_star, 2, True)),
    ('73', 'Snow, continuous, moderate', _pattern(_star, 3, True)),
    ('75', 'Snow, continuous, heavy', _pattern(_star, 4, True)),
    ('80', 'Rain shower, slight', _shower(_dot(30, 22))),
    ('85', 'Snow shower, slight', _shower(_star(30, 22))),
    ('89', 'Hail shower, slight', _shower('<path d="M30 12L37 26H23Z" fill="%s"/>' % INK)),
    ('95', 'Thunderstorm, slight or moderate, with rain or snow', _storm() + _dot(46, 14, 3.6)),
]


def wx_svg(body, label):
    return '<svg class="wx" viewBox="0 0 60 60" role="img" aria-label="%s">%s</svg>' % (label, body)
