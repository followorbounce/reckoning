"""Wave 5 room: Light. An optical bench that traces rays exactly through lenses, prisms, blocks, drops and mirrors.
Page builders called from build.py. Every number quoted in the text is computed here by running assets/optics.js
(the same code the pages and tests/check_wave5.js use), so the prose cannot drift from the instruments."""
import html
import json
import os
import subprocess

E = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))
KATEX = ('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">\n'
         '<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>\n')
TEX_RUN = ('<script>document.addEventListener("DOMContentLoaded",function(){if(!window.katex)return;document.querySelectorAll(".tex").forEach('
           'function(el){try{katex.render(el.getAttribute("data-tex"),el,{displayMode:true,throwOnError:false})}catch(e){el.textContent=el.getAttribute("data-tex")}})});</script>\n')
MATS = ['water', 'silica', 'bk7', 'f2', 'diamond']


def tex(t):
    return '<div class="formula"><span class="tex" data-tex="%s"></span></div>' % E(t)


def values():
    js = r'''
var O = require(process.argv[1]), L = O.LINES, out = {mats: {}};
['water','silica','bk7','f2','diamond'].forEach(function (m) {
  var nd = O.index(m, L.d);
  out.mats[m] = {name: O.MATERIALS[m].name, src: O.MATERIALS[m].src, nF: O.index(m, L.F), nd: nd, nC: O.index(m, L.C), abbe: O.abbe(m),
    crit: O.criticalDeg(nd, 1), brew: O.brewsterDeg(1, nd), R0: O.fresnel(1, nd, 1, 1).R};
});
var w = function (l) { return O.index('water', l); };
out.bow = {red: O.rainbowDeg(w(700), 1).angle, yellow: O.rainbowDeg(w(589.29), 1).angle, violet: O.rainbowDeg(w(400), 1).angle,
  red2: O.rainbowDeg(w(700), 2).angle, violet2: O.rainbowDeg(w(400), 2).angle, i1: O.rainbowDeg(w(589.29), 1).iDeg, b1: O.rainbowDeg(w(589.29), 1).b};
var nb = O.index('bk7', L.d), mn = O.prismMin(60, nb);
out.prism = {D: mn.D, i: mn.i, DF: O.prismMin(60, O.index('bk7', L.F)).D, DC: O.prismMin(60, O.index('bk7', L.C)).D,
  fD: O.prismMin(60, O.index('f2', L.F)).D - O.prismMin(60, O.index('f2', L.C)).D};
var tl = O.thickLens(nb, 100, -100, 12);
out.lens = {f: tl.f, bfd: tl.bfd, fF: O.thickLens(O.index('bk7', L.F), 100, -100, 12).bfd, fC: O.thickLens(O.index('bk7', L.C), 100, -100, 12).bfd};
console.log(JSON.stringify(out));'''
    r = subprocess.run(['node', '-e', js, os.path.join(ROOT, 'assets', 'optics.js')], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def mat_select(id_, default='bk7', only=None):
    names = {'water': 'Water', 'silica': 'Fused silica', 'bk7': 'Crown glass (N-BK7)', 'f2': 'Flint glass (N-F2)', 'diamond': 'Diamond'}
    return '<select id="%s">%s</select>' % (id_, ''.join('<option value="%s"%s>%s</option>' % (m, ' selected' if m == default else '', names[m])
                                                      for m in (only or MATS)))


def bench(page_key, label):
    return ('<div class="figure bench" data-page="%s"><canvas role="img" aria-label="%s"></canvas>'
            '<span class="hint">rays traced exactly · drag the yellow handles where shown</span></div>' % (page_key, E(label)))


LIMITS = ('<div class="then col"><b>What this model leaves out</b><p>These are rays, the geometrical-optics picture: light is treated as lines '
          'that bend and split at surfaces. Diffraction and interference, which need the wave picture, are not shown. The bench is a flat '
          'cross-section, so a lens here is really a cylinder of glass seen end-on. That is exact for rays in the plane of the drawing. Air '
          'is taken as n = 1, and the glass and water indices are given relative to air, so the angles are right. Colours on screen are an '
          'approximation of the spectrum.</p></div>')


def hub(page):
    cards = [('refraction', 'Refraction and total reflection', 'Snell’s law at one surface, how much light a surface reflects, the critical angle and Brewster’s angle.'),
             ('lenses', 'Lenses', 'Converging and diverging lenses traced surface by surface: focal points, spherical and chromatic aberration, images.'),
             ('prism', 'Prisms and colour', 'Deviation, minimum deviation, and white light opened into a spectrum by dispersion.'),
             ('mirrors', 'Mirrors', 'Plane, spherical, parabolic and convex mirrors, and why a telescope mirror is a parabola.'),
             ('rainbow', 'The rainbow', 'One drop of water, one reflection inside, and the 42° circle that every drop paints.'),
             ('bench', 'Free bench', 'Put lenses, prisms, blocks, drops and mirrors anywhere, aim the light, and see what happens.')]
    body = '''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Light</p>
<div class="head"><p class="eyebrow">Room · wave 5</p><h1>Light</h1>
<p class="lede col">Light runs straight until it meets something. At every surface part of it bends into the new material and part of it bounces
off, and in glass or water each colour bends by a slightly different amount. This room traces rays exactly: Snell’s law is applied at the real
curved surface, never a small-angle shortcut, and each surface sends back its share of light by Fresnel’s formulas. So, for rays in the plane of the drawing,
what you see is what a lens designer’s software shows.</p></div>
<section class="block"><div class="grid">%s</div></section>
<section class="block"><h2>How the bench works</h2><p class="col">Every ray starts at a source and is followed from surface to surface. At each one
the program finds the exact point where the ray meets the surface and the surface’s normal there. It then applies Snell’s law to get the refracted
ray and Fresnel’s equations to split off the reflected one. Past the critical angle nothing is transmitted and all the light is reflected. A ray’s
brightness on screen follows the share of light it carries. White light is traced as twelve wavelengths from 405 to 680 nm. Indices come from
published dispersion formulas: the glass maker’s data for crown and flint glass, Malitson for fused silica, Daimon and Masumura for water, and
Peter for diamond. The code is checked at every build against published indices, closed-form results and an independent paraxial calculation.</p></section>''' % ''.join(
        '<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in cards)
    return page('light/index.html', 'Light · Reckoning', 'An optical bench that traces rays exactly through lenses, prisms, glass blocks, water drops and mirrors.', body, nav='light')


def light_pages(page, src_link):
    V = values()
    m = V['mats']
    out = [hub(page)]
    up = '../../'
    scripts = '<script src="%sassets/optics.js"></script>\n<script src="%sassets/light.js"></script>\n' % (up, up)

    # ------------------------------------------------------------------ refraction
    rows = ''.join('<tr><td>%s</td><td class="num">%.4f</td><td class="num">%.4f</td><td class="num">%.4f</td><td class="num">%.1f</td><td class="num">%.1f°</td><td class="num">%.1f %%</td><td>%s</td></tr>'
                   % (E(v['name']), v['nF'], v['nd'], v['nC'], v['abbe'], v['crit'], 100 * v['R0'], src_link(v['src'], short=True)) for k, v in ((k, m[k]) for k in MATS))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / Refraction</p>
<div class="head"><p class="eyebrow">Light · one surface</p><h1>Refraction and total reflection</h1>
<p class="lede col">Light slows down in glass and water, and a ray that meets the boundary at a slant changes direction. Here a laser is aimed at
the middle of the flat face of a half-cylinder. On the round side every ray runs along a radius, so it crosses that face without bending, and the
flat face is the only one that counts. Switch the direction to send the light out of the glass instead, then tilt it past the critical angle.</p></div>
<div class="shape">{bench('refraction', 'A laser ray meeting the flat face of a glass half-cylinder, with the reflected and refracted rays')}
<div class="stack"><div class="plate"><p class="label">Set up</p>
<div class="row" role="group" aria-label="Direction"><button type="button" data-dir="in" aria-pressed="true">Air → glass</button><button type="button" class="ghost" data-dir="out" aria-pressed="false">Glass → air</button></div>
<div class="sliders"><label>Material {mat_select('rmat')}<span></span></label>
<label>Angle θ₁ <input type="range" id="rang" min="0" max="89.5" step="0.1" value="40"><output id="rangv"></output></label>
<label>Wavelength <input type="range" id="rlam" min="400" max="700" step="1" value="589"><output id="rlamv"></output></label></div></div>
<div class="plate" aria-live="polite"><p class="label">Measured on the ray</p><div class="qty" id="rq"></div><p class="small" id="rnote"></p></div></div></div>
<section class="block"><h2>Snell’s law</h2><p class="col">Angles are measured from the <b>normal</b>, the line square to the surface. The
<b>refractive index</b> n of a material is how many times slower light travels in it than in vacuum: n = c/v. Going into a slower material, the
ray turns towards the normal. Coming out, it turns away.</p>
{tex(r'n_1 \sin\theta_1 = n_2 \sin\theta_2')}
<p class="col">The index depends on the colour (wavelength) of the light. Blue light is slowed more than red, and that is all a prism needs to
make a spectrum. The table gives the index at three wavelengths the glass trade uses: the blue F line of hydrogen (486.1 nm), the yellow d line of
helium (587.6 nm) and the red C line of hydrogen (656.3 nm). The <b>Abbe number</b> V = (n<sub>d</sub> − 1)/(n<sub>F</sub> − n<sub>C</sub>)
measures how little a material spreads the colours: the higher it is, the less the colours separate.</p>
<div class="tablewrap"><table><thead><tr><th>Material</th><th>n<sub>F</sub></th><th>n<sub>d</sub></th><th>n<sub>C</sub></th><th>Abbe V</th><th>Critical angle</th><th>Reflected at 0°</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="small col">Computed from each material’s published dispersion formula, the same code the bench runs. Indices are relative to air. Water at 20 °C. Peter’s diamond measurements end at 644 nm, so the bench’s diamond beyond that is a slight extrapolation.</p></section>
<section class="block"><h2>Total internal reflection</h2><p class="col">Going from glass into air, the refracted ray leans further from the normal than
the incoming one. At the <b>critical angle</b> it skims along the surface, and beyond that angle no light gets out at all: the surface becomes a
perfect mirror. For crown glass the critical angle is {m['bk7']['crit']:.1f}°, for water {m['water']['crit']:.1f}° and for diamond only {m['diamond']['crit']:.1f}°.
That small angle traps light inside a cut diamond and helps it sparkle. Optical fibres, the prisms in binoculars and the rain sensor on a
windscreen all work by total internal reflection.</p>
{tex(r'\sin\theta_c = \frac{n_2}{n_1} \qquad (n_1 > n_2)')}</section>
<section class="block"><h2>How much is reflected</h2><p class="col">Every surface reflects some light. Fresnel’s equations give the share. It
depends on the angle and on the <b>polarisation</b>, the direction in which the light’s electric field vibrates. Head on, crown glass reflects
{100 * m['bk7']['R0']:.1f} % from each surface. Towards grazing incidence it reflects almost everything, which is why a lake mirrors the far shore but
lets you see the bottom at your feet.</p>
{tex(r'R_s = \left(\frac{n_1\cos\theta_1 - n_2\cos\theta_2}{n_1\cos\theta_1 + n_2\cos\theta_2}\right)^2 \qquad R_p = \left(\frac{n_1\cos\theta_2 - n_2\cos\theta_1}{n_1\cos\theta_2 + n_2\cos\theta_1}\right)^2')}
<p class="col">At <b>Brewster’s angle</b>, tan θ<sub>B</sub> = n<sub>2</sub>/n<sub>1</sub> ({m['bk7']['brew']:.1f}° for crown glass), light polarised in the plane of
the drawing is not reflected at all. The reflected and refracted rays are then exactly at right angles. Glare off water and roads is therefore
mostly polarised horizontally, and polarising sunglasses block that direction. The bench shows the average for unpolarised light.</p></section>
<div class="then col"><b>Then and now</b><p>The law was first written down by Ibn Sahl in Baghdad around 984, in a treatise on burning mirrors and
lenses (identified by the historian Roshdi Rashed in 1990). It was found again by Thomas Harriot about 1602 and by Willebrord Snell in 1621, neither
of whom published it, and first printed by René Descartes in <i>La Dioptrique</i> (1637). Augustin Fresnel derived the reflection formulas in 1823,
from a theory of light as a wave.</p></div>
{LIMITS}'''
    out.append(page('light/refraction/index.html', 'Refraction and total reflection · Reckoning',
                    'Snell’s law on an exact ray tracer: refraction into and out of glass, water and diamond, Fresnel reflection, the critical angle and Brewster’s angle.',
                    body, extra_head=KATEX, scripts=scripts + TEX_RUN, nav='light'))

    # ------------------------------------------------------------------ lenses
    L = V['lens']
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / Lenses</p>
<div class="head"><p class="eyebrow">Light · two surfaces</p><h1>Lenses</h1>
<p class="lede col">A lens is two refracting surfaces close together. Thicker in the middle, it bends parallel light together to a focus. Thinner in
the middle, it spreads light as if from a point in front of it. Here every ray is traced through both real spherical surfaces, so you see what a
simple formula hides: the rays from the rim do not focus where the rays near the axis do.</p></div>
<div class="shape">{bench('lenses', 'Rays passing through a lens and coming to a focus')}
<div class="stack"><div class="plate"><p class="label">The lens</p><div class="sliders">
<label>Type <select id="ltype"><option value="biconvex">Biconvex (converging)</option><option value="plano-convex">Plano-convex (converging)</option><option value="meniscus">Meniscus (converging)</option>
<option value="biconcave">Biconcave (diverging)</option><option value="plano-concave">Plano-concave (diverging)</option><option value="ideal">Ideal thin lens (a model)</option></select><span></span></label>
<label id="lRrow">Radius R <input type="range" id="lR" min="40" max="300" step="1" value="100"><output id="lRv"></output></label>
<label id="lfrow" hidden>Focal length <input type="range" id="lf" min="-200" max="200" step="1" value="100"><output id="lfv"></output></label>
<label>Diameter <input type="range" id="lD" min="10" max="90" step="1" value="50"><output id="lDv"></output></label>
<label id="lmatrow">Material {mat_select('lmat')}<span></span></label></div></div>
<div class="plate"><p class="label">The light</p><div class="sliders">
<label>Source <select id="llight"><option value="beam">Parallel beam (distant object)</option><option value="point">Point on the axis</option></select><span></span></label>
<label id="ltiltrow">Beam tilt <input type="range" id="ltilt" min="-12" max="12" step="0.5" value="0"><output id="ltiltv"></output></label>
<label id="lurow" hidden>Object distance <input type="range" id="lu" min="40" max="400" step="5" value="220"><output id="luv"></output></label>
<label>Rays <input type="range" id="ln" min="3" max="31" step="2" value="11"><output id="lnv"></output></label>
<label>Colour <select id="lcol"><option value="mono">One colour (d line)</option><option value="white">White light</option></select><span></span></label></div></div>
<div class="plate" aria-live="polite"><p class="label">Measured</p><div class="qty" id="lq"></div></div></div></div>
<section class="block"><h2>The lensmaker’s formula</h2><p class="col">Light travels left to right. A surface’s radius R is positive when its centre
of curvature lies to the right of it. So a biconvex lens has R<sub>1</sub> &gt; 0 and R<sub>2</sub> &lt; 0. For a lens of index n and centre thickness t,
the focal length f is</p>
{tex(r'\frac{1}{f} = (n-1)\left[\frac{1}{R_1} - \frac{1}{R_2} + \frac{(n-1)\,t}{n\,R_1 R_2}\right]')}
<p class="col">The focal length is measured from the lens’s principal plane. The <b>back focal distance</b>, from the last surface to the focus F′,
is what you measure with a ruler. <b>Power</b> is 1/f in dioptres when f is in metres: a +2.5 reading glass has f = 400 mm. For the default lens here
(crown glass, R = ±100 mm, 12 mm thick) f = {L['f']:.1f} mm and the back focal distance is {L['bfd']:.1f} mm.</p></section>
<section class="block"><h2>Two flaws of a simple lens</h2><p class="col"><b>Spherical aberration.</b> A sphere is easy to grind but is not the
shape that sends every ray to one point. Rays through the rim are bent too much and cross the axis short of the focus, so the image of a star is a
small blur, not a point. Make the lens wider and watch the crossing points spread along the axis. Opticians reduce the flaw by sharing the bending
between surfaces (turn a plano-convex lens with its curved side to the parallel light), by stopping down the aperture, or by grinding an
<b>asphere</b>.</p>
<p class="col"><b>Chromatic aberration.</b> The index is higher for blue, so blue focuses closer to the lens than red. For the default lens the
blue F light focuses {L['fC'] - L['fF']:.2f} mm before the red C light. Choose white light and look at the coloured fringe at the focus. An
<b>achromatic doublet</b> cures most of it: a converging crown-glass lens cemented to a weaker diverging flint-glass lens, whose larger
dispersion cancels the crown’s while leaving some converging power.</p></section>
<section class="block"><h2>The ideal thin lens</h2><p class="col">The ideal thin lens is a model with no thickness and no aberrations. Every ray
from one point meets again at one point. It is what the familiar formula describes, with u the object distance in front of the lens, v the image
distance behind it (negative when the image is virtual) and magnification −v/u. Choose it, put a point source on the axis, and compare it with a
real lens of the same focal length.</p>
{tex(r'\frac{1}{u} + \frac{1}{v} = \frac{1}{f}')}</section>
<div class="then col"><b>Then and now</b><p>Reading stones, polished domes of rock crystal or glass laid on a page, are older than spectacles. Spectacles
appeared in northern Italy in the late 1280s: in a sermon preached in Florence in February 1306, the Pisan friar Giordano said the art of making
them had been found less than twenty years before. The achromatic doublet was made by Chester Moor Hall in the 1730s and patented by John Dollond in 1758. Today a camera lens of a dozen
elements is designed by tracing many thousands of rays, exactly as this bench does, only in three dimensions.</p></div>
{LIMITS}'''
    out.append(page('light/lenses/index.html', 'Lenses · Reckoning',
                    'Converging and diverging lenses traced surface by surface: focal points, the lensmaker’s formula, spherical and chromatic aberration, and the ideal thin lens.',
                    body, extra_head=KATEX, scripts=scripts + TEX_RUN, nav='light'))

    # ------------------------------------------------------------------ prism
    Pm = V['prism']
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / Prisms and colour</p>
<div class="head"><p class="eyebrow">Light · dispersion</p><h1>Prisms and colour</h1>
<p class="lede col">A prism bends light twice, both times towards its thick base. White light comes out as a fan of colours, because each colour has
its own refractive index. Turn the incoming ray and watch the deviation fall to a least value, then rise again.</p></div>
<div class="shape">{bench('prism', 'A ray of white light entering a glass prism and leaving as a spectrum')}
<div class="stack"><div class="plate"><p class="label">The prism and the ray</p><div class="sliders">
<label>Apex angle A <input type="range" id="pA" min="20" max="75" step="1" value="60"><output id="pAv"></output></label>
<label>Material {mat_select('pmat')}<span></span></label>
<label>Incidence i <input type="range" id="pi" min="0" max="89" step="0.1" value="50"><output id="piv"></output></label>
<label>Light <select id="pcol"><option value="white">White light</option><option value="mono">One colour</option></select><span></span></label>
<label>Wavelength <input type="range" id="plam" min="400" max="700" step="1" value="589"><output id="plamv"></output></label></div>
<div class="row"><button type="button" id="pmin">Set to minimum deviation</button></div></div>
<div class="plate" aria-live="polite"><p class="label">Measured</p><div class="qty" id="pq"></div></div></div></div>
<section class="block"><h2>Deviation</h2><p class="col">The ray meets the first face at angle i and leaves the second at angle e. Its total turn,
the <b>deviation</b>, is</p>
{tex(r'\delta = i + e - A')}
<p class="col">Turn the incoming ray and δ passes through a least value, the <b>minimum deviation</b>. It happens when the ray crosses the prism
symmetrically, parallel to the base, entering and leaving at the same angle. There the index follows from two angles alone. Measuring them on a
prism of the glass is how glass makers measure indices to five decimal places:</p>
{tex(r'n = \frac{\sin\frac{A+\delta_{\min}}{2}}{\sin\frac{A}{2}}')}
<p class="col">For a 60° prism of crown glass in yellow light, δ<sub>min</sub> = {Pm['D']:.2f}°, reached at i = {Pm['i']:.1f}°. Make the incidence too
small, or the prism too steep, and the ray meets the second face beyond the critical angle and is totally reflected inside.</p></section>
<section class="block"><h2>Dispersion</h2><p class="col">In blue F light the same crown prism deviates by {Pm['DF']:.2f}° and in red C light by
{Pm['DC']:.2f}°, which opens a fan of {Pm['DF'] - Pm['DC']:.2f}°. A flint glass prism opens it to {Pm['fD']:.2f}°. Flint glasses, with lead or titanium
oxide in them, spread colours more for the same amount of bending, which is what a spectroscope needs and an achromatic lens exploits.</p>
<p class="col">A prism with a 90° corner is also used without any colour at all: light enters the long face square on, is totally reflected
by the two short faces, and goes back the way it came (try the right-angle prism on the <a href="../bench/">free bench</a>). Binoculars use such prisms (Ignazio Porro, 1854) to fold the
light path and turn the image the right way up.</p></section>
<div class="then col"><b>Then and now</b><p>Prisms making colours were well known, but people thought the glass coloured the light. From 1666 Isaac
Newton experimented with prisms. Passing a single colour from one prism through a second, he found that it did not change. White light is a mixture, and the prism only sorts it.
He reported this in 1672 and set it out in <i>Opticks</i> (1704) ({src_link('newton1704', short=True)}). Newton counted seven colours, choosing the
number to match the notes of the musical scale; the spectrum itself is continuous. In 1814 Joseph von Fraunhofer saw dark lines crossing the solar
spectrum and used them to measure the dispersion of his glasses. The F and C lines in the table on the refraction page still carry his letters (his
D is the yellow sodium line). The d line beside them is a line of helium, an element found only in 1868.</p></div>
{LIMITS}'''
    out.append(page('light/prism/index.html', 'Prisms and colour · Reckoning',
                    'A prism on an exact ray tracer: deviation, minimum deviation, measuring the index, and white light opened into a spectrum.',
                    body, extra_head=KATEX, scripts=scripts + TEX_RUN, nav='light'))

    # ------------------------------------------------------------------ mirrors
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / Mirrors</p>
<div class="head"><p class="eyebrow">Light · reflection</p><h1>Mirrors</h1>
<p class="lede col">A mirror has one rule: the ray leaves at the same angle to the normal as it arrived. Curve the mirror and the normals tip,
and parallel light gathers to a focus. A sphere gathers it almost to a point. A parabola gathers it exactly, but only for light along its axis.</p></div>
<div class="shape">{bench('mirrors', 'Parallel rays reflecting from a curved mirror towards its focus')}
<div class="stack"><div class="plate"><p class="label">The mirror</p><div class="sliders">
<label>Shape <select id="mshape"><option value="spherical">Concave, spherical</option><option value="parabolic">Concave, parabolic</option><option value="convex">Convex, spherical</option><option value="plane">Plane</option></select><span></span></label>
<label id="mfrow">Focal length <input type="range" id="mf" min="40" max="200" step="1" value="100"><output id="mfv"></output></label>
<label>Diameter <input type="range" id="mD" min="20" max="240" step="2" value="160"><output id="mDv"></output></label>
<label>Light tilt <input type="range" id="mtilt" min="-10" max="10" step="0.5" value="0"><output id="mtiltv"></output></label>
<label>Rays <input type="range" id="mn" min="3" max="41" step="2" value="15"><output id="mnv"></output></label></div></div>
<div class="plate" aria-live="polite"><p class="label">Measured</p><div class="qty" id="mq"></div></div></div></div>
<section class="block"><h2>Spherical mirrors</h2><p class="col">For rays close to the axis, a spherical mirror of radius R focuses parallel light
halfway between itself and its centre of curvature C:</p>
{tex(r'f = \frac{R}{2}')}
<p class="col">A ray striking at height h, where the radius from C makes the angle α with the axis (sin α = h/R), crosses the axis a distance
R/(2 cos α) from C. That is nearer the mirror than F, so a wide spherical mirror has spherical aberration like a lens. A <b>convex</b> mirror spreads
light as if from a virtual focus behind it. That gives a wide view in a small mirror, at the price of images that look further away than they are.</p></section>
<section class="block"><h2>The parabola</h2><p class="col">A parabola is the curve whose every point is as far from the focus as from a fixed
line behind it. That makes every ray parallel to the axis reflect through the focus, however far from the axis it strikes. Choose the parabolic
mirror: the spherical aberration reads zero. Then tilt the light a few degrees. The rays no longer meet at one point but cross unevenly, off to one side. Seen
in a real telescope, where the cross-section becomes a whole image, that error is a comet-shaped blur called <b>coma</b>, and it limits the useful
field of a parabolic telescope. Used the other way round, a lamp at the focus of a parabola sends out a parallel beam, as in a
searchlight. A dish aerial gathers radio waves the same way.</p></section>
<div class="then col"><b>Then and now</b><p>Isaac Newton’s first reflecting telescope (1668) used a spherical mirror of polished speculum metal. John
Hadley showed the Royal Society a reflector with a true parabolic mirror in 1721, and parabolic main mirrors served most large telescopes until the
mid-20th century, the 5 m Hale telescope (1948) among them. Most large telescopes since, from Hubble to Keck, use a pair of hyperbolic mirrors
(the Ritchey–Chrétien design) that cancels coma as well. A mirror cannot have chromatic aberration, because reflection treats every colour the same. That is one reason the largest
telescopes are reflectors.</p></div>
{LIMITS}'''
    out.append(page('light/mirrors/index.html', 'Mirrors · Reckoning',
                    'Plane, spherical, parabolic and convex mirrors traced exactly: f = R/2, spherical aberration, why telescopes use parabolas, and coma.',
                    body, extra_head=KATEX, scripts=scripts + TEX_RUN, nav='light'))

    # ------------------------------------------------------------------ rainbow
    Bw = V['bow']
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / The rainbow</p>
<div class="head"><p class="eyebrow">Light · one drop</p><h1>The rainbow</h1>
<p class="lede col">Sunlight enters a raindrop, reflects once off the back of it, and comes out again. Rays that strike the drop at different
heights come out turned by different amounts. Near one particular height they bunch together, and that bunching, a little different for each colour,
is the bow.</p></div>
<div class="shape">{bench('rainbow', 'Sunlight entering a drop of water, reflecting inside and leaving split into colours')}
<div class="stack"><div class="plate"><p class="label">The drop</p><div class="sliders">
<label>Light <select id="rbmode"><option value="one">One ray of sunlight</option><option value="many">Sunlight across the whole drop</option></select><span></span></label>
<label id="rbbrow">Height b <input type="range" id="rbb" min="0" max="0.99" step="0.001" value="0.86"><output id="rbbv"></output></label>
<label class="check"><input type="checkbox" id="rbonly" checked> Show only light that reflects once inside</label></div></div>
<div class="plate" aria-live="polite"><p class="label">Computed</p><div class="qty" id="rbq"></div></div></div></div>
<div class="figure chart"><svg id="rbchart" viewBox="0 0 600 260" role="img" aria-label="Angle from the antisolar point against the height at which the ray strikes the drop, for red and violet light"></svg></div>
<p class="small col">The chart shows where rays from each height end up. The curves flatten at their peaks (the dots), where many neighbouring rays
leave at almost the same angle. That pile-up makes the bright bow. Red peaks at a larger angle than violet, so red is on the outside.</p>
<section class="block"><h2>Descartes’ calculation</h2><p class="col">A ray striking the drop at height b (as a fraction of the radius) meets the
surface at angle i with sin i = b, and refracts to r with sin i = n sin r. Each refraction, on entering and again on leaving, turns it by i − r, and each reflection inside
turns it by 180° − 2r. With one reflection inside, the total turn is</p>
{tex(r'D = 2(i - r) + (180^\circ - 2r)')}
<p class="col">D is least where cos² i = (n² − 1)/3. That is at b = {Bw['b1']:.3f}, i = {Bw['i1']:.1f}° for yellow light. The light leaving there makes
an angle 180° − D with the direction straight away from the Sun, the <b>antisolar point</b>, where your head’s shadow falls. Every drop at that angle
sends you its bright light, so the bow is a circle around the antisolar point: {Bw['red']:.1f}° for red, {Bw['yellow']:.1f}° for yellow and
{Bw['violet']:.1f}° for violet light.</p>
<p class="col">With two reflections inside, the least turn comes where cos² i = (n² − 1)/8. That gives the fainter <b>secondary bow</b>, from about
{Bw['red2']:.1f}° (red, now on the inside) to {Bw['violet2']:.1f}° (violet, outside): its colours are reversed. No light from one or two reflections leaves between the two bows, so the sky
there is darker: <b>Alexander’s dark band</b>.</p></section>
<div class="then col"><b>Then and now</b><p>Theodoric of Freiberg explained the bow with water-filled glass globes about 1307: refraction, a
reflection inside, refraction again. René Descartes traced rays through a drop by calculation in <i>Les Météores</i> (1637)
({src_link('descartes1637', short=True)}) and found the 42° angle. Newton then explained the colours. Ray optics cannot explain everything. The faint
pastel <b>supernumerary bows</b> just inside the main one come from interference, a wave effect, worked out by Thomas Young (1803) and George Airy
(1838).</p></div>
{LIMITS}'''
    out.append(page('light/rainbow/index.html', 'The rainbow · Reckoning',
                    'Rays through a drop of water: Descartes’ minimum deviation, the 42° primary bow, the 51° secondary bow and Alexander’s dark band.',
                    body, extra_head=KATEX, scripts=scripts + TEX_RUN, nav='light'))

    # ------------------------------------------------------------------ free bench
    adds = [('biconvex', 'Converging lens'), ('biconcave', 'Diverging lens'), ('prism', 'Prism'), ('rprism', 'Right-angle prism'), ('slab', 'Glass block'), ('half', 'Half-cylinder'),
            ('drop', 'Drop'), ('plane', 'Plane mirror'), ('concave', 'Concave mirror'), ('parabolic', 'Parabolic mirror'), ('thin', 'Ideal lens')]
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Light</a> / Free bench</p>
<div class="head"><p class="eyebrow">Light · sandbox</p><h1>Free bench</h1>
<p class="lede col">Add optical parts, drag them anywhere, turn them, and aim the light. Drag the yellow dot to move the source and the small ring to
aim it. Tap a part to select it, then turn, resize, change its material or remove it. Everything is traced exactly, as on the other pages.</p></div>
<div class="figure bench wide" data-page="bench"><canvas role="img" aria-label="An optical bench with lenses, prisms and mirrors"></canvas><span class="hint">drag parts and the light · tap a part to select it</span></div>
<div class="mapgrid" style="margin-top:12px">
<div class="plate"><p class="label">Add a part</p><div class="row">{''.join('<button type="button" class="ghost" data-add="%s">%s</button>' % (k, E(n)) for k, n in adds)}</div>
<div class="row"><button type="button" class="ghost" id="bclear">Clear the bench</button></div></div>
<div class="plate"><p class="label">The light</p><div class="sliders">
<label>Source <select id="bsrc"><option value="beam">Parallel beam</option><option value="point">Point source</option><option value="laser">Single ray</option></select><span></span></label>
<label>Colour <select id="bcol"><option value="white">White light</option><option value="mono">One colour</option></select><span></span></label>
<label id="blamrow" hidden>Wavelength <input type="range" id="blam" min="400" max="700" step="1" value="589"><output id="blamv"></output></label>
<label id="bwrow">Beam width <input type="range" id="bw" min="4" max="120" step="1" value="36"><output id="bwv"></output></label>
<label id="bsprow" hidden>Spread <input type="range" id="bsp" min="2" max="120" step="1" value="30"><output id="bspv"></output></label>
<label id="bnrow">Rays <input type="range" id="bn" min="1" max="31" step="1" value="9"><output id="bnv"></output></label></div></div>
<div class="plate" id="bsel" hidden><p class="label" id="bname">Selected</p><div class="sliders">
<label>Turn <input type="range" id="brot" min="-180" max="180" step="1" value="0"><output id="brotv"></output></label>
<label>Size <input type="range" id="bsize" min="40" max="200" step="5" value="100"><output id="bsizev"></output></label>
<label id="bmatrow">Material {mat_select('bmat')}<span></span></label></div>
<div class="row"><button type="button" class="ghost" id="bdel">Remove</button></div></div></div>
<p class="small" id="bq" aria-live="polite"></p>
<section class="block"><h2>Things to try</h2><ul class="col">
<li>Put two converging lenses in a row, a short focal length behind a longer one, about the sum of their focal lengths apart. That is a Keplerian telescope: a parallel beam goes in and a narrower parallel beam comes out.</li>
<li>Send a single ray into a right-angled prism through its long face. It comes back out the way it came, totally reflected twice.</li>
<li>Aim a narrow beam at a glass drop and at a water drop. Compare where the light that reflects once inside comes out.</li>
<li>Put a diverging lens in a converging beam just before the focus. The focus moves back: that is a Barlow lens, or the back half of a telephoto lens.</li>
<li>Tilt a block of glass in a beam. The rays come out parallel to how they went in, only shifted sideways.</li></ul></section>
{LIMITS}'''
    out.append(page('light/bench/index.html', 'Free bench · Reckoning',
                    'An optical sandbox: lenses, prisms, blocks, drops and mirrors you can place and turn, with every ray traced exactly.',
                    body, scripts=scripts, nav='light'))
    return out
