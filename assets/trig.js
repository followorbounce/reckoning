/* Trigonometry page: a draggable unit circle and a triangle solver (maths in trigmath.js). */
(function () {
  'use strict';
  var T = window.RK_TRIG, M = Math, NS = 'http://www.w3.org/2000/svg';
  var POINTS = ['N', 'N by E', 'NNE', 'NE by N', 'NE', 'NE by E', 'ENE', 'E by N', 'E', 'E by S', 'ESE', 'SE by E', 'SE', 'SE by S', 'SSE', 'S by E',
    'S', 'S by W', 'SSW', 'SW by S', 'SW', 'SW by W', 'WSW', 'W by S', 'W', 'W by N', 'WNW', 'NW by W', 'NW', 'NW by N', 'NNW', 'N by W'];
  function f(x, n) { if (!isFinite(x) || M.abs(x) > 1e6) return '∞ (undefined)'; var s = x.toFixed(n === undefined ? 4 : n); return (s === '-0.0000' ? '0.0000' : s).replace('-', '−'); }

  // ---------------------------------------------------------------- unit circle
  var svg = document.getElementById('uc'), sl = document.getElementById('ucd'), out = document.getElementById('ucdv'), q = document.getElementById('ucq');
  if (svg) {
    var drag = false;
    var draw = function () {
      var d = +sl.value, r = d * M.PI / 180, c = M.cos(r), s = M.sin(r), t = M.tan(r);
      out.textContent = d;
      var h = '<line x1="-1.4" y1="0" x2="1.4" y2="0" stroke="var(--muted)" stroke-width="0.006"/><line x1="0" y1="-1.4" x2="0" y2="1.4" stroke="var(--muted)" stroke-width="0.006"/>' +
        '<circle cx="0" cy="0" r="1" fill="none" stroke="var(--ink)" stroke-width="0.012"/>' +
        '<line x1="1" y1="-1.4" x2="1" y2="1.4" stroke="var(--muted)" stroke-width="0.006" stroke-dasharray="0.03 0.03"/>';
      var a0 = 0, sweep = r;   // angle arc
      h += '<path d="M0.22 0 A0.22 0.22 0 ' + (sweep > M.PI ? 1 : 0) + ' 0 ' + (0.22 * c) + ' ' + (-0.22 * s) + '" fill="none" stroke="var(--signal)" stroke-width="0.012"/>';
      if (M.abs(c) > 1e-9) {
        var ty = M.max(-1.4, M.min(1.4, t));
        h += '<line x1="0" y1="0" x2="1" y2="' + (-ty) + '" stroke="var(--signal)" stroke-width="0.006" opacity=".6"/>' +
          '<line x1="1" y1="0" x2="1" y2="' + (-ty) + '" stroke="var(--signal)" stroke-width="0.02"/>';
      }
      h += '<line x1="0" y1="0" x2="' + c + '" y2="0" stroke="var(--flag-b)" stroke-width="0.024"/>' +
        '<line x1="' + c + '" y1="0" x2="' + c + '" y2="' + (-s) + '" stroke="var(--ok)" stroke-width="0.024"/>' +
        '<line x1="0" y1="0" x2="' + c + '" y2="' + (-s) + '" stroke="var(--ink)" stroke-width="0.012"/>' +
        '<circle id="ucpt" cx="' + c + '" cy="' + (-s) + '" r="0.06" fill="var(--signal)" stroke="var(--sheet)" stroke-width="0.015" style="cursor:grab"/>' +
        '<text x="1.04" y="-0.03" font-size="0.09">1</text><text x="' + (c / 2 - 0.05) + '" y="0.12" font-size="0.09">cos θ</text>' +
        '<text x="' + (c + (c >= 0 ? 0.04 : -0.3)) + '" y="' + (-s / 2) + '" font-size="0.09">sin θ</text>';
      svg.innerHTML = h;
      var ex = T.EXACT[String(d)], bearing = ((90 - d) % 360 + 360) % 360, pt = M.round(bearing / 11.25) % 32;
      var quad = d % 90 === 0 ? 'on an axis' : 'quadrant ' + 'I II III IV'.split(' ')[M.floor(d / 90) % 4];
      q.innerHTML = '<div><span>θ</span><span>' + d + '° = ' + f(r, 5) + ' rad = ' + f(d / 0.9, 3) + ' gon</span></div>' +
        '<div><span>sin θ</span><span>' + f(s) + (ex ? ' = ' + ex[0] : '') + '</span></div>' +
        '<div><span>cos θ</span><span>' + f(c) + (ex ? ' = ' + ex[1] : '') + '</span></div>' +
        '<div><span>tan θ</span><span>' + (M.abs(c) < 1e-12 ? 'undefined' : f(t)) + (ex && ex[2] !== '∞' ? ' = ' + ex[2] : '') + '</span></div>' +
        '<div><span>Where</span><span>' + quad + '</span></div>' +
        '<div><span>As a bearing</span><span>' + String(M.round(bearing * 100) / 100).padStart(3, '0') + '° ≈ ' + POINTS[pt] + '</span></div>';
    };
    var fromEvent = function (e) {
      var p = svg.createSVGPoint(); p.x = e.clientX; p.y = e.clientY;
      var l = p.matrixTransform(svg.getScreenCTM().inverse()), a = M.atan2(-l.y, l.x) * 180 / M.PI;
      if (a < 0) a += 360;
      sl.value = M.round(a * 4) / 4; draw();
    };
    svg.addEventListener('pointerdown', function (e) { drag = true; svg.setPointerCapture(e.pointerId); fromEvent(e); });
    svg.addEventListener('pointermove', function (e) { if (drag) fromEvent(e); });
    svg.addEventListener('pointerup', function () { drag = false; });
    svg.style.touchAction = 'none';
    sl.addEventListener('input', draw);
    document.querySelectorAll('[data-ang]').forEach(function (b) { b.addEventListener('click', function () { sl.value = b.getAttribute('data-ang'); draw(); }); });
    draw();
  }

  // ---------------------------------------------------------------- triangle solver
  var kindSel = document.getElementById('tk'), tin = document.getElementById('tin'), tout = document.getElementById('tout'), tsvg = document.getElementById('tsvg');
  if (!kindSel) return;
  var FIELDS = { SSS: [['a', 7], ['b', 5], ['c', 6]], SAS: [['b', 5], ['c', 6], ['A', 50]], ASA: [['B', 40], ['C', 75], ['a', 6]],
                 AAS: [['A', 50], ['B', 60], ['a', 6]], SSA: [['a', 4.5], ['b', 6], ['A', 40]] };
  function inputs() {
    tin.innerHTML = '';
    FIELDS[kindSel.value].forEach(function (fd) {
      var lab = document.createElement('label'); lab.className = 'small';
      var ang = /[ABC]/.test(fd[0]);
      lab.innerHTML = (ang ? 'angle ' : 'side ') + '<b>' + fd[0] + '</b>' + (ang ? ' (°)' : '') + ' <input type="number" step="any" min="0" value="' + fd[1] + '" data-k="' + fd[0] + '" style="width:6.5em">';
      tin.appendChild(lab);
    });
    tin.querySelectorAll('input').forEach(function (i) { i.addEventListener('input', solve); });
    solve();
  }
  function solve() {
    var g = {};
    tin.querySelectorAll('input').forEach(function (i) { g[i.getAttribute('data-k')] = parseFloat(i.value); });
    var sols = T.solve(kindSel.value, g), h = '';
    if (!sols.length) {
      tout.innerHTML = '<p class="warn">No triangle has these measurements' + (kindSel.value === 'SSA' ? ': side a is too short to reach the other side.' : '.') + '</p>';
      tsvg.innerHTML = ''; return;
    }
    if (kindSel.value === 'SSA') h += '<p class="small">' + (sols.length === 2 ? '<b>Two triangles</b> fit: the ambiguous case. Side a can swing to either side of the foot of the height.' : 'Exactly one triangle fits.') + '</p>';
    sols.forEach(function (s, i) {
      h += (sols.length > 1 ? '<p class="label">Solution ' + (i + 1) + '</p>' : '') +
        '<div><span>a, b, c</span><span>' + f(s.a, 3) + ', ' + f(s.b, 3) + ', ' + f(s.c, 3) + '</span></div>' +
        '<div><span>A, B, C</span><span>' + f(s.A, 2) + '°, ' + f(s.B, 2) + '°, ' + f(s.C, 2) + '°</span></div>' +
        '<div><span>Area</span><span>' + f(s.area, 3) + '</span></div>';
    });
    tout.innerHTML = h;
    // draw: vertex A at origin, side c along the x axis to B, C above
    var shapes = sols.map(function (s) { return [[0, 0], [s.c, 0], [s.b * M.cos(s.A * M.PI / 180), s.b * M.sin(s.A * M.PI / 180)]]; });
    var xs = [], ys = [];
    shapes.forEach(function (p) { p.forEach(function (v) { xs.push(v[0]); ys.push(v[1]); }); });
    var x0 = M.min.apply(null, xs), x1 = M.max.apply(null, xs), y1 = M.max.apply(null, ys), k = M.min(340 / (x1 - x0 || 1), 240 / (y1 || 1));
    function P(v) { return [30 + (v[0] - x0) * k, 270 - v[1] * k]; }
    var cols = ['var(--flag-b)', 'var(--signal)'], svgh = '';
    shapes.forEach(function (p, i) {
      var q2 = p.map(P);
      svgh += '<polygon points="' + q2.map(function (v) { return v.join(','); }).join(' ') + '" fill="' + cols[i] + '" fill-opacity="0.12" stroke="' + cols[i] + '" stroke-width="2"' + (i ? ' stroke-dasharray="6 4"' : '') + '/>';
      svgh += '<text x="' + (q2[1][0] + 4) + '" y="' + (q2[1][1] + 16) + '" class="lbl">B' + (shapes.length > 1 ? (i + 1) : '') + '</text>';
    });
    var a = P(shapes[0][0]), cc = P(shapes[0][2]);
    svgh += '<text x="' + (a[0] - 18) + '" y="' + (a[1] + 16) + '" class="lbl">A</text><text x="' + (cc[0] + 6) + '" y="' + (cc[1] - 6) + '" class="lbl">C</text>';
    tsvg.innerHTML = svgh;
  }
  kindSel.addEventListener('change', inputs);
  inputs();
})();
