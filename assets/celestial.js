/* Celestial sphere page: a three.js sky with the celestial equator, hour circles, the ecliptic and the Sun
   for a chosen day; the ecliptic band of signs against constellations; this year's dates.
   Equatorial (α, δ) maps to (cos δ cos α, sin δ, −cos δ sin α): north is up, right ascension runs
   anticlockwise seen from the north celestial pole. */
(function () {
  'use strict';
  var A = window.RK_ASTRO, M = Math, D2R = M.PI / 180;
  A.setBounds(window.RK_CONST);
  var NAMES = window.RK_CNAMES, SIGNS = window.RK_SIGNS;
  var y = new Date().getUTCFullYear(), j0 = A.jdCal(y, 1, 1), days = M.round(A.jdCal(y + 1, 1, 1) - j0);
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function css(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function dstr(j) { var d = A.dateFromJd(j); return d.getUTCDate() + ' ' + MON[d.getUTCMonth()]; }
  function hm(deg) { var t = M.round(deg / 15 * 60), h = M.floor(t / 60) % 24, m = t % 60; return h + 'h ' + String(m).padStart(2, '0') + 'm'; }
  var epsNow = A.sun(A.jd(new Date())).eps0;

  // ---------------------------------------------------------------- the ecliptic band and the tables
  var spans = [], prev = null, start = 0;
  for (var l = 0; l <= 360; l += 0.05) {
    var q = A.eclToEq(l % 360, 0, epsNow), c = A.constellation(q.ra, q.dec, y);
    if (c !== prev) { if (prev) spans.push([prev, start, l]); prev = c; start = l; }
  }
  spans.push([prev, start, 360]);
  if (spans.length > 1 && spans[0][0] === spans[spans.length - 1][0]) { var last = spans.pop(); spans[0] = [last[0], last[1] - 360, spans[0][2]]; }
  var band = document.getElementById('band');
  function drawBand(lam) {
    var X = function (v) { return 20 + v / 360 * 960; }, g = '';
    SIGNS.forEach(function (s, i) {
      g += '<rect x="' + X(i * 30) + '" y="30" width="' + (960 / 12) + '" height="44" class="b-sign' + (i % 2 ? ' alt' : '') + '"/>' +
        '<text x="' + X(i * 30 + 15) + '" y="50" text-anchor="middle" font-size="18">' + s[1] + '︎</text><text x="' + X(i * 30 + 15) + '" y="67" text-anchor="middle" font-size="10">' + s[0] + '</text>';
    });
    spans.forEach(function (s, i) {
      var a = s[1], b = s[2], pieces = a < 0 ? [[a + 360, 360], [0, b]] : [[a, b]];
      pieces.forEach(function (p) {
        g += '<rect x="' + X(p[0]) + '" y="82" width="' + (X(p[1]) - X(p[0])) + '" height="44" class="b-con' + (i % 2 ? ' alt' : '') + (s[0] === 'Oph' ? ' oph' : '') + '"/>';
      });
      var mid = (a + b) / 2; if (mid < 0) mid += 360;
      if (b - a > 6) g += '<text x="' + X(mid) + '" y="108" text-anchor="middle" font-size="11">' + (NAMES[s[0]] || s[0]) + '</text>';
      else g += '<text x="' + X(mid) + '" y="140" text-anchor="middle" font-size="10">' + s[0] + '</text>';
    });
    g += '<text x="20" y="22" font-size="11">Signs: 12 × 30° from the March equinox</text><text x="20" y="160" font-size="11">Constellations on the ecliptic (IAU boundaries, ' + y + ')</text>';
    if (lam !== undefined) g += '<line x1="' + X(lam) + '" x2="' + X(lam) + '" y1="26" y2="130" stroke="var(--signal)" stroke-width="3"/><circle cx="' + X(lam) + '" cy="26" r="7" fill="var(--flag-y)" stroke="var(--signal)"/>';
    band.innerHTML = g;
  }
  var tr = A.sunTransits(y), ctab = document.getElementById('ctab');
  if (ctab) {
    var first = tr[0], rows = '';
    tr.forEach(function (t, i) {
      var nxt = i + 1 < tr.length ? tr[i + 1].jd : first.jd + (A.jdCal(y + 1, 1, 1) - j0);
      rows += '<tr' + (t.to === 'Oph' ? ' class="hl"' : '') + '><td><b>' + (NAMES[t.to] || t.to) + '</b> <span class="mono small">' + t.to + '</span></td><td class="num">' + dstr(t.jd) + '</td><td class="num">' + M.round(nxt - t.jd) + '</td></tr>';
    });
    ctab.innerHTML = rows;
  }
  document.querySelectorAll('[data-sign]').forEach(function (td) {
    var i = +td.getAttribute('data-sign'), lam = i * 30, guess = j0 + ((lam - 280 + 360) % 360) / 0.9856;
    td.textContent = dstr(A.sunAtLongitude(lam, guess));
  });

  // ---------------------------------------------------------------- the day slider and the readout
  var sl = document.getElementById('cday'), slv = document.getElementById('cdayv'), cq = document.getElementById('cq');
  var todayIdx = M.max(0, M.min(days - 1, M.floor(A.jd(new Date()) - j0)));
  sl.max = days - 1; sl.value = todayIdx;
  var sunMesh = null;
  function update() {
    var j = j0 + (+sl.value) + 0.5, s = A.sun(j), con = A.constellation(s.ra, s.dec, A.year(j));
    slv.textContent = dstr(j);
    cq.innerHTML = '<div><span>Ecliptic longitude λ</span><span>' + s.lon.toFixed(2) + '°</span></div>' +
      '<div><span>Right ascension α</span><span>' + hm(s.ra) + '</span></div>' +
      '<div><span>Declination δ</span><span>' + (s.dec >= 0 ? '+' : '−') + M.abs(s.dec).toFixed(2) + '°</span></div>' +
      '<div><span>Sign (30° division)</span><span>' + SIGNS[M.floor(s.lon / 30) % 12][1] + '︎ ' + SIGNS[M.floor(s.lon / 30) % 12][0] + ' ' + (s.lon % 30).toFixed(1) + '°</span></div>' +
      '<div><span>In front of</span><span>' + (NAMES[con] || con) + '</span></div>' +
      '<div><span>Obliquity ε</span><span>' + s.eps0.toFixed(4) + '°</span></div>';
    drawBand(s.lon);
    if (sunMesh) sunMesh.position.copy(eq(s.ra, s.dec, 1));
  }
  function eq(ra, dec, r) { return new THREE.Vector3(r * M.cos(dec * D2R) * M.cos(ra * D2R), r * M.sin(dec * D2R), -r * M.cos(dec * D2R) * M.sin(ra * D2R)); }
  sl.addEventListener('input', update);
  document.getElementById('ctoday').addEventListener('click', function () { sl.value = todayIdx; update(); });

  // ---------------------------------------------------------------- 3D sphere
  var canvas = document.getElementById('celes');
  if (!window.THREE || !canvas) { update(); return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }); }
  catch (e) { canvas.parentNode.insertAdjacentHTML('beforeend', '<p class="hint">3D view needs WebGL</p>'); update(); return; }
  var scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(34, 1, 0.1, 50);
  camera.position.set(2.6, 1.5, 3.0); camera.lookAt(0, 0, 0);
  var controls = new THREE.OrbitControls(camera, canvas); controls.enablePan = false; controls.minDistance = 2.4; controls.maxDistance = 9; controls.enableDamping = true;
  function lineOf(pts, color, op) { return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: new THREE.Color(color), transparent: op < 1, opacity: op })); }
  var blue = css('--flag-b') || '#1d4f91', red = css('--signal') || '#c8261d', ink = css('--ink') || '#14212b', yel = css('--flag-y') || '#e8b500';
  var shell = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), new THREE.MeshBasicMaterial({ color: new THREE.Color(css('--tint') || '#e7ecec'), transparent: true, opacity: 0.25, side: THREE.BackSide }));
  scene.add(shell);
  var i, pts;
  pts = []; for (i = 0; i <= 360; i += 2) pts.push(eq(i, 0, 1)); scene.add(lineOf(pts, blue, 1));
  [-60, -30, 30, 60].forEach(function (d) { var p = []; for (var a = 0; a <= 360; a += 3) p.push(eq(a, d, 1)); scene.add(lineOf(p, blue, 0.25)); });
  for (var h = 0; h < 24; h += 2) { var p2 = []; for (var d = -90; d <= 90; d += 3) p2.push(eq(h * 15, d, 1)); scene.add(lineOf(p2, blue, h % 6 ? 0.25 : 0.55)); }
  pts = []; for (i = 0; i <= 360; i += 2) { var e = A.eclToEq(i, 0, epsNow); pts.push(eq(e.ra, e.dec, 1.002)); } scene.add(lineOf(pts, red, 1));
  // ticks every 30° on the ecliptic
  for (i = 0; i < 360; i += 30) { var e1 = A.eclToEq(i, 0, epsNow); var a1 = eq(e1.ra, e1.dec, 0.96), a2 = eq(e1.ra, e1.dec, 1.04); scene.add(lineOf([a1, a2], red, 1)); }
  scene.add(lineOf([new THREE.Vector3(0, -1.2, 0), new THREE.Vector3(0, 1.2, 0)], ink, 0.7));
  var earth = new THREE.Mesh(new THREE.SphereGeometry(0.12, 24, 16), new THREE.MeshBasicMaterial({ color: new THREE.Color(blue) })); scene.add(earth);
  sunMesh = new THREE.Mesh(new THREE.SphereGeometry(0.06, 20, 14), new THREE.MeshBasicMaterial({ color: new THREE.Color(yel) })); scene.add(sunMesh);
  function label(text, pos, color, size) {
    var cv = document.createElement('canvas'), ctx = cv.getContext('2d'), fs = 44;
    ctx.font = '600 ' + fs + 'px "IBM Plex Mono", monospace';
    var w = M.ceil(ctx.measureText(text).width) + 16; cv.width = w; cv.height = fs + 16;
    ctx.font = '600 ' + fs + 'px "IBM Plex Mono", monospace'; ctx.fillStyle = color; ctx.textBaseline = 'middle'; ctx.fillText(text, 8, cv.height / 2);
    var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(cv), transparent: true, depthTest: false }));
    var s = size || 0.1; sp.scale.set(s * w / cv.height, s, 1); sp.position.copy(pos); scene.add(sp);
  }
  label('North celestial pole', new THREE.Vector3(0, 1.3, 0), ink, 0.08);
  label('March equinox ♈︎', eq(0, 0, 1.18), red, 0.08);
  label('September equinox', eq(180, 0, 1.18), red, 0.08);
  var js = A.eclToEq(90, 0, epsNow), jw = A.eclToEq(270, 0, epsNow);
  label('June solstice', eq(js.ra, js.dec, 1.16), red, 0.07);
  label('December solstice', eq(jw.ra, jw.dec, 1.16), red, 0.07);
  for (h = 0; h < 24; h += 6) label(h + 'h', eq(h * 15, 0, 1.08), blue, 0.07);
  label('equator', eq(105, -4, 1.06), blue, 0.06); label('ecliptic', (function () { var e2 = A.eclToEq(140, 0, epsNow); return eq(e2.ra, e2.dec + 4, 1.06); })(), red, 0.06);
  function resize() { var w = canvas.parentNode.clientWidth, hh = canvas.parentNode.clientHeight || w; renderer.setPixelRatio(M.min(2, window.devicePixelRatio || 1)); renderer.setSize(w, hh, false); camera.aspect = w / hh; camera.updateProjectionMatrix(); }
  window.addEventListener('resize', resize); resize();
  window.RK_RENDER = function () { renderer.render(scene, camera); };
  (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
  update();
})();
