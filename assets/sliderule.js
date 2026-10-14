/* Logarithms page: log calculator and a working slide rule (scale maths in trigmath.js).
   The rule is drawn in a 1000 × 300 SVG box: scale length 900 units from x = 50.
   Stator (fixed body): K and A above the slide, D and L below. Slide: B, CI, C. */
(function () {
  'use strict';
  var T = window.RK_TRIG, M = Math;
  // ---------------------------------------------------------------- calculator
  var lx = document.getElementById('lx'), lq = document.getElementById('lq');
  function fmt(x, n) { return x.toFixed(n).replace('-', '−'); }
  function calc() {
    var x = parseFloat((lx.value || '').replace(/[\s,]/g, ''));
    if (!(x > 0) || !isFinite(x)) { lq.innerHTML = '<div><span>Enter a positive number</span><span></span></div>'; return; }
    var p = T.logParts(x), n = T.normalise(x);
    lq.innerHTML = '<div><span>log₁₀ x</span><span>' + fmt(p.log, 6) + '</span></div>' +
      '<div><span>characteristic</span><span>' + String(p.characteristic).replace('-', '−') + ' (decimal point: ' + (p.characteristic >= 0 ? (p.characteristic + 1) + ' digit' + (p.characteristic ? 's' : '') + ' before it' : (-p.characteristic - 1) + ' zero' + (p.characteristic === -2 ? '' : 's') + ' after it') + ')</span></div>' +
      '<div><span>mantissa</span><span>' + fmt(p.mantissa, 6) + ' = log ' + n.m.toPrecision(6) + '</span></div>' +
      '<div><span>as printed in tables</span><span>' + p.bar + '</span></div>' +
      '<div><span>check: 10^log x</span><span>' + M.pow(10, p.log).toPrecision(8) + '</span></div>' +
      '<div><span>natural log, ln x</span><span>' + fmt(M.log(x), 6) + ' = log x ÷ log e</span></div>';
  }
  if (lx) {
    lx.addEventListener('input', calc);
    document.querySelectorAll('[data-lx]').forEach(function (b) { b.addEventListener('click', function () { lx.value = b.getAttribute('data-lx'); calc(); }); });
    calc();
  }

  // ---------------------------------------------------------------- slide rule
  var svg = document.getElementById('sr'), out = document.getElementById('srout');
  if (!svg) return;
  var X0 = 50, L = 900, off = 0, cur = M.log10(2), reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ROWS = { K: [8, 'stator', 3, false], A: [52, 'stator', 2, false], B: [104, 'slide', 2, false], CI: [148, 'slide', 1, true], C: [192, 'slide', 1, false], D: [236, 'stator', 1, false], L: [276, 'stator', 0, false] };
  function ticks(decades) {   // positions (0..1) and labels for a log scale spanning `decades` decades
    var t = [];
    for (var d = 0; d < decades; d++) {
      var base = M.pow(10, d);
      for (var v = 1; v < 10 - 1e-9; v += (v < 2 ? 0.05 : v < 5 ? 0.1 : 0.1)) {
        var vv = M.round(v * 100) / 100, pos = (d + M.log10(vv)) / decades, major = M.abs(vv - M.round(vv)) < 1e-9, half = M.abs(vv * 2 - M.round(vv * 2)) < 1e-9;
        if (decades > 1 && !major && !(vv < 2 && half) && M.abs(vv * 10 - M.round(vv * 10)) > 1e-9) continue;
        if (decades > 1 && !major && vv >= 5 && !half) continue;
        var lab = major && (decades < 3 || [1, 2, 3, 5].indexOf(M.round(vv)) >= 0) && !(decades === 2 && vv > 5 && vv !== 8) ? String(vv * base) : (decades === 1 && vv < 2 && M.abs(vv * 10 - M.round(vv * 10)) < 1e-9 ? '·' + String(vv).slice(-1) : '');
        t.push([pos, major ? 1 : half ? 0.65 : 0.4, lab]);
      }
    }
    t.push([1, 1, String(M.pow(10, decades))]);
    return t;
  }
  function scaleSvg(name, y, dx) {
    var r = ROWS[name], dec = r[2], inv = r[3], g = '', tk;
    if (name === 'L') { tk = []; for (var i = 0; i <= 100; i++) tk.push([i / 100, i % 10 === 0 ? 1 : i % 5 === 0 ? 0.65 : 0.4, i % 10 === 0 ? (i / 100).toFixed(1) : '']); }
    else tk = ticks(dec);
    var up = (name === 'K' || name === 'A' || name === 'C' || name === 'CI');   // ticks hang from the edge nearest the slide joint
    tk.forEach(function (t) {
      var x = X0 + dx + (inv ? 1 - t[0] : t[0]) * L, h = t[1] * 12;
      g += '<line x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="' + (up ? y + 26 : y) + '" y2="' + (up ? y + 26 - h : y + h) + '"/>';
      if (t[2]) g += '<text x="' + x.toFixed(1) + '" y="' + (up ? y + 10 : y + 26) + '" text-anchor="middle" font-size="' + (t[2].charAt(0) === '·' ? 8 : 11) + '">' + t[2].replace('·', '') + '</text>';
    });
    g += '<text x="' + (X0 + dx - 14) + '" y="' + (y + 18) + '" text-anchor="end" font-size="14" font-weight="600" class="lbl">' + name + '</text>';
    return g;
  }
  function read(name) {   // value under the cursor on a scale, or null when the cursor is off the slide
    var p = cur;
    if (ROWS[name][1] === 'slide') { p = cur - off; if (p < -1e-9 || p > 1 + 1e-9) return null; }
    if (name === 'L') return p;
    if (name === 'CI') return M.pow(10, 1 - p);
    return M.pow(10, p * ROWS[name][2]);
  }
  function draw() {
    var dx = off * L, xc = X0 + cur * L;
    var h = '<rect x="20" y="0" width="960" height="310" class="sr-body"/>' +
      '<rect x="' + (X0 + dx - 30) + '" y="94" width="' + (L + 60) + '" height="132" class="sr-slide"/>';
    ['K', 'A', 'D', 'L'].forEach(function (n) { h += scaleSvg(n, ROWS[n][0], 0); });
    ['B', 'CI', 'C'].forEach(function (n) { h += scaleSvg(n, ROWS[n][0], dx); });
    h += '<rect x="' + (xc - 22) + '" y="0" width="44" height="310" class="sr-cursor"/><line x1="' + xc + '" x2="' + xc + '" y1="0" y2="310" class="sr-hair"/>';
    svg.innerHTML = h;
    var parts = ['D', 'C', 'CI', 'A', 'B', 'K', 'L'].map(function (n) { var v = read(n); return n + ' ' + (v === null ? '—' : (n === 'L' ? v.toFixed(3) : v.toPrecision(3))); });
    if (!out.dataset.lock) out.textContent = 'Cursor reads: ' + parts.join(' · ');
  }
  function anim(toOff, toCur, msg) {
    out.dataset.lock = '';
    var o0 = off, c0 = cur, t0 = performance.now(), dur = reduce ? 0 : 700;
    (function step(now) {
      var k = dur ? M.min(1, (now - t0) / dur) : 1, e = k < 0.5 ? 2 * k * k : 1 - M.pow(-2 * k + 2, 2) / 2;
      off = o0 + (toOff - o0) * e; cur = c0 + (toCur - c0) * e; draw();
      if (k < 1) requestAnimationFrame(step); else { out.dataset.lock = '1'; out.textContent = msg; }
    })(t0);
  }
  function sig(x) { return T.normalise(x).m.toPrecision(3); }
  var EX = {
    mul: function (a, b) {
      var r = T.slideMultiply(a, b);
      return [r.offset, r.offset + M.log10(b), (r.shift ? 'The answer would run off the right end, so the 10 of C goes over ' + a + ' on D (the right index). ' : 'Put the 1 of C over ' + a + ' on D. ') +
        'Move the cursor to ' + b + ' on C; D reads ' + sig(a * b) + '. You place the point: ' + a + ' × ' + b + ' = ' + (a * b).toPrecision(4) + '.'];
    },
    div: function (a, b) {
      var o = M.log10(a) - M.log10(b), c = o >= 0 ? o : o + 1;
      return [o, c, 'Put ' + b + ' on C over ' + a + ' on D. Under the ' + (o >= 0 ? '1' : '10') + ' of C, D reads ' + sig(a / b) + ': ' + a + ' ÷ ' + b + ' = ' + (a / b).toPrecision(4) + '.'];
    },
    sq: function (a) { return [0, M.log10(a), 'Cursor on ' + a + ' on D; A reads ' + sig(a * a) + ' (A is a two-decade scale, so the square is ' + a * a + ').']; },
    cube: function (a) { return [0, M.log10(a), 'Cursor on ' + a + ' on D; K reads ' + sig(a * a * a) + ': ' + a + '³ = ' + (a * a * a).toPrecision(4) + '.']; },
    rec: function (a) { return [0, M.log10(a), 'Slide closed, cursor on ' + a + ' on C; CI reads ' + sig(1 / a) + ': 1/' + a + ' = ' + 1 / a + '.']; },
    log: function (a) { return [0, M.log10(a), 'Cursor on ' + a + ' on D; L reads ' + M.log10(a).toFixed(3) + ', the mantissa: log ' + a + ' = ' + M.log10(a).toFixed(4) + '.']; }
  };
  document.querySelectorAll('[data-sr]').forEach(function (b) {
    b.addEventListener('click', function () {
      var p = b.getAttribute('data-sr').split(':'), r = EX[p[0]].apply(null, p.slice(1).map(Number));
      anim(r[0], r[1], r[2]);
    });
  });
  // dragging: on the slide band moves the slide, elsewhere moves the cursor
  var mode = null, lastX = 0;
  function local(e) { var p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY; return p.matrixTransform(svg.getScreenCTM().inverse()); }
  svg.addEventListener('pointerdown', function (e) {
    var l = local(e); delete out.dataset.lock;
    mode = (l.y > 94 && l.y < 226 && M.abs(l.x - (X0 + cur * L)) > 22) ? 'slide' : 'cursor';
    lastX = l.x; svg.setPointerCapture(e.pointerId);
    if (mode === 'cursor') { cur = M.max(0, M.min(1, (l.x - X0) / L)); draw(); }
  });
  svg.addEventListener('pointermove', function (e) {
    if (!mode) return;
    var l = local(e);
    if (mode === 'slide') { off = M.max(-1, M.min(1, off + (l.x - lastX) / L)); lastX = l.x; }
    else cur = M.max(0, M.min(1, (l.x - X0) / L));
    draw();
  });
  svg.addEventListener('pointerup', function () { mode = null; });
  svg.style.touchAction = 'pan-y';
  draw();
})();
