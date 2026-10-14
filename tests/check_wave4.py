"""Wave 4 checks: Ship and Code of life data, the glossary and the naming page; then runs tests/check_wave4.js.

Reference values (load-line sizes, base formulas, helix relations) are typed here from the primary texts,
separately from the data files they check."""
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'data'))
sys.path.insert(0, ROOT)
from ship import PARTS, LOADLINE  # noqa: E402
from life import IUPAC, BASES, FORMS, STRUCT, RING, HBONDS, B_SOLUTION_BP_PER_TURN  # noqa: E402
from glossary import TERMS, SAME_WORD  # noqa: E402
from names import GODS, WEEKDAYS, MONTHS, ELEMENTS, MOON_THEMES  # noqa: E402
from units import UNITS  # noqa: E402
from sources import SOURCES  # noqa: E402

fails, n = 0, 0


def ok(c, msg):
    global fails, n
    n += 1
    if not c:
        fails += 1
        print('FAIL', msg)


# ---------------------------------------------------------------- load line: Annex I, regs 4-7 and 40 (sizes in mm)
ok(LOADLINE['deck_line'] == (300, 25), 'reg. 4 deck line 300 x 25 mm')
ok(LOADLINE['ring_outer'] == 300 and LOADLINE['ring_width'] == 25, 'reg. 5 ring 300 mm outside, 25 mm wide')
ok(LOADLINE['ring_bar'] == (450, 25), 'reg. 5 horizontal line 450 x 25 mm')
ok(LOADLINE['line'] == (230, 25), 'reg. 6 lines 230 x 25 mm')
ok(LOADLINE['vertical_from_ring'] == 540, 'reg. 6 vertical line 540 mm forward of the ring centre')
ok(LOADLINE['letters'] == (115, 75), 'reg. 7 letters 115 x 75 mm')
ok(LOADLINE['wna_add_mm'] == 50 and LOADLINE['wna_max_length_m'] == 100, 'reg. 40(6) WNA +50 mm for ships of 100 m or less')
ok(LOADLINE['tropical_fraction'] == 48, 'reg. 40(3)/(5) one forty-eighth')

# then-and-now: "35 cubic feet of sea water to the ton" (long ton, sea water 64 lb/ft³ ≈ 1.025 t/m³)
U = {u['id']: u['f'] for u in UNITS}
lb, ft = U.get('lb'), U.get('ft')
ok(lb is not None and ft is not None, 'pound and foot defined')
if lb and ft:
    ft3 = ft ** 3
    long_ton = 2240 * lb
    vol = long_ton / F(1025) / ft3          # m³ of sea water at 1025 kg/m³, in cubic feet
    ok(abs(float(vol) - 35.0) < 0.02, 'a long ton of sea water is 35 ft³ (got %.3f)' % float(vol))
    rho64 = 64 * lb / ft3
    ok(abs(float(rho64) - 1025) < 0.5, '64 lb/ft³ = 1025 kg/m³ (got %.2f)' % float(rho64))
    ok(abs(float(2240 / F(625, 10)) - 35.84) < 1e-9, 'fresh water at 62.5 lb/ft³: 35.84 ft³ per long ton')

# every part is drawn and tappable
import rooms4  # noqa: E402
svg = rooms4.midship_svg()
for k, name, grp, desc in PARTS:
    ok('data-part="%s"' % k in svg, 'part drawn: ' + k)
    ok(len(desc) > 40 and desc.endswith('.'), 'part described: ' + k)
ok(len({k for k, *_ in PARTS}) == len(PARTS), 'part ids unique')

# ---------------------------------------------------------------- IUPAC: the names say the same as the sets in dnamath.js
r = subprocess.run(['node', '-e', 'console.log(JSON.stringify(require(process.argv[1]).SETS))', os.path.join(ROOT, 'assets', 'dnamath.js')], capture_output=True, text=True)
SETS = json.loads(r.stdout)
NAME = {'adenine': 'A', 'cytosine': 'C', 'guanine': 'G', 'thymine': 'T'}
for letter, meaning, mnemonic in IUPAC:
    if letter == 'N':
        got = 'ACGT'
    elif meaning.split()[0] in NAME:
        got = NAME[meaning.split()[0]]
    else:
        got = ''.join(sorted(re.findall(r'\b([ACGT])\b', meaning)))
    ok(got == ''.join(sorted(SETS[letter])), 'IUPAC %s: "%s" = {%s}' % (letter, meaning, SETS[letter]))
    if mnemonic.startswith('not '):
        missing = mnemonic.split()[1].rstrip(':')
        ok(missing not in SETS[letter] and len(SETS[letter]) == 3, 'IUPAC %s excludes %s' % (letter, missing))
ok([l for l, *_ in IUPAC] == list('ACGTRYSWKMBDHVN'), 'IUPAC table order and completeness')
# strong/weak agree with the hydrogen-bond counts of the pairs
ok(len(HBONDS['GC']) == 3 and len(HBONDS['AT']) == 2, 'G·C three hydrogen bonds, A·T two')
ok(SETS['S'] == 'CG' and SETS['W'] == 'AT', 'S = strong = G/C (3 bonds), W = weak = A/T (2 bonds)')

# ---------------------------------------------------------------- base structures give the right formulas
VAL = {'C': 4, 'N': 3, 'O': 2}
FORMULA = {'A': 'C5H5N5', 'G': 'C5H5N5O', 'C': 'C4H5N3O', 'T': 'C5H6N2O2', 'U': 'C4H4N2O2'}   # free bases
for key, name, kind, letter, formula, groups, where in BASES:
    ring, dbl, subs = STRUCT[key]
    atoms, bonds = RING[ring]
    order = {a: 0 for a in atoms}
    for a, b in bonds:
        order[a] += 1; order[b] += 1
    for a, b in dbl:
        ok(frozenset((a, b)) in {frozenset(x) for x in bonds}, '%s: double bond %s=%s is a ring bond' % (key, a, b))
        order[a] += 1; order[b] += 1
    cnt = {'C': 0, 'H': 0, 'N': 0, 'O': 0}
    for at, grp, bo in subs:
        order[at] += bo
        if grp == 'O':
            cnt['O'] += 1
        elif grp == 'NH2':
            cnt['N'] += 1; cnt['H'] += 2
        elif grp == 'CH3':
            cnt['C'] += 1; cnt['H'] += 3
    for a in atoms:
        cnt[a[0]] += 1
        h = VAL[a[0]] - order[a]
        ok(h >= 0, '%s: atom %s within valence' % (key, a))
        cnt['H'] += max(h, 0)
    got = ''.join('%s%s' % (e, cnt[e] if cnt[e] > 1 else '') for e in 'CHNO' if cnt[e])
    ok(got == FORMULA[key] == formula, '%s formula from the drawing: %s (expected %s)' % (name, got, FORMULA[key]))
    ok(kind == ring, '%s is a %s' % (name, ring))

# ---------------------------------------------------------------- helix parameters hang together
for f, hand, nbp, rise, twist, pitch, diam, tilt, grooves, where, src in FORMS:
    ok(abs(abs(twist) - 360 / nbp) < 0.1, '%s-DNA: twist %.1f° = 360/%d' % (f, twist, nbp))
    ok(abs(pitch - rise * nbp) < 0.01, '%s-DNA: pitch %.2f = rise x bp per turn = %.3f' % (f, pitch, rise * nbp))
    ok((hand == 'left') == (twist < 0), '%s-DNA: sign of twist matches the hand' % f)
    ok(src in SOURCES, '%s-DNA source key' % f)
ok(abs(B_SOLUTION_BP_PER_TURN - 10.4) < 1e-9, 'B-DNA in solution: 10.4 bp per turn (Wang 1979)')

# ---------------------------------------------------------------- glossary and names
ok(len({t[0] for t in TERMS}) == len(TERMS), 'glossary: English terms unique')
for en, es, fr, d, link in TERMS:
    ok(es and fr and d.endswith('.'), 'glossary row complete: ' + en)
for w, uses in SAME_WORD:
    ok(len(uses) >= 2, 'same word has at least two meanings: ' + w)
ok(len(WEEKDAYS) == 7, 'seven days')
months = ' '.join(m for m, t in MONTHS)
for m in ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'):
    ok(m in months, 'month listed: ' + m)
ok('December' in months, 'September to December listed')
for p, *_ in MOON_THEMES:
    ok(p in ('Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'), 'moon theme planet: ' + p)
sym = {'Helium': 'He', 'Selenium': 'Se', 'Tellurium': 'Te', 'Mercury': 'Hg', 'Uranium': 'U', 'Neptunium': 'Np', 'Plutonium': 'Pu', 'Cerium': 'Ce',
       'Palladium': 'Pd', 'Titanium': 'Ti', 'Promethium': 'Pm', 'Thorium': 'Th', 'Vanadium': 'V'}
for name, s, t in ELEMENTS:
    ok(sym.get(name) == s, 'element symbol: %s = %s' % (name, s))

# ---------------------------------------------------------------- the JS checks
r = subprocess.run(['node', os.path.join(ROOT, 'tests', 'check_wave4.js')], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if line.startswith('FAIL') or line.startswith('note'):
        print(line)
ok(r.returncode == 0, 'JS checks: ' + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr))
js = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
print(('%d of %d checks FAILED' % (fails, n)) if fails else 'wave 4: %d checks passed (%s)' % (n, js))
sys.exit(1 if fails else 0)
