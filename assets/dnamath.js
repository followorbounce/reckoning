/* Code of life maths. Pure functions; window.RK_DNA in the page, module.exports in node (tests/check_wave4.js).
   1. IUPAC-IUB (1985) letters for incompletely specified bases: each letter is a SET of bases, and every other
      table (complement, names, matching) is generated from those sets.
   2. Helix geometry from helical parameters (rise, twist), for the 3D model.
   3. Topology of closed DNA: linking number, twist and writhe of a ribbon, by the Gauss integral on polygons
      (exact solid-angle form for pairs of straight segments). Lk = Tw + Wr is checked, not assumed. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RK_DNA = factory();
})(this, function () {
  'use strict';
  var M = Math;

  // ---------------------------------------------------------------- 1. the IUPAC letters
  var SETS = { A: 'A', C: 'C', G: 'G', T: 'T', R: 'AG', Y: 'CT', S: 'CG', W: 'AT', K: 'GT', M: 'AC', B: 'CGT', D: 'AGT', H: 'ACT', V: 'ACG', N: 'ACGT' };
  var ORDER = 'ACGTRYSWKMBDHVN'.split('');
  var PAIR = { A: 'T', T: 'A', C: 'G', G: 'C' };
  var BY_SET = {}; ORDER.forEach(function (k) { BY_SET[SETS[k]] = k; });
  function norm(s) { return s.split('').sort().join(''); }
  function setOf(ch) { ch = ch.toUpperCase(); if (ch === 'U') ch = 'T'; return SETS[ch] || null; }
  function letterOf(set) { return BY_SET[norm(set)] || null; }
  function complement(ch) {
    var up = ch.toUpperCase(), rna = up === 'U';
    var s = setOf(up); if (!s) return ch;
    var c = letterOf(s.split('').map(function (b) { return PAIR[b]; }).join(''));
    if (rna) c = 'A';
    return ch === up ? c : c.toLowerCase();
  }
  function revcomp(seq, rna) {
    var out = seq.split('').reverse().map(complement).join('');
    return rna ? out.replace(/T/g, 'U').replace(/t/g, 'u') : out;
  }
  function count(seq) { var n = 1; for (var i = 0; i < seq.length; i++) { var s = setOf(seq[i]); if (s) n *= s.length; } return n; }
  function expand(seq, limit) {
    var out = [''];
    for (var i = 0; i < seq.length; i++) {
      var s = setOf(seq[i]); if (!s) continue;
      var nx = [];
      out.forEach(function (p) { s.split('').forEach(function (b) { if (nx.length < (limit || 1e6)) nx.push(p + b); }); });
      out = nx;
    }
    return out;
  }
  function clean(seq) { return seq.toUpperCase().replace(/[^ACGTURYSWKMBDHVN]/g, ''); }
  // a pattern letter matches a sequence letter when the sequence letter's set lies inside the pattern letter's set
  function matches(pat, seq) {
    var hits = [];
    pat = clean(pat); seq = clean(seq);
    if (!pat.length) return hits;
    var ps = pat.split('').map(setOf);
    for (var i = 0; i + pat.length <= seq.length; i++) {
      var ok = true;
      for (var k = 0; k < pat.length && ok; k++) { var s = setOf(seq[i + k]); for (var j = 0; j < s.length; j++) if (ps[k].indexOf(s[j]) < 0) { ok = false; break; } }
      if (ok) hits.push(i);
    }
    return hits;
  }
  function gc(seq) { var s = clean(seq).replace(/U/g, 'T'), n = 0, g = 0; for (var i = 0; i < s.length; i++) if ('ACGT'.indexOf(s[i]) >= 0) { n++; if (s[i] === 'G' || s[i] === 'C') g++; } return n ? g / n : 0; }

  // ---------------------------------------------------------------- 2. helix geometry
  // rise in nm per base pair, twist in degrees per base pair (negative = left-handed)
  function helixFrames(n, rise, twist) {
    var out = [];
    for (var i = 0; i < n; i++) out.push({ z: i * rise, a: i * twist * M.PI / 180 });
    return out;
  }

  // ---------------------------------------------------------------- 3. topology
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function add(a, b) { return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]; }
  function mul(a, k) { return [a[0] * k, a[1] * k, a[2] * k]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function unit(a) { var l = M.sqrt(dot(a, a)); return l ? mul(a, 1 / l) : [0, 0, 0]; }
  function asin(x) { return M.asin(M.max(-1, M.min(1, x))); }
  // solid angle (signed) seen between segment p1→p2 and segment p3→p4 (Klenin & Langowski 2000)
  function omega(p1, p2, p3, p4) {
    var r13 = sub(p3, p1), r14 = sub(p4, p1), r23 = sub(p3, p2), r24 = sub(p4, p2);
    var n1 = unit(cross(r13, r14)), n2 = unit(cross(r14, r24)), n3 = unit(cross(r24, r23)), n4 = unit(cross(r23, r13));
    var o = asin(dot(n1, n2)) + asin(dot(n2, n3)) + asin(dot(n3, n4)) + asin(dot(n4, n1));
    var s = dot(cross(sub(p4, p3), sub(p2, p1)), r13);
    return s > 0 ? o : s < 0 ? -o : 0;
  }
  // Gauss linking integral of two closed polygons (an integer when they do not touch)
  function linking(a, b) {
    var s = 0, na = a.length, nb = b.length;
    for (var i = 0; i < na; i++) for (var j = 0; j < nb; j++) s += omega(a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]);
    return s / (4 * M.PI);
  }
  // writhe: the same integral of a closed curve with itself (adjacent segments contribute nothing)
  function writhe(a) {
    var s = 0, n = a.length;
    for (var i = 0; i < n; i++) for (var j = i + 2; j < n; j++) {
      if (i === 0 && j === n - 1) continue;
      s += omega(a[i], a[i + 1], a[j], a[(j + 1) % n]);
    }
    return 2 * s / (4 * M.PI);
  }
  // rotate v about unit axis k by angle t (Rodrigues)
  function rot(v, k, t) { var c = M.cos(t), s = M.sin(t); return add(add(mul(v, c), mul(cross(k, v), s)), mul(k, dot(k, v) * (1 - c))); }
  // the rotation that carries unit tangent t1 to t2 by the smallest angle, applied to v (parallel transport)
  function transport(v, t1, t2) {
    var ax = cross(t1, t2), s = M.sqrt(dot(ax, ax)), c = dot(t1, t2);
    return s < 1e-12 ? v : rot(v, mul(ax, 1 / s), M.atan2(s, c));
  }
  function tangents(a) { var n = a.length, t = []; for (var i = 0; i < n; i++) t.push(unit(sub(a[(i + 1) % n], a[i]))); return t; }
  // Build a closed ribbon on the curve with total twist chosen so the ribbon closes with linking number Lk.
  // Twist is spread evenly by arc length on top of the twist-free (parallel-transported) frame.
  // Returns twist computed from the frame's holonomy, writhe from the Gauss integral, and the edge curve.
  function ribbon(a, Lk, width) {
    var n = a.length, t = tangents(a), u = [], len = [0];
    var u0 = unit(cross(t[0], M.abs(t[0][2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]));
    u.push(u0);
    for (var i = 1; i <= n; i++) {
      u.push(transport(u[i - 1], t[i - 1], t[i % n]));
      len.push(len[i - 1] + M.sqrt(dot(sub(a[i % n], a[i - 1]), sub(a[i % n], a[i - 1]))));
    }
    // holonomy: the angle from u0 to the transported u after one full circuit, about t0
    var un = u[n], hol = M.atan2(dot(cross(u0, un), t[0]), dot(u0, un));
    var Wr = writhe(a);
    // twist needed: the frame must turn by −hol (mod 2π) to close; pick the branch whose Tw + Wr is nearest Lk
    var base = -hol / (2 * M.PI), Tw = base + M.round(Lk - Wr - base);
    var S = len[n], edge = [], frame = [];
    for (i = 0; i < n; i++) {
      var ui = rot(u[i], t[i], 2 * M.PI * Tw * len[i] / S);
      frame.push(ui); edge.push(add(a[i], mul(ui, width)));
    }
    return { Tw: Tw, Wr: Wr, Lk: Tw + Wr, holonomy: hol, edge: edge, frame: frame };
  }

  // closed curves for supercoiled DNA, scaled to a circle of length 2π·R
  // toroidal (solenoidal) supercoil: n turns around a ring; hand = +1 right-handed, −1 left-handed
  // (the coil turns about the direction of travel round the ring by the right-hand rule when hand = +1)
  function toroid(N, R, amp, n, hand) {
    var p = [];
    for (var i = 0; i < N; i++) { var t = 2 * M.PI * i / N, r = R + amp * M.cos(n * t); p.push([r * M.cos(t), r * M.sin(t), -hand * amp * M.sin(n * t)]); }
    return p;
  }
  // interwound (plectonemic) supercoil: a long loop whose two arms wind round each other k half-turns per unit;
  // hand = +1 right-handed, −1 left-handed. s in [0,1] goes from the open loop to the fully wound one.
  function plectoneme(N, Lhalf, w, turns, s, hand) {
    var p = [], straight = 2 * Lhalf, arcL = M.PI * w, total = 2 * straight + 2 * arcL;
    for (var i = 0; i < N; i++) {
      var d = total * i / N, x, y;
      if (d < straight) { x = -Lhalf + d; y = -w; }
      else if (d < straight + arcL) { var a = (d - straight) / w - M.PI / 2; x = Lhalf + w * M.cos(a); y = w * M.sin(a); }
      else if (d < 2 * straight + arcL) { x = Lhalf - (d - straight - arcL); y = w; }
      else { var b = (d - 2 * straight - arcL) / w + M.PI / 2; x = -Lhalf + w * M.cos(b); y = w * M.sin(b); }
      var k = hand * s * turns * 2 * M.PI / (2 * Lhalf), ang = k * x;
      p.push([x, y * M.cos(ang), y * M.sin(ang)]);
    }
    return p;
  }

  return { SETS: SETS, ORDER: ORDER, setOf: setOf, letterOf: letterOf, complement: complement, revcomp: revcomp, count: count, expand: expand,
    clean: clean, matches: matches, gc: gc, helixFrames: helixFrames, omega: omega, linking: linking, writhe: writhe, ribbon: ribbon,
    toroid: toroid, plectoneme: plectoneme, tangents: tangents };
});
