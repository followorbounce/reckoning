/* Reckoning: plane trigonometry and logarithm helpers. Pure functions, used by the pages and by
   tests/check_wave3.js (node). Angles in degrees. */
(function (root) {
  'use strict';
  var M = Math, D2R = M.PI / 180, R2D = 180 / M.PI;
  function sin(d) { return M.sin(d * D2R); }
  function cos(d) { return M.cos(d * D2R); }
  function acos(x) { return R2D * M.acos(M.max(-1, M.min(1, x))); }
  function asin(x) { return R2D * M.asin(M.max(-1, M.min(1, x))); }
  function ok(t) { return t.a > 0 && t.b > 0 && t.c > 0 && t.A > 0 && t.B > 0 && t.C > 0 && M.abs(t.A + t.B + t.C - 180) < 1e-6; }
  function area(t) { return 0.5 * t.b * t.c * sin(t.A); }

  /* Solve a plane triangle. Sides a, b, c are opposite angles A, B, C.
     kind: 'SSS' {a,b,c} | 'SAS' {b,c,A} | 'ASA' {B,C,a} | 'AAS' {A,B,a} | 'SSA' {a,b,A}.
     Returns a list of solutions (SSA can give 0, 1 or 2). */
  function solve(kind, g) {
    var out = [], t;
    if (kind === 'SSS') {
      var a = g.a, b = g.b, c = g.c;
      if (a + b <= c || a + c <= b || b + c <= a) return [];
      t = { a: a, b: b, c: c, A: acos((b * b + c * c - a * a) / (2 * b * c)), B: acos((a * a + c * c - b * b) / (2 * a * c)) };
      t.C = 180 - t.A - t.B; out.push(t);
    } else if (kind === 'SAS') {
      if (g.A <= 0 || g.A >= 180) return [];
      var aa = M.sqrt(g.b * g.b + g.c * g.c - 2 * g.b * g.c * cos(g.A));
      t = { a: aa, b: g.b, c: g.c, A: g.A, B: acos((aa * aa + g.c * g.c - g.b * g.b) / (2 * aa * g.c)) };
      t.C = 180 - t.A - t.B; out.push(t);
    } else if (kind === 'ASA' || kind === 'AAS') {
      var A, B, C, k;
      if (kind === 'ASA') { B = g.B; C = g.C; A = 180 - B - C; }
      else { A = g.A; B = g.B; C = 180 - A - B; }
      if (A <= 0 || B <= 0 || C <= 0) return [];
      k = g.a / sin(A);
      out.push({ a: g.a, b: k * sin(B), c: k * sin(C), A: A, B: B, C: C });
    } else if (kind === 'SSA') {
      // two sides a, b and the angle A opposite a: the ambiguous case
      if (g.A <= 0 || g.A >= 180) return [];
      var s = g.b * sin(g.A) / g.a;
      if (s > 1 + 1e-12) return [];
      var B1 = asin(M.min(1, s)), cands = [B1];
      if (M.abs(B1 - 90) > 1e-9) cands.push(180 - B1);
      cands.forEach(function (Bx) {
        var Cx = 180 - g.A - Bx;
        if (Cx > 1e-9) out.push({ a: g.a, b: g.b, c: g.a * sin(Cx) / sin(g.A), A: g.A, B: Bx, C: Cx });
      });
    }
    return out.filter(ok).map(function (x) { x.area = area(x); return x; });
  }

  /* exact values at the special angles, as text (the checks compare them with Math.sin/cos) */
  var EXACT = {
    0: ['0', '1', '0'], 30: ['1/2', '√3/2', '√3/3'], 45: ['√2/2', '√2/2', '1'], 60: ['√3/2', '1/2', '√3'], 90: ['1', '0', '∞'],
    120: ['√3/2', '−1/2', '−√3'], 135: ['√2/2', '−√2/2', '−1'], 150: ['1/2', '−√3/2', '−√3/3'], 180: ['0', '−1', '0'],
    210: ['−1/2', '−√3/2', '√3/3'], 225: ['−√2/2', '−√2/2', '1'], 240: ['−√3/2', '−1/2', '√3'], 270: ['−1', '0', '∞'],
    300: ['−√3/2', '1/2', '−√3'], 315: ['−√2/2', '√2/2', '−1'], 330: ['−1/2', '√3/2', '−√3/3'],
    15: ['(√6−√2)/4', '(√6+√2)/4', '2−√3'], 18: ['(√5−1)/4', '√(10+2√5)/4', '√(25−10√5)/5'], 36: ['√(10−2√5)/4', '(1+√5)/4', '√(5−2√5)'],
    72: ['√(10+2√5)/4', '(√5−1)/4', '√(5+2√5)'], 75: ['(√6+√2)/4', '(√6−√2)/4', '2+√3']
  };
  /* evaluate the small expression language used in EXACT (√, √(…), /, +, −, numbers) */
  function evalExact(s) {
    if (s === '∞') return Infinity;
    var js = s.replace(/−/g, '-').replace(/√\(/g, 'Math.sqrt(').replace(/√(\d+)/g, 'Math.sqrt($1)').replace(/(\d|\))(Math|\()/g, '$1*$2');
    if (!/^[-+*/().\d\sMathsqrt]+$/.test(js)) throw new Error('bad exact value ' + s);
    return Function('return (' + js + ')')();
  }

  /* logarithms: characteristic and mantissa, with the bar notation of log tables for numbers < 1 */
  function logParts(x) {
    var L = M.log10(x), c = M.floor(L), m = L - c;
    if (m > 1 - 5e-13) { c += 1; m = 0; }
    return { log: L, characteristic: c, mantissa: m, bar: c < 0 ? (String(-c).split('').map(function (d) { return d + '̄'; }).join('') + m.toFixed(4).slice(1)) : (c + m.toFixed(4).slice(1)) };
  }
  /* slide-rule scales: position along the rule (0..1) of value v on each scale */
  var SCALES = {
    D: function (v) { return M.log10(v); },           // 1..10
    C: function (v) { return M.log10(v); },
    CI: function (v) { return 1 - M.log10(v); },      // 10..1, reciprocals
    A: function (v) { return M.log10(v) / 2; },       // 1..100, squares
    B: function (v) { return M.log10(v) / 2; },
    K: function (v) { return M.log10(v) / 3; },       // 1..1000, cubes
    L: function (v) { return v; }                     // 0..1, the mantissa itself (linear)
  };
  /* multiply on C and D: put C1 (or C10) over a on D, read b on C; returns the D reading in [1,10) and the shift */
  function slideMultiply(a, b) {
    var pa = SCALES.D(a), pb = SCALES.C(b), p = pa + pb, shift = 0;
    if (p >= 1) { p -= 1; shift = 1; }                 // run off the end: use the right index (C10)
    return { reading: M.pow(10, p), offset: shift ? pa - 1 : pa, shift: shift };
  }
  function normalise(x) { var e = M.floor(M.log10(x)); return { m: x / M.pow(10, e), e: e }; }

  var T = { solve: solve, EXACT: EXACT, evalExact: evalExact, logParts: logParts, SCALES: SCALES, slideMultiply: slideMultiply, normalise: normalise, sin: sin, cos: cos };
  if (typeof module !== 'undefined' && module.exports) module.exports = T; else root.RK_TRIG = T;
})(this);
