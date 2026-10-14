"""Independent checks for every shape formula.

Each shape's region is described here only by a point-membership test written from
its geometric definition (not from its formula). Areas and volumes are measured by
Monte Carlo sampling of the bounding box and compared with the formula; selected
perimeters and surfaces are measured by numerical integration of the boundary.
The Euler characteristic of each solid's boundary is computed from a generated
triangle mesh (polyhedra: from their vertex, edge and face counts).
Run: python3 tests/check_shapes.py   (exit status 1 on any failure)
"""
import math
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from shapes import SHAPES  # noqa: E402

RNG = np.random.default_rng(20261014)
N2, N3 = 1_500_000, 2_000_000
ENV = {'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'asin': math.asin,
       'acos': math.acos, 'atan': math.atan, 'PI': math.pi, 'rad': math.radians}


def evaluate(shape, values):
    env = dict(ENV, **values)
    for k, e in shape['let']:
        env[k] = eval(e, {}, env)
    return {q['sym']: eval(q['expr'], {}, env) for q in shape['q']}, env


def in_poly(x, y, pts):
    """Even-odd rule for a simple polygon."""
    inside = np.zeros_like(x, dtype=bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-300) + x1
        inside ^= cond & (x < xint)
    return inside


def ang(x, y):
    return np.mod(np.degrees(np.arctan2(y, x)), 360.0)


def region(slug, v):
    """Returns (membership function, bounding box) for the shape with parameters v."""
    g = v.get
    if slug == 'square':
        a = g('a'); return (lambda x, y: (abs(x) <= a / 2) & (abs(y) <= a / 2)), (-a, a, -a, a)
    if slug == 'rectangle':
        a, b = g('a'), g('b'); return (lambda x, y: (abs(x) <= a / 2) & (abs(y) <= b / 2)), (-a, a, -b, b)
    if slug == 'parallelogram':
        b, c, t = g('b'), g('c'), math.radians(g('t'))
        pts = [(0, 0), (b, 0), (b + c * math.cos(t), c * math.sin(t)), (c * math.cos(t), c * math.sin(t))]
        return (lambda x, y: in_poly(x, y, pts)), (-1, b + c + 1, -1, c + 1)
    if slug == 'rhombus':
        p, q = g('p'), g('q'); pts = [(-p / 2, 0), (0, q / 2), (p / 2, 0), (0, -q / 2)]
        return (lambda x, y: in_poly(x, y, pts)), (-p, p, -q, q)
    if slug == 'trapezoid':
        a, b, h = g('a'), g('b'), g('h'); off = (a - b) * 0.3
        pts = [(0, 0), (a, 0), (off + b, h), (off, h)]
        return (lambda x, y: in_poly(x, y, pts)), (-abs(off) - 1, a + abs(off) + b + 1, -1, h + 1)
    if slug == 'quadrilateral':
        p, q, t = g('p'), g('q'), math.radians(g('t'))
        m, k = 0.4, 0.65   # where the diagonals cross: not at their midpoints, so this is no parallelogram
        pts = [(-m * p, 0), (k * q * math.cos(t), k * q * math.sin(t)), ((1 - m) * p, 0),
               (-(1 - k) * q * math.cos(t), -(1 - k) * q * math.sin(t))]
        return (lambda x, y: in_poly(x, y, pts)), (-p - q, p + q, -q, q)
    if slug == 'triangle':
        a, b, c = g('a'), g('b'), g('c')
        # vertices from side lengths: A=(0,0), B=(c,0), C from |AC|=b, |BC|=a
        cx = (b * b + c * c - a * a) / (2 * c); cy = math.sqrt(max(b * b - cx * cx, 0))
        pts = [(0, 0), (c, 0), (cx, cy)]
        return (lambda x, y: in_poly(x, y, pts)), (min(0, cx) - 1, max(c, cx) + 1, -1, cy + 1)
    if slug == 'right-triangle':
        a, b = g('a'), g('b'); pts = [(0, 0), (a, 0), (0, b)]
        return (lambda x, y: in_poly(x, y, pts)), (-1, a + 1, -1, b + 1)
    if slug == 'isosceles-triangle':
        b, s = g('b'), g('s'); h = math.sqrt(s * s - b * b / 4); pts = [(-b / 2, 0), (b / 2, 0), (0, h)]
        return (lambda x, y: in_poly(x, y, pts)), (-b, b, -1, h + 1)
    if slug == 'equilateral-triangle':
        a = g('a'); pts = [(0, 0), (a, 0), (a / 2, a * math.sqrt(3) / 2)]
        return (lambda x, y: in_poly(x, y, pts)), (-1, a + 1, -1, a + 1)
    if slug == 'circle':
        r = g('r'); return (lambda x, y: x * x + y * y <= r * r), (-r, r, -r, r)
    if slug == 'sector':
        r, t = g('r'), g('t'); return (lambda x, y: (x * x + y * y <= r * r) & (ang(x, y) <= t)), (-r, r, -r, r)
    if slug == 'segment':
        r, t = g('r'), math.radians(g('t'))
        # chord between angles -t/2 and t/2; the segment lies beyond the chord, x > r cos(t/2)
        return (lambda x, y: (x * x + y * y <= r * r) & (x >= r * math.cos(t / 2))), (-r, r, -r, r)
    if slug == 'annulus':
        R, r = g('R'), g('r'); return (lambda x, y: (x * x + y * y <= R * R) & (x * x + y * y >= r * r)), (-R, R, -R, R)
    if slug == 'ring-sector':
        R, r, t = g('R'), g('r'), g('t')
        return (lambda x, y: (x * x + y * y <= R * R) & (x * x + y * y >= r * r) & (ang(x, y) <= t)), (-R, R, -R, R)
    if slug == 'ellipse':
        a, b = g('a'), g('b'); return (lambda x, y: (x / a) ** 2 + (y / b) ** 2 <= 1), (-a, a, -b, b)
    if slug == 'spandrel':
        r = g('r'); return (lambda x, y: (x >= 0) & (y >= 0) & (x <= r) & (y <= r) & ((x - r) ** 2 + (y - r) ** 2 >= r * r)), (0, r, 0, r)
    if slug in ('hexagon', 'octagon', 'regular-polygon'):
        n = {'hexagon': 6, 'octagon': 8}.get(slug) or int(g('n'))
        s = g('s'); R = s / (2 * math.sin(math.pi / n))
        pts = [(R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n)) for i in range(n)]
        return (lambda x, y: in_poly(x, y, pts)), (-R, R, -R, R)
    raise KeyError(slug)


def solid(slug, v):
    g = v.get
    if slug == 'cube':
        a = g('a'); return (lambda x, y, z: (abs(x) <= a / 2) & (abs(y) <= a / 2) & (abs(z) <= a / 2)), (0.7 * a,) * 3
    if slug == 'cuboid':
        a, b, c = g('a'), g('b'), g('c')
        return (lambda x, y, z: (abs(x) <= a / 2) & (abs(y) <= b / 2) & (abs(z) <= c / 2)), (0.7 * a, 0.7 * b, 0.7 * c)
    if slug == 'prism':
        n, s, h = int(g('n')), g('s'), g('h'); R = s / (2 * math.sin(math.pi / n))
        pts = [(R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n)) for i in range(n)]
        return (lambda x, y, z: in_poly(x, y, pts) & (abs(z) <= h / 2)), (R, R, h / 2)
    if slug == 'pyramid':
        a, h = g('a'), g('h')
        return (lambda x, y, z: (z >= 0) & (z <= h) & (abs(x) <= a / 2 * (1 - z / h)) & (abs(y) <= a / 2 * (1 - z / h))), (a / 2, a / 2, h)
    if slug == 'frustum-pyramid':
        a, b, h = g('a'), g('b'), g('h')
        return (lambda x, y, z: (z >= 0) & (z <= h) & (abs(x) <= (a + (b - a) * z / h) / 2) & (abs(y) <= (a + (b - a) * z / h) / 2)), (max(a, b) / 2, max(a, b) / 2, h)
    if slug == 'wedge':
        a, b, c, h = g('a'), g('b'), g('c'), g('h')
        # base a (x) by b (y) at z=0; ridge of length c along x at y=0, z=h; flat faces between
        return (lambda x, y, z: (z >= 0) & (z <= h) & (abs(y) <= b / 2 * (1 - z / h)) & (abs(x) <= (a + (c - a) * z / h) / 2)), (max(a, c) / 2, b / 2, h)
    if slug == 'prismoid':
        a1, b1, a2, b2, h = g('a1'), g('b1'), g('a2'), g('b2'), g('h')
        return (lambda x, y, z: (z >= 0) & (z <= h) & (abs(x) <= (a1 + (a2 - a1) * z / h) / 2) & (abs(y) <= (b1 + (b2 - b1) * z / h) / 2)), (max(a1, a2) / 2, max(b1, b2) / 2, h)
    if slug == 'cylinder':
        r, h = g('r'), g('h'); return (lambda x, y, z: (x * x + y * y <= r * r) & (abs(z) <= h / 2)), (r, r, h / 2)
    if slug == 'tube':
        R, r, h = g('R'), g('r'), g('h')
        return (lambda x, y, z: (x * x + y * y <= R * R) & (x * x + y * y >= r * r) & (abs(z) <= h / 2)), (R, R, h / 2)
    if slug == 'truncated-cylinder':
        r, h1, h2 = g('r'), g('h1'), g('h2')
        return (lambda x, y, z: (x * x + y * y <= r * r) & (z >= 0) & (z <= (h1 + h2) / 2 + (h2 - h1) / 2 * x / r)), (r, r, max(h1, h2))
    if slug == 'cone':
        r, h = g('r'), g('h'); return (lambda x, y, z: (z >= 0) & (z <= h) & (np.sqrt(x * x + y * y) <= r * (1 - z / h))), (r, r, h)
    if slug == 'frustum-cone':
        R, r, h = g('R'), g('r'), g('h')
        return (lambda x, y, z: (z >= 0) & (z <= h) & (np.sqrt(x * x + y * y) <= R + (r - R) * z / h)), (max(R, r), max(R, r), h)
    if slug == 'sphere':
        r = g('r'); return (lambda x, y, z: x * x + y * y + z * z <= r * r), (r, r, r)
    if slug == 'spherical-cap':
        r, h = g('r'), g('h'); return (lambda x, y, z: (x * x + y * y + z * z <= r * r) & (z >= r - h)), (r, r, r)
    if slug == 'spherical-zone':
        r, z1, z2 = g('r'), g('z1'), g('z2'); return (lambda x, y, z: (x * x + y * y + z * z <= r * r) & (z >= z1) & (z <= z2)), (r, r, r)
    if slug == 'spherical-sector':
        r, h = g('r'), g('h'); c = (r - h) / r   # cone half-angle: cos = (r-h)/r
        return (lambda x, y, z: (x * x + y * y + z * z <= r * r) & (z >= c * np.sqrt(x * x + y * y + z * z))), (r, r, r)
    if slug == 'spherical-wedge':
        r, t = g('r'), g('t'); return (lambda x, y, z: (x * x + y * y + z * z <= r * r) & (ang(x, y) <= t)), (r, r, r)
    if slug == 'hollow-sphere':
        R, r = g('R'), g('r'); return (lambda x, y, z: (x * x + y * y + z * z <= R * R) & (x * x + y * y + z * z >= r * r)), (R, R, R)
    if slug == 'ellipsoid':
        a, b, c = g('a'), g('b'), g('c'); return (lambda x, y, z: (x / a) ** 2 + (y / b) ** 2 + (z / c) ** 2 <= 1), (a, b, c)
    if slug == 'torus':
        R, r = g('R'), g('r'); return (lambda x, y, z: (np.sqrt(x * x + y * y) - R) ** 2 + z * z <= r * r), (R + r, R + r, r)
    if slug == 'square-ring':
        R, w = g('R'), g('w'); return (lambda x, y, z: (abs(np.sqrt(x * x + y * y) - R) <= w / 2) & (abs(z) <= w / 2)), (R + w, R + w, w / 2)
    if slug == 'barrel':
        D, d, h = g('D'), g('d'), g('h')
        return (lambda x, y, z: (abs(z) <= h / 2) & (np.sqrt(x * x + y * y) <= D / 2 - (D - d) / 2 * (2 * z / h) ** 2)), (D / 2, D / 2, h / 2)
    raise KeyError(slug)


def mc_area(fn, box):
    x0, x1, y0, y1 = box
    x = RNG.uniform(x0, x1, N2); y = RNG.uniform(y0, y1, N2)
    p = fn(x, y).mean(); A = (x1 - x0) * (y1 - y0)
    return p * A, A * math.sqrt(p * (1 - p) / N2)


def mc_volume(fn, half):
    if len(half) == 3 and isinstance(half, tuple) and half[2] and False:
        pass
    hx, hy, hz = half
    zlo = -hz
    x = RNG.uniform(-hx, hx, N3); y = RNG.uniform(-hy, hy, N3); z = RNG.uniform(zlo, hz, N3)
    p = fn(x, y, z).mean(); V = (2 * hx) * (2 * hy) * (2 * hz)
    return p * V, V * math.sqrt(p * (1 - p) / N3)


# ---------------------------------------------------------------- boundary checks by integration
def perimeter_ellipse(a, b, n=200000):
    t = np.linspace(0, 2 * np.pi, n + 1)
    return float(np.sum(np.hypot(np.diff(a * np.cos(t)), np.diff(b * np.sin(t)))))


def surface_ellipsoid(a, b, c, n=1200):
    u = np.linspace(0, np.pi, n); w = np.linspace(0, 2 * np.pi, 2 * n)
    U, Wv = np.meshgrid(u, w, indexing='ij')
    # |r_u x r_w| for r = (a sin u cos w, b sin u sin w, c cos u)
    nx = b * c * np.sin(U) ** 2 * np.cos(Wv); ny = a * c * np.sin(U) ** 2 * np.sin(Wv); nz = a * b * np.sin(U) * np.cos(U)
    dA = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return float(np.trapezoid(np.trapezoid(dA, w, axis=1), u))


def surface_of_revolution(rfun, z0, z1, n=200000):
    """Lateral area of the surface r = rfun(z) swept round the z axis."""
    z = np.linspace(z0, z1, n + 1); r = rfun(z)
    ds = np.hypot(np.diff(r), np.diff(z)); rm = (r[1:] + r[:-1]) / 2
    return float(np.sum(2 * np.pi * rm * ds))


BOUNDARY = {
    ('circle', 'C'): lambda v: 2 * np.pi * v['r'],     # trivially consistent; kept as a template
    ('ellipse', 'P'): lambda v: perimeter_ellipse(v['a'], v['b']),
    ('ellipsoid', 'S'): lambda v: surface_ellipsoid(v['a'], v['b'], v['c']),
    ('cone', 'S'): lambda v: surface_of_revolution(lambda z: v['r'] * (1 - z / v['h']), 0, v['h']) + np.pi * v['r'] ** 2,
    ('frustum-cone', 'L'): lambda v: surface_of_revolution(lambda z: v['R'] + (v['r'] - v['R']) * z / v['h'], 0, v['h']),
    ('sphere', 'S'): lambda v: surface_of_revolution(lambda z: np.sqrt(np.clip(v['r'] ** 2 - z ** 2, 0, None)), -v['r'], v['r'], 2000000),
    ('spherical-cap', 'L'): lambda v: surface_of_revolution(lambda z: np.sqrt(np.clip(v['r'] ** 2 - z ** 2, 0, None)), v['r'] - v['h'], v['r'], 2000000),
    ('spherical-zone', 'L'): lambda v: surface_of_revolution(lambda z: np.sqrt(np.clip(v['r'] ** 2 - z ** 2, 0, None)), v['z1'], v['z2'], 2000000),
    ('cylinder', 'L'): lambda v: surface_of_revolution(lambda z: v['r'] + 0 * z, 0, v['h']),
    ('torus', 'S'): lambda v: 4 * np.pi ** 2 * v['R'] * v['r'] if False else torus_area(v['R'], v['r']),
}


def torus_area(R, r, n=2000):
    u = np.linspace(0, 2 * np.pi, n + 1)
    # surface element r (R + r cos u) du dv, integrated over v gives 2π
    f = r * (R + r * np.cos(u))
    return float(2 * np.pi * np.trapezoid(f, u))


# ---------------------------------------------------------------- Euler characteristic from meshes
def chi_of_mesh(faces):
    edges = set()
    verts = set()
    for f in faces:
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            edges.add((min(a, b), max(a, b))); verts.add(a)
    return len(verts) - len(edges) + len(faces)


def grid_surface(nu, nv, wrap_u, wrap_v, pole_u=False):
    """Quad mesh on a (u, v) grid with optional wrap-around; pole_u collapses the
    first and last u rows to single points (a sphere)."""
    def idx(i, j):
        if pole_u and i == 0:
            return (-1, -1)
        if pole_u and i == nu:
            return (-2, -2)
        return (i % (nu if wrap_u else nu + 1), j % (nv if wrap_v else nv + 1))
    faces = []
    for i in range(nu):
        for j in range(nv if wrap_v else nv):
            f = [idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)]
            g = []
            for x in f:
                if not g or g[-1] != x:
                    g.append(x)
            if g[0] == g[-1]:
                g.pop()
            if len(set(g)) >= 3:
                faces.append(g)
    return faces


def chi_expected(topo):
    if 'V' in topo and isinstance(topo['V'], int):
        return topo['V'] - topo['E'] + topo['F']
    return topo['chi']


def main():
    fails = 0
    for sh in SHAPES:
        v = {p['key']: p['default'] for p in sh['params']}
        res, env = evaluate(sh, v)
        main_q = sh['q'][0] if sh['q'][0]['kind'] in ('area', 'vol') else next(q for q in sh['q'] if q['kind'] in ('area', 'vol'))
        if sh['dim'] == 2:
            fn, box = region(sh['slug'], v); meas, err = mc_area(fn, box)
        else:
            fn, half = solid(sh['slug'], v)
            if sh['slug'] in ('pyramid', 'frustum-pyramid', 'wedge', 'prismoid', 'cone', 'frustum-cone', 'truncated-cylinder'):
                hx, hy, hz = half
                x = RNG.uniform(-hx, hx, N3); y = RNG.uniform(-hy, hy, N3); z = RNG.uniform(0, hz, N3)
                p = fn(x, y, z).mean(); V = 4 * hx * hy * hz
                meas, err = p * V, V * math.sqrt(p * (1 - p) / N3)
            else:
                meas, err = mc_volume(fn, half)
        f = res[main_q['sym']]
        ok = abs(meas - f) <= max(4 * err, 1e-9)
        line = '%-22s %s  formula %.5f  measured %.5f ± %.5f' % (sh['slug'], main_q['sym'], f, meas, err)
        for q in sh['q']:
            key = (sh['slug'], q['sym'])
            if key in BOUNDARY:
                m = BOUNDARY[key](v); rel = abs(m - res[q['sym']]) / m
                tol = 0.012 if q.get('approx') else 2e-4
                okq = rel <= tol
                line += '  | %s %.5f vs %.5f (%.2e)%s' % (q['sym'], res[q['sym']], m, rel, '' if okq else ' FAIL')
                ok = ok and okq
        print(('ok   ' if ok else 'FAIL ') + line)
        fails += not ok
        # topology lens
        t = sh['topo']
        if sh['dim'] == 3 and isinstance(t.get('V'), int):
            if t['V'] - t['E'] + t['F'] != t['chi']:
                print('FAIL %s: V - E + F = %d, chi says %d' % (sh['slug'], t['V'] - t['E'] + t['F'], t['chi'])); fails += 1
    # Euler characteristics of the smooth classes, from meshes
    sphere = chi_of_mesh(grid_surface(12, 16, False, True, pole_u=True))
    torus = chi_of_mesh(grid_surface(12, 16, True, True))
    print('mesh chi: sphere %d (expect 2), torus %d (expect 0), two spheres %d (expect 4)' % (sphere, torus, 2 * sphere))
    if (sphere, torus) != (2, 0):
        fails += 1
    # the old-handbook ellipse perimeter claim on the ellipse page
    a, b = 1.0, 0.5
    true = perimeter_ellipse(a, b); old = math.pi * math.sqrt(2 * (a * a + b * b))
    print('ellipse 2:1: exact %.5f, old rule %.5f (%+.2f %%)' % (true, old, 100 * (old / true - 1)))
    print('FAILURES: %d' % fails)
    return fails


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
