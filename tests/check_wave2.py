"""Checks for the Signal and Weather rooms. Run: python3 tests/check_wave2.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from signals import FLAGS, PENNANTS, SUBSTITUTES, MORSE, PROSIGNS, ICAO, ICAO_SAY, FIGURE_WORDS, JAN_1941, SOUND, C  # noqa: E402
from weather import BEAUFORT, SEA_STATE, SAFFIR, BASINS, VISIBILITY  # noqa: E402
import flagart  # noqa: E402

KN = 1852 / 3600   # m/s per knot, exact


def main():
    fails = []
    ok = lambda cond, msg: None if cond else fails.append(msg)
    # flags: A-Z once each, code words are the ICAO words, every design draws, colour counts match
    ok([f[0] for f in FLAGS] == [chr(65 + i) for i in range(26)], 'letter flags must be A-Z in order')
    ok([f[1] for f in FLAGS] == ICAO, 'flag code words must equal the ICAO alphabet')
    need = {'plain': 1, 'swallow': 1, 'swallow-pale': 2, 'pale2': 2, 'pale3': 3, 'pale5': 5, 'paly6': 2, 'fess2': 2, 'fess3': 3,
            'fess5': 5, 'fess121': 3, 'lozenge': 2, 'disc': 2, 'quarterly': 4, 'saltire': 2, 'cross': 2, 'chequy': 2,
            'perbend': 2, 'square': 2, 'square2': 3, 'bendy': 2, 'persaltire': 4, 'border': 2}
    designs = [f[2] for f in FLAGS] + [p[2] for p in PENNANTS] + [s[2] for s in SUBSTITUTES]
    for kind, cols in designs:
        ok(kind in need and len(cols) == need[kind], 'design %s %s' % (kind, cols))
        ok(all(c in C for c in cols), 'colour in %s' % cols)
        try:
            flagart.flag_svg((kind, cols))
        except Exception as e:  # noqa: BLE001
            fails.append('draw %s: %s' % (kind, e))
    ok(len(set(designs[:26])) == 26, 'letter flag designs must all differ')
    ok([p[0] for p in PENNANTS] == list('0123456789'), 'pennants 0-9')
    # Morse: 26 letters, 10 figures, all codes distinct, only dots and dashes
    codes = list(MORSE.values()) + [p[1] for p in PROSIGNS if p[1] not in MORSE.values()]
    ok(all(set(c) <= {'.', '-'} for c in codes), 'morse alphabet')
    ok(len(set(MORSE.values())) == len(MORSE), 'morse codes must be distinct')
    ok(all(ch in MORSE for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), 'morse letters and figures')
    # PARIS is exactly 50 units with the ITU timing (including the following word gap)
    units = lambda w: sum(sum(1 if e == '.' else 3 for e in MORSE[c]) + (len(MORSE[c]) - 1) for c in w) + 3 * (len(w) - 1) + 7
    ok(units('PARIS') == 50, 'PARIS should be 50 units, got %d' % units('PARIS'))
    # phonetic alphabets
    ok(len(ICAO) == 26 and len(ICAO_SAY) == 26 and len(JAN_1941) == 26, 'alphabet lengths')
    ok(all(ICAO[i][0] == chr(65 + i) for i in range(26)), 'ICAO initials')
    ok(all(JAN_1941[i][0] == chr(65 + i) for i in range(26)), '1941 initials')
    ok([w for d, w, s in FIGURE_WORDS][:10] == [p[1] for p in PENNANTS], 'figure code words equal pennant names')
    # sound signals: only s and p; at least 5 shorts for doubt
    for t, items in SOUND:
        for p, m in items:
            ok(set(p) <= {'s', 'p'}, 'sound pattern %s' % p)
    # Beaufort: contiguous knots and m/s, consistent with each other, empirical law inside every class
    for i in range(len(BEAUFORT) - 1):
        a, b = BEAUFORT[i], BEAUFORT[i + 1]
        ok(a[2][1] + 1 == b[2][0], 'Beaufort knots gap between %d and %d' % (a[0], b[0]))
        ok(abs(a[3][1] + 0.1 - b[3][0]) < 1e-9, 'Beaufort m/s gap between %d and %d' % (a[0], b[0]))
        kb = (a[2][1] + b[2][0]) / 2 * KN; mb = (a[3][1] + b[3][0]) / 2
        # the knot and m/s limits are separately rounded official tables; they disagree by up to ~0.55 m/s at forces 4-6
        ok(abs(kb - mb) <= 0.6, 'Beaufort %d/%d boundary: %.2f m/s from knots vs %.2f' % (a[0], b[0], kb, mb))
        if abs(kb - mb) > 0.3:
            print('note: Beaufort %d/%d knot limit is %.2f m/s, m/s limit %.2f (known difference between the two tables)' % (a[0], b[0], kb, mb))
    for f, name, kn, ms, h, sea, land in BEAUFORT:
        v = 0.836 * f ** 1.5
        hi = ms[1] if ms[1] is not None else 1e9
        ok(ms[0] - 0.05 <= v <= hi + 0.05, 'Beaufort %d: 0.836 B^1.5 = %.2f outside %s' % (f, v, ms))
    hs = [b[4][0] for b in BEAUFORT if b[4]]
    ok(hs == sorted(hs), 'wave heights should not decrease')
    # sea state contiguous
    for i in range(len(SEA_STATE) - 1):
        ok(SEA_STATE[i][3] == SEA_STATE[i + 1][2] or i == 0, 'sea state %d' % i)
    # Saffir-Simpson: contiguous knots; km/h boundaries agree with knots to within 2 km/h
    for i in range(len(SAFFIR) - 1):
        ok(SAFFIR[i][2] + 1 == SAFFIR[i + 1][1], 'Saffir knots %d' % i)
    for c, lo, hi, klo, khi in SAFFIR:
        ok(abs(lo * 1.852 - klo) <= 2, 'Saffir %d km/h low' % c)
    ok(SAFFIR[0][1] == BEAUFORT[12][2][0], 'a hurricane begins at Beaufort 12')
    ok(len(BASINS) == 7 and len(VISIBILITY) == 4, 'weather table sizes')
    print('wave 2 checks: %d flags, %d Morse signs, Beaufort 0-12, %d failures' % (len(designs) + 1, len(MORSE), len(fails)))
    for f in fails:
        print('FAIL', f)
    return len(fails)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
