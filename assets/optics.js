/* Geometrical optics in a plane: exact ray tracing through glass shapes, mirrors and an ideal thin lens.
   Pure functions; window.RK_OPTICS in the page, module.exports in node (tests/check_wave5.js).
   Units: millimetres for lengths, nanometres for wavelengths, radians inside, degrees only in helpers named *Deg.
   Every refraction uses Snell's law at the real surface (no small-angle shortcut); every refraction also
   splits off a reflected ray with the Fresnel reflectance for unpolarised light; past the critical angle the
   light is totally reflected. The surrounding medium is air. Every index here is relative to air, as glass
   catalogues give it, so taking air as n = 1 is exact. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RK_OPTICS = factory();
})(this, function () {
  'use strict';
  var M = Math, D2R = M.PI / 180, EPS = 1e-7;

  // ---------------------------------------------------------------- materials: Sellmeier dispersion formulas
  // n² − 1 = Σ B λ² / (λ² − C), λ in micrometres. Coefficients as published (sources in data/sources.py: key).
  // Glass catalogues give the index relative to air, which is what the tracer needs (air is n = 1 here). The water
  // formula gives the absolute index (against vacuum), so it is divided by the index of air (vac: true).
  var MATERIALS = {
    water: { name: 'Water (20 °C)', src: 'daimon2007', vac: true,
      B: [5.684027565e-1, 1.726177391e-1, 2.086189578e-2, 1.130748688e-1], C: [5.101829712e-3, 1.821153936e-2, 2.620722293e-2, 1.069792721e1] },
    silica: { name: 'Fused silica', src: 'malitson1965',
      B: [0.6961663, 0.4079426, 0.8974794], C: [0.0684043 * 0.0684043, 0.1162414 * 0.1162414, 9.896161 * 9.896161] },
    bk7: { name: 'Crown glass (N-BK7)', src: 'schott',
      B: [1.03961212, 0.231792344, 1.01046945], C: [0.00600069867, 0.0200179144, 103.560653] },
    f2: { name: 'Flint glass (N-F2)', src: 'schott',
      B: [1.39757037, 0.159201403, 1.2686543], C: [0.00995906143, 0.0546931752, 119.248346] },
    diamond: { name: 'Diamond', src: 'peter1923',
      B: [0.3306, 4.3356], C: [0.175 * 0.175, 0.106 * 0.106] }
  };
  function index(mat, lam) {
    if (typeof mat === 'number') return mat;
    var m = MATERIALS[mat], l2 = (lam / 1000) * (lam / 1000), s = 1;
    for (var i = 0; i < m.B.length; i++) s += m.B[i] * l2 / (l2 - m.C[i]);
    return m.vac ? M.sqrt(s) / airIndex(lam) : M.sqrt(s);
  }
  function airIndex(lam) {   // dry air, Peck & Reeder 1972 (15 °C, 101 325 Pa), n − 1 scaled by density to 20 °C like the glass and water data
    var s2 = 1 / ((lam / 1000) * (lam / 1000));
    return 1 + 1e-8 * (8060.51 + 2480990 / (132.274 - s2) + 17455.7 / (39.32957 - s2)) * 288.15 / 293.15;
  }
  // Fraunhofer lines used to describe dispersion (nm)
  var LINES = { F: 486.1327, d: 587.5618, D: 589.29, C: 656.2725 };
  function abbe(mat) { return (index(mat, LINES.d) - 1) / (index(mat, LINES.F) - index(mat, LINES.C)); }

  // ---------------------------------------------------------------- one surface
  // d: unit direction, N: unit normal facing the incoming ray (d·N < 0).
  function refractDir(d, N, n1, n2) {
    var ci = -(d[0] * N[0] + d[1] * N[1]), eta = n1 / n2, k = 1 - eta * eta * (1 - ci * ci);
    if (k < 0) return null;   // total internal reflection
    var a = eta * ci - M.sqrt(k);
    return [eta * d[0] + a * N[0], eta * d[1] + a * N[1]];
  }
  function reflectDir(d, N) {
    var ci = -(d[0] * N[0] + d[1] * N[1]);
    return [d[0] + 2 * ci * N[0], d[1] + 2 * ci * N[1]];
  }
  // Fresnel reflectance; returns {s, p, R} (R = unpolarised mean), cosines of the angles of incidence and transmission
  function fresnel(n1, n2, ci, ct) {
    var rs = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct), rp = (n1 * ct - n2 * ci) / (n1 * ct + n2 * ci);
    return { s: rs * rs, p: rp * rp, R: (rs * rs + rp * rp) / 2 };
  }
  function criticalDeg(n1, n2) { return n1 > n2 ? M.asin(n2 / n1) / D2R : null; }
  function brewsterDeg(n1, n2) { return M.atan(n2 / n1) / D2R; }

  // ---------------------------------------------------------------- shapes (local frame; optical axis = +x)
  // Primitives: seg {a, b, n (outward normal)}; arc {c, r, s (+1: outward = (p − c)/r), side (−1: x ≤ cx, +1: x ≥ cx, 0: any), y0, y1};
  // par {f, h}: the parabola x = −y²/(4f), |y| ≤ h/2 (focus at (−f, 0)); thin {h, f}: ideal lens on x = 0.
  function seg(a, b, n) { return { t: 'seg', a: a, b: b, n: n }; }
  function poly(v) {   // vertices anticlockwise
    var out = [];
    for (var i = 0; i < v.length; i++) {
      var a = v[i], b = v[(i + 1) % v.length], dx = b[0] - a[0], dy = b[1] - a[1], L = M.hypot(dx, dy);
      out.push(seg(a, b, [dy / L, -dx / L]));
    }
    return out;
  }
  function sagX(vx, R, y) {   // x of a spherical surface with vertex vx and signed radius R (R > 0: centre to the right) at height y
    if (!isFinite(R)) return vx;
    return vx + R - (R > 0 ? 1 : -1) * M.sqrt(R * R - y * y);
  }
  // A lens: signed radii R1 (first surface), R2 (second), centre thickness tc, diameter D. Returns null if the shape is impossible.
  function lensPrims(R1, R2, tc, D) {
    var h = D / 2, xf = -tc / 2, xb = tc / 2;
    if ((isFinite(R1) && M.abs(R1) < h) || (isFinite(R2) && M.abs(R2) < h)) return null;
    var ef = sagX(xf, R1, h), eb = sagX(xb, R2, h);
    if (eb - ef < 0.2) return null;   // edges must not cross (0.2 mm minimum edge)
    var p = [];
    p.push(isFinite(R1) ? { t: 'arc', c: [xf + R1, 0], r: M.abs(R1), s: R1 > 0 ? 1 : -1, side: R1 > 0 ? -1 : 1, y0: -h, y1: h } : seg([xf, -h], [xf, h], [-1, 0]));
    p.push(isFinite(R2) ? { t: 'arc', c: [xb + R2, 0], r: M.abs(R2), s: R2 > 0 ? -1 : 1, side: R2 > 0 ? -1 : 1, y0: -h, y1: h } : seg([xb, -h], [xb, h], [1, 0]));
    p.push(seg([eb, h], [ef, h], [0, 1]), seg([ef, -h], [eb, -h], [0, -1]));
    return p;
  }
  function minThickness(R1, R2, D) {   // smallest centre thickness that leaves a 1 mm edge
    var h = D / 2, a = isFinite(R1) ? sagX(0, R1, h) : 0, b = isFinite(R2) ? sagX(0, R2, h) : 0;
    return M.max(1, 1 + a - b);
  }
  function build(o) {
    var p, h;
    switch (o.kind) {
      case 'lens': p = lensPrims(o.R1, o.R2, o.tc, o.D); return p && { prims: p, region: true };
      case 'prism': {   // isosceles prism, apex angle A at the top, equal faces L; centred on its centroid
        var A = o.A * D2R, L = o.L, H = L * M.cos(A / 2), w = L * M.sin(A / 2), c = H / 3;
        return { prims: poly([[-w, -c], [w, -c], [0, H - c]]), region: true };
      }
      case 'slab': return { prims: poly([[-o.w / 2, -o.h / 2], [o.w / 2, -o.h / 2], [o.w / 2, o.h / 2], [-o.w / 2, o.h / 2]]), region: true };
      case 'half':   // half-cylinder: flat face on x = 0 facing −x, round side to the right
        return { prims: [{ t: 'arc', c: [0, 0], r: o.r, s: 1, side: 1, y0: -o.r, y1: o.r }, seg([0, -o.r], [0, o.r], [-1, 0])], region: true };
      case 'drop': return { prims: [{ t: 'arc', c: [0, 0], r: o.r, s: 1, side: 0, y0: null, y1: null }], region: true };
      case 'mirror': h = o.D / 2;   // reflecting curves, concave side towards −x
        if (o.shape === 'plane') return { prims: [seg([0, -h], [0, h], [-1, 0])], mirror: true };
        if (o.shape === 'parabolic') return { prims: [{ t: 'par', f: o.f, h: o.D }], mirror: true };
        if (o.shape === 'convex') return { prims: [{ t: 'arc', c: [o.R, 0], r: o.R, s: -1, side: -1, y0: -h, y1: h }], mirror: true };
        return { prims: [{ t: 'arc', c: [-o.R, 0], r: o.R, s: 1, side: 1, y0: -h, y1: h }], mirror: true };
      case 'thin': return { prims: [{ t: 'thin', h: o.D, f: o.f }], thin: true };
    }
    return null;
  }

  // ---------------------------------------------------------------- intersections (local frame)
  function hitSeg(q, p, d) {
    var ex = q.b[0] - q.a[0], ey = q.b[1] - q.a[1], den = d[0] * ey - d[1] * ex;
    if (M.abs(den) < 1e-14) return null;
    var ax = q.a[0] - p[0], ay = q.a[1] - p[1], t = (ax * ey - ay * ex) / den, u = (ax * d[1] - ay * d[0]) / den;
    if (t > EPS && u >= -1e-12 && u <= 1 + 1e-12) return { t: t, n: q.n };
    return null;
  }
  function hitArc(q, p, d) {
    var ox = p[0] - q.c[0], oy = p[1] - q.c[1], b = ox * d[0] + oy * d[1], c = ox * ox + oy * oy - q.r * q.r, disc = b * b - c;
    if (disc < 0) return null;
    var sq = M.sqrt(disc), ts = [-b - sq, -b + sq];
    for (var i = 0; i < 2; i++) {
      var t = ts[i];
      if (t <= EPS) continue;
      var x = p[0] + t * d[0], y = p[1] + t * d[1];
      if (q.side < 0 && x > q.c[0] + 1e-9) continue;
      if (q.side > 0 && x < q.c[0] - 1e-9) continue;
      if (q.y0 !== null && (y < q.y0 - 1e-9 || y > q.y1 + 1e-9)) continue;
      return { t: t, n: [q.s * (x - q.c[0]) / q.r, q.s * (y - q.c[1]) / q.r] };
    }
    return null;
  }
  function hitPar(q, p, d) {   // x + y²/(4f) = 0
    var k = 1 / (4 * q.f), A = k * d[1] * d[1], B = d[0] + 2 * k * p[1] * d[1], C = p[0] + k * p[1] * p[1], ts;
    if (M.abs(A) < 1e-14) ts = [-C / B];
    else { var disc = B * B - 4 * A * C; if (disc < 0) return null; var s = M.sqrt(disc); ts = [(-B - s) / (2 * A), (-B + s) / (2 * A)].sort(function (a, b) { return a - b; }); }
    for (var i = 0; i < ts.length; i++) {
      var t = ts[i]; if (!(t > EPS)) continue;
      var y = p[1] + t * d[1];
      if (M.abs(y) > q.h / 2 + 1e-9) continue;
      var nx = 1, ny = y / (2 * q.f), L = M.hypot(nx, ny);
      return { t: t, n: [nx / L, ny / L] };
    }
    return null;
  }
  function hitThin(q, p, d) {
    if (M.abs(d[0]) < 1e-14) return null;
    var t = -p[0] / d[0], y = p[1] + t * d[1];
    if (t > EPS && M.abs(y) <= q.h / 2) return { t: t, n: [d[0] > 0 ? -1 : 1, 0], y: y };
    return null;
  }
  var HIT = { seg: hitSeg, arc: hitArc, par: hitPar, thin: hitThin };

  // ---------------------------------------------------------------- scene and tracing
  // scene: array of objects {kind, x, y, rot (deg), mat, ...}; each gets ._g = build(o) (call prepare after edits).
  function prepare(scene) { scene.forEach(function (o) { o._g = build(o); }); return scene; }
  function nearest(scene, p, d) {
    var best = null;
    for (var k = 0; k < scene.length; k++) {
      var o = scene[k]; if (!o._g) continue;
      var a = -(o.rot || 0) * D2R, ca = M.cos(a), sa = M.sin(a);
      var px = p[0] - o.x, py = p[1] - o.y;
      var lp = [ca * px - sa * py, sa * px + ca * py], ld = [ca * d[0] - sa * d[1], sa * d[0] + ca * d[1]];
      for (var j = 0; j < o._g.prims.length; j++) {
        var q = o._g.prims[j], h = HIT[q.t](q, lp, ld);
        if (h && (!best || h.t < best.t)) {
          var cb = M.cos(-a), sb = M.sin(-a);
          best = { t: h.t, o: o, prim: q, n: [cb * h.n[0] - sb * h.n[1], sb * h.n[0] + cb * h.n[1]], ly: h.y, ld: ld, rot: -a };
        }
      }
    }
    return best;
  }
  function exitBox(p, d, box) {   // distance to leave the drawing box
    var t = Infinity;
    if (d[0] > 0) t = M.min(t, (box[2] - p[0]) / d[0]); else if (d[0] < 0) t = M.min(t, (box[0] - p[0]) / d[0]);
    if (d[1] > 0) t = M.min(t, (box[3] - p[1]) / d[1]); else if (d[1] < 0) t = M.min(t, (box[1] - p[1]) / d[1]);
    return M.max(t, 0);
  }
  /* trace one ray. ray: {x, y, dx, dy, lam, I}. opt: {box [x0, y0, x1, y1], minI (default 0.02), maxDepth (60)}.
     Returns {segs: [{x0, y0, x1, y1, I, lam, n, main, k (internal reflections so far; mirror bounces count too)}], events: [...]} — events describe each surface met by the main ray
     (the transmitted path; after total internal reflection, the reflected one). */
  function trace(scene, ray, opt) {
    opt = opt || {};
    var box = opt.box || [-1e4, -1e4, 1e4, 1e4], minI = opt.minI === undefined ? 0.02 : opt.minI, maxDepth = opt.maxDepth || 60;
    var L = M.hypot(ray.dx, ray.dy), segs = [], events = [];
    var stack = [{ p: [ray.x, ray.y], d: [ray.dx / L, ray.dy / L], I: ray.I === undefined ? 1 : ray.I, inside: null, depth: 0, main: true, k: 0 }];
    while (stack.length) {
      var r = stack.pop(), lam = ray.lam;
      var nIn = r.inside ? index(r.inside.mat, lam) : 1;
      var h = r.depth < maxDepth ? nearest(scene, r.p, r.d) : null;
      if (!h) {
        var te = exitBox(r.p, r.d, box);
        segs.push({ x0: r.p[0], y0: r.p[1], x1: r.p[0] + te * r.d[0], y1: r.p[1] + te * r.d[1], I: r.I, lam: lam, n: nIn, main: r.main, k: r.k, end: true });
        continue;
      }
      var q = [r.p[0] + h.t * r.d[0], r.p[1] + h.t * r.d[1]];
      segs.push({ x0: r.p[0], y0: r.p[1], x1: q[0], y1: q[1], I: r.I, lam: lam, n: nIn, main: r.main, k: r.k });
      var g = h.o._g, N = h.n, dn = r.d[0] * N[0] + r.d[1] * N[1];
      if (g.mirror) {
        if (dn > 0) N = [-N[0], -N[1]];
        var rd = reflectDir(r.d, N);
        if (r.main) events.push({ type: 'mirror', x: q[0], y: q[1], th: M.acos(M.min(1, M.abs(dn))) / D2R, o: h.o });
        stack.push({ p: q, d: rd, I: r.I, inside: null, depth: r.depth + 1, main: r.main, k: r.k + 1 });
        continue;
      }
      if (g.thin) {   // ideal lens: slope (dy/|dx|, local frame) drops by y/f — every ray from one point meets again at one point
        var ld = h.ld, sx = ld[0] > 0 ? 1 : -1, u = ld[1] / M.abs(ld[0]) - h.ly / h.o.f, Lu = M.hypot(1, u);
        var nl = [sx / Lu, u / Lu], cb = M.cos(h.rot), sb = M.sin(h.rot);
        if (r.main) events.push({ type: 'thin', x: q[0], y: q[1], o: h.o });
        stack.push({ p: q, d: [cb * nl[0] - sb * nl[1], sb * nl[0] + cb * nl[1]], I: r.I, inside: null, depth: r.depth + 1, main: r.main, k: r.k });
        continue;
      }
      var entering = dn < 0, n1, n2, inside2;
      if (entering) { n1 = 1; n2 = index(h.o.mat, lam); inside2 = h.o; }
      else { n1 = index(h.o.mat, lam); n2 = 1; inside2 = null; N = [-N[0], -N[1]]; }
      var ci = -(r.d[0] * N[0] + r.d[1] * N[1]), td = refractDir(r.d, N, n1, n2), rdir = reflectDir(r.d, N);
      var thI = M.acos(M.min(1, ci)) / D2R;
      if (!td) {
        if (r.main) events.push({ type: 'tir', x: q[0], y: q[1], thI: thI, n1: n1, n2: n2, R: 1, o: h.o });
        stack.push({ p: q, d: rdir, I: r.I, inside: entering ? null : h.o, depth: r.depth + 1, main: r.main, k: r.k + (entering ? 0 : 1) });
        continue;
      }
      var ct = -(td[0] * N[0] + td[1] * N[1]), F = fresnel(n1, n2, ci, ct);
      if (r.main) events.push({ type: 'refract', x: q[0], y: q[1], thI: thI, thT: M.acos(M.min(1, ct)) / D2R, n1: n1, n2: n2, R: F.R, Rs: F.s, Rp: F.p, entering: entering, o: h.o });
      if (r.I * F.R >= minI) stack.push({ p: q, d: rdir, I: r.I * F.R, inside: entering ? null : h.o, depth: r.depth + 1, main: false, k: r.k + (entering ? 0 : 1) });
      stack.push({ p: q, d: td, I: r.I * (1 - F.R), inside: inside2, depth: r.depth + 1, main: r.main, k: r.k });
    }
    return { segs: segs, events: events };
  }
  // the main ray's final direction and where it ends (for measurements)
  function finalRay(res) {
    var m = res.segs.filter(function (s) { return s.main; }), s = m[m.length - 1], L = M.hypot(s.x1 - s.x0, s.y1 - s.y0);
    return { x: s.x0, y: s.y0, dx: (s.x1 - s.x0) / L, dy: (s.y1 - s.y0) / L };
  }
  function axisCrossing(fr) { return M.abs(fr.dy) < 1e-15 ? Infinity : fr.x - fr.y * fr.dx / fr.dy; }   // x where the ray meets y = 0

  // ---------------------------------------------------------------- closed forms (shown on the pages; checked against the tracer)
  function thickLens(n, R1, R2, tc) {   // power, focal length, back focal distance (measured from the second vertex)
    var c1 = isFinite(R1) ? 1 / R1 : 0, c2 = isFinite(R2) ? 1 / R2 : 0;
    var P = (n - 1) * (c1 - c2 + (n - 1) * tc * c1 * c2 / n), f = 1 / P;
    return { P: P, f: f, bfd: f * (1 - (n - 1) * tc * c1 / n) };
  }
  function prismDeviation(Adeg, n, ideg) {   // deviation (deg), or null if the ray is totally reflected at the second face
    var A = Adeg * D2R, i = ideg * D2R, r1 = M.asin(M.sin(i) / n), r2 = A - r1, s = n * M.sin(r2);
    if (M.abs(s) > 1) return null;
    return (i + M.asin(s) - A) / D2R;
  }
  function prismMin(Adeg, n) {   // minimum deviation and the angle of incidence that gives it (symmetric passage)
    var A = Adeg * D2R, s = n * M.sin(A / 2);
    if (s >= 1) return null;
    return { D: (2 * M.asin(s) - A) / D2R, i: M.asin(s) / D2R };
  }
  function nFromMinDev(Adeg, Ddeg) { return M.sin((Adeg + Ddeg) * D2R / 2) / M.sin(Adeg * D2R / 2); }
  function dropDeviation(n, b, k) {   // total turn (deg) of a ray with impact parameter b (0..1) after k internal reflections
    var i = M.asin(b), r = M.asin(b / n);
    return (2 * (i - r) + k * (M.PI - 2 * r)) / D2R;
  }
  function rainbowDeg(n, k) {   // Descartes: the turn is least where cos² i = (n² − 1)/(k² + 2k); bow radius from the antisolar point
    var ci = M.sqrt((n * n - 1) / (k * k + 2 * k)), b = M.sqrt(1 - ci * ci), D = dropDeviation(n, b, k);
    return { b: b, iDeg: M.acos(ci) / D2R, D: D, angle: k % 2 ? 180 - D : D - 180 };
  }

  // ---------------------------------------------------------------- colour of a wavelength (an approximation of the spectrum on screen)
  function rgb(lam) {
    var r = 0, g = 0, b = 0, f;
    if (lam < 440) { r = -(lam - 440) / 60; b = 1; } else if (lam < 490) { g = (lam - 440) / 50; b = 1; }
    else if (lam < 510) { g = 1; b = -(lam - 510) / 20; } else if (lam < 580) { r = (lam - 510) / 70; g = 1; }
    else if (lam < 645) { r = 1; g = -(lam - 645) / 65; } else r = 1;
    f = lam < 420 ? 0.3 + 0.7 * (lam - 380) / 40 : lam > 700 ? 0.3 + 0.7 * (780 - lam) / 80 : 1;
    return [M.round(255 * M.pow(r * f, 0.8)), M.round(255 * M.pow(g * f, 0.8)), M.round(255 * M.pow(b * f, 0.8))];
  }
  var WHITE = [405, 430, 455, 480, 505, 530, 555, 580, 605, 630, 655, 680];   // wavelengths traced for "white" light

  return { MATERIALS: MATERIALS, LINES: LINES, index: index, airIndex: airIndex, abbe: abbe, refractDir: refractDir, reflectDir: reflectDir, fresnel: fresnel,
    criticalDeg: criticalDeg, brewsterDeg: brewsterDeg, lensPrims: lensPrims, minThickness: minThickness, build: build, prepare: prepare,
    trace: trace, finalRay: finalRay, axisCrossing: axisCrossing, thickLens: thickLens, prismDeviation: prismDeviation, prismMin: prismMin,
    nFromMinDev: nFromMinDev, dropDeviation: dropDeviation, rainbowDeg: rainbowDeg, rgb: rgb, WHITE: WHITE, D2R: D2R, sagX: sagX };
});
