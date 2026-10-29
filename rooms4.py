"""Wave 4 rooms: Ship and Code of life, plus the glossary and the naming page. Page builders called from build.py."""
import html
import json
import math

from ship import PARTS, LOADLINE
from life import IUPAC, BASES, FORMS, B_SOLUTION_BP_PER_TURN
from glossary import TERMS, SAME_WORD
from names import GODS, MOON_THEMES, DWARF, WEEKDAYS, MONTHS, ELEMENTS

E = html.escape
KATEX = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">\n'
         '<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>\n')
TEX_RUN = ('<script>document.addEventListener("DOMContentLoaded",function(){if(!window.katex)return;document.querySelectorAll(".tex").forEach('
           'function(el){try{katex.render(el.getAttribute("data-tex"),el,{displayMode:true,throwOnError:false})}catch(e){el.textContent=el.getAttribute("data-tex")}})});</script>\n')
THREE = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
         '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>\n')


def tex(t):
    return '<div class="formula"><span class="tex" data-tex="%s"></span></div>' % E(t)


def hub(page, room, title, lede, cards, desc):
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / {E(title)}</p>
<div class="head"><p class="eyebrow">Room · wave 4</p><h1>{E(title)}</h1>
<p class="lede col">{lede}</p></div>
<section class="block"><div class="grid">{''.join('<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in cards)}</div></section>'''
    return page('%s/index.html' % room, '%s · Reckoning' % title, desc, body, nav=room)


# =====================================================================================  the midship section drawing
B2, D, DB, RB = 10.0, 12.0, 1.5, 2.0          # half-breadth, depth, double-bottom height, bilge radius (m)
TWEEN, HATCH, CAMBER = 7.5, 4.0, 0.25
K, CX, KY = 30.0, 450.0, 560.0                # px per metre; centreline x; keel y


def X(y):
    return CX + y * K


def Y(z):
    return KY - z * K


def deck_z(y):
    return D + CAMBER * (1 - (y / B2) ** 2)


def pts(p, mirror=False):
    return ' '.join('%.1f,%.1f' % (X(-y if mirror else y), Y(z)) for y, z in p)


def path(p, mirror=False, close=False):
    s = 'M' + ' L'.join('%.1f %.1f' % (X(-y if mirror else y), Y(z)) for y, z in p)
    return s + (' Z' if close else '')


def shell_line():
    """The outer shell from the keel edge round the bilge to the deck edge, starboard side, as (y, z) points."""
    p = [(0.8, 0.0), (B2 - RB, 0.0)]
    for i in range(1, 19):
        a = -math.pi / 2 + math.pi / 2 * i / 18
        p.append((B2 - RB + RB * math.cos(a), RB + RB * math.sin(a)))
    p.append((B2, D))
    return p


def girth_split(p, cuts):
    """Split a polyline at the given girth distances; returns the pieces."""
    out, cur, s = [], [p[0]], 0.0
    cuts = list(cuts)
    for a, b in zip(p, p[1:]):
        L = math.dist(a, b)
        while cuts and s + L >= cuts[0]:
            t = (cuts[0] - s) / L
            m = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            cur.append(m); out.append(cur); cur = [m]
            cuts.pop(0)
        cur.append(b); s += L
    out.append(cur)
    return out


def midship_svg():
    """Original drawing of a transversely framed, double-bottom general cargo ship, with the longitudinal system as an
    alternative layer. Each part is a <g data-part> so it can be tapped; a wide transparent copy of each stroke makes it easy to hit."""
    g = {k: [] for k, *_ in PARTS}
    sw = {}   # extra marks per part

    def add(part, d, cls='', width=None, fill=False, both=True, extra=''):
        for mirror in ((False, True) if both else (False,)):
            dd = d(mirror) if callable(d) else d
            g[part].append('<path d="%s" class="%s"%s%s/>' % (dd, ('pf ' if fill else 'ps ') + cls, (' style="stroke-width:%.1f"' % width) if width else '', extra))

    shell = shell_line()
    girth = sum(math.dist(a, b) for a, b in zip(shell, shell[1:]))
    # strakes: garboard (A) from the keel edge, then B, C on the bottom, the bilge strake round the turn, side strakes, sheerstrake
    bilge_start = B2 - RB - 0.8
    bilge_len = math.pi * RB / 2
    cuts = [1.9, bilge_start - 0.4, bilge_start + bilge_len + 0.4, girth - 1.5]
    pieces = girth_split(shell, cuts)
    names = ['garboard', 'bottom', 'bilge', 'shell', 'sheer']
    for nm, pc in zip(names, pieces):
        add(nm, lambda m, pc=pc: path(pc, m), 'shellp')
    add('keel', lambda m: path([(0, -0.02), (0.8, -0.02)], m), 'keelp')
    # strake letters on the port side, from the keel up
    letters = ''
    step = 1.9
    n = int(girth // step)
    for i in range(n + 1):
        s = min(i * step + step / 2, girth - 0.5)
        acc = 0.0
        for a, b in zip(shell, shell[1:]):
            L = math.dist(a, b)
            if acc + L >= s:
                t = (s - acc) / L
                y, z = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
                nx, nz = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
                letters += '<text x="%.1f" y="%.1f" class="strk" text-anchor="middle">%s</text>' % (X(-(y + nx * 0.7)), Y(z + nz * 0.7) + 4, 'ABCDEFGHIJKLMNOP'[i])
                break
            acc += L
    # double bottom
    add('tanktop', lambda m: path([(0, DB), (B2 - RB, DB)], m), 'platep')
    mx, mz = B2 - RB + RB * math.cos(-math.pi / 4), RB + RB * math.sin(-math.pi / 4)
    add('margin', lambda m: path([(B2 - RB, DB), (mx, mz)], m), 'platep')
    add('cgirder', path([(0, 0), (0, DB)]), 'platep', both=False)
    add('sgirder', lambda m: path([(4.5, 0), (4.5, DB)], m), 'platep')
    floor = [(0.06, 0.08), (B2 - RB, 0.08)]
    for i in range(0, 7):
        a = -math.pi / 2 + (math.pi / 4) * i / 6
        floor.append((B2 - RB + (RB - 0.08) * math.cos(a), RB + (RB - 0.08) * math.sin(a)))
    floor += [(B2 - RB, DB - 0.05), (0.06, DB - 0.05)]
    holes = ''
    for hy in (2.3, 6.6):
        holes += ' M%.1f %.1f a %.1f %.1f 0 1 0 %.1f 0 a %.1f %.1f 0 1 0 %.1f 0 Z' % (X(hy) - 0.75 * K, Y(0.75), 0.75 * K, 0.42 * K, 1.5 * K, 0.75 * K, 0.42 * K, -1.5 * K)
    add('floor', lambda m: path(floor, m, True) + (holes if not m else holes.replace('M%.1f' % (X(2.3) - 0.75 * K), 'M%.1f' % (X(-2.3) - 0.75 * K)).replace('M%.1f' % (X(6.6) - 0.75 * K), 'M%.1f' % (X(-6.6) - 0.75 * K))),
        'floorf', fill=True, extra=' fill-rule="evenodd"')
    add('bracket', lambda m: path([(B2 - RB, DB), (B2 - 0.18, DB), (B2 - 0.3, 3.4)], m, True), 'brk', fill=True)
    add('bilgekeel', lambda m: path([(mx, mz), (mx + 0.75 * math.cos(-math.pi / 4), mz + 0.75 * math.sin(-math.pi / 4))], m), 'platep', width=5)
    # transverse frame (in the plane of the drawing) / web frame for the longitudinal system
    add('frame', lambda m: path([(B2 - 0.06, 2.6), (B2 - 0.06, D - 0.35), (B2 - 0.32, D - 0.35), (B2 - 0.32, 2.6)], m, True), 'framef tr', fill=True)
    add('web', lambda m: path([(B2 - 0.06, 2.4), (B2 - 0.06, D - 0.5), (B2 - 1.0, D - 0.5), (B2 - 1.0, 2.6)], m, True), 'framef lg', fill=True)
    # decks
    deck = [(HATCH, deck_z(HATCH))] + [(y / 10, deck_z(y / 10)) for y in range(int(HATCH * 10) + 5, int(B2 * 10) - 13, 5)] + [(B2 - 1.4, deck_z(B2 - 1.4))]
    add('deck', lambda m: path(deck, m), 'platep')
    add('stringer', lambda m: path([(B2 - 1.4, deck_z(B2 - 1.4)), (B2, D)], m), 'platep', width=6)
    beam = [(HATCH, deck_z(HATCH) - 0.05)] + [(y / 10, deck_z(y / 10) - 0.05) for y in range(int(HATCH * 10) + 5, int(B2 * 10) - 3, 5)] + [(B2 - 0.32, deck_z(B2 - 0.32) - 0.05)]
    beam_lo = [(y, z - 0.35) for y, z in reversed(beam)]
    add('beam', lambda m: path(beam + beam_lo, m, True), 'framef', fill=True)
    add('knee', lambda m: path([(B2 - 0.32, D - 0.4), (B2 - 1.5, deck_z(B2 - 1.5) - 0.4), (B2 - 0.32, D - 1.6)], m, True), 'brk', fill=True)
    add('tween', lambda m: path([(HATCH, TWEEN), (B2 - 0.32, TWEEN)], m), 'platep')
    add('tween', lambda m: path([(HATCH, TWEEN - 0.05), (B2 - 0.32, TWEEN - 0.05), (B2 - 0.32, TWEEN - 0.35), (HATCH, TWEEN - 0.35)], m, True), 'framef', fill=True)
    add('pillar', lambda m: path([(HATCH - 0.1, DB), (HATCH - 0.1, TWEEN - 0.35)], m), 'platep', width=2.5)
    add('pillar', lambda m: path([(HATCH - 0.1, TWEEN), (HATCH - 0.1, deck_z(HATCH) - 0.4)], m), 'platep', width=2.5)
    add('coaming', lambda m: path([(HATCH, deck_z(HATCH) - 0.4), (HATCH, deck_z(HATCH) + 1.0)], m), 'platep')
    add('coaming', path([(-HATCH - 0.15, deck_z(HATCH) + 1.0), (HATCH + 0.15, deck_z(HATCH) + 1.0)]), 'platep', width=5, both=False)
    add('bulwark', lambda m: path([(B2, D), (B2, D + 1.05)], m), 'platep')
    add('bulwark', lambda m: path([(B2 - 0.25, D + 1.1), (B2 + 0.1, D + 1.1)], m), 'platep', width=6)
    add('stay', lambda m: path([(B2 - 0.9, deck_z(B2 - 0.9)), (B2 - 0.05, D + 0.95), (B2 - 0.05, D + 0.05)], m, True), 'brk', fill=True)
    # longitudinals (shown only for the longitudinal system): small bulb sections
    lp = [(y, 0.28) for y in (1.4, 2.9, 5.6, 7.2)] + [(y, DB - 0.28) for y in (1.4, 2.9, 5.6, 7.2)] + \
         [(B2 - 0.3, z) for z in (3.4, 4.6, 5.8, 7.0, 8.3, 9.5, 10.7)] + [(y, deck_z(y) - 0.3) for y in (4.9, 5.9, 6.9, 7.9, 8.9)]
    marks = ''.join('<circle cx="%.1f" cy="%.1f" r="4.2"/><circle cx="%.1f" cy="%.1f" r="4.2"/>' % (X(y), Y(z), X(-y), Y(z)) for y, z in lp)
    g['long'].append('<g class="lgdots lg">%s</g>' % marks)
    # callout numbers (starboard side only)
    anchors = {'keel': (0.4, -0.5), 'garboard': (1.3, -0.55), 'bottom': (6.2, -0.55), 'cgirder': (0, 0.75), 'sgirder': (4.5, 0.75),
               'floor': (3.4, 0.3), 'tanktop': (5.6, DB + 0.45), 'margin': (8.55, 0.95), 'bilge': (9.6, 0.15), 'bilgekeel': (10.4, -0.1),
               'bracket': (9.3, 2.0), 'shell': (10.6, 5.0), 'frame': (9.4, 5.2), 'sheer': (10.6, 11.2), 'deck': (6.0, D + 0.85),
               'stringer': (8.1, D + 0.7), 'beam': (6.4, D - 0.55), 'knee': (8.9, D - 1.1), 'tween': (6.8, TWEEN + 0.45),
               'pillar': (HATCH - 0.55, 4.6), 'coaming': (HATCH + 0.5, D + 1.0), 'bulwark': (10.6, D + 0.6), 'stay': (9.0, D + 1.55),
               'long': (7.2, DB - 0.75), 'web': (8.55, 7.0)}
    nums = {k: i + 1 for i, (k, *_) in enumerate(PARTS)}
    body = ''
    for k, *_ in PARTS:
        y, z = anchors[k]
        cls = ' lg' if k in ('long', 'web') else (' tr' if k == 'frame' else '')
        body += '<g class="part%s" data-part="%s" tabindex="-1">%s<g class="callout"><circle cx="%.1f" cy="%.1f" r="9"/><text x="%.1f" y="%.1f" text-anchor="middle">%d</text></g></g>' % (
            cls, k, ''.join(g[k]), X(y), Y(z), X(y), Y(z) + 3.6, nums[k])
    water = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="sea"/><line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" class="wl"/><text x="%.1f" y="%.1f" class="wlt">LWL</text>' % (
        X(-B2 - 1.4), Y(8.0), 2 * (B2 + 1.4) * K, 8.6 * K, X(-B2 - 1.4), X(B2 + 1.4), Y(8.0), Y(8.0), X(-B2 - 1.35), Y(8.0) - 6)
    cl = '<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" class="cl"/><text x="%.1f" y="%.1f" class="wlt" text-anchor="middle">centreline</text>' % (X(0), X(0), Y(-0.9), Y(D + 1.6), X(0), Y(D + 1.75))
    side = '<text x="%.1f" y="%.1f" class="wlt" text-anchor="middle">PORT · strakes lettered from the keel</text><text x="%.1f" y="%.1f" class="wlt" text-anchor="middle">STARBOARD · parts numbered</text>' % (
        X(-5.5), Y(-1.35), X(5.5), Y(-1.35))
    return ('<svg id="mid" class="sys-tr" viewBox="60 140 780 470" role="img" aria-label="Midship section of a double-bottom cargo ship; tap a part to name it">'
            + water + cl + side + body + letters + '</svg>')


# =====================================================================================  SHIP
def ship_pages(page, src_link):
    out = []
    out.append(hub(page, 'ship', 'Ship',
                   'A ship is a girder that floats. This room takes one apart: the named pieces of its hull, the arithmetic of floating and loading, '
                   'and the geometry that decides whether a ship that has been pushed over comes back upright.',
                   [('structure', 'The hull, piece by piece', 'A midship section with every part named: keel, strakes, floors, frames, beams, knees and the rest.'),
                    ('buoyancy', 'Buoyancy and the load line', 'Displacement, tonnes per centimetre, fresh-water allowance, and the load-line mark drawn to the Convention’s measurements.'),
                    ('stability', 'Stability', 'Load a hull and watch G, B and M, the righting lever and the IMO criteria. Computed from the hull’s own shape.')],
                   'Ship structure, buoyancy and load lines, and an interactive stability simulator.'))

    # ------------------------------------------------------------------ structure
    groups, legend = [], ''
    for i, (k, name, grp, desc) in enumerate(PARTS):
        if grp not in groups:
            groups.append(grp)
            legend += '%s<p class="label">%s</p><ol class="parts" start="%d">' % ('</ol>' if i else '', E(grp), i + 1)
        legend += '<li><button type="button" class="ghost pbtn%s" data-part="%s">%s</button></li>' % (' lg' if grp.startswith('Long') else '', k, E(name))
    legend += '</ol>'
    pjson = json.dumps({k: [n, d] for k, n, g, d in PARTS}, ensure_ascii=False)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Ship</a> / The hull</p>
<div class="head"><p class="eyebrow">Ship · structure</p><h1>The hull, piece by piece</h1>
<p class="lede col">Cut a cargo ship across the middle and you see a box girder. It is closed below by a double bottom and above by the deck, and
stiffened by ribs. Tap a part, or a name in the list, to see what it is and what it does.</p></div>
<div class="figure mid">{midship_svg()}</div>
<div class="mapgrid" style="margin-top:12px"><div class="plate"><p class="label">Framing system</p>
<div class="row" role="radiogroup" aria-label="Framing system"><button type="button" class="sysb" data-sys="tr" aria-pressed="true">Transverse</button><button type="button" class="sysb ghost" data-sys="lg" aria-pressed="false">Longitudinal</button></div>
<p class="small" id="sysnote"></p><p class="small">LWL: the load waterline.</p></div>
<div class="plate" aria-live="polite"><p class="label" id="pname">Tap a part</p><p id="pdesc" class="small">Parts on the starboard side are numbered; the strakes on the port side are lettered from the keel up.</p></div></div>
<section class="block"><h2>All the parts</h2><div class="legend">{legend}</div></section>
<section class="block"><h2>Why a ship is built like this</h2><p class="col">Waves load a ship like a beam: lifted at the middle by a crest it
<b>hogs</b>, with the deck stretched and the bottom squeezed; lifted at the ends it <b>sags</b>, and the stresses reverse. The material far from
the middle of the section, the deck and the bottom, does most of the work, just as the flanges of an I-beam do. That is why the stringer plate,
the sheerstrake and the keel are made thicker than the plating between them, and why openings in the deck are kept narrow and have rounded corners.</p>
<p class="col">In the <b>transverse system</b> a frame, a floor and a beam at every frame space form a closed ring that keeps the section in
shape; the plating alone carries the bending. In the <b>longitudinal system</b>, introduced by Joseph Isherwood (the first ship built on it, the tanker <i>Paul Paix</i>, sailed in 1908), closely spaced
fore-and-aft stiffeners add to the hull girder itself, and deep web frames several metres apart hold them up. Long ships, tankers and bulk
carriers are built longitudinally, at least in the bottom and deck.</p></section>
<div class="then col"><b>Then and now</b><p>Older ships were riveted: frames were angle bars, plates overlapped in their strakes, and the joints were
caulked. Welding, general after the Second World War, lets plates butt edge to edge, and the welded Liberty ships whose hulls cracked in cold seas
taught builders about brittle steel and stress concentrations at sharp corners. The names of the parts did not change. The drawing here is a
simplified, original diagram, and it is not to scale for plate thickness.</p></div>'''
    script = '<script>window.RK_PARTS = %s;</script>\n<script src="../../assets/hull.js"></script>\n' % pjson
    out.append(page('ship/structure/index.html', 'The hull, piece by piece · Reckoning', 'A tappable midship section of a cargo ship with every structural part named and explained.',
                    body, scripts=script, nav='ship'))

    # ------------------------------------------------------------------ buoyancy and load line
    LL = LOADLINE
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Ship</a> / Buoyancy and the load line</p>
<div class="head"><p class="eyebrow">Ship · buoyancy</p><h1>Buoyancy and the load line</h1>
<p class="lede col">A floating ship pushes aside its own mass of water (Archimedes). Its <b>displacement</b> is that mass. The heavier the
load, the deeper it floats. The <b>load line</b> painted on its side marks how deep it may legally go, in each season and in each kind of water.</p></div>
<div class="shape"><div class="figure ll"><svg id="llsvg" viewBox="0 0 640 520" role="img" aria-label="Load line mark drawn to scale"></svg></div>
<div class="stack"><div class="plate"><p class="label">The ship</p><div class="sliders">
<label>Length L <input type="range" id="lL" min="40" max="300" step="1" value="150"><output id="lLv"></output></label>
<label>Breadth B <input type="range" id="lB" min="8" max="50" step="0.5" value="23"><output id="lBv"></output></label>
<label>Summer draught T <input type="range" id="lT" min="2" max="18" step="0.1" value="9.5"><output id="lTv"></output></label>
<label><span>Block coefficient C<sub>B</sub></span> <input type="range" id="lCb" min="0.5" max="0.88" step="0.01" value="0.75"><output id="lCbv"></output></label>
<label><span>Waterplane coeff. C<sub>W</sub></span> <input type="range" id="lCw" min="0.65" max="0.95" step="0.01" value="0.85"><output id="lCwv"></output></label>
<label>Water density <input type="range" id="lrho" min="1.000" max="1.025" step="0.001" value="1.025"><output id="lrhov"></output></label>
</div><div class="qty" id="lq"></div></div></div></div>
<section class="block"><h2>The arithmetic</h2><p class="col">The block coefficient C<sub>B</sub> says how much of the box L × B × T the hull fills (about 0.8 for a
tanker, 0.6 for a fast container ship); C<sub>W</sub> does the same for the waterplane. With sea water at 1.025 t/m³:</p>
{tex(r'\Delta = \rho\,L\,B\,T\,C_B \qquad \mathrm{TPC} = \frac{\rho\,A_W}{100} = \frac{\rho\,L\,B\,C_W}{100} \qquad \mathrm{FWA} = \frac{\Delta}{40\,\mathrm{TPC}}\ \text{cm}')}
<p class="col"><b>TPC</b>, tonnes per centimetre immersion, is the load that sinks the ship one centimetre deeper. The <b>fresh water allowance</b>
is how much deeper the same ship floats in fresh water (density 1.000) than in the sea: for a wall-sided hull it comes to exactly 1/40 of the draught,
because fresh water is 1/40 less dense. In dock water between the two densities the allowance is taken in proportion
(Convention, article 12).</p></section>
<section class="block"><h2>The marks</h2><p class="col">The <b>deck line</b> marks the freeboard deck. Below it, by the assigned summer freeboard, the centre of the
<b>ring</b> (300 mm across, 25 mm wide) sits at the summer load line, with a 450 mm bar whose upper edge runs through its centre. Beside it, lines 230 mm long
mark the other load lines. The <b>upper edge</b> of each line is the limit. Tropical (T) is 1/48 of the summer draught above summer (S),
winter (W) the same below, and Winter North Atlantic (WNA), only for ships of 100 m or less, 50 mm below winter. The fresh-water lines (F, TF) lie aft of the vertical
line, raised by the fresh water allowance. The letters beside the ring identify the authority that assigned the freeboard. Sizes and rules: the {src_link('icll1966', True)} Convention, Annex I, regulations 4 to 8 and 40.</p></section>
<div class="then col"><b>Then and now</b><p>Samuel Plimsoll’s campaign against overloaded “coffin ships” led to compulsory load-line marks in British law in
1876; the first international convention came in 1930, the present one in 1966. Older handbooks give the fresh-water rule as 1/48 of the draught: the
1966 Convention still allows that figure, but only when the displacement at the summer waterline cannot be certified. Otherwise the allowance is Δ / 40 TPC.
Before metric units, the same rules were written with tons of 2240 lb, and with 35 cubic feet of sea water to the ton.</p></div>'''
    script = '<script>window.RK_LL = %s;</script>\n<script src="../../assets/stability.js"></script>\n<script src="../../assets/loadline.js"></script>\n' % json.dumps(LL) + TEX_RUN
    out.append(page('ship/buoyancy/index.html', 'Buoyancy and the load line · Reckoning', 'Displacement, tonnes per centimetre, fresh water allowance and the load line mark drawn to the 1966 Convention.',
                    body, extra_head=KATEX, scripts=script, nav='ship'))

    # ------------------------------------------------------------------ stability
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Ship</a> / Stability</p>
<div class="head"><p class="eyebrow">Ship · stability</p><h1>Stability</h1>
<p class="lede col">Weight acts down through the centre of gravity <b>G</b>; buoyancy acts up through the centre of the underwater volume, <b>B</b>.
Upright they are in line. Heel the ship and B moves towards the low side. If it moves far enough to lie outside G, the two forces form a couple
that turns the ship back. The arm of that couple is the righting lever <b>GZ</b>.</p></div>
<div class="shape"><div class="figure stab"><svg id="stsvg" viewBox="0 0 600 450" role="img" aria-label="Heeled ship section showing G, B, M and the righting lever"></svg></div>
<div class="stack"><div class="plate"><p class="label">Load the ship</p>
<div class="row"><select id="shull" aria-label="Hull"></select></div>
<div class="sliders">
<label>Draught T <input type="range" id="sT" step="0.01"><output id="sTv"></output></label>
<label>Height of G, KG <input type="range" id="sKG" step="0.01"><output id="sKGv"></output></label>
<label>G off centre <input type="range" id="sGy" step="0.01" value="0"><output id="sGyv"></output></label>
<label>Slack tank width <input type="range" id="sFs" min="0" step="0.1" value="0"><output id="sFsv"></output></label>
<label>Heel to show <input type="range" id="sH" min="0" max="90" step="0.5" value="20"><output id="sHv"></output></label>
</div><div class="qty" id="sq"></div></div></div></div>
<section class="block"><h2>The righting-lever curve</h2>
<div class="figure gzc"><svg id="gzsvg" viewBox="0 0 760 330" role="img" aria-label="GZ curve from 0 to 90 degrees of heel"></svg></div>
<p class="small col">Shaded: the areas the criteria measure. Dashed: the tangent at the origin, which reaches GM at one radian (57.3°); for small heels GZ ≈ GM sin θ.</p>
<div class="tablewrap" style="max-width:760px"><table><thead><tr><th>IMO criterion (2008 IS Code, A 2.2)</th><th>Required</th><th>This loading</th><th></th></tr></thead><tbody id="crit"></tbody></table></div>
<p class="small col">The criteria come from {src_link('imois2008', True)}. They apply to real ships of full form whose curves come from their own hull lines; here they are applied to a
prism so you can see how loading changes them, not to certify anything. Downflooding through openings, wind and the effect of the ship’s ends are not modelled.</p></section>
<section class="block"><h2>How it is computed</h2><p class="col">Nothing here comes from a stored table. For every angle the program cuts the hull section with a
waterline, moves the waterline until the cut-off area equals the upright underwater area (the displacement does not change when a ship heels), and takes the centroid of
that area as B. Then GZ is the horizontal distance between B and G. The hull is a prism, the same section along the whole length, so the calculation is
exact for a barge and an approximation for a ship.</p>
{tex(r'KM = KB + BM,\quad BM = \frac{I}{\nabla} = \frac{B^2}{12\,T}\ \text{(box)},\qquad GM = KM - KG,\qquad GZ \approx GM\sin\theta')}
{tex(r'GZ = \sin\theta\left(GM + \tfrac12 BM\tan^2\theta\right)\quad\text{(wall-sided, until the deck edge immerses)}')}
<p class="small col">Checked when the site is built: for a box, KB = T/2 and BM = B²/12T; GZ agrees with the wall-sided formula to 10⁻⁶ m up to deck-edge
immersion; a circular section gives GZ = (KM − KG) sin θ at every angle, because its metacentre is fixed at the centre; the angle of loll matches
tan θ = √(2|GM|/BM); and GZ(−θ) = −GZ(θ).</p></section>
<div class="lens col"><b>Free surface</b><p>Liquid in a partly filled tank flows to the low side as the ship heels, so its weight acts as if G were higher. For a
rectangular tank of breadth b the virtual rise is (ρ<sub>tank</sub>/ρ<sub>sea</sub>) · l b³ / 12 ∇. The cube makes wide tanks dangerous, which is why tanks
are divided by fore-and-aft bulkheads. Try the slack-tank slider.</p></div>
<div class="then col"><b>Then and now</b><p>Older practice gave stability as a table of KM and a “stability curve” for a few loadings, worked out by hand with
planimeters and integrators. The 1968 and 1993 IMO recommendations became the mandatory 2008 IS Code, which added weather criteria for wind and rolling.
The physics of G, B and M has not changed since Pierre Bouguer named the metacentre in 1746.</p></div>'''
    script = '<script src="../../assets/stability.js"></script>\n<script src="../../assets/stab-ui.js"></script>\n' + TEX_RUN
    out.append(page('ship/stability/index.html', 'Stability · Reckoning', 'Load a hull and watch G, B, M and the righting-lever curve, with the IMO intact stability criteria.',
                    body, extra_head=KATEX, scripts=script, nav='ship'))
    return out


# =====================================================================================  bases as skeletal formulas
from life import RING, STRUCT, HBONDS  # noqa: E402


def base_geom(key, cx, cy, r, facing):
    """Atom positions for a base. facing='right': the Watson-Crick edge (N1 of a purine) points right;
    facing='left': the edge (N3 of a pyrimidine) points left. y is downward (SVG)."""
    ring = STRUCT[key][0]
    if ring == 'purine':
        ang = {'N1': 0, 'C6': 60, 'C5': 120, 'C4': 180, 'N3': 240, 'C2': 300}
    else:
        ang = {'N3': 180, 'C4': 120, 'C5': 60, 'C6': 0, 'N1': 300, 'C2': 240}
    pos = {a: (cx + r * math.cos(math.radians(d)), cy - r * math.sin(math.radians(d))) for a, d in ang.items()}
    if ring == 'purine':   # five-membered ring built outward on the C4-C5 edge
        a, b = pos['C5'], pos['C4']
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = mx - cx, my - cy
        nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
        ap = r / (2 * math.tan(math.pi / 5)); R5 = r / (2 * math.sin(math.pi / 5))
        pc = (mx + nx * ap, my + ny * ap)
        t5 = math.atan2(a[1] - pc[1], a[0] - pc[0]); t4 = math.atan2(b[1] - pc[1], b[0] - pc[0])
        diff = math.atan2(math.sin(t4 - t5), math.cos(t4 - t5))
        step = -math.copysign(2 * math.pi / 5, diff)   # walk from C5 away from C4: C5, N7, C8, N9, (C4)
        for i, nm in enumerate(('N7', 'C8', 'N9'), 1):
            t = t5 + step * i
            pos[nm] = (pc[0] + R5 * math.cos(t), pc[1] + R5 * math.sin(t))
        centre5 = pc
    else:
        centre5 = None
    if facing == 'left' and ring == 'purine' or facing == 'right' and ring == 'pyrimidine':
        pos = {k: (2 * cx - x, y) for k, (x, y) in pos.items()}
        if centre5:
            centre5 = (2 * cx - centre5[0], centre5[1])
    subs = {}
    for atom, grp, order in STRUCT[key][2]:
        x, y = pos[atom]
        dx, dy = x - cx, y - cy
        if atom == 'C5' and ring == 'pyrimidine' or atom not in ('C6', 'C4', 'C2', 'C5'):
            pass
        L = math.hypot(dx, dy)
        subs[atom] = (x + dx / L * r * 0.95, y + dy / L * r * 0.95, grp, order)
    return pos, subs, centre5


def base_svg(key, cx, cy, r, facing, show_numbers=False):
    pos, subs, c5 = base_geom(key, cx, cy, r, facing)
    ring, dbl, _ = STRUCT[key]
    names, bonds = RING[ring]
    dbl = {frozenset(b) for b in dbl}
    out = ''
    def shorten(p, q, a_lab, b_lab):
        (x1, y1), (x2, y2) = p, q
        L = math.hypot(x2 - x1, y2 - y1)
        s1 = 8.5 if a_lab else 0; s2 = 8.5 if b_lab else 0
        return (x1 + (x2 - x1) * s1 / L, y1 + (y2 - y1) * s1 / L, x2 - (x2 - x1) * s2 / L, y2 - (y2 - y1) * s2 / L)
    for a, b in bonds:
        x1, y1, x2, y2 = shorten(pos[a], pos[b], a[0] != 'C', b[0] != 'C')
        out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/>' % (x1, y1, x2, y2)
        if frozenset((a, b)) in dbl:   # second line drawn inside the ring it belongs to
            in5 = ring == 'purine' and a in ('N7', 'C8', 'N9') or b in ('N7', 'C8', 'N9') and ring == 'purine'
            cxr, cyr = (c5 if in5 else (cx, cy))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = cxr - mx, cyr - my; L = math.hypot(dx, dy)
            o = 4.2
            ux, uy = (x2 - x1), (y2 - y1); ul = math.hypot(ux, uy)
            sh = 0.16
            out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/>' % (
                x1 + dx / L * o + ux * sh, y1 + dy / L * o + uy * sh, x2 + dx / L * o - ux * sh, y2 + dy / L * o - uy * sh)
    for atom, (x, y, grp, order) in subs.items():
        x0, y0 = pos[atom]
        x1, y1, x2, y2 = shorten((x0, y0), (x, y), False, True)
        out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/>' % (x1, y1, x2, y2)
        if order == 2:
            dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy)
            out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/>' % (x1 - dy / L * 4.5, y1 + dx / L * 4.5, x2 - dy / L * 4.5, y2 + dx / L * 4.5)
        lab = {'NH2': 'NH₂' if x >= x0 else 'H₂N', 'CH3': 'CH₃' if x >= x0 else 'H₃C', 'O': 'O'}[grp]
        anchor = 'middle' if abs(x - x0) < 4 else ('start' if x > x0 else 'end')
        dxl = -6 if anchor == 'start' else 6 if anchor == 'end' else 0
        out += '<text x="%.1f" y="%.1f" text-anchor="%s" class="at %s">%s</text>' % (x + dxl, y + 5, anchor, 'ox' if grp == 'O' else 'ni' if grp == 'NH2' else '', lab)
    sugar = 'N9' if ring == 'purine' else 'N1'
    hN = {'G': 'N1', 'T': 'N3', 'U': 'N3'}.get(key)
    for nm in names:
        x, y = pos[nm]
        if nm[0] == 'N':
            out += '<text x="%.1f" y="%.1f" text-anchor="middle" class="at ni">N</text>' % (x, y + 5)
            if nm == hN or nm == sugar:
                # H (or the bond to the sugar) pointing away from the ring
                ccx, ccy = (c5 if (ring == 'purine' and nm in ('N7', 'C8', 'N9')) else (cx, cy))
                dx, dy = x - ccx, y - ccy; L = math.hypot(dx, dy)
                if nm == sugar:
                    out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd sug"/><text x="%.1f" y="%.1f" text-anchor="middle" class="small-t">to sugar (C1′)</text>' % (
                        x + dx / L * 9, y + dy / L * 9, x + dx / L * r * 0.95, y + dy / L * r * 0.95, x + dx / L * r * 1.25, y + dy / L * r * 1.25 + 4)
                else:
                    out += '<text x="%.1f" y="%.1f" text-anchor="middle" class="at">H</text>' % (x + dx / L * 17, y + dy / L * 17 + 5)
        if show_numbers:
            ccx, ccy = (c5 if (ring == 'purine' and nm in ('N7', 'C8', 'N9')) else (cx, cy))
            out += '<text x="%.1f" y="%.1f" text-anchor="middle" class="num-t">%s</text>' % (x + (ccx - x) * 0.3, y + (ccy - y) * 0.3 + 3, nm[1:])
    return out, pos, subs


def pair_svg(pu, py, r=30):
    W, H = 470, 230
    cy = 110
    cx1, cx2 = 150, 150 + 4 * r
    a, pos1, sub1 = base_svg(pu, cx1, cy, r, 'right')
    b, pos2, sub2 = base_svg(py, cx2, cy, r, 'left')
    hb = ''
    def edge(base, at, sub, pos, side):
        """x of the near edge of an atom's label, facing the partner (side=+1: label on the left base, edge to its right)."""
        if at in sub:
            x, y, grp, order = sub[at]
            w = 30 if grp == 'NH2' else 8
            return x + side * w, y
        x, y = pos[at]
        ring_h = (base, at) in (('G', 'N1'), ('T', 'N3'), ('U', 'N3'))
        return x + side * (24 if ring_h else 9), y
    for p_at, y_at, donor in HBONDS[pu + py]:
        x1, y1 = edge(pu, p_at, sub1, pos1, 1)
        x2, y2 = edge(py, y_at, sub2, pos2, -1)
        hb += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="hb"/>' % (x1 + 3, y1, x2 - 3, y2)
    n = len(HBONDS[pu + py])
    title = '%s · %s: %s hydrogen bonds' % ({'A': 'adenine', 'G': 'guanine'}[pu], {'T': 'thymine', 'C': 'cytosine'}[py], 'two' if n == 2 else 'three')
    return '<figure class="pairfig"><svg viewBox="0 0 %d %d" role="img" aria-label="%s">%s%s%s</svg><figcaption class="small">%s</figcaption></figure>' % (W, H, E(title), a, b, hb, E(title))


def single_svg(key):
    ring = STRUCT[key][0]
    s, _, _ = base_svg(key, 140 if ring == 'purine' else 105, 95, 30, 'right' if ring == 'purine' else 'left', True)
    return '<svg viewBox="10 32 215 135" role="img" aria-label="%s">%s</svg>' % (E(key), s)


def nucleotide_svg():
    """Schematic nucleotide: phosphate on 5′, sugar ring with numbered carbons, base on 1′, 3′-OH."""
    cx, cy, r = 190, 120, 42
    ring = {'O4′': 90, 'C1′': 18, 'C2′': -54, 'C3′': -126, 'C4′': 162}
    p = {k: (cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for k, a in ring.items()}
    order = ['O4′', 'C1′', 'C2′', 'C3′', 'C4′']
    s = ''.join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/>' % (p[a][0], p[a][1], p[b][0], p[b][1]) for a, b in zip(order, order[1:] + order[:1]))
    s += '<text x="%.1f" y="%.1f" text-anchor="middle" class="at ox">O</text>' % (p['O4′'][0], p['O4′'][1] - 6)
    for k in ('C1′', 'C2′', 'C3′', 'C4′'):
        s += '<text x="%.1f" y="%.1f" text-anchor="middle" class="num-t">%s</text>' % (cx + (p[k][0] - cx) * 0.62, cy + (p[k][1] - cy) * 0.62 + 4, k[1:])
    c5 = (p['C4′'][0] - 30, p['C4′'][1] - 40)
    s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/><text x="%.1f" y="%.1f" class="num-t">5′</text>' % (p['C4′'][0], p['C4′'][1], c5[0], c5[1], c5[0] + 6, c5[1] + 4)
    s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/><circle cx="%.1f" cy="%.1f" r="22" class="phos"/><text x="%.1f" y="%.1f" text-anchor="middle" class="at">P</text><text x="%.1f" y="%.1f" text-anchor="middle" class="small-t">phosphate</text>' % (
        c5[0], c5[1], c5[0] - 45, c5[1] - 10, c5[0] - 66, c5[1] - 14, c5[0] - 66, c5[1] - 9, c5[0] - 66, c5[1] - 44)
    c3, c2 = p['C3′'], p['C2′']
    s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/><text x="%.1f" y="%.1f" text-anchor="middle" class="at ox">OH</text><text x="%.1f" y="%.1f" text-anchor="middle" class="small-t">3′ end: the next phosphate joins here</text>' % (
        c3[0], c3[1], c3[0] - 20, c3[1] + 26, c3[0] - 26, c3[1] + 42, c3[0] - 10, c3[1] + 62)
    s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/><text x="%.1f" y="%.1f" class="small-t">2′: H in DNA, OH in RNA</text>' % (
        c2[0], c2[1], c2[0] + 20, c2[1] + 26, c2[0] + 24, c2[1] + 40)
    bx, by = p['C1′'][0] + 50, p['C1′'][1] - 18
    s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="bd"/><rect x="%.1f" y="%.1f" width="96" height="40" rx="6" class="basebox"/><text x="%.1f" y="%.1f" text-anchor="middle" class="at">base</text><text x="%.1f" y="%.1f" text-anchor="middle" class="small-t">A, G, C, T (or U)</text>' % (
        p['C1′'][0], p['C1′'][1], bx, by + 20, bx, by, bx + 48, by + 25, bx + 48, by + 58)
    return '<svg viewBox="0 0 400 230" role="img" aria-label="A nucleotide: phosphate, sugar and base">%s</svg>' % s


def js_iupac(root):
    import subprocess, os
    r = subprocess.run(['node', '-e', 'var D=require(process.argv[1]);console.log(JSON.stringify(D.ORDER.map(function(c){return [c,D.SETS[c],D.complement(c)]})))',
                        os.path.join(root, 'assets', 'dnamath.js')], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


# =====================================================================================  CODE OF LIFE
def life_pages(page, src_link, root):
    out = []
    out.append(hub(page, 'life', 'Code of life',
                   'DNA is a code written in four letters, held in two strands that wind round each other. This room covers the letters themselves, '
                   'the shorthand biologists use when a letter is uncertain, the shapes the double helix can take, and the topology of DNA that is closed into a loop.',
                   [('bases', 'Bases and pairing', 'The four bases drawn atom by atom, the nucleotide, and why A pairs with T and G with C.'),
                    ('iupac', 'The IUPAC letters', 'R, Y, N and the rest: a decoder that expands, complements and searches sequences.'),
                    ('helix', 'The double helix', 'A, B and Z DNA in 3D, with their dimensions.'),
                    ('supercoil', 'Supercoiling', 'Topology lens: linking number = twist + writhe, computed on a ribbon you can coil.')],
                   'DNA bases and pairing, the IUPAC ambiguity letters with a decoder, the A, B and Z helices, and supercoiling as topology.'))

    # ------------------------------------------------------------------ bases
    rows = ''.join('<tr><td class="sym">%s</td><td>%s</td><td>%s</td><td class="mono">%s</td><td class="small">%s</td><td class="small">%s</td></tr>' % (
        k, E(n), kind, E(f.translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))), E(g), E(w)) for k, n, kind, l, f, g, w in BASES)
    singles = ''.join('<figure class="basefig">%s<figcaption><b>%s</b> · %s</figcaption></figure>' % (single_svg(k), E(n), kind) for k, n, kind, *_ in BASES)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Code of life</a> / Bases and pairing</p>
<div class="head"><p class="eyebrow">Code of life · the letters</p><h1>Bases and pairing</h1>
<p class="lede col">Each letter of DNA is a <b>base</b>, a flat ring of carbon and nitrogen. Two are double rings, the <b>purines</b> adenine and guanine; two are single rings,
the <b>pyrimidines</b> cytosine and thymine. RNA uses uracil in place of thymine. The edges of the bases carry hydrogen atoms and lone pairs placed so that
A fits only T and G fits only C.</p></div>
<section class="block"><div class="basegrid">{singles}</div>
<p class="small col">Skeletal formulas: each corner without a letter is a carbon atom, and hydrogens on carbon are not drawn. Small numbers are the standard ring numbering.
Blue: nitrogen; red: oxygen. Checked when the site is built: counting the drawn atoms and filling each one’s valence with hydrogen gives the molecular formula in the table.</p>
<div class="tablewrap"><table><thead><tr><th></th><th>Base</th><th>Ring</th><th>Formula</th><th>Groups</th><th>In</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="block"><h2>The pairs</h2><div class="pairs">{pair_svg('A', 'T')}{pair_svg('G', 'C')}</div>
<p class="col">Red dashes are hydrogen bonds: a hydrogen on one base held by a nitrogen or oxygen on the other. A·T makes two, G·C makes three,
so DNA rich in G and C holds its strands together more firmly and needs more heat to separate. The bonds to the sugars (bottom left and bottom right) lie
the same distance apart in both pairs. Because of this, either pair fits the same helix, and the sequence can be anything at all. This was the key observation of {src_link('watsoncrick1953', True)}.</p></section>
<section class="block"><h2>The nucleotide</h2><div class="nucfig">{nucleotide_svg()}</div>
<p class="col">A <b>nucleotide</b> is a base on a sugar (deoxyribose in DNA, ribose in RNA) with a phosphate. The sugar’s carbons are numbered with primes:
the phosphate hangs on 5′ and links to the 3′ carbon of the next sugar, so every strand has a direction, written 5′ → 3′. The two strands of a
double helix run in opposite directions, which is why the partner of a sequence is read backwards: its <a href="../iupac/">reverse complement</a>.</p></section>
<div class="then col"><b>Then and now</b><p>Chargaff found in 1950 that DNA contains as much A as T and as much G as C, without knowing why. The answer was
the pairing above (1953). The bases were drawn for years in other tautomeric forms, with hydrogens in different places; Watson and Crick’s model worked
only once the keto and amino forms shown here were used.</p></div>'''
    out.append(page('life/bases/index.html', 'Bases and pairing · Reckoning', 'The four DNA bases drawn atom by atom, the nucleotide, and Watson–Crick pairing.', body, nav='life'))

    # ------------------------------------------------------------------ IUPAC
    js = js_iupac(root)
    meaning = {l: (m, mn) for l, m, mn in IUPAC}
    rows = ''.join('<tr><td class="sym">%s</td><td>%s</td><td class="small">%s</td><td class="mono">%s</td><td class="sym">%s</td></tr>' % (
        l, E(meaning[l][0]), E(meaning[l][1]), '{' + ', '.join(st) + '}', c) for l, st, c in js)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Code of life</a> / The IUPAC letters</p>
<div class="head"><p class="eyebrow">Code of life · shorthand</p><h1>The IUPAC letters</h1>
<p class="lede col">Sequencers are not always sure which base they read, and many enzymes recognise a family of sequences rather than one. The IUPAC–IUB code
gives every <b>set</b> of bases its own letter: R for “A or G”, N for “any”. Fifteen letters cover all fifteen non-empty sets of four bases.</p></div>
<div class="plate"><p class="label">Decoder</p>
<div class="row"><input id="iseq" type="text" value="GTYRAC" spellcheck="false" autocapitalize="characters" aria-label="Sequence with IUPAC letters" style="flex:1;min-width:220px;font-family:var(--mono)">
<label class="small"><input type="checkbox" id="irna" style="min-height:auto"> RNA (U for T)</label></div>
<div class="row">{''.join('<button class="ghost" type="button" data-iseq="%s">%s</button>' % (v, E(n)) for v, n in (('GTYRAC', 'HincII site'), ('GANTC', 'HinfI site'), ('YATR', 'Y A T R'), ('TATAWAWR', 'TATA box (consensus)'), ('NNNN', 'NNNN')))}</div>
<div class="qty" id="iq"></div></div>
<div class="plate"><p class="label">Find a pattern in a sequence (both strands)</p>
<div class="row"><input id="ipat" type="text" value="GTYRAC" spellcheck="false" autocapitalize="characters" aria-label="Pattern" style="width:12em;font-family:var(--mono)"></div>
<textarea id="itgt" rows="3" spellcheck="false" aria-label="Sequence to search" style="width:100%;font:16px var(--mono)">ATGGTCAACGCTAGTTAACCGGTCGACATTGTTGACGGAGTCAACTAG</textarea>
<div id="ihits" class="seqout"></div></div>
<section class="block"><h2>The table</h2><div class="tablewrap" style="max-width:820px"><table><thead><tr><th>Letter</th><th>Means</th><th>Why that letter</th><th>Set</th><th>Complement</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small col">Code: {src_link('iupac1985', True)}. The sets live in one table in the site’s code; the meanings, the complements and the decoder are all generated from it,
and the build checks that the complement of every letter’s complement is the letter itself, and that the meanings above say the same as the sets.</p></section>
<div class="lens col"><b>Why the complements come out this way</b><p>Complementing a set swaps A with T and G with C inside it. Purines become pyrimidines, so R ↔ Y. Strong stays strong and weak
stays weak, so S and W are their own complements. Keto and amino swap (K ↔ M), and “not A” becomes “not T” (B ↔ V), just as D ↔ H.</p></div>'''
    out.append(page('life/iupac/index.html', 'The IUPAC letters · Reckoning', 'IUPAC ambiguity letters for nucleic acids with a decoder, complements and a two-strand pattern search.',
                    body, scripts='<script src="../../assets/dnamath.js"></script>\n<script src="../../assets/iupac.js"></script>\n', nav='life'))

    # ------------------------------------------------------------------ helix
    frows = ''.join('<tr><td class="sym">%s</td><td>%s</td><td class="num">%s</td><td class="num">%.3f</td><td class="num">%+.1f°</td><td class="num">%.2f</td><td class="num">≈ %.1f</td><td class="num">%+d°</td><td class="small">%s</td><td class="small">%s</td></tr>' % (
        f, h, n, r, t, p, d, tl, E(g), E(w)) for f, h, n, r, t, p, d, tl, g, w, k in FORMS)
    fjson = json.dumps([{'f': f, 'hand': h, 'n': n, 'rise': r, 'twist': t, 'pitch': p, 'diam': d} for f, h, n, r, t, p, d, *_ in FORMS])
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Code of life</a> / The double helix</p>
<div class="head"><p class="eyebrow">Code of life · shape</p><h1>The double helix</h1>
<p class="lede col">The two strands wind round a common axis with the base pairs stacked between them like the treads of a spiral stair. The same chemistry
can take more than one shape: the familiar <b>B</b> form, the squat <b>A</b> form, and the left-handed <b>Z</b> form.</p></div>
<div class="shape"><div class="figure globe" style="aspect-ratio:3/4"><canvas id="hx" aria-label="Double helix in 3D: drag to turn"></canvas><p class="hint">drag to turn</p></div>
<div class="stack"><div class="plate"><p class="label">Form</p><div class="row" role="radiogroup" aria-label="Form">{''.join('<button type="button" class="hxf%s" data-f="%s" aria-pressed="%s">%s-DNA</button>' % ('' if f == 'B' else ' ghost', f, 'true' if f == 'B' else 'false', f) for f, *_ in FORMS)}</div>
<div class="sliders"><label>Base pairs <input type="range" id="hxn" min="6" max="36" step="1" value="24"><output id="hxnv"></output></label></div>
<div class="qty" id="hxq"></div>
<p class="small"><span class="key" style="background:#2f7d4f"></span> A &nbsp;<span class="key" style="background:#c8261d"></span> T &nbsp;<span class="key" style="background:#e8b500"></span> G &nbsp;<span class="key" style="background:#1d4f91"></span> C</p></div></div></div>
<section class="block"><h2>The three forms</h2><div class="tablewrap"><table><thead><tr><th>Form</th><th>Hand</th><th>bp per turn</th><th>Rise per bp (nm)</th><th>Twist per bp</th><th>Pitch (nm)</th><th>Diameter (nm)</th><th>Base-pair tilt</th><th>Grooves</th><th>Found in</th></tr></thead><tbody>{frows}</tbody></table></div>
<p class="small col">A and B: fibre models of {src_link('arnott1972', True)}; Z: the crystal structure of {src_link('wang1979z', True)}. Diameters and tilts are rounded, as given in {src_link('saenger1984', True)}.
In solution B-DNA turns a little less tightly than in fibres: {src_link('wang1979', True)} measured {B_SOLUTION_BP_PER_TURN} ± 0.1 bp per turn.
The build checks that the twist is 360° divided by the base pairs per turn, and that the pitch is the rise times the base pairs per turn. The 3D model is drawn from these numbers. It is a diagram, not an atomic model.</p></section>
<div class="then col"><b>Then and now</b><p>The 1953 model had 10 base pairs per turn and a pitch of 3.4 nm, read from Rosalind Franklin and Raymond Gosling’s X-ray photographs of
the B form. The left-handed Z form was not seen until 1979, when a short (CG)<sub>3</sub> crystal was solved at atomic resolution. In it the backbone zigzags
because the repeating unit is two base pairs, not one.</p></div>'''
    out.append(page('life/helix/index.html', 'The double helix · Reckoning', 'A-, B- and Z-DNA in 3D with their helical parameters.',
                    body, scripts=THREE + '<script>window.RK_FORMS = %s;</script>\n<script src="../../assets/dnamath.js"></script>\n<script src="../../assets/helix.js"></script>\n' % fjson, nav='life'))

    # ------------------------------------------------------------------ supercoil
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Code of life</a> / Supercoiling</p>
<div class="head"><p class="eyebrow">Code of life · topology lens</p><h1>Supercoiling</h1>
<p class="lede col">Many DNA molecules are closed loops: bacterial chromosomes, plasmids, the DNA of mitochondria. Once a loop is closed, the number of times one strand
winds round the other, the <b>linking number</b> Lk, cannot change without cutting a strand. It can still be spent in two ways: as <b>twist</b>
(the strands winding round each other) or as <b>writhe</b> (the whole axis coiling on itself).</p></div>
{tex(r'\mathrm{Lk} = \mathrm{Tw} + \mathrm{Wr}')}
<div class="shape"><div class="figure globe" style="aspect-ratio:1/1"><canvas id="sc" aria-label="Closed DNA ribbon in 3D: drag to turn"></canvas><p class="hint">drag to turn</p></div>
<div class="stack"><div class="plate"><p class="label">The loop</p>
<div class="row" role="radiogroup" aria-label="Kind of supercoil"><button type="button" class="scf" data-f="plect" aria-pressed="true">Interwound</button><button type="button" class="scf ghost" data-f="toroid" aria-pressed="false">Toroidal</button></div>
<div class="sliders"><label>Extra turns ΔLk <input type="range" id="scl" min="-6" max="6" step="1" value="-4"><output id="sclv"></output></label>
<label>Coiling <input type="range" id="scs" min="0" max="1" step="0.02" value="0.6"><output id="scsv"></output></label></div>
<div class="qty" id="scq"></div></div>
<p class="small">The ribbon’s two colours are its two edges; count how often they swap to see the twist. The ribbon shows only the extra turns, ΔLk:
the 1 turn per 10.4 base pairs of the relaxed helix is left out so the picture stays readable.</p></div></div>
<section class="block"><h2>What the numbers mean</h2><p class="col">Drag <b>Coiling</b> and watch the exchange. With the loop flat, all the extra turns are twist.
As the axis coils, writhe grows and twist shrinks by exactly the same amount, while Lk stays fixed. Nothing is cut, so Lk cannot change. A strained,
over- or under-twisted helix relieves itself by coiling, as a twisted telephone cord does.</p>
<p class="col">The page computes all three numbers independently. <b>Writhe</b> is the Gauss double integral of the axis with itself; <b>twist</b> comes from how much the
ribbon turns about the axis beyond parallel transport; <b>Lk</b> is the Gauss linking integral of the ribbon’s two edges, treated as two separate closed curves.
That Tw + Wr equals that integer is the Călugăreanu–White–Fuller theorem ({src_link('white1969', True)}; {src_link('fuller1971', True)}). Here it is a measurement, not an assumption.
Integrals use the exact formula for straight segments of {src_link('klenin2000', True)}.</p></section>
<section class="block"><h2>In the cell</h2><p class="col">DNA in cells is usually <b>negatively</b> supercoiled: it has fewer turns than a relaxed helix, which makes the strands easier
to open for copying and reading. Negative supercoils take a right-handed interwound shape or a left-handed toroidal one; the second is how DNA wraps round
the histone spools of chromatin. Enzymes called <b>topoisomerases</b> change Lk on purpose: type I cut one strand and change Lk in steps of 1, type II cut both
and pass a double strand through, in steps of 2. Bacterial <b>gyrase</b> spends energy to add negative turns ({src_link('gellert1976', True)}). Supercoiling itself
was discovered in a small viral DNA ({src_link('vinograd1965', True)}).</p></section>
<div class="lens col"><b>Topology lens</b><p>Linking number is a topological invariant: no bending or stretching changes it, only cutting does. Twist and writhe are not:
they depend on the exact shape. Compare the <a href="../../shape/topology/">Euler characteristic</a>, another number that survives any deformation, and the
<a href="https://followorbounce.github.io/knots/">Knot Atlas</a>, where knots are classified by invariants of the same kind.</p></div>'''
    out.append(page('life/supercoil/index.html', 'Supercoiling · Reckoning', 'Linking number, twist and writhe of closed DNA, computed live on a ribbon you can coil.',
                    body, extra_head=KATEX, scripts=THREE + '<script src="../../assets/dnamath.js"></script>\n<script src="../../assets/supercoil.js"></script>\n' + TEX_RUN, nav='life'))
    return out


# =====================================================================================  GLOSSARY and NAMES
def glossary_page(page, src_link):
    def link(l, up):
        if not l:
            return ''
        return l if l.startswith('http') else up + l
    rows = ''.join('<tr data-q="%s"><td>%s</td><td lang="es">%s</td><td lang="fr">%s</td><td class="small">%s</td></tr>' % (
        E(' '.join((en, es, fr, d)).lower()), ('<a href="%s">%s</a>' % (E(link(l, '../')), E(en))) if l else E(en), E(es), E(fr), E(d)) for en, es, fr, d, l in TERMS)
    same = ''.join('<div class="card"><h3>%s</h3><ul class="small">%s</ul></div>' % (E(w), ''.join(
        '<li><b>%s</b>: %s</li>' % (E(room), ('<a href="%s">%s</a>' % (E(link(l, '../')), E(m))) if l else E(m)) for room, m, l in uses)) for w, uses in SAME_WORD)
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Glossary</p>
<div class="head"><p class="eyebrow">Reference · {len(TERMS)} terms</p><h1>Glossary</h1>
<p class="lede col">The words of the sea and the ship in English, Spanish and French, each linked to the page that explains it. Below them are words that
mean different things in different rooms of this handbook.</p></div>
<div class="plate"><p class="label">Find a word</p><div class="row"><input id="gq" type="search" placeholder="in any of the three languages" aria-label="Filter the glossary" style="flex:1;min-width:200px"></div></div>
<section class="block"><div class="tablewrap"><table id="gtab"><thead><tr><th>English</th><th>Español</th><th>Français</th><th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small col">Nouns are given with their article, because the gender comes with the word. Spellings and nautical senses checked in {src_link('rae', True)} and {src_link('cnrtl', True)}.
Some words have more than one equivalent at sea; the one given is the usual one in a ship’s papers.</p></section>
<section class="block"><h2>One word, several meanings</h2><div class="grid">{same}</div></section>'''
    script = '''<script>
(function(){var q=document.getElementById('gq'),rows=document.querySelectorAll('#gtab tbody tr');
q.addEventListener('input',function(){var t=q.value.trim().toLowerCase();rows.forEach(function(r){r.hidden=t&&r.getAttribute('data-q').indexOf(t)<0;});});})();
</script>
'''
    return page('glossary/index.html', 'Glossary · Reckoning', 'Nautical terms in English, Spanish and French, and words that mean different things in different fields.', body, scripts=script, nav='glossary', ld=[{
        '@type': 'DefinedTermSet', 'name': 'Reckoning glossary', 'url': 'https://followorbounce.github.io/reckoning/glossary/',
        'inLanguage': ['en', 'es', 'fr'],
        'hasDefinedTerm': [{'@type': 'DefinedTerm', 'name': en, 'description': d,
                            'alternateName': [x for x in (es, fr) if x]} for en, es, fr, d, l in TERMS]}])


def names_page(page, src_link):
    gods = ''.join('<tr><td>%s</td><td>%s</td><td class="small">%s</td><td class="small">%s</td></tr>' % (E(g), E(r), E(d), E(t)) for g, r, d, t in GODS)
    moons = ''.join('<tr><td><b>%s</b></td><td class="small">%s</td><td class="small">%s</td></tr>' % (E(p), E(m), E(t)) for p, m, t in MOON_THEMES)
    dwarf = ''.join('<li><b>%s</b>: %s</li>' % (E(n), E(t)) for n, t in DWARF)
    days = ''.join('<tr><td><b>%s</b></td><td class="small">%s</td><td><i>%s</i></td><td lang="es">%s</td><td lang="fr">%s</td></tr>' % (E(e), E(o), E(l), E(s), E(f)) for e, o, l, s, f, n in WEEKDAYS)
    dnotes = ' '.join(E(n) for *_, n in WEEKDAYS if n)
    months = ''.join('<tr><td><b>%s</b></td><td class="small">%s</td></tr>' % (E(m), E(t)) for m, t in MONTHS)
    els = ''.join('<tr><td>%s</td><td class="sym">%s</td><td class="small">%s</td></tr>' % (E(n), E(s), E(t)) for n, s, t in ELEMENTS)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / Names from the sky</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · naming</p><h1>Names from the sky</h1>
<p class="lede col">The gods of Greece and Rome named the planets, and through them the days of the week, half the months and a dozen chemical elements.
Today the International Astronomical Union keeps the custom alive with a theme for each planet’s moons.</p></div>
<section class="block"><h2>Gods and what carries their names</h2><div class="tablewrap"><table><thead><tr><th>Greek</th><th>Roman</th><th>God of</th><th>Named after them</th></tr></thead><tbody>{gods}</tbody></table></div>
<p class="small col">Rome took most Greek gods by identifying them with its own (Zeus with Iuppiter, Hera with Juno); a few, like Apollo, came over with their Greek names.
The Roman god of the Sun was Sol. Apollo and Artemis came to be linked with the Sun and Moon only later. For the planets themselves, see <a href="../planets/">Planets and their names</a>.</p></section>
<section class="block"><h2>Moons: a theme for each planet</h2><div class="tablewrap"><table><thead><tr><th>Planet</th><th>Moons</th><th>Theme</th></tr></thead><tbody>{moons}</tbody></table></div>
<p class="small col">Rules and themes: {src_link('gazetteer', True)}; Jupiter’s convention: {src_link('carnegie2018', True)}.</p>
<h3>Dwarf planets</h3><ul class="col">{dwarf}</ul></section>
<section class="block"><h2>The week</h2><div class="tablewrap"><table><thead><tr><th>English</th><th>Old English: whose day</th><th>Latin</th><th>Spanish</th><th>French</th></tr></thead><tbody>{days}</tbody></table></div>
<p class="small col">The seven-day week named after the seven moving lights of the sky (Sun, Moon and the five planets seen by eye) spread through the Roman world in the first centuries AD.
The Germanic peoples put their own gods in place of the Roman ones. {dnotes} Etymologies: {src_link('oed', True)}.</p></section>
<section class="block"><h2>The months</h2><div class="tablewrap" style="max-width:720px"><table><tbody>{months}</tbody></table></div>
<p class="small col">September to December keep the numbers of a Roman year that began in March, which is why the ninth month is called the seventh.</p></section>
<section class="block"><h2>Elements</h2><div class="tablewrap" style="max-width:820px"><table><thead><tr><th>Element</th><th>Symbol</th><th>Named after</th></tr></thead><tbody>{els}</tbody></table></div>
<p class="small col">Name origins: {src_link('rsc', True)}.</p></section>'''
    return page('sky/names/index.html', 'Names from the sky · Reckoning', 'Greek and Roman gods and the planets, moons, weekdays, months and elements named after them.', body, nav='sky')
