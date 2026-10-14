"""Unit factors against reference values typed independently from NIST SP 811
Appendix B and NIST Handbook 44 Appendix C; temperature fixed points; prefixes.
Run: python3 tests/check_units.py (exit status 1 on any failure)."""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from units import UNITS, BY_ID, TEMP_OFFSET, KINDS  # noqa: E402
from si import PREFIXES, BASE, DERIVED, CONSTANTS  # noqa: E402
from sources import SOURCES  # noqa: E402

REF = {  # unit id: value in SI, as published (exact where NIST marks it exact)
    'in': '0.0254', 'ft': '0.3048', 'yd': '0.9144', 'mi': '1609.344', 'nmi': '1852', 'fathom': '1.8288',
    'usft': None, 'admmi': '1853.184', 'chain': '20.1168', 'rod': '5.0292', 'furlong': '201.168',
    'lb': '0.45359237', 'oz': '0.028349523125', 'gr': '0.00006479891', 'dr': '0.0017718451953125',
    'ozt': '0.0311034768', 'dwt': '0.00155517384', 'cwt': '50.80234544', 'lton': '1016.0469088', 'ston': '907.18474',
    'ct': '0.0002', 'slug': None,
    'acre': '4046.8564224', 'rood': '1011.7141056', 'mi2': '2589988.110336', 'ft2': '0.09290304', 'in2': '0.00064516',
    'in3': '0.000016387064', 'ft3': '0.028316846592', 'yd3': '0.764554857984', 'cord': '3.624556363776',
    'galus': '0.003785411784', 'qtus': '0.000946352946', 'ptus': '0.000473176473', 'flozus': '0.0000295735295625',
    'tbsp': '0.00001478676478125', 'tsp': '0.00000492892159375', 'bbl': '0.158987294928', 'buus': '0.03523907016688',
    'galimp': '0.00454609', 'ptimp': '0.00056826125', 'flozimp': '0.0000284130625',
    'kmh': None, 'mph': '0.44704', 'kn': None, 'fps': '0.3048',
    'lbf': '4.4482216152605', 'kgf': '9.80665',
    'atm': '101325', 'bar': '100000', 'mmHg': '133.322387415', 'psi': None,
    'calth': '4.184', 'calIT': '4.1868', 'btu': '1055.05585262', 'kWh': '3600000', 'ftlbf': '1.3558179483314004',
    'hp': '745.69987158227022', 'PS': '735.49875', 'au': '149597870700',
}
FLOAT_REF = {'usft': 0.3048006096012192, 'slug': 14.593902937206364, 'kmh': 0.2777777777777778, 'kn': 0.5144444444444445,
             'psi': 6894.757293168361, 'geomi': 1855.32484655}


def to_k(uid, x):
    u = BY_ID[uid]
    return u['f'] * F(x) + TEMP_OFFSET[uid]


def main():
    fails = 0
    ids = [u['id'] for u in UNITS]
    if len(ids) != len(set(ids)):
        print('FAIL duplicate unit ids'); fails += 1
    for u in UNITS:
        if u['kind'] not in KINDS:
            print('FAIL kind', u['id']); fails += 1
        if u['src'] not in SOURCES:
            print('FAIL source', u['id'], u['src']); fails += 1
    for uid, ref in REF.items():
        u = BY_ID[uid]
        if ref is None:
            continue
        if u['f'] != F(ref):
            print('FAIL %-8s %s != %s' % (uid, float(u['f']), ref)); fails += 1
    for uid, ref in FLOAT_REF.items():
        rel = abs(float(BY_ID[uid]['f']) - ref) / ref
        if rel > 1e-9:
            print('FAIL %-8s %r vs %r' % (uid, float(BY_ID[uid]['f']), ref)); fails += 1
    # temperature fixed points
    pts = [('degC', 0, F(27315, 100)), ('degC', 100, F(37315, 100)), ('degF', 32, F(27315, 100)), ('degF', 212, F(37315, 100)),
           ('degR', 0, F(0)), ('degR', F(49167, 100), F(27315, 100))]
    for uid, x, k in pts:
        if to_k(uid, x) != k:
            print('FAIL temperature', uid, x, float(to_k(uid, x)), float(k)); fails += 1
    if to_k('degC', -40) != to_k('degF', -40):
        print('FAIL -40 °C should equal -40 °F'); fails += 1
    # prefixes: 24, unique exponents and symbols, 2022 additions present
    exps = [p[0] for p in PREFIXES]; syms = [p[2] for p in PREFIXES]
    if len(PREFIXES) != 24 or len(set(exps)) != 24 or len(set(syms)) != 24:
        print('FAIL prefixes'); fails += 1
    if {'ronna', 'quetta', 'ronto', 'quecto'} - {p[1] for p in PREFIXES}:
        print('FAIL 2022 prefixes missing'); fails += 1
    if len(BASE) != 7 or len(CONSTANTS) != 7 or len(DERIVED) != 22:
        print('FAIL SI table sizes'); fails += 1
    print('units: %d, checked against references: %d, FAILURES: %d' % (len(UNITS), len([r for r in REF.values() if r]) + len(FLOAT_REF), fails))
    return fails


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
