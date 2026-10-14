/* Reckoning shape pages: sliders -> live quantities (the same formula strings the build
   checks) -> a figure drawn to scale (SVG for plane figures; solids hand over to solid.js). */
(function () {
  'use strict';
  var S = window.RK_SHAPE; if (!S) return;
  var M = Math, PI = M.PI;
  var env = { sqrt: M.sqrt, sin: M.sin, cos: M.cos, tan: M.tan, asin: M.asin, acos: M.acos, atan: M.atan, abs: M.abs, PI: PI,
    rad: function (d) { return d * PI / 180; } };
  function js(expr) { return expr.replace(/\band\b/g, '&&').replace(/\bor\b/g, '||'); }
  function compile(expr, names) { return new Function('E', 'V', 'with (E) { with (V) { return (' + js(expr) + '); } }'); }
  var lets = S.let.map(function (l) { return [l[0], compile(l[1])]; });
  var qs = S.q.map(function (q) { return compile(q.expr); });
  var valid = S.valid ? compile(S.valid[0]) : null;
  var V = {};
  S.params.forEach(function (p) { V[p.key] = p.default; });

  var unitSel = document.getElementById('lenunit');
  function suffix(kind) {
    var u = unitSel ? unitSel.value : '';
    if (kind === 'deg') return '°';
    if (!u) return '';
    return ' ' + u + (kind === 'area' ? '²' : kind === 'vol' ? '³' : '');
  }
  function num(x) {
    if (!isFinite(x)) return '—';
    var a = M.abs(x);
    var d = a >= 1000 ? 1 : a >= 100 ? 2 : a >= 10 ? 3 : 4;
    return x.toFixed(d).replace(/\.?0+$/, '');
  }
  function compute() {
    var W = Object.assign({}, V);
    lets.forEach(function (l) { W[l[0]] = l[1](env, W); });
    var ok = valid ? !!valid(env, W) : true;
    var vals = qs.map(function (f) { try { return f(env, W); } catch (e) { return NaN; } });
    return { ok: ok, vals: vals, W: W };
  }
  var qBox = document.getElementById('qty'), warn = document.getElementById('warn');
  function render() {
    var r = compute();
    warn.hidden = r.ok; if (!r.ok) warn.textContent = S.valid[1];
    qBox.querySelectorAll('[data-i]').forEach(function (el) {
      var i = +el.getAttribute('data-i'), q = S.q[i];
      el.textContent = r.ok ? (q.approx ? '≈ ' : '') + num(r.vals[i]) + suffix(q.kind) : '—';
    });
    if (S.dim === 2) draw2d(r.W, r.ok); else if (window.RK_SOLID) window.RK_SOLID(S.slug, r.W, r.ok);
  }
  document.querySelectorAll('.sliders input').forEach(function (inp) {
    var key = inp.getAttribute('data-k'), out = inp.parentNode.querySelector('output');
    inp.addEventListener('input', function () { V[key] = parseFloat(inp.value); out.textContent = inp.value; render(); });
  });
  if (unitSel) unitSel.addEventListener('change', render);
  var reset = document.getElementById('reset');
  if (reset) reset.addEventListener('click', function () {
    S.params.forEach(function (p) { V[p.key] = p.default; var i = document.querySelector('[data-k="' + p.key + '"]'); i.value = p.default; i.parentNode.querySelector('output').textContent = p.default; });
    render();
  });

  /* ---------------- 2D figures ---------------- */
  var svg = document.getElementById('fig2d');
  function arcPts(cx, cy, r, a0, a1, n) {
    var p = []; n = n || 64;
    for (var i = 0; i <= n; i++) { var a = a0 + (a1 - a0) * i / n; p.push([cx + r * M.cos(a), cy + r * M.sin(a)]); }
    return p;
  }
  function regular(n, R, rot) { var p = []; for (var i = 0; i < n; i++) { var a = rot + 2 * PI * i / n; p.push([R * M.cos(a), R * M.sin(a)]); } return p; }
  function geom(slug, v) {
    var G = { shapes: [], holes: [], dims: [], labels: [] };
    function poly(p) { G.shapes.push(p); }
    function dim(a, b, t, off) { G.dims.push([a, b, t, off || 0]); }
    var r, t, a, b, h, p;
    switch (slug) {
      case 'square': a = v.a; poly([[0, 0], [a, 0], [a, a], [0, a]]); dim([0, 0], [a, 0], 'a', -1); G.aux = [[[0, 0], [a, a]]]; break;
      case 'rectangle': poly([[0, 0], [v.a, 0], [v.a, v.b], [0, v.b]]); dim([0, 0], [v.a, 0], 'a', -1); dim([v.a, 0], [v.a, v.b], 'b', 1); break;
      case 'parallelogram': t = v.t * PI / 180; h = v.c * M.sin(t); a = v.c * M.cos(t);
        poly([[0, 0], [v.b, 0], [v.b + a, h], [a, h]]); dim([0, 0], [v.b, 0], 'b', -1); G.aux = [[[a, 0], [a, h]]]; G.labels.push([a + 0.08, h / 2, 'h']); break;
      case 'rhombus': poly([[-v.p / 2, 0], [0, v.q / 2], [v.p / 2, 0], [0, -v.q / 2]]); G.aux = [[[-v.p / 2, 0], [v.p / 2, 0]], [[0, -v.q / 2], [0, v.q / 2]]];
        G.labels.push([v.p / 4, 0.12, 'p']); G.labels.push([0.08, v.q / 4, 'q']); break;
      case 'trapezoid': p = (v.a - v.b) * 0.3; poly([[0, 0], [v.a, 0], [p + v.b, v.h], [p, v.h]]); dim([0, 0], [v.a, 0], 'a', -1); dim([p, v.h], [p + v.b, v.h], 'b', 1);
        G.aux = [[[p, 0], [p, v.h]]]; G.labels.push([p + 0.08, v.h / 2, 'h']); break;
      case 'quadrilateral': t = v.t * PI / 180;
        var A1 = [-0.4 * v.p, 0], C1 = [0.6 * v.p, 0], B1 = [0.65 * v.q * M.cos(t), 0.65 * v.q * M.sin(t)], D1 = [-0.35 * v.q * M.cos(t), -0.35 * v.q * M.sin(t)];
        poly([A1, B1, C1, D1]); G.aux = [[A1, C1], [B1, D1]]; G.labels.push([0.3 * v.p, -0.25, 'p']); G.labels.push([B1[0] * 0.5 + 0.1, B1[1] * 0.5, 'q']); break;
      case 'triangle': a = v.a; b = v.b; var c = v.c, cx = (b * b + c * c - a * a) / (2 * c), cy = M.sqrt(M.max(b * b - cx * cx, 0));
        poly([[0, 0], [c, 0], [cx, cy]]); dim([0, 0], [c, 0], 'c', -1); G.labels.push([(c + cx) / 2 + 0.15, cy / 2, 'a']); G.labels.push([cx / 2 - 0.3, cy / 2, 'b']); break;
      case 'right-triangle': poly([[0, 0], [v.a, 0], [0, v.b]]); dim([0, 0], [v.a, 0], 'a', -1); dim([0, 0], [0, v.b], 'b', -1);
        G.aux = [[[0.3, 0], [0.3, 0.3]], [[0, 0.3], [0.3, 0.3]]]; G.labels.push([v.a / 2 + 0.1, v.b / 2 + 0.1, 'c']); break;
      case 'isosceles-triangle': h = M.sqrt(M.max(v.s * v.s - v.b * v.b / 4, 0)); poly([[-v.b / 2, 0], [v.b / 2, 0], [0, h]]); dim([-v.b / 2, 0], [v.b / 2, 0], 'b', -1);
        G.aux = [[[0, 0], [0, h]]]; G.labels.push([0.08, h / 2, 'h']); G.labels.push([v.b / 4 + 0.2, h / 2, 's']); break;
      case 'equilateral-triangle': h = v.a * M.sqrt(3) / 2; poly([[0, 0], [v.a, 0], [v.a / 2, h]]); dim([0, 0], [v.a, 0], 'a', -1); G.aux = [[[v.a / 2, 0], [v.a / 2, h]]]; break;
      case 'circle': poly(arcPts(0, 0, v.r, 0, 2 * PI, 96)); G.aux = [[[0, 0], [v.r, 0]]]; G.labels.push([v.r / 2, 0.12, 'r']); break;
      case 'sector': t = v.t * PI / 180; poly([[0, 0]].concat(arcPts(0, 0, v.r, 0, t, 72))); G.ghost = arcPts(0, 0, v.r, 0, 2 * PI, 96);
        G.labels.push([v.r / 2, -0.25, 'r']); G.labels.push([0.35 * M.cos(t / 2), 0.35 * M.sin(t / 2), 'θ']); break;
      case 'segment': t = v.t * PI / 180; poly(arcPts(0, 0, v.r, -t / 2, t / 2, 72)); G.ghost = arcPts(0, 0, v.r, 0, 2 * PI, 96);
        G.aux = [[[0, 0], [v.r * M.cos(t / 2), v.r * M.sin(t / 2)]], [[0, 0], [v.r * M.cos(t / 2), -v.r * M.sin(t / 2)]]]; G.labels.push([0.3, 0, 'θ']); break;
      case 'annulus': poly(arcPts(0, 0, v.R, 0, 2 * PI, 96)); if (v.r < v.R) G.holes.push(arcPts(0, 0, v.r, 0, 2 * PI, 96));
        G.aux = [[[0, 0], [v.R * 0.7071, v.R * 0.7071]], [[0, 0], [-v.r, 0]]]; G.labels.push([v.R * 0.45, v.R * 0.25, 'R']); G.labels.push([-v.r / 2, 0.12, 'r']); break;
      case 'ring-sector': t = v.t * PI / 180; poly(arcPts(0, 0, v.R, 0, t, 72).concat(arcPts(0, 0, M.min(v.r, v.R), t, 0, 72))); G.ghost = arcPts(0, 0, v.R, 0, 2 * PI, 96); break;
      case 'ellipse': p = []; for (var i = 0; i <= 96; i++) { var u = 2 * PI * i / 96; p.push([v.a * M.cos(u), v.b * M.sin(u)]); } poly(p);
        G.aux = [[[0, 0], [v.a, 0]], [[0, 0], [0, v.b]]]; G.labels.push([v.a / 2, 0.12, 'a']); G.labels.push([0.08, v.b / 2, 'b']); break;
      case 'spandrel': r = v.r; poly([[0, 0], [r, 0]].concat(arcPts(r, r, r, -PI / 2, -PI, 48)).concat([[0, r]])); G.ghost = arcPts(r, r, r, PI, 1.5 * PI, 48);
        G.aux = [[[0, r], [r, r]], [[r, 0], [r, r]]]; dim([0, 0], [r, 0], 'r', -1); break;
      case 'hexagon': poly(regular(6, v.s, 0)); dim([v.s, 0], [v.s / 2, v.s * M.sqrt(3) / 2], 's', 1); break;
      case 'octagon': r = v.s / (2 * M.sin(PI / 8)); poly(regular(8, r, PI / 8)); break;
      case 'regular-polygon': var n = M.round(v.n); r = v.s / (2 * M.sin(PI / n)); poly(regular(n, r, PI / 2 - PI / n)); G.ghost = arcPts(0, 0, r, 0, 2 * PI, 96); break;
    }
    return G;
  }
  function draw2d(v, ok) {
    var G = geom(S.slug, v), all = [];
    [G.shapes, G.holes, G.ghost ? [G.ghost] : [], (G.aux || []), G.dims.map(function (d) { return [d[0], d[1]]; })].forEach(function (L) { L.forEach(function (p) { all = all.concat(p); }); });
    G.labels.forEach(function (l) { all.push([l[0], l[1]]); });
    if (!all.length) return;
    var xs = all.map(function (q) { return q[0]; }), ys = all.map(function (q) { return q[1]; });
    var x0 = M.min.apply(null, xs), x1 = M.max.apply(null, xs), y0 = M.min.apply(null, ys), y1 = M.max.apply(null, ys);
    var W = 400, H = 300, pad = 34, s = M.min((W - 2 * pad) / M.max(x1 - x0, 1e-6), (H - 2 * pad) / M.max(y1 - y0, 1e-6));
    var ox = (W - (x1 - x0) * s) / 2, oy = (H - (y1 - y0) * s) / 2;
    function X(x) { return (ox + (x - x0) * s).toFixed(1); }
    function Y(y) { return (H - oy - (y - y0) * s).toFixed(1); }
    function path(p, close) { return p.map(function (q, i) { return (i ? 'L' : 'M') + X(q[0]) + ' ' + Y(q[1]); }).join('') + (close ? 'Z' : ''); }
    var o = '';
    if (G.ghost) o += '<path class="aux" d="' + path(G.ghost, true) + '"/>';
    var d = G.shapes.map(function (p) { return path(p, true); }).join('') + G.holes.map(function (p) { return path(p.slice().reverse(), true); }).join('');
    o += '<path class="shp" fill-rule="evenodd" d="' + d + '"' + (ok ? '' : ' style="opacity:.35"') + '/>';
    (G.aux || []).forEach(function (p) { o += '<path class="aux" d="' + path(p) + '"/>'; });
    G.dims.forEach(function (dm) {
      var a = dm[0], b = dm[1], dx = b[0] - a[0], dy = b[1] - a[1], L = M.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, k = 14 / s * (dm[3] || 0);
      var A = [a[0] + nx * k, a[1] + ny * k], B = [b[0] + nx * k, b[1] + ny * k];
      o += '<path class="dim" d="' + path([A, B]) + '"/>';
      o += '<text class="lbl" text-anchor="middle" x="' + X((A[0] + B[0]) / 2 + nx * 10 / s * (dm[3] || 1)) + '" y="' + (+Y((A[1] + B[1]) / 2 + ny * 10 / s * (dm[3] || 1)) + 4) + '">' + dm[2] + '</text>';
    });
    G.labels.forEach(function (l) { o += '<text class="lbl" x="' + X(l[0]) + '" y="' + Y(l[1]) + '">' + l[2] + '</text>'; });
    svg.innerHTML = o;
  }
  render();
})();
