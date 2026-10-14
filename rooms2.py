"""Wave 2 rooms: Signal and Weather. Page builders called from build.py."""
import html
import json
import os

from signals import FLAGS, PENNANTS, SUBSTITUTES, ANSWERING, MORSE, MORSE_NAMES, PROSIGNS, TIMING, ICAO, ICAO_SAY, FIGURE_WORDS, JAN_1941, SOUND
from weather import BEAUFORT, BEAUFORT_OLD_NAMES, SEA_STATE, VISIBILITY, FOG_TERMS, SAFFIR, BASINS
from flagart import flag_svg, WX, wx_svg

E = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))


def _blasts(p):
    return ''.join('<i class="%s"></i>' % ('pb' if c == 'p' else 'sb') for c in p)


def signal_pages(page, src_link):
    out = []
    # ---------------------------------------------------------------- hub
    cards = [('flags', 'Code flags', '26 letter flags, 10 numeral pennants, substitutes; every single-flag meaning.'),
             ('hoist', 'Flag hoist', 'Type a word and see it hoisted, with substitutes where letters repeat.'),
             ('morse', 'Morse code', 'Hear it at any speed, see the timing, and train your ear.'),
             ('phonetic', 'Phonetic alphabet', 'Alfa to Zulu and the figure code words, and the alphabet they replaced.'),
             ('sound', 'Sound signals', 'Whistle signals for manoeuvring and in fog, played at their real length.')]
    strip = ''.join(flag_svg(f[2], title=f[1], cls='flag sm') for f in FLAGS[:13])
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Signal</p>
<div class="head"><p class="eyebrow">Room · wave 2</p><h1>Signal</h1>
<p class="lede col">How ships talk without a shared language: flags that each carry a whole sentence, Morse by lamp, radio
and whistle, and spelling words that survive a bad line. Everything here follows the current International Code of Signals
and the ITU and IMO rules, with older practice noted where it differs.</p>
<div class="flagstrip" aria-hidden="true">{strip}</div></div>
<section class="block"><div class="grid">{''.join('<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in cards)}</div></section>'''
    out.append(page('signal/index.html', 'Signal · Reckoning', 'Code flags, Morse code, phonetic alphabets and sound signals, interactive and sourced.', body, nav='signal'))

    # ---------------------------------------------------------------- flags
    tiles = ''.join('<div class="ftile" id="flag-%s">%s<div><h3>%s <span class="small">%s</span></h3><p>%s</p>%s</div></div>' % (
        L, flag_svg(d, title='%s flag, %s' % (L, w)), L, E(w), E(m), ('<p class="small">%s</p>' % E(n)) if n else '') for L, w, d, m, n in FLAGS)
    pen = ''.join('<div class="ftile">%s<div><h3>%s <span class="small">%s</span></h3></div></div>' % (flag_svg(d, 'pennant', title='numeral pennant %s' % D), D, E(w)) for D, w, d in PENNANTS)
    subs = ''.join('<div class="ftile">%s<div><h3>%s</h3><p>%s</p></div></div>' % (flag_svg(d, 'triangle', title=n), E(n), E(m)) for k, n, d, m in SUBSTITUTES)
    subs += '<div class="ftile">%s<div><h3>%s</h3><p>%s</p></div></div>' % (flag_svg(ANSWERING[1], 'pennant', title=ANSWERING[0]), E(ANSWERING[0]), E(ANSWERING[2]))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Signal</a> / Code flags</p>
<div class="head"><p class="eyebrow">Signal · 40 flags</p><h1>Code flags</h1>
<p class="lede col">Each letter flag spells its letter, and flown alone it carries a complete, urgent message that every
ship understands in any language. Two- and three-flag groups look up longer messages in the Code book.</p></div>
<section class="block"><h2>Letter flags and their single-flag meanings</h2><div class="fgrid">{tiles}</div>
<p class="small">Meanings and designs: {src_link('ics')}. Wording is lightly shortened; the Code is authoritative.</p></section>
<div class="then col"><b>Then and now</b><p>The present Code dates from 1969 (revised 2005). Under the earlier code many single flags meant
something else, and its flags were named Affirm, Baker and so on rather than Alfa, Bravo.</p></div>
<section class="block"><h2>Numeral pennants</h2><div class="fgrid">{pen}</div></section>
<section class="block"><h2>Substitutes and the answering pennant</h2><div class="fgrid">{subs}</div>
<p class="col">A ship carries one flag of each kind. When a letter appears twice in a hoist, a substitute stands in for the repeated
flag: try it on the <a href="../hoist/">hoist page</a>.</p></section>'''
    out.append(page('signal/flags/index.html', 'Code flags · Reckoning', 'All International Code of Signals flags and pennants with their single-flag meanings.', body, nav='signal'))

    # ---------------------------------------------------------------- hoist
    data = {'letters': {L: flag_svg(d, title=L) for L, w, d, m, n in FLAGS}, 'digits': {D: flag_svg(d, 'pennant', title=D) for D, w, d in PENNANTS},
            'subs': [flag_svg(d, 'triangle', title=n) for k, n, d, m in SUBSTITUTES], 'meanings': {L: m for L, w, d, m, n in FLAGS},
            'words': dict([(L, w) for L, w, d, m, n in FLAGS] + [(D, w) for D, w, d in PENNANTS])}
    presets = ''.join('<button class="ghost" type="button" data-hoist="%s">%s</button>' % (p, p) for p in ('V', 'O', 'NC', 'BOOK', 'AA', 'DEEP', '1225'))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Signal</a> / Flag hoist</p>
<div class="head"><p class="eyebrow">Signal · composer</p><h1>Flag hoist</h1>
<p class="lede col">Flags are read from the top down. Type letters or figures; a repeated flag is replaced by the substitute
that points back to it.</p></div>
<div class="plate"><p class="label">Hoist</p>
<div class="row"><input id="htext" type="text" value="BOOK" maxlength="12" aria-label="Letters and figures to hoist" autocapitalize="characters" spellcheck="false">{presets}</div>
<div class="hoist"><div id="hmast" class="hmast"></div></div>
<p class="prov" id="hout" aria-live="polite"></p></div>
<div class="lens col"><b>How substitutes count</b><p>The first substitute repeats the uppermost flag of the group of the same class (letters, or numeral
pennants) directly above it; the second repeats the second; the third the third. In BOOK the second O repeats the second letter of
the hoist, so it is shown by the second substitute. In AA the second A is the first substitute.</p></div>
<p class="small">Rule: {src_link('ics')}, chapter 1 (general instructions).</p>'''
    scripts = '<script>window.RK_FLAGS = %s;</script>\n<script src="../../assets/hoist.js"></script>\n' % json.dumps(data, ensure_ascii=False)
    out.append(page('signal/hoist/index.html', 'Flag hoist composer · Reckoning', 'Compose a flag hoist; repeated flags use the correct substitute.', body, scripts=scripts, nav='signal'))

    # ---------------------------------------------------------------- morse
    rows = ''.join('<tr><td class="mono"><b>%s</b></td><td class="mono morse-code">%s</td><td>%s</td></tr>' % (
        E(k), v.replace('.', '·').replace('-', '−'), E(MORSE_NAMES.get(k, ''))) for k, v in MORSE.items())
    pros = ''.join('<tr><td>%s</td><td class="mono morse-code">%s</td><td class="small">%s</td></tr>' % (E(n), c.replace('.', '·').replace('-', '−'), E(w)) for n, c, w in PROSIGNS)
    tim = ''.join('<tr><td>%s</td><td class="num">%d</td></tr>' % (n, u) for n, u in TIMING)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Signal</a> / Morse code</p>
<div class="head"><p class="eyebrow">Signal · ITU-R M.1677-1</p><h1>Morse code</h1>
<p class="lede col">Everything in Morse is counted in one unit: a dot is one unit long, a dash three, and the silences between
elements, letters and words are one, three and seven. Speed is given in words per minute, using the word PARIS (exactly 50 units) as the standard word.</p></div>
<div class="plate"><p class="label">Send</p>
<div class="row"><input id="mtext" type="text" value="SOS DE RECKONING" aria-label="Text to send" autocapitalize="characters" spellcheck="false" style="flex:1;min-width:200px">
<button id="mplay" type="button">Play</button><span id="mlamp" class="lamp" aria-hidden="true"></span></div>
<div class="sliders"><label>Speed (wpm)<input id="mwpm" type="range" min="5" max="40" value="18"><output id="mwpmv">18</output></label>
<label>Farnsworth (wpm)<input id="mfwpm" type="range" min="5" max="40" value="18"><output id="mfwpmv">18</output></label>
<label>Tone (Hz)<input id="mtone" type="range" min="400" max="1000" step="10" value="650" oninput="this.nextElementSibling.textContent=this.value"><output>650</output></label></div>
<label class="row small"><input type="checkbox" id="moldgap" style="min-height:auto"> Use the older 5-unit gap between words</label>
<div class="mbar" id="mbar" aria-hidden="true"></div><p class="prov" id="minfo"></p>
<div class="row">{''.join('<button class="ghost" type="button" data-say="%s">%s</button>' % (s, s) for s in ('SOS', 'PARIS', 'CQ', 'TEST'))}</div></div>
<div class="plate"><p class="label">Train your ear</p>
<div class="row"><select id="dset" aria-label="Characters"><option value="easy">Short codes (E T I A N M…)</option><option value="letters">All letters</option><option value="digits">Figures</option><option value="all">Letters and figures</option></select>
<select id="dlen" aria-label="Group length"><option value="1">1 character</option><option value="3" selected>3 characters</option><option value="5">5 characters</option></select>
<button id="dlisten" type="button">Listen</button></div>
<div class="row"><input id="dans" type="text" aria-label="What you heard" autocapitalize="characters" spellcheck="false" autocomplete="off"><button class="ghost" id="dcheck" type="button">Check</button></div>
<p class="out" id="dres" aria-live="polite"></p></div>
<div class="then col"><b>Then and now</b><p>Some older manuals gave five units between words; the ITU recommendation uses seven. Tick the box above to hear the difference.
The commercial at (·−−·−·) was added in 2004 so that e-mail addresses could be sent.</p></div>
<section class="block"><h2>Timing</h2><div class="tablewrap" style="max-width:420px"><table><thead><tr><th>Element</th><th>Units</th></tr></thead><tbody>{tim}</tbody></table></div>
<p class="col small">At a speed of w words per minute one unit lasts 1.2/w seconds: 60 s divided by 50 units per word.</p></section>
<section class="block"><h2>The code</h2><div class="tablewrap"><table class="morsetab"><thead><tr><th>Sign</th><th>Code</th><th>Name</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="block"><h2>Procedure signals</h2><div class="tablewrap"><table><thead><tr><th>Signal</th><th>Code</th><th>Use</th></tr></thead><tbody>{pros}</tbody></table></div>
<p class="small">Source: {src_link('itu1677')}.</p></section>'''
    scripts = ('<script>window.RK_MORSE = %s;</script>\n<script src="../../assets/audio.js"></script>\n<script src="../../assets/morse.js"></script>\n'
               % json.dumps({'code': MORSE}))
    out.append(page('signal/morse/index.html', 'Morse code · Reckoning', 'International Morse code with sound, correct ITU timing, Farnsworth spacing and an ear-training drill.', body, scripts=scripts, nav='signal'))

    # ---------------------------------------------------------------- phonetic
    rows = ''.join('<tr><td class="mono"><b>%s</b></td><td><b>%s</b></td><td class="mono small">%s</td><td>%s</td></tr>' % (
        chr(65 + i), E(ICAO[i]), E(ICAO_SAY[i]), E(JAN_1941[i])) for i in range(26))
    figs = ''.join('<tr><td class="mono"><b>%s</b></td><td><b>%s</b></td><td class="mono small">%s</td></tr>' % (E(d), E(w), E(s)) for d, w, s in FIGURE_WORDS)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Signal</a> / Phonetic alphabet</p>
<div class="head"><p class="eyebrow">Signal · ITU and ICAO</p><h1>Phonetic alphabet</h1>
<p class="lede col">On a noisy radio B, D, E, P and T all sound alike. Each letter is therefore spoken as a word chosen to be
recognisable to speakers of English, French and Spanish alike. The same words name the code flags.</p></div>
<div class="plate"><p class="label">Spell it</p><div class="row"><input id="ptext" type="text" value="Reckoning" aria-label="Text to spell" spellcheck="false" style="flex:1;min-width:200px"></div>
<p class="out" id="pout" aria-live="polite"></p></div>
<section class="block"><h2>Letters</h2><div class="tablewrap"><table><thead><tr><th></th><th>Since 1956</th><th>Spoken as</th><th>US forces 1941 to mid-1950s</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Current alphabet: {src_link('iturr')}. The 1941 list: {src_link('jan')}.</p></section>
<section class="block"><h2>Figures</h2><p class="col">At sea and in the International Code of Signals, figures have their own code words, built from
a Latin-based root and the English number.</p>
<div class="tablewrap" style="max-width:560px"><table><thead><tr><th></th><th>Code word</th><th>Spoken as</th></tr></thead><tbody>{figs}</tbody></table></div></section>
<div class="then col"><b>Then and now</b><p>Before 1956 each service and country had its own list. The words Charlie, Mike, Victor and X-ray survived from
the wartime American list into today’s alphabet.</p></div>'''
    script = '''<script>
(function(){var W=%s,i=document.getElementById('ptext'),o=document.getElementById('pout');
function r(){o.textContent=i.value.toUpperCase().split('').map(function(c){return W[c]||(c===' '?'/':c)}).join(' ')}
i.addEventListener('input',r);r()})();
</script>
''' % json.dumps(dict([(chr(65 + i), ICAO[i]) for i in range(26)] + [(d, w) for d, w, s in FIGURE_WORDS if len(d) == 1]))
    out.append(page('signal/phonetic/index.html', 'Phonetic alphabet · Reckoning', 'The ICAO/ITU spelling alphabet and figure code words, with the 1941 alphabet it replaced.', body, scripts=script, nav='signal'))

    # ---------------------------------------------------------------- sound
    secs = ''
    for title, items in SOUND:
        rows = ''.join('<tr><td><button class="blast" type="button" data-blasts="%s" aria-label="Play %s">%s</button></td><td>%s</td></tr>' % (
            p, ' '.join('prolonged' if c == 'p' else 'short' for c in p), _blasts(p), E(m)) for p, m in items)
        secs += '<section class="block"><h2>%s</h2><div class="tablewrap"><table><tbody>%s</tbody></table></div></section>' % (E(title), rows)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Signal</a> / Sound signals</p>
<div class="head"><p class="eyebrow">Signal · COLREGs Part D</p><h1>Sound signals</h1>
<p class="lede col">When ships see each other, the whistle announces a turn before it shows. In fog, the whistle tells others
what kind of vessel is out there. A short blast lasts about one second; a prolonged blast four to six.</p></div>
<div class="plate"><p class="label">Legend</p><p><i class="sb"></i> short blast, about 1 s &nbsp; <i class="pb"></i> prolonged blast, 4 to 6 s (5 s here)</p>
<label class="row small"><input type="checkbox" id="hquick" style="min-height:auto"> Quick: play the rhythm at 40 % of real time</label>
<p class="small">Tap a pattern to hear it. On iPhone, the ringer switch must be on.</p></div>
{secs}
<div class="lens col"><b>Why the patterns are so short</b><p>A whistle carries meaning only if it cannot be mistaken. One, two, three short blasts map
to right, left and astern; anything longer than five short blasts means doubt. The fog signals add a tempo: the same pattern
every two minutes, so the listener can also judge whether the other vessel is approaching.</p></div>
<p class="small">Source: {src_link('colregs')}. At anchor and aground ships ring a bell (and a gong if 100 m or more long); those signals are not played here.</p>'''
    scripts = '<script src="../../assets/audio.js"></script>\n<script src="../../assets/horn.js"></script>\n'
    out.append(page('signal/sound/index.html', 'Sound signals · Reckoning', 'Ships’ whistle signals for manoeuvring and restricted visibility, played at their real length.', body, scripts=scripts, nav='signal'))
    return out


# ---------------------------------------------------------------- weather
def _land_path(W, H):
    """Natural Earth 110m land (topojson) -> SVG path in an equirectangular projection."""
    d = json.load(open(os.path.join(ROOT, 'data', 'land-110m.json')))
    sx, sy = d['transform']['scale']
    tx, ty = d['transform']['translate']
    arcs = []
    for a in d['arcs']:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(ix):
        pts = []
        for i in ix:
            seg = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts += seg if not pts else seg[1:]
        return pts

    def proj(lon, lat):
        return (lon + 180) / 360 * W, (90 - lat) / 180 * H
    paths = []
    for geom in d['objects']['land']['geometries']:
        polys = geom['arcs'] if geom['type'] == 'MultiPolygon' else [geom['arcs']]
        for poly in polys:
            for r in poly:
                ll = ring(r)
                d = ''
                for i, (lon, lat) in enumerate(ll):
                    x, y = proj(lon, lat)
                    jump = i == 0 or abs(lon - ll[i - 1][0]) > 180   # crossing the 180th meridian: start a new piece
                    d += ('M' if jump else 'L') + '%.1f %.1f' % (x, y)
                paths.append(d + 'Z')
    return ''.join(paths)


def weather_pages(page, src_link):
    out = []
    cards = [('beaufort', 'Beaufort scale', 'Wind force 0 to 12 with an animated sea drawn to scale.'),
             ('sea-state', 'State of the sea', 'The WMO sea-state code from calm to phenomenal.'),
             ('visibility', 'Visibility', 'Fog, mist and haze, and the visibility terms of marine forecasts.'),
             ('symbols', 'Weather symbols', 'The present-weather signs of the station model, from mist to thunderstorm.'),
             ('cyclones', 'Tropical cyclones', 'Where and when they form, what they are called, and how they are rated.')]
    body = f'''
<p class="crumbs"><a href="../index.html">Reckoning</a> / Weather</p>
<div class="head"><p class="eyebrow">Room · wave 2</p><h1>Weather</h1>
<p class="lede col">The scales sailors and observers use to put wind, sea and sky into numbers, with the codes of the
World Meteorological Organization and the definitions of national weather services.</p></div>
<section class="block"><div class="grid">{''.join('<a class="card" href="%s/"><h3>%s</h3><p class="small">%s</p></a>' % (s, E(n), E(w)) for s, n, w in cards)}</div></section>'''
    out.append(page('weather/index.html', 'Weather · Reckoning', 'Beaufort scale with an animated sea, sea state, visibility, weather symbols and tropical cyclones.', body, nav='weather'))

    # ---------------------------------------------------------------- beaufort
    js = []
    rows = []
    for f, name, kn, ms, h, sea, land in BEAUFORT:
        kn_t = '%d–%d' % kn if kn[1] is not None and kn[0] != kn[1] else ('%d+' % kn[0] if kn[1] is None else '&lt; 1')
        ms_t = '%.1f–%.1f' % ms if ms[1] is not None else '%.1f+' % ms[0]
        h_t = '—' if not h else ('%g' % h[0] + (' (%g)' % h[1] if h[1] else ''))
        mid = 0.836 * f ** 1.5
        js.append({'name': name, 'kn': kn_t.replace('&lt; ', '<'), 'ms': ms_t, 'h': list(h) if h else None, 'sea': sea, 'mid': mid})
        old = BEAUFORT_OLD_NAMES.get(f)
        rows.append('<tr><td class="num"><b>%d</b></td><td><b>%s</b>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="small">%s</td><td class="small">%s</td></tr>' % (
            f, E(name), ('<br><span class="small">formerly %s</span>' % E(old)) if old and old != name else '', kn_t, ms_t, h_t, E(sea), E(land)))
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Weather</a> / Beaufort scale</p>
<div class="head"><p class="eyebrow">Weather · WMO</p><h1>Beaufort scale</h1>
<p class="lede col">Francis Beaufort’s 1805 scale judged wind by its effect on a ship’s sails. Today it is read from the sea itself, and each
force has a defined range of wind speed. Move the slider: the sea below is drawn to scale beside a 10-metre boat.</p></div>
<div class="plate"><p class="label">Force</p>
<div class="seawrap"><canvas id="seacv" aria-label="Animated sea for the chosen Beaufort force"></canvas></div>
<div class="sliders"><label>Beaufort force<input id="bf" type="range" min="0" max="12" value="5"><output id="bfv">5</output></label></div>
<p class="prov" id="bfout" aria-live="polite"></p>
<p class="small">Illustration: wave height is the published probable height for the force, wavelength assumes a steepness of about 1/10, and each
wave moves at the deep-water speed for its length. Real seas also depend on fetch and duration.</p></div>
<section class="block"><h2>The scale</h2><div class="tablewrap"><table><thead><tr><th>Force</th><th>Name</th><th>Knots</th><th>m/s</th><th>Probable wave (max), m</th><th>Sea</th><th>On land</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="small">Sources: {src_link('mobeaufort')}; speed limits as in WMO practice. The descriptions are written for this site.</p></section>
<div class="lens col"><b>A formula behind the numbers</b><p>The speed ranges follow v ≈ 0.836 B<sup>3/2</sup> m/s, where B is the force:
force 6 gives 12.3 m/s, inside its 10.8–13.8 range. The build checks that every force’s mid-speed falls inside its own range.
It also found that the knot and m/s columns are two separately rounded tables: at forces 4 to 6 their boundaries differ by up to half a metre
per second (16.5 knots is 8.5 m/s, but the m/s table changes force at 8.0).</p></div>
<div class="then col"><b>Then and now</b><p>Older tables named forces 7 to 10 moderate gale, fresh gale, strong gale and whole gale. Speeds were attached
to the numbers only in the twentieth century; Beaufort’s own scale described the canvas a man-of-war could carry.</p></div>'''
    scripts = '<script>window.RK_BEAUFORT = %s;</script>\n<script src="../../assets/sea.js"></script>\n' % json.dumps(js, ensure_ascii=False)
    scripts += "<script>document.getElementById('bf').addEventListener('input',function(e){document.getElementById('bfv').textContent=e.target.value});</script>\n"
    out.append(page('weather/beaufort/index.html', 'Beaufort scale · Reckoning', 'The Beaufort wind scale with speeds, probable wave heights and an animated sea drawn to scale.', body, scripts=scripts, nav='weather'))

    # ---------------------------------------------------------------- sea state
    rows = ''.join('<tr><td class="num"><b>%d</b></td><td>%s</td><td class="num">%s</td><td><div class="hbar" style="width:%s%%"></div></td></tr>' % (
        c, E(n), ('%g' % lo if hi == lo else ('%g–%g' % (lo, hi) if hi is not None else 'over %g' % lo)), min(100, (hi or 18) / 18 * 100)) for c, n, lo, hi in SEA_STATE)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Weather</a> / State of the sea</p>
<div class="head"><p class="eyebrow">Weather · WMO code 3700</p><h1>State of the sea</h1>
<p class="lede col">Observers on ships report the sea as one figure from 0 to 9. The heights are for well-developed wind waves in
the open sea; the words come first and the heights are a guide.</p></div>
<div class="tablewrap"><table><thead><tr><th>Code</th><th>Description</th><th>Height, m</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Source: {src_link('wmo306')}. A height exactly on a boundary takes the lower code figure: 4 m is coded 5.</p>
<div class="lens col"><b>Sea and swell</b><p>Wind waves are raised by the wind blowing now; swell is wave energy that has travelled out of
the area where it was raised, long and regular. A calm day can carry a heavy swell from a storm a thousand miles away.</p></div>'''
    out.append(page('weather/sea-state/index.html', 'State of the sea · Reckoning', 'The WMO sea-state code 3700 from calm (glassy) to phenomenal.', body, nav='weather'))

    # ---------------------------------------------------------------- visibility
    vis = ''.join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (E(a), E(b)) for a, b in VISIBILITY)
    fog = ''.join('<tr><td><b>%s</b></td><td>%s</td></tr>' % (E(a), E(b)) for a, b in FOG_TERMS)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Weather</a> / Visibility</p>
<div class="head"><p class="eyebrow">Weather · marine forecasts</p><h1>Visibility</h1>
<p class="lede col">Visibility is the greatest distance at which a dark object can be seen and recognised against the sky.
At sea it decides how vessels must navigate and which sound signals they must make.</p></div>
<section class="block"><h2>Forecast terms</h2><div class="tablewrap" style="max-width:640px"><table><thead><tr><th>Term</th><th>Visibility</th></tr></thead><tbody>{vis}</tbody></table></div>
<p class="small">As used in UK shipping forecasts: {src_link('moglossary')}.</p></section>
<section class="block"><h2>Fog, mist and haze</h2><div class="tablewrap" style="max-width:760px"><table><tbody>{fog}</tbody></table></div></section>
<div class="then col"><b>Then and now</b><p>Older seamanship tables graded fog by the distance at which objects disappeared, from dense fog at about 50 yards
to excellent visibility beyond 30 miles. Forecasts now use four plain terms with fixed limits.</p></div>
<p class="col">In restricted visibility ships must sound the fog signals on the <a href="../../signal/sound/">sound signals</a> page.</p>'''
    out.append(page('weather/visibility/index.html', 'Visibility · Reckoning', 'Marine visibility terms and the difference between fog, mist and haze.', body, nav='weather'))

    # ---------------------------------------------------------------- symbols
    tiles = ''.join('<div class="wxtile">%s<div><b class="mono">ww %s</b><p>%s</p></div></div>' % (wx_svg(b, E(n)), c, E(n)) for c, n, b in WX)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Weather</a> / Weather symbols</p>
<div class="head"><p class="eyebrow">Weather · WMO code 4677</p><h1>Weather symbols</h1>
<p class="lede col">On a weather map each observing station reports “present weather” as a two-figure code, ww, from 00 to 99,
drawn as a small sign. The signs combine a few elements: a dot for rain, a comma for drizzle, a star for snow, a triangle for showers.</p></div>
<div class="lens col"><b>Reading the signs</b><p>Intensity is counted in elements: one, two, three or four dots for slight to heavy. Elements stacked
vertically mean intermittent; spread side by side, continuous. An inverted triangle beneath a sign makes it a shower.</p></div>
<section class="block"><h2>Common signs</h2><div class="wxgrid">{tiles}</div>
<p class="small">Meanings: {src_link('wmo306')}, code table 4677. The signs are redrawn here after the international station-model symbols; this is a selection of 20 of the 100.</p></section>'''
    out.append(page('weather/symbols/index.html', 'Weather symbols · Reckoning', 'Present-weather symbols from the WMO station model: rain, drizzle, snow, showers, fog and thunder.', body, nav='weather'))

    # ---------------------------------------------------------------- cyclones
    W, H = 1000, 500
    land = _land_path(W, H)

    def box(b):
        lon0, lat0, lon1, lat1 = b
        x = lambda lo: (lo + 180) / 360 * W
        y = lambda la: (90 - la) / 180 * H
        if lon1 < lon0:   # crosses the date line
            return [(x(lon0), y(lat1), W - x(lon0), y(lat0) - y(lat1)), (0, y(lat1), x(lon1), y(lat0) - y(lat1))]
        return [(x(lon0), y(lat1), x(lon1) - x(lon0), y(lat0) - y(lat1))]
    boxes = ''
    for i, (n, term, season, peak, b) in enumerate(BASINS):
        for (bx, by, bw, bh) in box(b):
            boxes += '<rect class="basin" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (bx, by, bw, bh)
        bx, by, bw, bh = box(b)[0]
        boxes += '<text class="blbl" x="%.1f" y="%.1f">%d</text>' % (bx + 6, by + 16, i + 1)
    eq = '<line class="eq" x1="0" x2="%d" y1="%d" y2="%d"/>' % (W, H // 2, H // 2)
    svg = '<svg class="map" viewBox="0 0 %d %d" role="img" aria-label="Tropical cyclone basins on a world map"><path class="land" d="%s"/>%s%s</svg>' % (W, H, land, eq, boxes)
    rows = ''.join('<tr><td class="num"><b>%d</b></td><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (i + 1, E(n), E(t), E(s), E(p)) for i, (n, t, s, p, b) in enumerate(BASINS))
    saff = ''.join('<tr><td class="num"><b>%d</b></td><td class="num">%s</td><td class="num">%s</td></tr>' % (c, '%d–%d' % (lo, hi) if hi else '%d+' % lo,
                   '%d–%d' % (klo, khi) if khi else '%d+' % klo) for c, lo, hi, klo, khi in SAFFIR)
    body = f'''
<p class="crumbs"><a href="../../index.html">Reckoning</a> / <a href="../">Weather</a> / Tropical cyclones</p>
<div class="head"><p class="eyebrow">Weather · basins and scale</p><h1>Tropical cyclones</h1>
<p class="lede col">The same storm is a hurricane, a typhoon or a cyclone depending on the ocean. They form over warm water away from the equator,
where the Earth’s rotation can set the air spinning; they almost never cross the equator.</p></div>
<div class="plate"><p class="label">Basins (approximate)</p><div class="mapwrap">{svg}</div></div>
<section class="block"><h2>Basins and seasons</h2><div class="tablewrap"><table><thead><tr><th></th><th>Basin</th><th>Called</th><th>Season</th><th>Peak</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small">Sources: {src_link('hrd')}; map: {src_link('naturalearth')}. The boxes mark the main breeding grounds, not official boundaries.</p></section>
<section class="block"><h2>Saffir–Simpson hurricane wind scale</h2><div class="tablewrap" style="max-width:560px"><table><thead><tr><th>Category</th><th>Wind, knots</th><th>km/h</th></tr></thead><tbody>{saff}</tbody></table></div>
<p class="small">One-minute sustained wind. Source: {src_link('nhc')}. A hurricane begins at 64 knots, Beaufort force 12.</p></section>
<div class="then col"><b>Then and now</b><p>Older charts drew storm tracks as hand-sketched average paths. Today each basin has a regional centre
that names storms and issues warnings, and decades of satellite tracks show where they really go.</p></div>'''
    out.append(page('weather/cyclones/index.html', 'Tropical cyclones · Reckoning', 'Tropical cyclone basins, local names, seasons, and the Saffir–Simpson scale.', body, nav='weather'))
    return out
