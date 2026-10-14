"""Wave 3 rooms: Number and Sky & sea. Page builders called from build.py."""
import html
import json
import os
import subprocess
import unicodedata as ud

from number import SYMBOLS, CONSTANT_LETTERS, GREEK, LOOKALIKES, POINTS
from sky import PLANETS, FACTS, ASPECTS, CONSTELLATIONS, SIGNS, PORTS, ROUTES, zone_letter

E = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))
KATEX = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">\n'
         '<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>\n')
TEX_RUN = ('<script>document.addEventListener("DOMContentLoaded",function(){if(!window.katex)return;document.querySelectorAll(".tex").forEach('
           'function(el){try{katex.render(el.getAttribute("data-tex"),el,{displayMode:true,throwOnError:false})}catch(e){el.textContent=el.getAttribute("data-tex")}})});</script>\n')
THREE = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>\n'
         '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>\n')


def tex(t):
    return '<div class="formula"><span class="tex" data-tex="%s"></span></div>' % E(t)


def cp(ch):
    return 'U+%04X' % ord(ch)


def land_rings():
    """Natural Earth 110 m land as rings of [lon, lat], rounded to 0.01°, for the globe and the maps."""
    d = json.load(open(os.path.join(ROOT, 'data', 'land-110m.json')))
    sx, sy = d['transform']['scale']
    tx, ty = d['transform']['translate']
    arcs = []
    for a in d['arcs']:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((round(x * sx + tx, 2), round(y * sy + ty, 2)))
        arcs.append(pts)
    rings = []
    for geom in d['objects']['land']['geometries']:
        polys = geom['arcs'] if geom['type'] == 'MultiPolygon' else [geom['arcs']]
        for poly in polys:
            for r in poly:
                pts = []
                for i in r:
                    seg = arcs[i] if i >= 0 else arcs[~i][::-1]
                    pts += seg if not pts else seg[1:]
                rings.append([list(p) for p in pts])
    return rings


def write_land():
    path = os.path.join(ROOT, 'assets', 'land.json')
    with open(path, 'w') as f:
        json.dump(land_rings(), f, separators=(',', ':'))


def js_exact():
    """The exact trigonometric values, read from assets/trigmath.js (the code the checks test), not retyped."""
    r = subprocess.run(['node', '-e', 'console.log(JSON.stringify(require(process.argv[1]).EXACT))', os.path.join(ROOT, 'assets', 'trigmath.js')],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def zone_rows():
    rows = ''
    for z in range(-12, 13):
        side = 'W' if z > 0 else 'E' if z < 0 else ''
        mer = '%d°%s' % (abs(z) * 15, side)
        if z == 0:
            strip = '7.5°W – 7.5°E'
        elif abs(z) == 12:
            strip = '172.5°E – 180°' if z < 0 else '180° – 172.5°W'
        else:
            strip = '%.1f°%s – %.1f°%s' % (abs(z) * 15 - 7.5, side, abs(z) * 15 + 7.5, side)
        rows += '<tr><td class="mono"><b>%s</b></td><td class="num">%s</td><td class="num">%s</td><td class="small">%s</td></tr>' % (
            zone_letter(z), ('%+d' % z).replace('-', '−') if z else '0', mer, strip)
    return rows


def hub(page, room, title, lede, cards, desc, eyebrow='Room · wave 3'):
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / {E(title)}</p>
<div class="head"><p class="eyebrow">{eyebrow}</p><h1>{E(title)}</h1>
<p class="lede col">{lede}</p></div>
<section class="block"><div class="grid">{''.join('<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in cards)}</div></section>'''
    return page('%s/index.html' % room, '%s · Reckoning' % title, desc, body, nav=room)


# =====================================================================================  NUMBER
def number_pages(page, src_link):
    out = []
    out.append(hub(page, 'number', 'Number',
                   'The written language of calculation: the symbols and where they came from, the Greek letters and what each one usually stands for, '
                   'angles and the unit circle, and logarithms, the trick that turned multiplication into addition and kept navigators, engineers and '
                   'astronomers calculating for 350 years.',
                   [('symbols', 'Mathematical symbols', 'Sixty signs with their meaning, their Unicode name and, where known, their first printed use.'),
                    ('greek', 'Greek alphabet', 'All 24 letters, what each usually means in science, the look-alikes, and a drill.'),
                    ('trig', 'Trigonometry', 'The unit circle you can turn, exact values, angle units, and a triangle solver that handles the ambiguous case.'),
                    ('logarithms', 'Logarithms and the slide rule', 'Characteristic and mantissa, and a working slide rule with C, D, A, B, CI, K and L scales.')],
                   'Mathematical symbols, the Greek alphabet, trigonometry and logarithms with a working slide rule.'))

    # ------------------------------------------------------------------ symbols
    groups = ''
    for g, items in SYMBOLS:
        rows = ''.join('<tr data-q="%s"><td class="sym">%s</td><td>%s</td><td class="mono small">%s</td><td class="mono small">%s<br>%s</td><td class="small">%s</td></tr>' % (
            E((ch + ' ' + name + ' ' + mean + ' ' + first).lower()), E(ch), E(mean), E(ex), cp(ch), E(name.lower()), E(first)) for ch, name, mean, ex, first in items)
        groups += '<tr class="grp"><td colspan="5">%s</td></tr>%s' % (E(g), rows)
    consts = ''.join('<tr><td class="sym"><i>%s</i></td><td class="mono">%s</td><td>%s</td><td class="small">%s</td></tr>' % (E(l), E(v), E(m), E(f)) for l, v, m, f in CONSTANT_LETTERS)
    nsym = sum(len(i) for g, i in SYMBOLS)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Number</a> / Symbols</p>
<div class="head"><p class="eyebrow">Number · {nsym} signs</p><h1>Mathematical symbols</h1>
<p class="lede col">Most of these signs are younger than printing. Each was proposed by one writer, competed with rivals for decades, and won
because it was easy to set in type and hard to misread. The table gives each sign’s meaning, an example, its exact Unicode character, and
its first known use where the history is well documented.</p></div>
<div class="plate"><p class="label">Find a sign</p><div class="row"><input id="sq" type="search" placeholder="e.g. equal, angle, union" aria-label="Filter symbols" style="flex:1;min-width:200px"></div></div>
<section class="block"><div class="tablewrap"><table id="symtab"><thead><tr><th>Sign</th><th>Meaning</th><th>Example</th><th>Unicode</th><th>First use</th></tr></thead><tbody>{groups}</tbody></table></div>
<p class="small col">Unicode names are checked against the Unicode Character Database when the site is built. First uses: {src_link('cajori')}; a blank means
the origin is uncertain or was not checked. Sign list for scientific writing: {src_link('iaustyle')}, 5.223; current standard: {src_link('iso80000')}.</p></section>
<section class="block"><h2>Constants written as letters</h2><div class="tablewrap"><table><thead><tr><th>Letter</th><th>Value</th><th>Meaning</th><th>First use</th></tr></thead><tbody>{consts}</tbody></table></div>
<p class="small col">Variables are set in italic type; these fixed constants are printed upright in the ISO convention (π, e, i), as are units and functions such as sin and log.</p></section>
<div class="then col"><b>Then and now</b><p>Until the 1500s most algebra was written out in words: “the thing” for the unknown, “is equal to” spelled in full.
The equals sign appeared in 1557 because, as Recorde wrote, no two things can be more equal than a pair of parallel lines. Some signs lost their
contest: Harriot’s 1631 “&lt;” for “less than” beat Hérigone’s use of the same mark for an angle three years later, and the angle sign was reshaped.
The IAU style manual of 1989 still allows × only between numbers, not in symbolic formulae, where a dot is preferred.</p></div>'''
    script = '''<script>
(function(){var q=document.getElementById('sq'),rows=document.querySelectorAll('#symtab tbody tr');
q.addEventListener('input',function(){var t=q.value.trim().toLowerCase();rows.forEach(function(r){if(r.classList.contains('grp')){r.hidden=!!t;return;}r.hidden=t&&r.getAttribute('data-q').indexOf(t)<0;});});})();
</script>
'''
    out.append(page('number/symbols/index.html', 'Mathematical symbols · Reckoning', 'Mathematical signs with meaning, Unicode character and first printed use.', body, scripts=script, nav='number'))

    # ------------------------------------------------------------------ greek
    cards = ''.join('<div class="gk" id="gk-%s"><div class="gl"><span>%s</span><span>%s</span>%s</div><div><h3>%s</h3><p class="small">%s</p></div></div>' % (
        n, E(c), E(s), ('<span class="gv" title="variant forms">%s</span>' % E(' '.join(v))) if v else '', n, E(u)) for n, c, s, v, u in GREEK)
    looks = ''.join('<tr><td class="sym">%s</td><td class="mono small">%s %s</td><td class="sym">%s</td><td class="mono small">%s %s</td><td class="small">%s</td></tr>' % (
        E(ch), cp(ch), E(nm.lower()), E(pr), cp(pr), E(ud.name(pr).lower()), E(note)) for ch, nm, pr, kind, note in LOOKALIKES)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Number</a> / Greek alphabet</p>
<div class="head"><p class="eyebrow">Number · 24 letters</p><h1>Greek alphabet</h1>
<p class="lede col">Science ran out of Latin letters long ago. The Greek alphabet supplies the second set, and many letters have settled
meanings: λ is a wavelength, ρ a density, Ω the ohm. In astronomy α, δ give a star’s place on the sky and λ, β its place along the ecliptic.</p></div>
<div class="plate"><p class="label">Name that letter</p>
<div class="drill"><div class="gbig" id="gq" aria-live="polite">α</div><div class="row" id="gopts"></div></div>
<p class="out" id="gres" aria-live="polite"></p><p class="small" id="gscore"></p></div>
<section class="block"><h2>The letters</h2><div class="gkgrid">{cards}</div>
<p class="small col">Character names: {src_link('unicode')}. Unicode spells λ “lamda”, a spelling also used in modern Greek.</p></section>
<section class="block"><h2>Look-alikes</h2><p class="col">Some symbols have their own Unicode characters that look exactly like Greek letters. Text that mixes
them searches and sorts badly, so the standard asks for the plain letter.</p>
<div class="tablewrap"><table><thead><tr><th></th><th>Character</th><th></th><th>Use instead</th><th>Note</th></tr></thead><tbody>{looks}</tbody></table></div></section>
<div class="lens col"><b>How letters are set</b><p>A letter that stands for a quantity is italic: <i>λ</i> = 500 nm. A unit or prefix symbol is upright:
μm, Ω. Writing <i>μ</i>m in italics turns the prefix into a quantity, so the rule matters. Sources: {src_link('si', True)}, {src_link('iso80000', True)}.</p></div>'''
    gdata = json.dumps([[n, s, c] for n, c, s, v, u in GREEK], ensure_ascii=False)
    script = '''<script>
(function(){var G=%s,q=document.getElementById('gq'),o=document.getElementById('gopts'),res=document.getElementById('gres'),sc=document.getElementById('gscore'),right=0,tries=0,cur;
function pick(n){return Math.floor(Math.random()*n)}
function next(){cur=pick(24);var cap=Math.random()<0.35,opts=[cur];while(opts.length<4){var k=pick(24);if(opts.indexOf(k)<0)opts.push(k)}
opts.sort(function(){return Math.random()-0.5});q.textContent=G[cur][cap?2:1];o.innerHTML='';
opts.forEach(function(k){var b=document.createElement('button');b.type='button';b.className='ghost';b.textContent=G[k][0];
b.addEventListener('click',function(){tries++;if(k===cur){right++;res.className='out good';res.textContent='Yes: '+G[cur][2]+' '+G[cur][1]+' is '+G[cur][0]+'.'}
else{res.className='out bad';res.textContent='No: that is '+G[cur][0]+'; '+G[k][1]+' is '+G[k][0]+'.'}sc.textContent=right+' of '+tries+' right';setTimeout(next,900)});o.appendChild(b)})}
next()})();
</script>
''' % gdata
    out.append(page('number/greek/index.html', 'Greek alphabet · Reckoning', 'The 24 Greek letters, their usual meanings in science, Unicode look-alikes and a drill.', body, scripts=script, nav='number'))

    # ------------------------------------------------------------------ trig
    exact_rows = ''.join('<tr><td class="num">%s°</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td></tr>' % (d, *v) for d, v in
                         sorted((int(k), x) for k, x in js_exact().items()) if d <= 90)
    angle_units = [('turn', '1 turn', '360°', '2π rad'), ('degree', '1°', '1/360 turn', 'π/180 rad'), ('minute of arc', '1′', '1/60°', 'π/10 800 rad'),
                   ('second of arc', '1″', '1/60′', 'π/648 000 rad'), ('radian (SI)', '1 rad', '180/π ° ≈ 57.295 78°', 'arc length = radius'),
                   ('gon (grade)', '1 gon', '0.9°', 'π/200 rad'), ('point of the compass', '1 point', '11.25°', 'π/16 rad'), ('NATO mil', '1 mil', '360/6400 °', 'π/3200 rad')]
    au = ''.join('<tr><td>%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td></tr>' % (E(a), E(b), E(c), E(d)) for a, b, c, d in angle_units)
    pts = ''.join('<span class="pt"><b>%s</b> %s°</span>' % (E(p), ('%.2f' % (i * 11.25)).rstrip('0').rstrip('.')) for i, p in enumerate(POINTS))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Number</a> / Trigonometry</p>
<div class="head"><p class="eyebrow">Number · plane trigonometry</p><h1>Trigonometry</h1>
<p class="lede col">Sine and cosine are coordinates: walk an angle round a circle of radius 1, and the point you reach is (cos θ, sin θ).
Everything else, including the tangent, the laws of sines and cosines and every navigator’s traverse table, follows from that picture.</p></div>
<div class="shape">
<div class="figure" style="aspect-ratio:1/1"><svg id="uc" viewBox="-1.45 -1.45 2.9 2.9" role="img" aria-label="Unit circle"></svg><p class="hint">drag the point</p></div>
<div class="stack"><div class="plate"><p class="label">Angle</p>
<div class="sliders"><label>θ (degrees)<input id="ucd" type="range" min="0" max="360" step="0.25" value="30"><output id="ucdv">30</output></label></div>
<div class="row">{''.join('<button class="ghost" type="button" data-ang="%s">%s°</button>' % (a, a) for a in (0, 30, 45, 60, 90, 120, 135, 180, 225, 270, 300))}</div>
<div class="qty" id="ucq"></div></div>
<p class="small col">Green: sin θ (height). Blue: cos θ (width). Red: tan θ, the length cut off on the tangent line at x = 1. As a navigator’s bearing,
angles run clockwise from north instead; the panel gives both.</p></div></div>
<section class="block"><h2>Exact values</h2><p class="col">At a few angles the values are exact surds, from the half-square (45°) and the half-equilateral triangle (30°, 60°);
15° and 75° follow by the addition formulas, 18°, 36° and 72° from the regular pentagon. Each entry here is checked against the computer’s sine when the site is built.</p>
<div class="tablewrap" style="max-width:640px"><table><thead><tr><th>θ</th><th>sin θ</th><th>cos θ</th><th>tan θ</th></tr></thead><tbody>{exact_rows}</tbody></table></div></section>
<section class="block"><h2>Solve a triangle</h2>
<p class="col">Name the sides a, b, c and the opposite angles A, B, C. Any three facts that include a side fix the triangle, with one exception:
two sides and an angle that is not between them (SSA) can give two different triangles, one, or none. That is the <i>ambiguous case</i>.</p>
<div class="shape"><div class="plate"><p class="label">Given</p>
<div class="row"><select id="tk" aria-label="What is given"><option value="SSS">three sides (SSS)</option><option value="SAS">two sides and the angle between (SAS)</option>
<option value="ASA">two angles and the side between (ASA)</option><option value="AAS">two angles and another side (AAS)</option><option value="SSA" selected>two sides and an angle not between (SSA)</option></select></div>
<div class="row" id="tin"></div><div id="tout" class="qty" aria-live="polite"></div></div>
<div class="figure"><svg id="tsvg" viewBox="0 0 400 300" role="img" aria-label="Solved triangle"></svg></div></div>
{tex(r'\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C} \qquad a^2=b^2+c^2-2bc\cos A')}
<p class="small col">The solver is the same code that the build checks: 2 000 random triangles are recovered from every kind of data, and the number of SSA solutions is compared with a ruler-and-compass construction.</p></section>
<section class="block"><h2>Units of angle</h2><div class="tablewrap" style="max-width:720px"><table><thead><tr><th>Unit</th><th>Symbol</th><th>Size</th><th>In radians</th></tr></thead><tbody>{au}</tbody></table></div>
<p class="col">The 32 points of the mariner’s compass, 11¼° apart:</p><div class="points">{pts}</div></section>
<div class="then col"><b>Then and now</b><p>Navigators worked with printed tables of logarithms of sines, and of the <i>haversine</i>, hav θ = sin²(θ/2), which keeps every
quantity positive and avoids sign errors. The same haversine formula computes the great-circle distances on the <a href="../../sky/sailing/">sailing page</a>.
Courses were once given in points (“west by south”); today they are three-figure bearings, 000° to 359°.</p></div>'''
    scripts = '<script src="../../assets/trigmath.js"></script>\n<script src="../../assets/trig.js"></script>\n' + TEX_RUN
    out.append(page('number/trig/index.html', 'Trigonometry · Reckoning', 'An interactive unit circle, exact values, angle units and a triangle solver with the ambiguous case.',
                    body, extra_head=KATEX, scripts=scripts, nav='number'))

    # ------------------------------------------------------------------ logarithms
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Number</a> / Logarithms</p>
<div class="head"><p class="eyebrow">Number · logarithms</p><h1>Logarithms and the slide rule</h1>
<p class="lede col">The logarithm of a number is the power of 10 that gives it: log 1000 = 3, log 2 ≈ 0.301. Because powers add when numbers
multiply, a table of logarithms turns every multiplication into an addition, and every root into a division. A slide rule does the same
addition with two rulers laid side by side.</p></div>
<div class="plate"><p class="label">Take a logarithm</p>
<div class="row"><input id="lx" type="text" inputmode="decimal" value="0.0345" aria-label="Number" style="width:10em;font-family:var(--mono)">
{''.join('<button class="ghost" type="button" data-lx="%s">%s</button>' % (x, x) for x in ('2', '3456', '0.0345', '1000', '299792458'))}</div>
<div class="qty" id="lq"></div></div>
<section class="block"><h2>Characteristic and mantissa</h2><div class="col stack">
<p>A logarithm splits into two parts. The whole-number <b>characteristic</b> says where the decimal point is; the decimal <b>mantissa</b> depends only
on the digits. So 3.456, 345.6 and 0.003 456 share the mantissa 0.5386, and a printed table needed only the mantissas of numbers from 1 to 10.</p>
<p>For numbers below 1 the tables kept the mantissa positive and wrote a negative characteristic with a bar over it:
log 0.0345 = −1.4622 was written 2̄.5378, meaning −2 + 0.5378.</p></div>
{tex(r'\log(ab)=\log a+\log b \qquad \log\frac{a}{b}=\log a-\log b \qquad \log a^n = n\log a')}</section>
<section class="block"><h2>A working slide rule</h2>
<p class="col">Drag the middle strip (the slide) and the hairline (the cursor), or use the examples. Distances on the C and D scales are proportional to
logarithms, so sliding C along D adds logarithms: to multiply 2 × 3, put the 1 of C over 2 on D and read D under 3 on C.</p>
<div class="rule-wrap"><svg id="sr" viewBox="0 0 1000 310" role="img" aria-label="Slide rule"></svg></div>
<div class="row">{''.join('<button class="ghost" type="button" data-sr="%s">%s</button>' % (k, l) for k, l in (('mul:2:3', '2 × 3'), ('mul:3.7:4.6', '3.7 × 4.6'), ('div:8.4:2.1', '8.4 ÷ 2.1'), ('sq:7', '7²'), ('cube:2.5', '2.5³'), ('rec:4', '1/4'), ('log:3', 'log 3')))}</div>
<p class="prov" id="srout" aria-live="polite"></p>
<div class="tablewrap" style="max-width:720px"><table><thead><tr><th>Scale</th><th>Range</th><th>Position along the rule</th><th>Used for</th></tr></thead><tbody>
<tr><td><b>D</b>, <b>C</b></td><td class="mono">1 – 10</td><td class="mono">log x</td><td>multiplication and division</td></tr>
<tr><td><b>CI</b></td><td class="mono">10 – 1</td><td class="mono">1 − log x</td><td>reciprocals</td></tr>
<tr><td><b>A</b>, <b>B</b></td><td class="mono">1 – 100</td><td class="mono">½ log x</td><td>squares and square roots</td></tr>
<tr><td><b>K</b></td><td class="mono">1 – 1000</td><td class="mono">⅓ log x</td><td>cubes and cube roots</td></tr>
<tr><td><b>L</b></td><td class="mono">0 – 1</td><td class="mono">x</td><td>the mantissa itself: log of the D reading</td></tr></tbody></table></div>
<p class="small col">A slide rule gives three significant figures; you place the decimal point yourself, which is exactly what the characteristic does.</p></section>
<div class="then col"><b>Then and now</b><p>John Napier published logarithms in 1614 and Henry Briggs, with Napier’s agreement, recast them in base 10 within a few years.
William Oughtred described logarithmic scales that move against each other in <i>The Circles of Proportion</i> (1632). For the next 340 years slide rules
and log tables did the arithmetic of ships, bridges, aircraft and the first spacecraft, until pocket electronic calculators replaced them in the 1970s.</p></div>'''
    scripts = '<script src="../../assets/trigmath.js"></script>\n<script src="../../assets/sliderule.js"></script>\n' + TEX_RUN
    out.append(page('number/logarithms/index.html', 'Logarithms and the slide rule · Reckoning', 'Logarithms, characteristic and mantissa, and a working slide rule with seven scales.',
                    body, extra_head=KATEX, scripts=scripts, nav='number'))
    return out


# =====================================================================================  SKY & SEA
def sky_pages(page, src_link):
    out = []
    write_land()
    out.append(hub(page, 'sky', 'Sky & sea',
                   'Where you are and what time it is were once the same question, answered from the sky. This room covers the coordinates of the '
                   'Earth and the heavens, the shortest way across a sphere, the several kinds of time, and the planets and the band of constellations they move through.',
                   [('globe', 'Latitude and longitude', 'A globe you can turn and tap, and why a minute of latitude is about one nautical mile.'),
                    ('sailing', 'Great circle and rhumb line', 'The shortest route against the constant course, drawn on two different map projections.'),
                    ('time', 'Kinds of time', 'Apparent, mean, zone and sidereal time, live, and the equation of time across the year.'),
                    ('celestial', 'The celestial sphere', 'Right ascension and declination, the ecliptic, and why the signs no longer match the constellations.'),
                    ('planets', 'Planets and their names', 'Symbols, gods and discoverers, and an orrery showing where each planet is today.')],
                   'Latitude and longitude, great circles and rhumb lines, the kinds of time, the celestial sphere and the planets.'))

    # ------------------------------------------------------------------ globe
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / Latitude and longitude</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · coordinates</p><h1>Latitude and longitude</h1>
<p class="lede col">Latitude is how far north or south you are, measured as an angle from the equator; longitude is how far east or west,
measured from the meridian through Greenwich. Two angles fix any point on Earth. Turn the globe, and tap anywhere to read its position.</p></div>
<div class="shape"><div class="figure globe" style="aspect-ratio:1/1"><canvas id="globe" aria-label="Globe: drag to turn, tap to read a position"></canvas><p class="hint">drag to turn · tap to read</p></div>
<div class="stack"><div class="plate"><p class="label">Position</p>
<div class="row"><label class="small">Latitude <input id="glat" type="number" step="0.01" min="-90" max="90" value="51.48" style="width:8em"></label>
<label class="small">Longitude <input id="glon" type="number" step="0.01" min="-180" max="180" value="0" style="width:8em"></label></div>
<div class="row">{''.join('<button class="ghost" type="button" data-ll="%s,%s">%s</button>' % (la, lo, E(n)) for n, la, lo in (('Greenwich', 51.4779, -0.0015), ('North Pole', 90, 0), ('Equator, 0°', 0, 0), ('Cape Horn', -55.98, -67.27), ('Honolulu', 21.31, -157.87)))}</div>
<div class="qty" id="gq"></div></div>
<p class="small col">Red: equator. Yellow: tropics and polar circles, at the obliquity of the ecliptic for this year. Blue: prime meridian and the 180th meridian.</p></div></div>
<section class="block"><h2>How long is a minute?</h2>
<p class="col">The Earth is slightly flattened (WGS 84: equatorial radius 6 378 137 m, flattening 1/298.257 223 563), so a minute of latitude is a
little longer near the poles, where the surface is flatter. Averaged over the globe it is close to 1852 m, and that is where the nautical mile
comes from. A minute of longitude shrinks with the cosine of the latitude and vanishes at the poles.</p>
<div class="tablewrap" style="max-width:720px"><table><thead><tr><th>Latitude</th><th>1′ of latitude</th><th>1′ of longitude</th><th>Geocentric latitude</th></tr></thead><tbody id="mtab"></tbody></table></div>
<p class="small col">Computed live from the WGS 84 ellipsoid ({src_link('wgs84', True)}). The build checks the code against the length of the meridian quadrant,
10 001 965.729 m from the equator to the pole. Geocentric latitude is the angle seen from the Earth’s centre; maps and GPS use the geodetic latitude; the two differ by up to 11.5′, at 45°.</p></section>
<div class="lens col"><b>Topology lens</b><p>No flat map can show a sphere without stretching it: Gauss proved in 1827 that distances on a curved surface cannot all be kept on a plane.
Every chart therefore chooses what to keep true. Mercator keeps angles, so a constant course is a straight line; the gnomonic projection keeps great circles straight.
See both on the <a href="../sailing/">sailing page</a>.</p></div>
<div class="then col"><b>Then and now</b><p>The British Admiralty mile was 6080 ft (1853.184 m), close to a minute of latitude in the English Channel. The international
nautical mile was fixed at exactly 1852 m in 1929; see <a href="../../measure/length/">length units</a>. Latitudes today refer to WGS 84; old charts used local datums that can differ by hundreds of metres.</p></div>'''
    scripts = THREE + '<script src="../../assets/navmath.js"></script>\n<script src="../../assets/astro.js"></script>\n<script src="../../assets/globe.js"></script>\n'
    out.append(page('sky/globe/index.html', 'Latitude and longitude · Reckoning', 'A globe you can turn and tap, with lengths of a minute of latitude and longitude on WGS 84.', body, scripts=scripts, nav='sky'))

    # ------------------------------------------------------------------ sailing
    opts = ''.join('<option value="%d">%s</option>' % (i, E(n)) for i, (n, la, lo) in enumerate(PORTS))
    routes = ''.join('<button class="ghost" type="button" data-route="%s|%s">%s → %s</button>' % (E(a), E(b), E(a), E(b)) for a, b in ROUTES)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / Great circle and rhumb line</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · sailings</p><h1>Great circle and rhumb line</h1>
<p class="lede col">There are two natural ways to cross an ocean. A <b>rhumb line</b> keeps the same compass course all the way: easy to steer, but longer.
A <b>great circle</b> is the shortest path on the sphere, but its course changes continuously. Pick two ports and compare them.</p></div>
<div class="plate"><p class="label">Voyage</p>
<div class="row"><select id="sfrom" aria-label="From">{opts}</select><span class="mono">→</span><select id="sto" aria-label="To">{opts}</select></div>
<div class="row">{routes}</div>
<div class="mapgrid"><figure><figcaption class="small">Mercator projection: the rhumb line is straight</figcaption><div class="mapbox"><svg id="mmerc" viewBox="0 0 720 520" role="img" aria-label="Mercator chart of the voyage"></svg></div></figure>
<figure><figcaption class="small">Gnomonic projection, centred on the route: the great circle is straight</figcaption><div class="mapbox"><svg id="mgno" viewBox="0 0 520 520" role="img" aria-label="Gnomonic chart of the voyage"></svg></div></figure></div>
<p class="small"><span class="key gc"></span> great circle &nbsp; <span class="key rl"></span> rhumb line</p>
<div class="tablewrap"><table><tbody id="sout"></tbody></table></div></div>
<section class="block"><h2>The formulas</h2><p class="col">On a sphere of radius R, with latitudes φ, longitudes λ, the great-circle distance is
computed with the haversine; the initial course from the spherical triangle formed with the pole. The rhumb line uses the <i>meridional parts</i>:
the stretched latitude scale of the Mercator chart.</p>
{tex(r'd = 2R\arcsin\sqrt{\sin^2\tfrac{\Delta\varphi}{2}+\cos\varphi_1\cos\varphi_2\sin^2\tfrac{\Delta\lambda}{2}} \qquad \tan C_0=\frac{\sin\Delta\lambda\,\cos\varphi_2}{\cos\varphi_1\sin\varphi_2-\sin\varphi_1\cos\varphi_2\cos\Delta\lambda}')}
{tex(r'\Delta\psi=\ln\frac{\tan(\pi/4+\varphi_2/2)}{\tan(\pi/4+\varphi_1/2)} \qquad \tan C=\frac{\Delta\lambda}{\Delta\psi} \qquad d=\frac{\Delta\varphi}{\cos C}\,R')}
<p class="small col">Distances use the navigator’s sphere, on which a minute of arc is exactly one nautical mile. The true distance on the WGS 84 ellipsoid comes
from {src_link('vincenty')}, the method checked here against its published worked example to the millimetre. The build also computes every great-circle
distance twice, by the haversine and by vectors, and compares the rhumb-line formula with a step-by-step integration along the track.</p></section>
<div class="then col"><b>Then and now</b><p>Without computers, navigators drew the great circle as a straight line on a gnomonic chart, read off points every few
degrees of longitude, transferred them to the Mercator chart and steered rhumb lines between them. The older <i>mid-latitude sailing</i> shortcut is shown
in the table: good over short distances, poor over long ones. Today’s chart plotters do the same calculation on the ellipsoid.</p></div>'''
    pdata = json.dumps([[n, la, lo] for n, la, lo in PORTS], ensure_ascii=False)
    scripts = '<script>window.RK_PORTS = %s;</script>\n<script src="../../assets/navmath.js"></script>\n<script src="../../assets/sailing.js"></script>\n' % pdata + TEX_RUN
    out.append(page('sky/sailing/index.html', 'Great circle and rhumb line · Reckoning', 'Compare great-circle and rhumb-line routes between ports on Mercator and gnomonic charts.',
                    body, extra_head=KATEX, scripts=scripts, nav='sky'))

    # ------------------------------------------------------------------ time
    zrows = zone_rows()
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / Kinds of time</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · time</p><h1>Kinds of time</h1>
<p class="lede col">“Noon” used to mean the moment the Sun crossed your meridian. That moment drifts through the year, differs from town to town,
and is not the moment a star returns to the same place. Each of those facts gave navigators and astronomers a different clock.</p></div>
<div class="plate"><p class="label">Now, at longitude</p>
<div class="row"><input id="tlon" type="number" step="0.1" min="-180" max="180" value="0" aria-label="Longitude, degrees east positive" style="width:8em">
<span class="small">° (east +, west −)</span>{''.join('<button class="ghost" type="button" data-lon="%s">%s</button>' % (lo, E(n)) for n, lo in (('Greenwich', 0), ('New York', -74.0), ('Tokyo', 139.7), ('Sydney', 151.2), ('Honolulu', -157.9)))}</div>
<div class="clocks" id="clocks" aria-live="off"></div>
<p class="small">Device clock: <span id="tdev" class="mono"></span>. Formulas: {src_link('noaasun', True)} (Sun) and {src_link('usnogast', True)} (sidereal time).</p></div>
<section class="block"><h2>The equation of time</h2>
<p class="col">A sundial and a clock agree on only four days a year. The difference, the <b>equation of time</b>, comes from two effects: the Earth moves
faster near perihelion in early January, and the Sun’s path is tilted to the equator, so equal steps along it are not equal steps of right ascension.</p>
<div class="figure eot"><svg id="eot" viewBox="0 0 720 300" role="img" aria-label="Equation of time across the year"></svg></div>
<div class="shape"><div class="figure" style="aspect-ratio:3/4;max-width:340px"><svg id="ana" viewBox="0 0 300 400" role="img" aria-label="Analemma"></svg></div>
<div class="col stack"><p>Plot the Sun’s declination against the equation of time and you get the <b>analemma</b>, the figure eight traced by the Sun if you photograph it at
the same clock time every few days for a year. Its top and bottom are the solstices; its width is the equation of time.</p>
<p class="small">The build checks this code against the published worked examples for 1992 October 13 (equation of time +13 m 42.7 s) and finds this year’s extremes,
about −14.2 min in February and +16.4 min in early November, with four zero crossings.</p></div></div></section>
<section class="block"><h2>Time zones at sea</h2>
<p class="col">Ships keep zone time: the ocean is divided into 15° strips centred on multiples of 15°, each one hour from the next. The zone description is the
number of hours you add to zone time to get UTC, so it is negative east of Greenwich. Each zone also has a letter; J is not used, and Z, for Greenwich, gave “Zulu time”.</p>
<div class="tablewrap" style="max-width:640px"><table><thead><tr><th>Letter</th><th>Zone description</th><th>Central meridian</th><th>Strip</th></tr></thead><tbody>{zrows}</tbody></table></div>
<p class="small col">Zone 12 is split by the date line: the half west of 180° (−12, M) is a day ahead of the half east of it (+12, Y). Land time zones follow borders and politics instead.</p></section>
<section class="block"><h2>Which clock is which</h2><div class="tablewrap"><table><thead><tr><th>Time</th><th>Kept by</th><th>Day length</th></tr></thead><tbody>
<tr><td><b>Apparent solar time</b></td><td>the real Sun; a sundial. Noon is when the Sun crosses your meridian.</td><td>differs from 24 h by up to about half a minute</td></tr>
<tr><td><b>Local mean time</b></td><td>an imaginary Sun moving evenly along the equator. Apparent time = mean time + equation of time.</td><td>24 h exactly</td></tr>
<tr><td><b>Zone time</b></td><td>local mean time of the zone’s central meridian.</td><td>24 h</td></tr>
<tr><td><b>UTC</b></td><td>atomic clocks, kept within 0.9 s of the Earth’s rotation (UT1) by leap seconds.</td><td>86 400 SI seconds (86 401 with a leap second)</td></tr>
<tr><td><b>Sidereal time</b></td><td>the stars: the hour angle of the March equinox. A star rises 3 min 56 s earlier each day by the clock.</td><td>23 h 56 min 4.09 s</td></tr>
</tbody></table></div></section>
<div class="then col"><b>Then and now</b><p>Until 1925 astronomers began the day at noon, so that a night’s observations kept one date. Greenwich Mean Time was the world’s
reference until UTC took over; leap seconds, added since 1972, are to stop by 2035 ({src_link('cgpm2022r4', True)}), when UTC will be allowed to drift further from the Earth’s rotation.</p></div>'''
    scripts = '<script src="../../assets/astro.js"></script>\n<script src="../../assets/navmath.js"></script>\n<script src="../../assets/skytime.js"></script>\n'
    out.append(page('sky/time/index.html', 'Kinds of time · Reckoning', 'Apparent, mean, zone, sidereal time and UTC live, with the equation of time and the analemma.', body, scripts=scripts, nav='sky'))

    # ------------------------------------------------------------------ celestial
    bounds = [[float(l.split()[0]), float(l.split()[1]), float(l.split()[2]), l.split()[3]] for l in open(os.path.join(ROOT, 'data', 'constbounds_1875.dat'))]
    signs = ''.join('<tr><td class="sym">%s︎</td><td>%s</td><td class="num">%d°–%d°</td><td class="mono small" data-sign="%d"></td></tr>' % (s, E(n), i * 30, i * 30 + 30, i) for i, (n, s, un) in enumerate(SIGNS))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / The celestial sphere</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · coordinates of the sky</p><h1>The celestial sphere</h1>
<p class="lede col">Seen from Earth, the stars sit on a vast sphere turning once a day. Extend the Earth’s equator and poles outward and you get the sky’s
coordinates: <b>declination</b> is latitude on the sky, <b>right ascension</b> is longitude, counted east in hours from the point where the Sun crosses the
equator in March. The Sun’s own yearly path, the <b>ecliptic</b>, is tilted 23.4° to that equator.</p></div>
<div class="shape"><div class="figure globe" style="aspect-ratio:1/1"><canvas id="celes" aria-label="Celestial sphere: drag to turn"></canvas><p class="hint">drag to turn</p></div>
<div class="stack"><div class="plate"><p class="label">The Sun on</p>
<div class="sliders"><label>Day of year<input id="cday" type="range" min="0" max="364" value="0"><output id="cdayv"></output></label></div>
<div class="row"><button class="ghost" type="button" id="ctoday">Today</button></div>
<div class="qty" id="cq"></div></div>
<p class="small col">Blue: celestial equator and the hour circles every 2 h. Red: the ecliptic, marked every 30°. Yellow: the Sun. The small globe at the centre is the Earth.</p></div></div>
<section class="block"><h2>Signs and constellations</h2>
<p class="col">Two thousand years ago the ecliptic was divided into twelve equal <b>signs</b> of 30°, each named after the constellation that lay in it.
The equinox, the starting point, slides westward along the ecliptic by about 50.3″ a year, a full circle in about 25 800 years, because the Earth’s axis
wobbles like a top (<b>precession</b>). The signs moved with the equinox; the stars did not. Today the March equinox lies in Pisces, and the Sun spends
most of each sign in the constellation before it. Since 1930 the constellations also have official boundaries, and the ecliptic crosses thirteen of them, including Ophiuchus.</p>
<div class="figure band"><svg id="band" viewBox="0 0 1000 170" role="img" aria-label="The ecliptic: signs against constellations"></svg></div>
<div class="tablewrap"><table><thead><tr><th>Constellation on the ecliptic</th><th>Sun enters (this year)</th><th>Days</th></tr></thead><tbody id="ctab"></tbody></table></div>
<div class="tablewrap" style="max-width:640px"><table><thead><tr><th></th><th>Sign</th><th>Ecliptic longitude</th><th>Sun enters (this year)</th></tr></thead><tbody>{signs}</tbody></table></div>
<p class="small col">Dates computed in your browser for the current year from the Sun’s position ({src_link('noaasun', True)}) and the official boundaries
({src_link('roman1987', True)}, precessed with the routine published with that table). The build checks the boundary lookup against the table’s
own test positions and ten bright stars. Constellation names: {src_link('iauconst', True)}.</p></section>
<div class="then col"><b>Then and now</b><p>Reckoning treats the zodiac as astronomy: the signs are a coordinate system, 30° steps of ecliptic longitude from
the equinox, and that is how they appear in old almanacs and navigation tables. They carry no meaning beyond position.</p></div>'''
    scripts = (THREE + '<script>window.RK_CONST = %s; window.RK_CNAMES = %s; window.RK_SIGNS = %s;</script>\n' % (
        json.dumps(bounds, separators=(',', ':')), json.dumps(CONSTELLATIONS, ensure_ascii=False), json.dumps([[n, s] for n, s, u in SIGNS], ensure_ascii=False)) +
        '<script src="../../assets/astro.js"></script>\n<script src="../../assets/celestial.js"></script>\n')
    out.append(page('sky/celestial/index.html', 'The celestial sphere · Reckoning', 'Right ascension, declination, the ecliptic, precession, and the signs against the 13 ecliptic constellations.',
                    body, scripts=scripts, nav='sky'))

    # ------------------------------------------------------------------ planets
    prow = ''
    for key, name, sym, un, roman, greek, why, abbr in PLANETS:
        f = FACTS.get(key)
        prow += '<tr><td class="sym">%s︎</td><td><b>%s</b><br><span class="mono small">%s</span></td><td>%s<br><span class="small">Greek: %s</span></td><td class="small">%s</td><td class="mono">%s</td><td class="num">%s</td></tr>' % (
            E(sym), E(name), cp(sym), E(roman), E(greek), E(why), E(abbr) or '—', ('%s' % f[3]) if f else '—')
    asp = ''.join('<tr><td class="sym">%s</td><td><b>%s</b></td><td class="small">%s</td></tr>' % (E(s) if s else '', E(n), E(d)) for s, u, n, d in ASPECTS)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Sky &amp; sea</a> / Planets</p>
<div class="head"><p class="eyebrow">Sky &amp; sea · the planets</p><h1>Planets and their names</h1>
<p class="lede col">“Planet” is Greek for wanderer: five bright points that move against the fixed stars. The Romans gave them the names of their gods,
and those names, with the old symbols, came down through astronomy and alchemy to us. Two more planets, found by telescope, were named to fit the pattern.</p></div>
<div class="plate"><p class="label">Orrery</p>
<div class="shape"><div class="figure" style="aspect-ratio:1/1"><svg id="orr" viewBox="-300 -300 600 600" role="img" aria-label="Positions of the planets around the Sun"></svg></div>
<div class="stack"><div class="sliders"><label>Date<input id="odate" type="range" min="-3650" max="3650" value="0"><output id="odatev"></output></label></div>
<div class="row"><button type="button" id="oplay">Play</button><button class="ghost" type="button" id="otoday">Today</button>
<label class="small row" style="gap:6px"><input type="checkbox" id="oscale" style="min-height:auto"> true distances</label></div>
<p class="small">Each dashed line runs from the Earth to a planet: the direction you would look. Press Play to watch a few years go by.</p></div></div>
<div class="tablewrap"><table><thead><tr><th>Planet</th><th>Angle from the Sun</th><th>Where to look</th><th>In front of</th><th>From Earth</th></tr></thead><tbody id="otab"></tbody></table></div>
<p class="small">Seen from above the north pole of the ecliptic; the arrow marks the direction of the March equinox. Distances are drawn on a square-root
scale unless you tick true distances. Positions: {src_link('jplapprox')}, good to about an arcminute between 1800 and 2050. The build checks
this code against a published worked example for Venus (1992 December 20) and against an independent formula for the Sun.</p></div>
<section class="block"><h2>Names, gods and symbols</h2><div class="tablewrap"><table><thead><tr><th></th><th>Name</th><th>Roman figure</th><th>Why the name</th><th>IAU abbr.</th><th>Moons</th></tr></thead><tbody>{prow}</tbody></table></div>
<p class="small col">Moon counts: {src_link('nasafact')} (March 2025); they grow as new small moons are confirmed. Abbreviations: {src_link('iaustyle', True)}, 5.25.
Symbols: {src_link('unicode', True)}.</p></section>
<section class="block"><h2>Configurations</h2><p class="col">Old almanacs printed these as symbols beside the planets. The table above the orrery says which one each planet is in today.</p>
<div class="tablewrap"><table><tbody>{asp}</tbody></table></div></section>
<div class="then col"><b>Then and now</b><p>The IAU’s style manual (1989) says the special symbols for planets and for phenomena such as conjunctions “should not be used” in
astronomical writing: write the word, and in table headings use letters such as Ma for Mars. Only ☉ and ⊕ survive, in M☉ and M⊕. Pluto was counted as the ninth
planet from 1930 until 2006, when the IAU defined a planet as a body that has cleared its orbit and made Pluto a dwarf planet ({src_link('iau2006', True)}).</p></div>'''
    pnames = {k: [n, s] for k, n, s, *_ in PLANETS}
    scripts = ('<script>window.RK_CONST = %s; window.RK_CNAMES = %s; window.RK_PL = %s;</script>\n' % (
        json.dumps(bounds, separators=(',', ':')), json.dumps(CONSTELLATIONS, ensure_ascii=False), json.dumps(pnames, ensure_ascii=False)) +
        '<script src="../../assets/astro.js"></script>\n<script src="../../assets/orrery.js"></script>\n')
    out.append(page('sky/planets/index.html', 'Planets and their names · Reckoning', 'Planet names, gods, symbols and discoverers, with a live orrery and the IAU rules on symbols.',
                    body, scripts=scripts, nav='sky'))
    return out
