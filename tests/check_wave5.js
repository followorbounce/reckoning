/* Wave 5 checks of the code the Light pages run (assets/optics.js).
   Reference values are typed here from the published tables (glass catalogue, Malitson 1965, IAPWS 1997 for water,
   diamond), and traced results are compared with closed forms written out in this file (Snell, Fresnel, prism and
   drop deviation, mirror crossings) or with an independent paraxial (ABCD matrix) calculation. The page's own closed
   forms (prismDeviation, rainbowDeg, thickLens…) are checked against those, not against each other. Exit 1 on any failure. */
'use strict';
var path = require('path'), M = Math;
var O = require(path.join(__dirname, '..', 'assets', 'optics.js'));
var fails = 0, n = 0, notes = [];
function ok(c, msg) { n++; if (!c) { fails++; console.log('FAIL ' + msg); } }
function near(a, b, tol, msg) { ok(M.abs(a - b) <= tol, msg + ': got ' + a + ', expected ' + b + ' ± ' + tol); }
var R = M.PI / 180;
function dirDeg(fr) { return M.atan2(fr.dy, fr.dx) / R; }
// closed forms written out here, independently of assets/optics.js
function devPrism(Adeg, nn, ideg) { var i = ideg * R, r1 = M.asin(M.sin(i) / nn), s = nn * M.sin(Adeg * R - r1); return M.abs(s) > 1 ? null : (i + M.asin(s)) / R - Adeg; }
function devDrop(nn, b, k) { var i = M.asin(b), r = M.asin(b / nn); return (2 * (i - r) + k * (M.PI - 2 * r)) / R; }

// ---------------------------------------------------------------- materials vs published indices
// glass catalogue (n_d at 587.56 nm, n_F, n_C, Abbe number v_d); Malitson 1965 for fused silica; water 20 °C; diamond.
near(O.index('bk7', 587.5618), 1.51680, 2e-5, 'N-BK7 n_d');
near(O.index('bk7', 486.1327), 1.52238, 2e-5, 'N-BK7 n_F');
near(O.index('bk7', 656.2725), 1.51432, 2e-5, 'N-BK7 n_C');
near(O.abbe('bk7'), 64.17, 0.03, 'N-BK7 Abbe number');
near(O.index('f2', 587.5618), 1.62005, 2e-5, 'N-F2 n_d');
near(O.abbe('f2'), 36.43, 0.03, 'N-F2 Abbe number');
near(O.index('silica', 587.5618), 1.45846, 5e-5, 'fused silica n_d');
near(O.abbe('silica'), 67.8, 0.2, 'fused silica Abbe number');
near(O.index('water', 589.29), 1.33299, 5e-5, 'water n_D at 20 °C relative to air (IAPWS 1.33335 / air 1.00027)');
near(O.airIndex(589.29), 1.000272, 3e-6, 'air at 20 °C: n − 1 = 2.72e-4 at the sodium D line');
(function () {   // the water formula against the IAPWS 1997 formulation (absolute index), 20 °C, 998.2071 kg/m³
  var a = [0.244257733, 9.74634476e-3, -3.73234996e-3, 2.68678472e-4, 1.58920570e-3, 2.45934259e-3, 0.900704920, -1.66626219e-2];
  function iapws(lam, T, rho) {
    var Tb = T / 273.15, rb = rho / 1000, lb = lam / 589, A = rb * (a[0] + a[1] * rb + a[2] * Tb + a[3] * lb * lb * Tb + a[4] / (lb * lb) +
      a[5] / (lb * lb - 0.2292020 * 0.2292020) + a[6] / (lb * lb - 5.432937 * 5.432937) + a[7] * rb * rb);
    return M.sqrt((2 * A + 1) / (1 - A));
  }
  [404.7, 486.1, 589.29, 656.3, 706.5].forEach(function (l) {
    near(O.index('water', l) * O.airIndex(l), iapws(l, 293.15, 998.2071), 3e-5, 'water at ' + l + ' nm: Sellmeier formula = IAPWS 1997');
  });
})();
near(O.index('diamond', 589.29), 2.4175, 1.5e-3, 'diamond n_D');
['bk7', 'f2', 'silica', 'water', 'diamond'].forEach(function (m) {
  ok(O.index(m, 400) > O.index(m, 550) && O.index(m, 550) > O.index(m, 700), m + ': normal dispersion (blue bends more)');
});

// ---------------------------------------------------------------- one surface
var nG = 1.5168;
near(O.fresnel(1, nG, 1, 1).R, M.pow((nG - 1) / (nG + 1), 2), 1e-15, 'Fresnel at normal incidence = ((n−1)/(n+1))²');
(function () {   // textbook values for n = 1.5 at 45°: R_s = 0.0920, R_p = 0.0085; and the tracer's event carries them
  var ct = M.cos(M.asin(M.sin(45 * R) / 1.5)), f = O.fresnel(1, 1.5, M.cos(45 * R), ct);
  near(f.s, 0.0920, 5e-5, 'Fresnel R_s, n = 1.5 at 45°'); near(f.p, 0.0085, 5e-5, 'Fresnel R_p, n = 1.5 at 45°');
  var sc = O.prepare([{ kind: 'slab', x: 0, y: 0, rot: 0, w: 20, h: 200, mat: 1.5 }]);
  var ev = O.trace(sc, { x: -50, y: 50, dx: M.cos(-45 * R), dy: M.sin(-45 * R), lam: 550 }).events[0];
  near(ev.R, (0.0920 + 0.0085) / 2, 1e-4, 'tracer: reflected share at 45° = (R_s + R_p)/2');
})();
(function () {
  var tb = M.atan(nG), ct = M.cos(M.asin(M.sin(tb) / nG)), f = O.fresnel(1, nG, M.cos(tb), ct);
  near(f.p, 0, 1e-15, 'no p-reflection at Brewster’s angle');
  near(O.brewsterDeg(1, nG), 56.60, 0.01, 'Brewster angle for n = 1.5168');
  near(tb + M.asin(M.sin(tb) / nG), M.PI / 2, 1e-12, 'at Brewster’s angle reflected and refracted rays are perpendicular');
  var g = O.fresnel(1, nG, M.cos(89.999 * R), M.cos(M.asin(M.sin(89.999 * R) / nG)));
  ok(g.R > 0.999, 'grazing incidence reflects almost everything');
})();
near(O.criticalDeg(nG, 1), M.asin(1 / nG) / R, 1e-12, 'critical angle = asin(1/n)');
near(O.criticalDeg(1.3330, 1), 48.61, 0.01, 'critical angle of water ≈ 48.6°');

// ---------------------------------------------------------------- tracer: slab (Snell, parallel exit, lateral shift)
(function () {
  var t = 20, sc = O.prepare([{ kind: 'slab', x: 0, y: 0, rot: 0, w: t, h: 200, mat: 'bk7' }]);
  [10, 30, 50, 70].forEach(function (a) {
    var res = O.trace(sc, { x: -50, y: -50 * M.tan(a * R), dx: M.cos(a * R), dy: M.sin(a * R), lam: 587.5618 }, { box: [-100, -200, 100, 200] });
    var e = res.events[0], nn = O.index('bk7', 587.5618);
    near(e.thI, a, 1e-9, 'slab: angle of incidence ' + a);
    near(M.sin(e.thT * R) * nn, M.sin(a * R), 1e-12, 'slab: n1 sin θ1 = n2 sin θ2 at ' + a + '°');
    var fr = O.finalRay(res);
    near(dirDeg(fr), a, 1e-9, 'slab: ray leaves parallel to how it came at ' + a + '°');
    var tr = M.asin(M.sin(a * R) / nn), shift = t * M.sin(a * R - tr) / M.cos(tr);
    var perp = M.abs((fr.x - 0) * M.sin(a * R) - (fr.y - 0) * M.cos(a * R));   // distance of the exit line from the entry line through the origin
    near(perp, shift, 1e-9, 'slab: lateral shift t sin(θ − θ′)/cos θ′ at ' + a + '°');
  });
})();

// ---------------------------------------------------------------- half-cylinder: total internal reflection
(function () {
  var nn = O.index('bk7', 587.5618), crit = M.asin(1 / nn) / R;
  var sc = O.prepare([{ kind: 'half', x: 0, y: 0, rot: 0, r: 60, mat: 'bk7' }]);
  function fromInside(a) {   // a ray aimed at the centre from outside the round side: it enters normally, meets the flat face at a
    var dx = -M.cos(a * R), dy = M.sin(a * R);
    return O.trace(sc, { x: -100 * dx, y: -100 * dy, dx: dx, dy: dy, lam: 587.5618 }, { box: [-200, -200, 200, 200] });
  }
  var r1 = fromInside(crit - 0.5), r2 = fromInside(crit + 0.5);
  near(r1.events[0].thI, 0, 1e-6, 'half-cylinder: enters the round face along the normal');
  ok(r1.events[1].type === 'refract', 'half-cylinder: just below the critical angle the ray gets out');
  ok(r1.events[1].thT > 80, 'half-cylinder: and leaves close to grazing (' + r1.events[1].thT.toFixed(2) + '°)');
  ok(r2.events[1].type === 'tir', 'half-cylinder: just above the critical angle it is totally reflected');
  near(r2.events[1].thI, crit + 0.5, 1e-6, 'half-cylinder: angle at the flat face = aim angle');
})();

// ---------------------------------------------------------------- prism: deviation, minimum deviation
(function () {
  var A = 60, lam = 587.5618, nn = O.index('bk7', lam);
  function traced(i) {   // incidence angle i on the left face; prism apex up, left face normal points to 150° (A = 60)
    var sc = O.prepare([{ kind: 'prism', x: 0, y: 0, rot: 0, A: A, L: 60, mat: 'bk7' }]);
    var g = sc[0]._g.prims[2];   // the left face (apex to lower-left corner); its outward normal points up and to the left
    var c = [(g.a[0] + g.b[0]) / 2, (g.a[1] + g.b[1]) / 2];
    var na = M.atan2(g.n[1], g.n[0]), da = na + M.PI + i * R;   // into the face, turned by i towards the apex side, so it bends towards the base
    var d = [M.cos(da), M.sin(da)];
    var res = O.trace(sc, { x: c[0] - 80 * d[0], y: c[1] - 80 * d[1], dx: d[0], dy: d[1], lam: lam }, { box: [-300, -300, 300, 300] });
    var fr = O.finalRay(res), dev = M.acos(M.max(-1, M.min(1, fr.dx * d[0] + fr.dy * d[1]))) / R;
    return { dev: dev, ev: res.events };
  }
  [40, 50, 60, 70].forEach(function (i) {
    var t = traced(i);
    near(t.ev[0].thI, i, 1e-9, 'prism: angle of incidence ' + i);
    near(t.dev, devPrism(A, nn, i), 1e-8, 'prism: traced deviation = i + e − A at i = ' + i + '°');
    near(O.prismDeviation(A, nn, i), devPrism(A, nn, i), 1e-10, 'prism: page formula = written-out formula at i = ' + i + '°');
  });
  var best = 1e9, bestI = 0;
  for (var i = 30; i <= 80; i += 0.01) { var d = devPrism(A, nn, i); if (d !== null && d < best) { best = d; bestI = i; } }
  var mn = O.prismMin(A, nn);
  near(best, mn.D, 1e-6, 'prism: scanned minimum deviation = 2 asin(n sin A/2) − A');
  near(bestI, mn.i, 0.02, 'prism: minimum at symmetric passage');
  near(O.nFromMinDev(A, mn.D), nn, 1e-12, 'prism: n = sin((A + D)/2)/sin(A/2)');
  near(mn.D, 38.65, 0.05, 'N-BK7 60° prism: minimum deviation ≈ 38.6° (from n_d = 1.5168)');
  ok(O.prismDeviation(A, nn, 20) === null, 'prism: at 20° the ray is totally reflected at the second face');
})();

// ---------------------------------------------------------------- lenses: paraxial focus vs thick-lens formula and ABCD matrices
function abcdBfd(n, R1, R2, t) {   // independent: refraction (1, 0; −(n2−n1)/(n2 R), n1/n2) in (y, angle) form, back focal distance
  function refr(n1, n2, Rr) { var P = isFinite(Rr) ? (n2 - n1) / Rr : 0; return [[1, 0], [-P / n2, n1 / n2]]; }
  function mul(a, b) { return [[a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]], [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]]]; }
  var Mx = mul(refr(n, 1, R2), mul([[1, t], [0, 1]], refr(1, n, R1)));
  return -Mx[0][0] / Mx[1][0];   // a ray (y = 1, angle 0) leaves with y = A, angle C: meets the axis A/(−C) after the lens
}
(function () {
  var nn = O.index('bk7', 587.5618);
  var lenses = [['biconvex', 100, -100, 12], ['plano-convex', 60, Infinity, 10], ['positive meniscus', 50, 120, 8], ['biconcave', -80, 80, 4], ['plano-concave', Infinity, 70, 4]];
  lenses.forEach(function (L) {
    var tc = L[3], sc = O.prepare([{ kind: 'lens', x: 0, y: 0, rot: 0, R1: L[1], R2: L[2], tc: tc, D: 40, mat: 'bk7' }]);
    ok(!!sc[0]._g, L[0] + ': lens shape builds');
    var res = O.trace(sc, { x: -200, y: 1e-4, dx: 1, dy: 0, lam: 587.5618 }, { box: [-2000, -500, 2000, 500] });
    var xc = O.axisCrossing(O.finalRay(res)) - tc / 2, tl = O.thickLens(nn, L[1], L[2], tc);
    near(xc, tl.bfd, 1e-4 * M.abs(tl.bfd), L[0] + ': traced paraxial back focus = thick-lens formula');
    near(tl.bfd, abcdBfd(nn, L[1], L[2], tc), 1e-9 * M.abs(tl.bfd), L[0] + ': thick-lens formula = ABCD matrices');
  });
  // spherical aberration: a marginal ray of a biconvex lens crosses the axis before the paraxial focus
  var sc = O.prepare([{ kind: 'lens', x: 0, y: 0, rot: 0, R1: 100, R2: -100, tc: 12, D: 40, mat: 'bk7' }]);
  var par = O.axisCrossing(O.finalRay(O.trace(sc, { x: -200, y: 1e-4, dx: 1, dy: 0, lam: 587.5618 })));
  var mar = O.axisCrossing(O.finalRay(O.trace(sc, { x: -200, y: 18, dx: 1, dy: 0, lam: 587.5618 })));
  ok(mar < par - 1, 'biconvex: marginal focus falls short of the paraxial focus (' + (par - mar).toFixed(2) + ' mm)');
  notes.push('biconvex R ±100, 12 mm, N-BK7, D 40: longitudinal spherical aberration at h = 18 mm: ' + (par - mar).toFixed(2) + ' mm');
  // chromatic: blue focuses closer than red
  var fb = O.axisCrossing(O.finalRay(O.trace(sc, { x: -200, y: 1e-4, dx: 1, dy: 0, lam: 486.1327 })));
  var fr = O.axisCrossing(O.finalRay(O.trace(sc, { x: -200, y: 1e-4, dx: 1, dy: 0, lam: 656.2725 })));
  ok(fb < fr, 'biconvex: F light focuses before C light');
  near(fr - fb, O.thickLens(O.index('bk7', 656.2725), 100, -100, 12).bfd - O.thickLens(O.index('bk7', 486.1327), 100, -100, 12).bfd, 1e-3, 'chromatic focal shift = difference of the thick-lens formula');
})();

// ---------------------------------------------------------------- ideal thin lens: perfect imaging, 1/f = 1/u + 1/v
(function () {
  var f = 100, u = 300, v = 1 / (1 / f - 1 / u), sc = O.prepare([{ kind: 'thin', x: 0, y: 0, rot: 0, f: f, D: 120 }]);
  [-0.12, -0.05, 0.03, 0.1].forEach(function (a) {
    [0, 10].forEach(function (y0) {
      var res = O.trace(sc, { x: -u, y: y0, dx: M.cos(a), dy: M.sin(a), lam: 550 }, { box: [-1000, -500, 1000, 500] });
      var fr = O.finalRay(res), yAtV = fr.y + (v - fr.x) * fr.dy / fr.dx;
      near(yAtV, -y0 * v / u, 1e-9, 'ideal lens: ray from (−' + u + ', ' + y0 + ') at ' + a + ' rad meets the image at v = 150, y = −m·y');
    });
  });
  var sc2 = O.prepare([{ kind: 'thin', x: 0, y: 0, rot: 0, f: -100, D: 80 }]);
  var fr2 = O.finalRay(O.trace(sc2, { x: -200, y: 10, dx: 1, dy: 0, lam: 550 }));
  near(O.axisCrossing(fr2), -100, 1e-9, 'ideal diverging lens: parallel ray seems to come from the focus in front');
})();

// ---------------------------------------------------------------- mirrors
(function () {
  var f = 80, sc = O.prepare([{ kind: 'mirror', shape: 'parabolic', x: 0, y: 0, rot: 0, f: f, D: 200 }]), worst = 0;
  for (var h = -95; h <= 95; h += 5) {
    if (h === 0) continue;
    var res = O.trace(sc, { x: -300, y: h, dx: 1, dy: 0, lam: 550 }, { box: [-400, -400, 400, 400] });
    worst = M.max(worst, M.abs(O.axisCrossing(O.finalRay(res)) + f));
  }
  ok(worst < 1e-9, 'parabolic mirror: every parallel ray passes through the focus (worst miss ' + worst + ' mm)');
  var Rr = 200, sp = O.prepare([{ kind: 'mirror', shape: 'spherical', x: 0, y: 0, rot: 0, R: Rr, D: 160 }]);
  [1e-4, 20, 50, 75].forEach(function (h) {
    var x = O.axisCrossing(O.finalRay(O.trace(sp, { x: -300, y: h, dx: 1, dy: 0, lam: 550 }))), al = M.asin(h / Rr);
    near(x, -Rr + Rr / (2 * M.cos(al)), 1e-8, 'spherical mirror: ray at h = ' + h + ' crosses the axis R/(2 cos α) from the centre');
  });
  var cv = O.prepare([{ kind: 'mirror', shape: 'convex', x: 0, y: 0, rot: 0, R: 200, D: 160 }]);
  near(O.axisCrossing(O.finalRay(O.trace(cv, { x: -300, y: 1e-4, dx: 1, dy: 0, lam: 550 }))), 100, 1e-6, 'convex mirror: virtual focus R/2 behind it');
  var pl = O.prepare([{ kind: 'mirror', shape: 'plane', x: 0, y: 0, rot: 30, D: 100 }]);
  var fr = O.finalRay(O.trace(pl, { x: -100, y: 0, dx: 1, dy: 0, lam: 550 }));
  near(dirDeg(fr), -120, 1e-9, 'plane mirror turned 30°: the ray turns by 2 × 30° plus the reflection');
})();

// ---------------------------------------------------------------- rainbow: Descartes vs scan vs tracer
(function () {
  [[589.29, 'D']].concat([[400, 'violet'], [700, 'red']]).forEach(function (w) {
    var nn = O.index('water', w[0]);
    [1, 2].forEach(function (k) {
      var best = 1e9;
      for (var b = 0; b <= 1; b += 1e-5) best = M.min(best, devDrop(nn, b, k));
      var rb = O.rainbowDeg(nn, k);
      near(best, rb.D, 1e-6, 'drop, ' + w[1] + ', k = ' + k + ': scanned least turn = Descartes formula');
    });
  });
  var nD = O.index('water', 589.29), p1 = O.rainbowDeg(nD, 1).angle, p2 = O.rainbowDeg(nD, 2).angle;
  near(p1, 42.0, 0.15, 'primary bow radius ≈ 42°');
  near(p2, 50.9, 0.3, 'secondary bow radius ≈ 51°');
  var spread = O.rainbowDeg(O.index('water', 700), 1).angle - O.rainbowDeg(O.index('water', 400), 1).angle;
  ok(spread > 1.5 && spread < 2.5, 'primary bow: red outside violet by about 2° (' + spread.toFixed(2) + '°)');
  notes.push('water at 589 nm: primary ' + p1.toFixed(2) + '°, secondary ' + p2.toFixed(2) + '°; red−violet ' + spread.toFixed(2) + '°');
  // tracer: the ray with one internal reflection leaves the drop turned by the formula
  var sc = O.prepare([{ kind: 'drop', x: 0, y: 0, rot: 0, r: 50, mat: 'water' }]);
  [0.3, 0.6, 0.86, 0.95].forEach(function (b) {
    var res = O.trace(sc, { x: -200, y: 50 * b, dx: 1, dy: 0, lam: 589.29 }, { box: [-400, -400, 400, 400], minI: 0 , maxDepth: 6 });
    var out = res.segs.filter(function (s) { return s.end && s.k === 1 && s.n === 1; })[0];
    var turn = -M.atan2(out.y1 - out.y0, out.x1 - out.x0) / R;   // came in at 0°; a ray in the upper half is turned clockwise
    var want = devDrop(nD, b, 1);
    near(((turn - want) % 360 + 540) % 360 - 180, 0, 1e-7, 'drop, b = ' + b + ': traced turn after one internal reflection = 2(i − r) + (180° − 2r)');
  });
})();

// ---------------------------------------------------------------- rotation, two reflections inside, front focus
(function () {   // a lens and its beam turned together by 30° focus at the same distance
  var nn = O.index('bk7', 587.5618), tl = O.thickLens(nn, 100, -100, 12), a = 30 * R;
  var sc = O.prepare([{ kind: 'lens', x: 20, y: -10, rot: 30, R1: 100, R2: -100, tc: 12, D: 40, mat: 'bk7' }]);
  var h = 1e-4, start = [20 - 200 * M.cos(a) - h * M.sin(a), -10 - 200 * M.sin(a) + h * M.cos(a)];
  var fr = O.finalRay(O.trace(sc, { x: start[0], y: start[1], dx: M.cos(a), dy: M.sin(a), lam: 587.5618 }));
  var lx = (fr.x - 20) * M.cos(a) + (fr.y + 10) * M.sin(a), ly = -(fr.x - 20) * M.sin(a) + (fr.y + 10) * M.cos(a);
  var ldx = fr.dx * M.cos(a) + fr.dy * M.sin(a), ldy = -fr.dx * M.sin(a) + fr.dy * M.cos(a);
  near(lx - ly * ldx / ldy - 6, tl.bfd, 1e-4 * tl.bfd, 'rotated lens (30°): back focus unchanged');
  var rev = O.thickLens(nn, 50, Infinity, 10), sc2 = O.prepare([{ kind: 'lens', x: 0, y: 0, rot: 0, R1: 50, R2: Infinity, tc: 10, D: 40, mat: 'bk7' }]);
  var fr2 = O.finalRay(O.trace(sc2, { x: 200, y: 1e-4, dx: -1, dy: 0, lam: 587.5618 }));
  near(-(O.axisCrossing(fr2)) - 5, O.thickLens(nn, -Infinity, -50, 10).bfd, 1e-4 * rev.f, 'plano-convex lit from behind: front focal distance = thickLens(n, −R2, −R1)');
  var sp = O.prepare([{ kind: 'prism', x: 5, y: 3, rot: 25, A: 60, L: 60, mat: 'bk7' }]), g = sp[0]._g.prims[2], c = [(g.a[0] + g.b[0]) / 2, (g.a[1] + g.b[1]) / 2];
  var rc = M.cos(25 * R), rs = M.sin(25 * R), cw = [5 + rc * c[0] - rs * c[1], 3 + rs * c[0] + rc * c[1]], nw = [rc * g.n[0] - rs * g.n[1], rs * g.n[0] + rc * g.n[1]];
  var da = M.atan2(nw[1], nw[0]) + M.PI + 50 * R, d = [M.cos(da), M.sin(da)];
  var fp = O.finalRay(O.trace(sp, { x: cw[0] - 80 * d[0], y: cw[1] - 80 * d[1], dx: d[0], dy: d[1], lam: 587.5618 }));
  near(M.acos(fp.dx * d[0] + fp.dy * d[1]) / R, devPrism(60, nn, 50), 1e-8, 'rotated, moved prism: same deviation');
  var dr = O.prepare([{ kind: 'drop', x: 0, y: 0, rot: 0, r: 50, mat: 'water' }]), nD = O.index('water', 589.29);
  [0.5, 0.95].forEach(function (b) {
    var res = O.trace(dr, { x: -200, y: 50 * b, dx: 1, dy: 0, lam: 589.29 }, { minI: 0, maxDepth: 8 });
    var out = res.segs.filter(function (s) { return s.end && s.k === 2 && s.n === 1; })[0];
    var turn = -M.atan2(out.y1 - out.y0, out.x1 - out.x0) / R;
    near(((turn - devDrop(nD, b, 2)) % 360 + 540) % 360 - 180, 0, 1e-7, 'drop, b = ' + b + ': turn after two internal reflections');
  });
  var cv = O.prepare([{ kind: 'mirror', shape: 'convex', x: 0, y: 0, rot: 0, R: 200, D: 160 }]);
  var xh = O.axisCrossing(O.finalRay(O.trace(cv, { x: -300, y: 60, dx: 1, dy: 0, lam: 550 }))), al = M.asin(60 / 200);
  near(xh, 200 - 200 / (2 * M.cos(al)), 1e-8, 'convex mirror, ray at h = 60: virtual crossing R/(2 cos α) from the centre');
})();

// ---------------------------------------------------------------- bookkeeping: the light a ray splits into adds up to what came in (Fresnel R itself is checked above)
(function () {
  var sc = O.prepare([{ kind: 'slab', x: 0, y: 0, rot: 0, w: 10, h: 200, mat: 'f2' }]);
  var res = O.trace(sc, { x: -50, y: 0, dx: M.cos(0.5), dy: M.sin(0.5), lam: 550 }, { box: [-400, -400, 400, 400], minI: 0, maxDepth: 40 });
  var out = res.segs.filter(function (s) { return s.end; }).reduce(function (a, s) { return a + s.I; }, 0);
  near(out, 1, 1e-6, 'slab: sum of every ray that leaves = 1 (no light made or lost)');
})();

notes.forEach(function (s) { console.log('note: ' + s); });
console.log(fails ? fails + ' of ' + n + ' JS checks FAILED' : 'wave 5 JS: ' + n + ' checks passed');
process.exit(fails ? 1 : 0);
