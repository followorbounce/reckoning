#!/usr/bin/env python3
"""Build the Reckoning site: python3 build.py

Runs the checks in tests/ first and stops if any fails, then writes every page from
the data in data/. Never hand-edit generated HTML (index.html and the measure/,
shape/, about/ folders, sitemap.xml, robots.txt)."""
import html
import json
import math
import os
import subprocess
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'data'))
from units import UNITS, KINDS, TEMP_OFFSET  # noqa: E402
from si import CONSTANTS, BASE, DERIVED, PREFIXES  # noqa: E402
from sources import SOURCES  # noqa: E402
from shapes import SHAPES, VALID  # noqa: E402
from texts import KIND_PAGES, SYSTEM_ORDER  # noqa: E402

SITE = 'https://followorbounce.github.io/reckoning/'
E = html.escape
KATEX = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">\n'
         '<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>\n')
THREE = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
         '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>\n')
FLAGS = ('<svg viewBox="0 0 36 24" aria-hidden="true"><rect width="36" height="24" fill="#c8261d"/>'
         '<rect x="15" width="6" height="24" fill="#e8b500"/><rect y="9" width="36" height="6" fill="#e8b500"/></svg>')

ROOMS = [
    ('measure', 'Measure', 'Units, their exact definitions, and a converter that says where every factor comes from.', 1),
    ('shape', 'Shape', 'Areas and volumes of 42 figures and solids, each formula checked, with a topology lens.', 1),
    ('number', 'Number', 'Symbols, Greek letters, trigonometry on the unit circle, logarithms and a working slide rule.', 3),
    ('sky', 'Sky & sea', 'Latitude and longitude on a globe, great circles against rhumb lines, the kinds of time.', 3),
    ('weather', 'Weather', 'The Beaufort scale with an animated sea, sea and visibility scales, weather symbols.', 2),
    ('signal', 'Signal', 'Code flags, Morse with sound and correct timing, phonetic alphabets, sound signals.', 2),
    ('ship', 'Ship', 'A hull cutaway with every named part, buoyancy, and a stability simulator.', 4),
    ('life', 'Code of life', 'DNA bases and pairing in 3D, the IUPAC letters, and supercoiling as topology.', 4),
]


def page(rel_path, title, desc, body, extra_head='', scripts='', nav=None):
    depth = rel_path.count('/')
    up = '../' * depth
    navs = ''.join('<a href="%s%s/"%s>%s</a>' % (up, k, ' aria-current="page"' if nav == k else '', n)
                   for k, n in (('measure', 'Measure'), ('shape', 'Shape'), ('about', 'About')))
    canon = SITE + (rel_path[:-len('index.html')] if rel_path.endswith('index.html') else rel_path)
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta name="theme-color" content="#14212b">
<link rel="icon" href="data:image/svg+xml,{FLAGS.replace('#', '%23').replace('"', "'")}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{up}assets/site.css">
{extra_head}<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "bba4e16a7d9b4d9985eda0cda2624e60"}}'></script>
</head>
<body>
<header class="bar"><div class="wrap">
<a class="mark" href="{up}index.html">{FLAGS}Reckoning</a>
<nav class="nav" aria-label="Rooms">{navs}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<p>Reckoning: an interactive handbook of measure, shape and signal. Every value cites a primary standard; every formula is checked when the site is built. <a href="{up}about/">How it is checked</a>.</p>
<p>Part of the <a href="https://followorbounce.github.io/">followorbounce</a> knowledge network.</p>
</div></footer>
{scripts}</body>
</html>
'''
    path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(out)
    return rel_path


# ------------------------------------------------------------------ helpers
def fnum(x, sig=12):
    """Exact Fraction -> decimal text: full if it terminates (up to 30 digits), else rounded with an ellipsis."""
    x = F(x)
    n, d = x.numerator, x.denominator
    t = d
    for p in (2, 5):
        while t % p == 0:
            t //= p
    neg = n < 0
    n = abs(n)
    if t == 1:
        ip, rem = divmod(n, d)
        digs = ''
        while rem and len(digs) < 30:
            rem *= 10
            q, rem = divmod(rem, d)
            digs += str(q)
        s = group_int(ip) + ('.' + group_frac(digs) if digs else '')
        return ('−' if neg else '') + s
    v = float(x)
    s = '%.*g' % (sig, v)
    if 'e' in s:
        m, e = s.split('e')
        return ('−' if neg else '') + m + ' × 10<sup>%d</sup>' % int(e) + '…'
    ip, _, fp = s.partition('.')
    return ('−' if neg else '') + group_int(int(ip)) + ('.' + group_frac(fp) if fp else '') + '…'


def group_int(i):
    s = str(i)
    out = ''
    while len(s) > 3:
        out = ' ' + s[-3:] + out
        s = s[:-3]
    return s + out


def group_frac(s):
    return ' '.join(s[i:i + 3] for i in range(0, len(s), 3))


def src_link(key, short=False):
    s = SOURCES[key]
    return '<a href="%s" rel="noopener"%s>%s</a>' % (E(s['url']), (' title="%s"' % E(s['title'])) if short else '', E(s['short'] if short else s['title']))


def units_json():
    kinds = {k: {'name': v['name'], 'si': v['si'], 'pair': list(KIND_PAGES[k]['pair'])} for k, v in KINDS.items()}
    us = []
    for u in UNITS:
        o = {'id': u['id'], 'name': u['name'], 'sym': u['sym'], 'kind': u['kind'], 'n': str(u['f'].numerator), 'd': str(u['f'].denominator),
             'exact': u['exact'], 'by': u['by'], 'src': u['src']}
        if u['kind'] == 'temperature':
            off = TEMP_OFFSET[u['id']]
            o['on'], o['od'] = str(off.numerator), str(off.denominator)
        us.append(o)
    return json.dumps({'kinds': kinds, 'units': us, 'sources': {k: v['by'].split(',')[0] for k, v in SOURCES.items()}},
                      ensure_ascii=False, separators=(',', ':'))


def converter(kind=None, pair=None, title='Convert'):
    ks = '' if kind else '<select class="ck" id="ck-%s" aria-label="Quantity"></select>' % (pair[0] if pair else 'all')
    uid = (kind or 'all') + '-' + (pair[0] if pair else 'x')
    return f'''<div class="plate converter"{' data-kind="%s"' % kind if kind else ''}{' data-pair="%s,%s"' % pair if pair else ''}>
  <p class="label">{E(title)}</p>
  <div class="row">{ks}<input class="ca" id="ca-{uid}" type="text" inputmode="decimal" value="1" aria-label="Amount">
    <select class="cf" id="cf-{uid}" aria-label="From unit"></select><button class="cs ghost" type="button" aria-label="Swap units">⇄</button>
    <select class="ct" id="ct-{uid}" aria-label="To unit"></select></div>
  <p class="out" aria-live="polite"></p>
  <div class="prov"></div>
</div>'''


def conv_scripts(up):
    return '<script>window.RK_UNITS = %s;</script>\n<script src="%sassets/convert.js"></script>\n' % (units_json(), up)


# ------------------------------------------------------------------ thumbnails for plane figures and solids
def thumb(sh):
    """A small static icon (SVG) for hub cards, drawn from default parameters."""
    v = {p['key']: p['default'] for p in sh['params']}
    s = sh['slug']
    pts = None
    W = 120
    def poly(p):
        xs = [q[0] for q in p]; ys = [q[1] for q in p]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        k = 80 / max(x1 - x0, y1 - y0, 1e-6)
        return ' '.join('%.1f,%.1f' % (60 + (q[0] - (x0 + x1) / 2) * k, 46 - (q[1] - (y0 + y1) / 2) * k) for q in p)
    def arc(cx, cy, r, a0, a1, n=48):
        return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    if sh['dim'] == 2:
        t = math.radians(v.get('t', 60))
        if s == 'square': pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        elif s == 'rectangle': pts = [(0, 0), (v['a'], 0), (v['a'], v['b']), (0, v['b'])]
        elif s == 'parallelogram': pts = [(0, 0), (v['b'], 0), (v['b'] + v['c'] * math.cos(t), v['c'] * math.sin(t)), (v['c'] * math.cos(t), v['c'] * math.sin(t))]
        elif s == 'rhombus': pts = [(-v['p'] / 2, 0), (0, v['q'] / 2), (v['p'] / 2, 0), (0, -v['q'] / 2)]
        elif s == 'trapezoid': o = (v['a'] - v['b']) * 0.3; pts = [(0, 0), (v['a'], 0), (o + v['b'], v['h']), (o, v['h'])]
        elif s == 'quadrilateral': pts = [(-0.4 * v['p'], 0), (0.65 * v['q'] * math.cos(t), 0.65 * v['q'] * math.sin(t)), (0.6 * v['p'], 0), (-0.35 * v['q'] * math.cos(t), -0.35 * v['q'] * math.sin(t))]
        elif s == 'triangle':
            a, b, c = v['a'], v['b'], v['c']; cx = (b * b + c * c - a * a) / (2 * c); pts = [(0, 0), (c, 0), (cx, math.sqrt(b * b - cx * cx))]
        elif s == 'right-triangle': pts = [(0, 0), (v['a'], 0), (0, v['b'])]
        elif s == 'isosceles-triangle': pts = [(-v['b'] / 2, 0), (v['b'] / 2, 0), (0, math.sqrt(v['s'] ** 2 - v['b'] ** 2 / 4))]
        elif s == 'equilateral-triangle': pts = [(0, 0), (1, 0), (0.5, math.sqrt(3) / 2)]
        elif s == 'circle': pts = arc(0, 0, 1, 0, 2 * math.pi)
        elif s == 'sector': pts = [(0, 0)] + arc(0, 0, 1, 0, t)
        elif s == 'segment': pts = arc(0, 0, 1, -t / 2, t / 2)
        elif s == 'ellipse': pts = [(v['a'] * math.cos(2 * math.pi * i / 64), v['b'] * math.sin(2 * math.pi * i / 64)) for i in range(65)]
        elif s == 'spandrel': pts = [(0, 0), (1, 0)] + arc(1, 1, 1, -math.pi / 2, -math.pi) + [(0, 1)]
        elif s in ('hexagon', 'octagon', 'regular-polygon'):
            n = {'hexagon': 6, 'octagon': 8}.get(s, 7); pts = [(math.cos(math.pi / 2 + 2 * math.pi * i / n), math.sin(math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
        elif s == 'annulus':
            return ('<svg viewBox="0 0 120 92" aria-hidden="true"><circle cx="60" cy="46" r="40" class="shp"/>'
                    '<circle cx="60" cy="46" r="21" class="shp2"/></svg>')
        elif s == 'ring-sector':
            pts = arc(0, 0, 1, 0, t) + arc(0, 0, 0.57, t, 0)
        return '<svg viewBox="0 0 120 92" aria-hidden="true"><polygon class="shp" points="%s"/></svg>' % poly(pts)
    # solids: simple line drawings by family
    icons = {
        'box': '<path class="shp" d="M30 34 L70 34 L70 74 L30 74 Z"/><path class="shp" d="M30 34 L48 20 L88 20 L70 34 Z"/><path class="shp" d="M70 34 L88 20 L88 60 L70 74 Z"/>',
        'prism': '<path class="shp" d="M36 30 L52 22 L74 22 L86 30 L74 38 L52 38 Z"/><path class="shp" d="M36 30 L36 72 L52 80 L52 38 Z M52 38 L52 80 L74 80 L74 38 Z M74 38 L74 80 L86 72 L86 30 Z"/>',
        'pyramid': '<path class="shp" d="M60 12 L28 70 L64 80 Z"/><path class="shp" d="M60 12 L64 80 L94 66 Z"/>',
        'frustum': '<path class="shp" d="M44 26 L76 26 L94 74 L26 74 Z"/><ellipse class="shp" cx="60" cy="26" rx="16" ry="4"/>',
        'wedge': '<path class="shp" d="M24 72 L84 72 L100 58 L40 58 Z"/><path class="shp" d="M40 58 L60 26 L100 58 Z M24 72 L44 40 L60 26 L40 58 Z"/>',
        'cylinder': '<path class="shp" d="M36 24 L36 72 A24 7 0 0 0 84 72 L84 24"/><ellipse class="shp" cx="60" cy="24" rx="24" ry="7"/>',
        'tube': '<path class="shp" d="M32 24 L32 72 A28 8 0 0 0 88 72 L88 24"/><ellipse class="shp" cx="60" cy="24" rx="28" ry="8"/><ellipse class="shp2" cx="60" cy="24" rx="15" ry="4"/>',
        'cone': '<path class="shp" d="M60 12 L34 72 A26 8 0 0 0 86 72 Z"/>',
        'sphere': '<circle class="shp" cx="60" cy="46" r="34"/><ellipse class="aux" cx="60" cy="46" rx="34" ry="10"/>',
        'cap': '<path class="shp" d="M26 58 A34 34 0 0 1 94 58 Z"/><ellipse class="shp" cx="60" cy="58" rx="34" ry="8"/>',
        'torus': '<ellipse class="shp" cx="60" cy="46" rx="44" ry="26"/><ellipse class="shp2" cx="60" cy="44" rx="20" ry="9"/>',
        'barrel': '<path class="shp" d="M40 18 Q24 46 40 76 L80 76 Q96 46 80 18 Z"/><ellipse class="shp" cx="60" cy="18" rx="20" ry="5"/>',
        'ellipsoid': '<ellipse class="shp" cx="60" cy="46" rx="46" ry="26"/><ellipse class="aux" cx="60" cy="46" rx="46" ry="8"/>',
    }
    fam = {'cube': 'box', 'cuboid': 'box', 'prism': 'prism', 'pyramid': 'pyramid', 'frustum-pyramid': 'frustum', 'wedge': 'wedge',
           'prismoid': 'frustum', 'cylinder': 'cylinder', 'tube': 'tube', 'truncated-cylinder': 'cylinder', 'cone': 'cone',
           'frustum-cone': 'frustum', 'sphere': 'sphere', 'spherical-cap': 'cap', 'spherical-zone': 'cap', 'spherical-sector': 'cone',
           'spherical-wedge': 'sphere', 'hollow-sphere': 'sphere', 'ellipsoid': 'ellipsoid', 'torus': 'torus', 'square-ring': 'torus',
           'barrel': 'barrel'}[s]
    return '<svg viewBox="0 0 120 92" aria-hidden="true">%s</svg>' % icons[fam]


# ------------------------------------------------------------------ pages
def home():
    cards = []
    for slug, name, what, wave in ROOMS:
        live = wave == 1
        inner = '<h3>%s %s</h3><p class="small">%s</p>' % (E(name), '' if live else '<span class="tag soon">wave %d</span>' % wave, E(what))
        cards.append('<a class="card" href="%s/">%s</a>' % (slug, inner) if live else '<div class="card room-off">%s</div>' % inner)
    body = f'''
<div class="head">
  <p class="eyebrow">An interactive handbook · wave 1 of 4</p>
  <h1>Reckoning</h1>
  <p class="lede col">Measure, shape, number, sky, weather, signal, ship and code: the reference tables a navigator, engineer or student
  reaches for, made into instruments you can use. Every value is traced to a current primary standard, and every formula is checked
  by computer each time the site is built.</p>
</div>
<section class="block"><h2>Rooms</h2><div class="grid">{''.join(cards)}</div></section>
<section class="block"><h2>Start here</h2>{converter(pair=('nmi', 'km'), title='Convert anything')}
<p class="small col">Results are exact when both units are defined exactly and the decimal ends. Otherwise they are rounded to
15 significant figures and marked with an ellipsis.</p></section>'''
    return page('index.html', 'Reckoning', 'An interactive handbook of measure, shape and signal: exact unit definitions, a sourced converter and 42 checked shape formulas.',
                body, scripts=conv_scripts(''))


def unit_rows(kind):
    rows = []
    us = [u for u in UNITS if u['kind'] == kind]
    order = {s: i for i, s in enumerate(SYSTEM_ORDER)}
    us.sort(key=lambda u: (order.get(u['system'], 99), u['f'] if kind != 'temperature' else 0))
    cur = None
    si = KINDS[kind]['si']
    for u in us:
        if u['system'] != cur:
            cur = u['system']
            rows.append('<tr class="grp"><td colspan="5">%s</td></tr>' % E(cur))
        if kind == 'temperature':
            val = 'T/K = %s · x + %s' % (fnum(u['f']), fnum(TEMP_OFFSET[u['id']]))
        else:
            val = fnum(u['f']) + ' ' + si
        tags = ('<span class="tag exact">exact</span>' if u['exact'] else '<span class="tag approx">approx.</span>')
        if u['status'] != 'current':
            tags += ' <span class="tag old">%s</span>' % u['status']
        note = ('<br><span class="small">%s</span>' % E(u['note'])) if u['note'] else ''
        rows.append('<tr%s><td><b>%s</b>%s</td><td class="mono">%s</td><td class="num">%s</td><td>%s%s</td><td class="small">%s</td></tr>' % (
            ' class="hist"' if u['status'] != 'current' else '', E(u['name']), (' <span class="mono small">%s</span>' % E(u['sym'])) if u['sym'] else '',
            E(u['by']), val, tags, note, src_link(u['src'], True)))
    return '<div class="tablewrap"><table><thead><tr><th>Unit</th><th>Defined as</th><th>In SI</th><th>Status</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>' % ''.join(rows)


def kind_page(kind):
    k = KINDS[kind]
    t = KIND_PAGES[kind]
    n = len([u for u in UNITS if u['kind'] == kind])
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Measure</a> / {E(k['name'])}</p>
<div class="head"><p class="eyebrow">Measure · {n} units</p><h1>{E(k['name'])}</h1><p class="lede col">{E(t['lede'])}</p></div>
{converter(kind=kind, pair=t['pair'], title='Convert ' + k['name'].lower())}
<div class="then col"><b>Then and now</b><p>{E(t['then'])}</p></div>
<section class="block"><h2>All {k['name'].lower()} units</h2>
<p class="small col">“Exact” means the unit is defined as an exact multiple of the SI unit; the decimal is printed in full when it ends.
Rows marked historical or obsolete are kept for reading old documents.</p>
{unit_rows(kind)}</section>'''
    return page('measure/%s/index.html' % kind, '%s units · Reckoning' % k['name'],
                '%s units with exact definitions, history and sources, and a converter.' % k['name'], body, scripts=conv_scripts('../../'), nav='measure')


def si_page():
    crows = ''.join('<tr><td class="mono"><b>%s</b></td><td>%s</td><td class="num">%s %s</td><td class="mono">%s</td></tr>' % (E(s), E(n), E(v), E(u), E(b)) for s, n, v, u, b in CONSTANTS)
    brows = ''.join('<tr><td class="mono"><b>%s</b></td><td><b>%s</b><br><span class="small">%s</span></td><td>%s</td><td class="small">%s</td></tr>' % (E(s), E(n), E(q), E(how), E(was)) for s, n, q, how, was in BASE)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Measure</a> / The SI</p>
<div class="head"><p class="eyebrow">Measure · since 20 May 2019</p><h1>The SI: seven constants</h1>
<p class="lede col">The International System of Units is built on seven constants of nature whose values are fixed by definition.
Every unit, from the metre to the volt, follows from them. No unit depends on a physical object any more.</p></div>
<section class="block"><h2>The defining constants</h2><p class="small col">Exact by definition: these numbers will never be revised.</p>
<div class="tablewrap"><table><thead><tr><th>Symbol</th><th>Constant</th><th>Exact value</th><th>Fixes</th></tr></thead><tbody>{crows}</tbody></table></div>
<p class="small">Source: {src_link('si')}.</p></section>
<section class="block"><h2>The seven base units</h2>
<div class="tablewrap"><table><thead><tr><th>Symbol</th><th>Unit</th><th>How it is fixed now</th><th>Then</th></tr></thead><tbody>{brows}</tbody></table></div></section>
<div class="lens col"><b>Why constants instead of objects</b><p>An object can be damaged, lost or slowly change: the old kilogram cylinder and its copies drifted apart by tens of micrograms.
A constant of nature is the same in every laboratory, so anyone with the right apparatus can realise the unit without travelling to Paris.</p></div>'''
    return page('measure/si/index.html', 'The SI and its seven constants · Reckoning', 'The seven defining constants of the SI, the base units they fix, and what each replaced.', body, nav='measure')


def derived_page():
    rows = ''.join('<tr><td class="mono"><b>%s</b></td><td>%s</td><td>%s</td><td class="mono">%s</td><td class="mono">%s</td></tr>' % (E(s), E(n), E(q), E(o) or '—', E(b)) for s, n, q, o, b in DERIVED)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Measure</a> / Derived units</p>
<div class="head"><p class="eyebrow">Measure · 22 special names</p><h1>Derived units</h1>
<p class="lede col">Every other SI unit is a product of powers of the seven base units. Twenty-two of them have their own names,
from the radian to the katal; the rest are written out, like metre per second.</p></div>
<div class="tablewrap"><table><thead><tr><th>Symbol</th><th>Name</th><th>Quantity</th><th>In other SI units</th><th>In base units</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Source: {src_link('si')}, Table 4.</p>
<div class="lens col"><b>Same unit, different quantity</b><p>The gray and the sievert are both J/kg, and the hertz and the becquerel are both s⁻¹.
The special names exist precisely so that a dose or a radioactivity is never confused with something else of the same dimension.</p></div>'''
    return page('measure/derived/index.html', 'Derived SI units · Reckoning', 'The 22 SI derived units with special names, in other SI units and in base units.', body, nav='measure')


def prefix_page():
    rows = ''.join('<tr><td class="mono"><b>%s</b></td><td>%s</td><td class="num">10<sup>%d</sup></td><td class="num">%s</td><td class="num">%d%s</td></tr>' % (
        E(sym), E(name), e, fnum(F(10) ** e), y, ' <span class="tag exact">new</span>' if y == 2022 else '') for e, name, sym, y in PREFIXES)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Measure</a> / Prefixes</p>
<div class="head"><p class="eyebrow">Measure · 24 prefixes</p><h1>Prefixes</h1>
<p class="lede col">A prefix multiplies a unit by a power of ten. Above a thousand they step by a thousand; the four newest,
ronna, quetta, ronto and quecto, were added in 2022, mainly because data storage and the mass of planets needed them.</p></div>
<div class="tablewrap"><table><thead><tr><th>Symbol</th><th>Prefix</th><th>Factor</th><th>Written out</th><th>Adopted</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Sources: {src_link('si')}; {src_link('cgpm2022')}.</p>
<div class="then col"><b>Then and now</b><p>Tables printed before 1991 stop at exa and atto, and those before 2022 at yotta and yocto.
Never combine prefixes: write nanometre, not millimicrometre. For mass, prefixes attach to the gram: milligram, not microkilogram.</p></div>'''
    return page('measure/prefixes/index.html', 'SI prefixes · Reckoning', 'All 24 SI prefixes from quecto to quetta, with the year each was adopted.', body, nav='measure')


def fractions_page():
    rows = []
    for k in range(1, 64):
        f = F(k, 64)
        name = '%d/%d' % (f.numerator, f.denominator)
        rows.append('<tr><td class="mono">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (name, fnum(f), fnum(f * F(254, 10))))
    foot = []
    for i in range(12):
        for j, fr in enumerate((F(0), F(1, 4), F(1, 2), F(3, 4))):
            inches = i + fr
            if inches == 0:
                continue
            foot.append('<tr><td class="mono">%s in</td><td class="num">%s ft</td></tr>' % (('%d' % i if i else '') + ((' ' if i else '') + '%d/%d' % (fr.numerator, fr.denominator) if fr else ''), fnum(inches / 12, 6)))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Measure</a> / Fractions and decimals</p>
<div class="head"><p class="eyebrow">Measure · exact</p><h1>Fractions of an inch</h1>
<p class="lede col">Rulers divide the inch by halves down to sixty-fourths; drawings and machines use decimals and millimetres.
Every 64th of an inch is a decimal that ends, and since the inch is exactly 25.4 mm, so is its value in millimetres.</p></div>
<div class="plate"><p class="label">Ruler</p>
<div class="ruler"><svg id="ruler" viewBox="0 0 660 120" role="img" aria-label="One inch divided into 64ths"></svg></div>
<label class="row">Sixty-fourths <input id="r64" type="range" min="1" max="64" value="24"></label>
<p class="out" id="rout" aria-live="polite"></p></div>
<section class="block"><h2>All 64ths</h2><div class="tablewrap"><table><thead><tr><th>Fraction</th><th>Inch</th><th>Millimetre</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section class="block"><h2>Inches as decimals of a foot</h2><p class="small col">Surveyors and builders often work in decimal feet. Twelfths do not end as decimals, so these are rounded.</p>
<div class="tablewrap"><table><thead><tr><th>Inches</th><th>Foot</th></tr></thead><tbody>{''.join(foot)}</tbody></table></div></section>'''
    script = r'''<script>
(function(){var s=document.getElementById('ruler'),r=document.getElementById('r64'),o=document.getElementById('rout');
function g(a,b){while(b){var t=a%b;a=b;b=t}return a}
function dec(n){var x=n/64;return x.toFixed(6).replace(/0+$/,'').replace(/\.$/,'')}
function mm(n){var x=n*25.4/64;return x.toFixed(7).replace(/0+$/,'').replace(/\.$/,'')}
function draw(){var n=+r.value,h='',X=30,W=600;for(var i=0;i<=64;i++){var L=i%64==0?70:i%32==0?60:i%16==0?50:i%8==0?40:i%4==0?30:i%2==0?22:14;
h+='<line x1="'+(X+W*i/64)+'" x2="'+(X+W*i/64)+'" y1="10" y2="'+(10+L)+'"'+(i==n?' class="sel"':'')+'/>'}
h+='<line x1="'+X+'" x2="'+(X+W)+'" y1="10" y2="10"/><text x="'+(X-4)+'" y="100">0</text><text x="'+(X+W-6)+'" y="100">1 in</text>';
s.innerHTML=h;var k=g(n,64);o.textContent=(n/k)+'/'+(64/k)+' in = '+dec(n)+' in = '+mm(n)+' mm (exact)'}
r.addEventListener('input',draw);draw()})();
</script>
'''
    return page('measure/fractions/index.html', 'Fractions of an inch · Reckoning', 'Every 64th of an inch as an exact decimal inch and millimetre, with a live ruler.', body, scripts=script, nav='measure')


def measure_hub():
    topics = [('si', 'The SI', 'Seven constants fix every unit.'), ('derived', 'Derived units', 'The 22 units with special names.'),
              ('prefixes', 'Prefixes', 'Quecto to quetta, 24 of them.')]
    topics += [(k, KINDS[k]['name'], '%d units, exact definitions.' % len([u for u in UNITS if u['kind'] == k])) for k in KINDS]
    topics += [('fractions', 'Fractions of an inch', '64ths as exact decimals and millimetres.')]
    cards = ''.join('<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in topics)
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Measure</p>
<div class="head"><p class="eyebrow">Room · {len(UNITS)} units</p><h1>Measure</h1>
<p class="lede col">What a unit is, how it is defined today, how it was defined before, and how to convert it exactly.</p></div>
{converter(pair=('ft', 'm'), title='Converter')}
<section class="block"><h2>Topics</h2><div class="grid">{cards}</div></section>'''
    return page('measure/index.html', 'Measure · Reckoning', 'Units of measurement: the SI, derived units, prefixes, and exact definitions of %d units with a sourced converter.' % len(UNITS),
                body, scripts=conv_scripts('../'), nav='measure')


def shape_hub():
    groups = []
    seen = []
    for sh in SHAPES:
        if (sh['dim'], sh['group']) not in seen:
            seen.append((sh['dim'], sh['group']))
    secs = []
    for dim, grp in seen:
        cards = ''.join('<a class="card" href="%s/"><div class="fig">%s</div><h3>%s</h3><p class="small">%s</p></a>' % (
            s['slug'], thumb(s), E(s['name']), E(s['what'])) for s in SHAPES if s['dim'] == dim and s['group'] == grp)
        secs.append('<section class="block"><p class="eyebrow">%s</p><h2>%s</h2><div class="grid">%s</div></section>' % ('Plane figures' if dim == 2 else 'Solids', E(grp), cards))
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Shape</p>
<div class="head"><p class="eyebrow">Room · {len(SHAPES)} figures and solids</p><h1>Shape</h1>
<p class="lede col">Areas, perimeters, volumes and surfaces. Change the dimensions and watch the figure and the numbers follow.
Every formula is checked at build time against an independent measurement of the shape.</p>
<p class="col"><a href="topology/">The topology lens</a>: which of these shapes are “the same” if you may stretch but not tear.</p></div>
{''.join(secs)}'''
    return page('shape/index.html', 'Shape · Reckoning', 'Areas and volumes of %d plane figures and solids, live and checked, with a topology lens.' % len(SHAPES), body, nav='shape')


def topo_text(sh):
    t = sh['topo']
    if sh['dim'] == 2:
        if t['holes']:
            return 'A region with one hole. Its Euler characteristic is 0: it can be stretched into any other ring, but never into a disc without tearing.'
        return 'Topologically a disc, like every figure here without a hole: Euler characteristic 1. Stretching turns it into a circle, a square or a star.'
    if t['class'] == 'solid torus':
        return 'A solid with one hole through it, like a ring or a pipe. Its surface is a torus: Euler characteristic 0, genus 1. No stretching makes it a ball.'
    if t['class'] == 'shell':
        return 'A solid with a sealed cavity. Its boundary is two separate spheres, so the Euler characteristic of the surface is 2 + 2 = 4.'
    if 'V' in t and isinstance(t['V'], int):
        return 'Topologically a ball. Its surface has V = %d vertices, E = %d edges and F = %d faces, and V − E + F = %d, as for every convex polyhedron (Euler, 1758).' % (t['V'], t['E'], t['F'], t['V'] - t['E'] + t['F'])
    if 'V' in t:
        return 'Topologically a ball. With n sides to the base: V = %s, E = %s, F = %s, so V − E + F = 2 for every n.' % (t['V'], t['E'], t['F'])
    return 'Topologically a ball: its surface can be stretched onto a sphere without tearing, so its Euler characteristic is 2.'


def shape_page(sh):
    up = '../../'
    data = {'slug': sh['slug'], 'dim': sh['dim'], 'params': sh['params'], 'let': sh['let'],
            'q': [{k: q[k] for k in ('sym', 'name', 'expr', 'kind', 'approx')} for q in sh['q']], 'valid': VALID.get(sh['slug'])}
    sliders = ''.join('<label>%s<input type="range" id="p-%s" data-k="%s" min="%s" max="%s" step="%s" value="%s"><output>%s</output></label>' % (
        E(p['label']), p['key'], p['key'], p['min'], p['max'], p['step'], p['default'], p['default']) for p in sh['params'])
    qty = ''.join('<div><span>%s <span class="mono">%s</span></span><span data-i="%d"></span></div>' % (E(q['name']), E(q['sym']), i) for i, q in enumerate(sh['q']))
    formulas = ''.join('<div class="formula"><span class="tex" data-tex="%s"></span>%s</div>' % (E(q['tex']), ' <span class="tag approx">approximation</span>' if q['approx'] else '') for q in sh['q'])
    fig = ('<div class="figure"><svg id="fig2d" viewBox="0 0 400 300" role="img" aria-label="%s drawn to scale"></svg></div>' % E(sh['name'])
           if sh['dim'] == 2 else
           '<div class="figure" id="fig3d"><p class="hint">Drag to turn · pinch or scroll to zoom</p></div>')
    then = ('<div class="then col"><b>Then and now</b><p>%s</p></div>' % E(sh['then'])) if sh.get('then') else ''
    checked = ', '.join(q['sym'] for q in sh['q'] if q['kind'] in ('area', 'vol'))
    aka = (' <span class="small">(%s)</span>' % E(sh['aka'])) if sh.get('aka') else ''
    body = f'''
<p class="crumbs"><a href="{up}index.html">Reckoning</a> / <a href="../">Shape</a> / {E(sh['name'])}</p>
<div class="head"><p class="eyebrow">{'Plane figure' if sh['dim'] == 2 else 'Solid'} · {E(sh['group'])}</p><h1>{E(sh['name'])}</h1>
<p class="lede col">{E(sh['what'])}{aka}</p></div>
<div class="shape">
  <div class="stack">{fig}
    <div class="row"><button class="ghost" id="reset" type="button">Reset</button>{'<button class="ghost" id="refit" type="button">Re-centre</button>' if sh['dim'] == 3 else ''}
    <label class="unitsel">Units <select id="lenunit"><option value="">none</option><option>m</option><option>cm</option><option>mm</option><option>in</option><option>ft</option></select></label></div>
  </div>
  <div class="stack">
    <div class="plate"><p class="label">Dimensions</p><div class="sliders">{sliders}</div></div>
    <div class="plate"><p class="label">Results</p><p class="warn" id="warn" hidden></p><div class="qty" id="qty">{qty}</div></div>
  </div>
</div>
<section class="block"><h2>Formulas</h2>{formulas}
<p class="col">{E(sh['why'])}</p>{then}
<p class="small">Checked: the {checked} formula agrees with a Monte Carlo measurement of the shape itself, made from its geometric definition, every time the site is built.</p></section>
<div class="lens col"><b>Topology lens</b><p>{topo_text(sh)} <a href="../topology/">More on the lens</a>.</p></div>'''
    scripts = '<script>window.RK_SHAPE = %s;</script>\n' % json.dumps(data, ensure_ascii=False)
    scripts += '<script>document.addEventListener("DOMContentLoaded",function(){if(!window.katex)return;document.querySelectorAll(".tex").forEach(function(el){try{katex.render(el.getAttribute("data-tex"),el,{displayMode:true,throwOnError:false})}catch(e){el.textContent=el.getAttribute("data-tex")}})});</script>\n'
    if sh['dim'] == 3:
        scripts = THREE + '<script src="%sassets/solid.js"></script>\n' % up + scripts
    scripts += '<script src="%sassets/shape.js"></script>\n' % up
    return page('shape/%s/index.html' % sh['slug'], '%s · Reckoning' % sh['name'], '%s: %s Live figure, checked formulas, topology.' % (sh['name'], sh['what']),
                body, extra_head=KATEX, scripts=scripts, nav='shape')


def topology_page():
    rows = []
    for sh in SHAPES:
        t = sh['topo']
        chi = t['chi'] if sh['dim'] == 3 else t['chi']
        rows.append('<tr><td><a href="../%s/">%s</a></td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
            sh['slug'], E(sh['name']), 'plane' if sh['dim'] == 2 else 'solid', E(t['class']), t['holes'], chi))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Shape</a> / Topology lens</p>
<div class="head"><p class="eyebrow">Shape · the lens</p><h1>Stretch, don’t tear</h1>
<p class="lede col">Geometry measures; topology asks what survives when measuring is forbidden. If a shape may be bent and stretched
but not torn or glued, a cube becomes a sphere and a pipe becomes a doughnut, but the doughnut can never become the ball: the hole
cannot be removed without tearing.</p></div>
<section class="block"><h2>The Euler characteristic</h2>
<p class="col">Draw any network of vertices, edges and faces on a surface and count: V − E + F. For any surface that can be stretched
onto a sphere the answer is always 2; for a torus it is always 0, however the network is drawn. Euler noticed the rule for polyhedra
in 1758, and it became one of the first invariants of topology: a number that stretching cannot change.</p>
<div class="lens col"><b>Checked when the site is built</b><p>A cube (8 − 12 + 6), a pyramid (5 − 8 + 5) and a wedge (6 − 9 + 5) all give 2. Triangulated meshes
of a sphere and a torus generated by the build script give 2 and 0. A hollow sphere has two separate boundary spheres: 2 + 2 = 4.</p></div></section>
<section class="block"><h2>Every shape on this site</h2>
<p class="small col">Plane figures: the characteristic of the region (disc 1, ring 0). Solids: the characteristic of the boundary surface.</p>
<div class="tablewrap"><table><thead><tr><th>Shape</th><th>Kind</th><th>Topological class</th><th>Holes</th><th>Euler χ</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>'''
    return page('shape/topology/index.html', 'The topology lens · Reckoning', 'Which shapes are the same when you may stretch but not tear: holes and the Euler characteristic.', body, nav='shape')


def about_page(report):
    srcs = ''.join('<li>%s, %s.</li>' % (src_link(k), E(v['by'])) for k, v in SOURCES.items())
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / About</p>
<div class="head"><p class="eyebrow">Method</p><h1>How it is checked</h1>
<p class="lede col">A handbook is only useful if it is right. These are the rules this one follows, and the checks that ran when this copy was built.</p></div>
<section class="block"><h2>Rules</h2><ul class="col">
<li>Every unit is stored once, as an exact fraction of its SI unit wherever the unit is defined exactly, with the source of that definition.</li>
<li>Values are compared with reference values typed in separately from the NIST tables; the build stops on any mismatch.</li>
<li>Every area and volume formula is compared with a Monte Carlo measurement of the shape, made from a point-in-shape test written from
the shape’s definition, not from its formula. Selected perimeters and surfaces are integrated numerically.</li>
<li>The formula shown on a page is the same expression that was checked; the page evaluates it live.</li>
<li>Old values are not deleted. They are shown as “then and now”, so old documents can still be read.</li>
<li>All text is new. The topics follow mid-century practical handbooks; no text or drawings are taken from them.</li>
</ul></section>
<section class="block"><h2>This build</h2><div class="prov"><pre style="white-space:pre-wrap;margin:0">{E(report)}</pre></div></section>
<section class="block"><h2>Review</h2><p class="col">Pages are reviewed through the lenses of the studio charter: mathematics (formulas, topology), physics and metrology
(units and constants), history (then-and-now notes), teaching (one clear point per page) and design (honest scales, accessibility).
These reviews are done by the author applying those lenses. An outside review by working practitioners has not happened yet; if you
find an error, it will be corrected and the correction noted.</p></section>
<section class="block"><h2>Sources</h2><ul class="col">{srcs}</ul></section>'''
    return page('about/index.html', 'How Reckoning is checked', 'The rules and automatic checks behind every value and formula in Reckoning, and its primary sources.', body, nav='about')


def run_checks():
    out = []
    for t in ('tests/check_units.py', 'tests/check_shapes.py'):
        r = subprocess.run([sys.executable, os.path.join(ROOT, t)], capture_output=True, text=True)
        out.append(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
        if r.returncode:
            print(r.stdout[-3000:], r.stderr[-3000:])
            sys.exit('checks failed: %s' % t)
    return out


def main():
    skip = '--skip-checks' in sys.argv
    lines = ['checks skipped'] if skip else run_checks()
    nshape = len(SHAPES)
    report = ('units: %d, of which %d exact\n' % (len(UNITS), sum(u['exact'] for u in UNITS)) +
              'shapes: %d (%d plane, %d solid); every area/volume formula checked\n' % (nshape, sum(s['dim'] == 2 for s in SHAPES), sum(s['dim'] == 3 for s in SHAPES)) +
              '\n'.join(lines))
    paths = [home(), measure_hub(), si_page(), derived_page(), prefix_page(), fractions_page()]
    paths += [kind_page(k) for k in KINDS]
    paths += [shape_hub(), topology_page()] + [shape_page(s) for s in SHAPES]
    paths.append(about_page(report))
    urls = ''.join('<url><loc>%s%s</loc></url>' % (SITE, p[:-len('index.html')] if p.endswith('index.html') else p) for p in paths)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s</urlset>\n' % urls)
    open(os.path.join(ROOT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % SITE)
    open(os.path.join(ROOT, '.nojekyll'), 'w').write('')
    print(report)
    print('wrote %d pages' % len(paths))


if __name__ == '__main__':
    main()
