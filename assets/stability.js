/* Ship stability for a prismatic hull (the same cross-section along the whole length), computed from the
   section polygon itself. Pure functions; window.RK_STAB in the page, module.exports in node (tests/check_wave4.js).
   Section coordinates: y across the ship (positive to starboard), z up from the keel, metres.
   Heel θ > 0 puts the starboard side down. A point's height above the still water is then h = −y sinθ + z cosθ − c.
   The righting lever is GZ = (B − G) · (cosθ, sinθ): positive when buoyancy pushes the ship back upright. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RK_STAB = factory();
})(this, function () {
  'use strict';
  var M = Math, D2R = M.PI / 180, RHO_SW = 1.025, RHO_FW = 1.000;   // t/m³

  // ---------------------------------------------------------------- sections (closed polygons, anticlockwise)
  function arc(cx, cz, r, a0, a1, n) { var p = []; for (var i = 0; i <= n; i++) { var a = a0 + (a1 - a0) * i / n; p.push([cx + r * M.cos(a), cz + r * M.sin(a)]); } return p; }
  function box(B, D) { return [[-B / 2, 0], [B / 2, 0], [B / 2, D], [-B / 2, D]]; }
  function bilge(B, D, r) {   // flat bottom, vertical sides, round bilge of radius r
    var p = arc(B / 2 - r, r, r, -M.PI / 2, 0, 24);
    p = p.concat([[B / 2, D], [-B / 2, D]]);
    return p.concat(arc(-B / 2 + r, r, r, M.PI, 1.5 * M.PI, 24));
  }
  function round(B, D, d) {   // lower half of an ellipse (half-breadth B/2, depth d) with vertical sides above it
    var p = [];
    for (var i = 0; i <= 48; i++) { var a = M.PI + M.PI * i / 48; p.push([B / 2 * M.cos(a), d + d * M.sin(a)]); }
    return p.concat([[B / 2, D], [-B / 2, D]]);
  }
  function circle(R, n) { return arc(0, R, R, -M.PI / 2, 1.5 * M.PI, n || 720).slice(0, -1); }
  var HULLS = {
    box: { name: 'Box barge', B: 12, D: 6, T: 3, KG: 4.2, poly: box(12, 6) },
    cargo: { name: 'Cargo ship section', B: 20, D: 12, T: 8, KG: 7.8, poly: bilge(20, 12, 2.5) },
    round: { name: 'Round-bilge workboat', B: 6, D: 3.2, T: 1.5, KG: 1.9, poly: round(6, 3.2, 1.9) }
  };

  // ---------------------------------------------------------------- polygon tools
  function areaCentroid(p) {
    var a = 0, cy = 0, cz = 0;
    for (var i = 0, n = p.length; i < n; i++) {
      var q = p[i], r = p[(i + 1) % n], k = q[0] * r[1] - r[0] * q[1];
      a += k; cy += (q[0] + r[0]) * k; cz += (q[1] + r[1]) * k;
    }
    a /= 2;
    return a ? { A: a, y: cy / (6 * a), z: cz / (6 * a) } : { A: 0, y: 0, z: 0 };
  }
  function clipBelow(p, s, c, th) {   // the part of polygon p with  −y sinθ + z cosθ < c  (Sutherland–Hodgman, one plane)
    var sn = M.sin(th), cs = M.cos(th), out = [];
    function h(q) { return -q[0] * sn + q[1] * cs - c; }
    for (var i = 0, n = p.length; i < n; i++) {
      var a = p[i], b = p[(i + 1) % n], ha = h(a), hb = h(b);
      if (ha <= 0) out.push(a);
      if ((ha < 0 && hb > 0) || (ha > 0 && hb < 0)) { var t = ha / (ha - hb); out.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]); }
    }
    return out;
  }
  function heights(p, th) { var sn = M.sin(th), cs = M.cos(th), lo = Infinity, hi = -Infinity; p.forEach(function (q) { var h = -q[0] * sn + q[1] * cs; if (h < lo) lo = h; if (h > hi) hi = h; }); return [lo, hi]; }

  // the waterline at heel θ that displaces the same area A0 (bisection; area grows monotonically with c)
  function waterline(p, A0, th) {
    var r = heights(p, th), lo = r[0], hi = r[1];
    for (var k = 0; k < 80; k++) { var mid = (lo + hi) / 2; if (areaCentroid(clipBelow(p, 0, mid, th)).A < A0) lo = mid; else hi = mid; }
    var c = (lo + hi) / 2, sub = clipBelow(p, 0, c, th);
    return { c: c, sub: sub, B: areaCentroid(sub) };
  }

  // ---------------------------------------------------------------- upright hydrostatics at draft T
  function widthAt(p, z) {   // waterplane breadth: the span of the section's crossings with the horizontal line z
    var xs = [];
    for (var i = 0, n = p.length; i < n; i++) {
      var a = p[i], b = p[(i + 1) % n];
      if ((a[1] - z) * (b[1] - z) < 0) xs.push(a[0] + (z - a[1]) / (b[1] - a[1]) * (b[0] - a[0]));
      else if (a[1] === z) xs.push(a[0]);
    }
    return xs.length ? M.max.apply(null, xs) - M.min.apply(null, xs) : 0;
  }
  function upright(p, T) {
    var sub = clipBelow(p, 0, T, 0), b = areaCentroid(sub), w = widthAt(p, T), I = w * w * w / 12;
    return { A: b.A, KB: b.z, w: w, I: I, BM: I / b.A, KM: b.z + I / b.A };
  }

  // ---------------------------------------------------------------- the righting-lever curve
  // opts: T draft, KG, Gy (transverse offset of G, + starboard), fsc (free-surface rise of G, m)
  function gz(p, opts, th) {
    var A0 = upright(p, opts.T).A, w = waterline(p, A0, th), KGf = opts.KG + (opts.fsc || 0), Gy = opts.Gy || 0;
    return (w.B.y - Gy) * M.cos(th) + (w.B.z - KGf) * M.sin(th);
  }
  function curve(p, opts, maxDeg, step) {
    maxDeg = maxDeg || 90; step = step || 1;
    var A0 = upright(p, opts.T).A, KGf = opts.KG + (opts.fsc || 0), Gy = opts.Gy || 0, out = [];
    for (var d = 0; d <= maxDeg + 1e-9; d += step) {
      var th = d * D2R, w = waterline(p, A0, th);
      out.push([d, (w.B.y - Gy) * M.cos(th) + (w.B.z - KGf) * M.sin(th)]);
    }
    return out;
  }
  function simpson(f, a, b, n) { n = n || 60; var h = (b - a) / n, s = f(a) + f(b); for (var i = 1; i < n; i++) s += (i % 2 ? 4 : 2) * f(a + i * h); return s * h / 3; }
  function areaUnder(p, opts, d0, d1) {   // ∫ GZ dθ in metre-radians
    var A0 = upright(p, opts.T).A, KGf = opts.KG + (opts.fsc || 0), Gy = opts.Gy || 0;
    return simpson(function (d) { var th = d * D2R, w = waterline(p, A0, th); return (w.B.y - Gy) * M.cos(th) + (w.B.z - KGf) * M.sin(th); }, d0, d1, 40) * D2R;
  }
  // wall-sided formula, exact for a box until the deck edge goes under or the bilge comes out
  function wallSided(GM, BM, th) { return M.sin(th) * (GM + BM / 2 * M.tan(th) * M.tan(th)); }

  // the angle at which a corner point of the section reaches the water
  function edgeAngle(p, opts, pt, submerge) {
    var A0 = upright(p, opts.T).A;
    for (var d = 0; d <= 90; d += 0.25) {
      var th = d * D2R, w = waterline(p, A0, th), h = -pt[0] * M.sin(th) + pt[1] * M.cos(th) - w.c;
      if (submerge ? h <= 0 : h >= 0) return d;
    }
    return null;
  }

  // equilibrium heel when G is off the centreline (or GM < 0): GZ = 0 with GZ rising through zero
  function equilibrium(p, opts) {
    var f = function (d) { return gz(p, opts, d * D2R); };
    var Gy = opts.Gy || 0, dir = Gy > 0 ? 1 : Gy < 0 ? -1 : 0;
    if (f(0.0001) > 0 && f(-0.0001) < 0 && dir === 0) return 0;
    if (!dir) dir = 1;   // unstable upright: loll to starboard by convention
    var prev = 0, fp = f(0);
    for (var d = 0.25 * dir; M.abs(d) <= 89; d += 0.25 * dir) {
      var fd = f(d);
      if ((dir > 0 && fp <= 0 && fd > 0) || (dir < 0 && fp >= 0 && fd < 0)) {
        var a = prev, b = d;
        for (var k = 0; k < 50; k++) { var m = (a + b) / 2; if ((f(m) > 0) === (dir > 0)) b = m; else a = m; }
        return (a + b) / 2;
      }
      prev = d; fp = fd;
    }
    return null;   // capsizes
  }

  // IMO 2008 Intact Stability Code, Part A, 2.2 (general criteria for cargo and passenger ships)
  function criteria(p, opts, curvePts) {
    var max = curvePts.reduce(function (m, q) { return q[1] > m[1] ? q : m; }, [0, -Infinity]);
    var gz30 = curvePts.filter(function (q) { return q[0] >= 30; }).reduce(function (m, q) { return M.max(m, q[1]); }, -Infinity);
    var u = upright(p, opts.T), GM = u.KM - opts.KG - (opts.fsc || 0);
    var a30 = areaUnder(p, opts, 0, 30), a40 = areaUnder(p, opts, 0, 40), a3040 = a40 - a30;
    return [
      ['Area under GZ, 0° to 30°', a30, 0.055, 'm·rad'],
      ['Area under GZ, 0° to 40°', a40, 0.09, 'm·rad'],
      ['Area under GZ, 30° to 40°', a3040, 0.03, 'm·rad'],
      ['GZ at 30° or more', gz30, 0.20, 'm'],
      ['Angle of maximum GZ', max[0], 25, '°'],
      ['Initial GM (corrected for free surface)', GM, 0.15, 'm']
    ].map(function (r) { return { name: r[0], value: r[1], min: r[2], unit: r[3], ok: r[1] >= r[2] }; });
  }

  // free-surface correction for a rectangular slack tank: rise of G = (ρ_tank/ρ_sea) · i / V,  i = l b³ / 12
  function freeSurface(bTank, lengthFraction, rhoTank, A0) { return (rhoTank / RHO_SW) * lengthFraction * bTank * bTank * bTank / 12 / A0; }

  // ---------------------------------------------------------------- displacement and load lines
  function hydro(L, B, T, Cb, Cw, rho) {
    rho = rho || RHO_SW;
    var V = L * B * T * Cb, disp = rho * V, Aw = L * B * Cw, tpc = rho * Aw / 100;
    return { V: V, disp: disp, Aw: Aw, tpc: tpc, fwa: disp / (40 * tpc) /* cm, ICLL 1966 reg. 40(7) */ };
  }
  // dock-water allowance: proportional to (1.025 − ρ), ICLL 1966 art. 12
  function dwa(fwaCm, rho) { return fwaCm * (RHO_SW - rho) / (RHO_SW - RHO_FW); }

  return { HULLS: HULLS, box: box, bilge: bilge, round: round, circle: circle, areaCentroid: areaCentroid, clipBelow: clipBelow,
    waterline: waterline, widthAt: widthAt, upright: upright, gz: gz, curve: curve, areaUnder: areaUnder, wallSided: wallSided,
    edgeAngle: edgeAngle, equilibrium: equilibrium, criteria: criteria, freeSurface: freeSurface, hydro: hydro, dwa: dwa,
    RHO_SW: RHO_SW, RHO_FW: RHO_FW, D2R: D2R };
});
