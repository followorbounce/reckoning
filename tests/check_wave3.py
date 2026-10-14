"""Checks for the Number and Sky & sea rooms. Run: python3 tests/check_wave3.py

Python side: every symbol, Greek letter, planet and sign against the Unicode database; look-alike
characters against Unicode normalisation; the 88 constellations against the boundary table.
Then runs tests/check_wave3.js, which checks the page JavaScript (assets/astro.js, navmath.js,
trigmath.js) against published worked examples."""
import os
import subprocess
import sys
import unicodedata as ud

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'data'))
from number import SYMBOLS, GREEK, LOOKALIKES, POINTS  # noqa: E402
from sky import PLANETS, ASPECTS, CONSTELLATIONS, SIGNS, PORTS, ROUTES, zone_letter  # noqa: E402
from sources import SOURCES  # noqa: E402


def main():
    fails = []
    ok = lambda c, m: None if c else fails.append(m)
    n = 0
    for group, items in SYMBOLS:
        for ch, name, *_ in items:
            n += 1
            ok(len(ch) == 1 and ud.name(ch, '?') == name, 'symbol %r: Unicode name is %s, data says %s' % (ch, ud.name(ch, '?'), name))
    ok(n == len({c for g, it in SYMBOLS for c, *_ in it}), 'duplicate symbols')
    # Greek: 24 letters in alphabetical order of the code points, names match Unicode (which spells LAMDA)
    ok(len(GREEK) == 24, 'Greek alphabet has 24 letters')
    small = [g[2] for g in GREEK]
    ok(small == sorted(small), 'Greek letters out of order')
    for name, cap, sm, var, use in GREEK:
        uname = name.upper().replace('LAMBDA', 'LAMDA')
        ok(ud.name(cap) == 'GREEK CAPITAL LETTER ' + uname, 'capital ' + name)
        ok(ud.name(sm) == 'GREEK SMALL LETTER ' + uname, 'small ' + name)
        for v in var:
            ok(ud.name(v).startswith('GREEK'), 'variant of ' + name)
            # symbol variants (ϑ, ϕ, ϖ …) fold to the letter; the final sigma ς is a letter of its own, used at the end of a word
            ok(v == '\u03c2' or ud.normalize('NFKC', v) == sm, 'variant %s of %s should fold to the letter' % (ud.name(v), name))
    for ch, name, pref, kind, note in LOOKALIKES:
        ok(ud.name(ch) == name, name)
        if kind == 'canon':
            ok(ud.normalize('NFC', ch) == pref, name + ' should be canonically equal to ' + ud.name(pref))
        elif kind == 'compat':
            ok(ud.normalize('NFC', ch) != pref and ud.normalize('NFKC', ch) == pref, name + ' should be a compatibility character')
        else:
            ok(ud.normalize('NFKC', ch) == ch, name + ' should have no decomposition')
    ok(len(POINTS) == 32 and len(set(POINTS)) == 32, '32 compass points')
    for p in PLANETS:
        ok(ud.name(p[2]) == p[3], 'planet symbol ' + p[0])
    for a in ASPECTS:
        if a[0]:
            ok(ud.name(a[0]) == a[1], 'aspect ' + a[2])
    ok([ud.name(s[1]) for s in SIGNS] == [s[2] for s in SIGNS] and len(SIGNS) == 12, 'zodiac sign symbols')
    abbs = {l.split()[3] for l in open(os.path.join(HERE, '..', 'data', 'constbounds_1875.dat'))}
    ok(len(CONSTELLATIONS) == 88 and abbs == set(CONSTELLATIONS), 'the 88 constellations vs the boundary table: %s' % (abbs ^ set(CONSTELLATIONS)))
    letters = [zone_letter(z) for z in range(-12, 13)]
    ok(len(set(letters)) == 25 and 'J' not in letters and letters[12] == 'Z', 'zone letters')
    names = {p[0] for p in PORTS}
    ok(all(a in names and b in names for a, b in ROUTES), 'route ports')
    ok(all(-90 <= la <= 90 and -180 <= lo <= 180 for _, la, lo in PORTS), 'port coordinates')
    for k in ('noaasun', 'usnogast', 'jplapprox', 'nasafact', 'roman1987', 'iaustyle', 'iau2006', 'vincenty', 'cgpm2022r4', 'unicode', 'iso80000', 'cajori', 'iauconst'):
        ok(k in SOURCES, 'source ' + k)
    r = subprocess.run(['node', os.path.join(HERE, 'check_wave3.js')], capture_output=True, text=True)
    out = r.stdout.strip()
    if r.returncode:
        fails.append('JS checks failed:\n' + out + r.stderr)
    for line in out.splitlines():
        if line.startswith('note:'):
            print(line)
    print('wave 3 checks: %d symbols, 24 Greek letters, 88 constellations; %s; %d failures' % (
        n, out.splitlines()[0].split(';')[0].replace('wave 3 checks: ', 'JS: ') if out else 'JS: no output', len(fails)))
    for f in fails:
        print('FAIL', f)
    return len(fails)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
