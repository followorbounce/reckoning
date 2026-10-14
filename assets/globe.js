/* Latitude and longitude page: a three.js globe with Natural Earth coastlines, the graticule and the
   special parallels; tap to read a position. Position (φ, λ) maps to (cos φ sin λ, sin φ, cos φ cos λ),
   so the prime meridian faces the viewer at the start and east is to the right. */
(function () {
  'use strict';
  var N = window.RK_NAV, A = window.RK_ASTRO, M = Math, D2R = M.PI / 180;
  var canvas = document.getElementById('globe'); if (!canvas) return;
  var latIn = document.getElementById('glat'), lonIn = document.getElementById('glon'), q = document.getElementById('gq');
  function css(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function v3(lat, lon, r) { r = r || 1; return new THREE.Vector3(r * M.cos(lat * D2R) * M.sin(lon * D2R), r * M.sin(lat * D2R), r * M.cos(lat * D2R) * M.cos(lon * D2R)); }

  // ---------------------------------------------------------------- table of minute lengths (no WebGL needed)
  var mt = document.getElementById('mtab');
  if (mt) {
    var h = '';
    for (var la = 0; la <= 90; la += 10) {
      var m = N.minuteLengths(la), g = N.geocentric(la);
      h += '<tr><td class="num">' + la + '°</td><td class="num">' + m.lat.toFixed(1) + ' m</td><td class="num">' + m.lon.toFixed(1) + ' m</td><td class="num">' + (la === 90 ? '90°' : N.fmtDM(g, '', '')) + '</td></tr>';
    }
    mt.innerHTML = h;
  }

  var eps = A.sun(A.jd(new Date())).eps0;   // mean obliquity of the ecliptic now
  var sel = { lat: +latIn.value, lon: +lonIn.value };
  function readout() {
    var la = sel.lat, lo = sel.lon, m = N.minuteLengths(la), zd = -M.round(lo / 15);
    var letters = { 0: 'Z' }; 'ABCDEFGHIKLM'.split('').forEach(function (c, i) { letters[-(i + 1)] = c; }); 'NOPQRSTUVWXY'.split('').forEach(function (c, i) { letters[i + 1] = c; });
    if (zd === 12 && lo > 0) zd = -12;
    var gw = [51.4779, -0.0015], d = N.haversine([la, lo], gw);
    q.innerHTML = '<div><span>Navigator</span><span>' + N.fmtDM(la, 'N', 'S') + '  ' + N.fmtDM(lo, 'E', 'W') + '</span></div>' +
      '<div><span>Degrees, minutes, seconds</span><span>' + N.fmtDMS(la, 'N', 'S') + '  ' + N.fmtDMS(lo, 'E', 'W') + '</span></div>' +
      '<div><span>Decimal degrees</span><span>' + la.toFixed(4) + ', ' + lo.toFixed(4) + '</span></div>' +
      '<div><span>1′ of latitude here</span><span>' + m.lat.toFixed(1) + ' m</span></div>' +
      '<div><span>1′ of longitude here</span><span>' + m.lon.toFixed(1) + ' m</span></div>' +
      '<div><span>Geocentric latitude</span><span>' + N.fmtDM(N.geocentric(la), 'N', 'S') + '</span></div>' +
      '<div><span>Time zone at sea</span><span>' + (zd > 0 ? '+' : zd < 0 ? '−' : '') + M.abs(zd) + ' (' + letters[zd] + ')</span></div>' +
      '<div><span>Great circle to Greenwich</span><span>' + M.round(d).toLocaleString('en-US') + ' nmi</span></div>';
  }

  if (!window.THREE) { readout(); return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }); }
  catch (e) { canvas.parentNode.insertAdjacentHTML('beforeend', '<p class="hint">3D view needs WebGL</p>'); readout(); return; }
  var scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
  camera.position.set(0, 0, 4.4);
  var controls = new THREE.OrbitControls(camera, canvas);
  controls.enablePan = false; controls.minDistance = 2.2; controls.maxDistance = 8; controls.enableDamping = true;
  var earth = new THREE.Group(); scene.add(earth);
  var ocean = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 48), new THREE.MeshBasicMaterial({ color: new THREE.Color(css('--tint') || '#e7ecec') }));
  earth.add(ocean);
  function line(pts, color, width, opacity) {
    var g = new THREE.BufferGeometry().setFromPoints(pts);
    return new THREE.Line(g, new THREE.LineBasicMaterial({ color: new THREE.Color(color), transparent: opacity < 1, opacity: opacity }));
  }
  function parallel(lat, color, op) { var p = []; for (var lo = -180; lo <= 180; lo += 2) p.push(v3(lat, lo, 1.003)); earth.add(line(p, color, 1, op)); }
  function meridian(lon, color, op) { var p = []; for (var la = -90; la <= 90; la += 2) p.push(v3(la, lon, 1.003)); earth.add(line(p, color, 1, op)); }
  var muted = css('--muted') || '#56646d';
  for (var la = -75; la <= 75; la += 15) if (la) parallel(la, muted, 0.35);
  for (var lo = -165; lo <= 180; lo += 15) if (lo !== 0 && lo !== 180) meridian(lo, muted, 0.35);
  parallel(0, css('--signal') || '#c8261d', 1);
  [eps, -eps, 90 - eps, -(90 - eps)].forEach(function (l) { parallel(l, css('--flag-y') || '#e8b500', 1); });
  meridian(0, css('--flag-b') || '#1d4f91', 1); meridian(180, css('--flag-b') || '#1d4f91', 1);
  fetch('../../assets/land.json').then(function (r) { return r.json(); }).then(function (rings) {
    var pos = [];
    rings.forEach(function (ring) {
      for (var i = 1; i < ring.length; i++) {
        var a = v3(ring[i - 1][1], ring[i - 1][0], 1.002), b = v3(ring[i][1], ring[i][0], 1.002);
        pos.push(a.x, a.y, a.z, b.x, b.y, b.z);
      }
    });
    var g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    earth.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: new THREE.Color(css('--ink') || '#14212b') })));
  }).catch(function () { /* coastlines are optional */ });
  var marker = new THREE.Mesh(new THREE.SphereGeometry(0.025, 16, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(css('--signal') || '#c8261d') }));
  earth.add(marker);
  var axis = line([new THREE.Vector3(0, -1.25, 0), new THREE.Vector3(0, 1.25, 0)], css('--ink') || '#14212b', 1, 0.6); earth.add(axis);

  // turn the camera so the selected point faces the viewer
  var target = null;
  function place(face) {
    marker.position.copy(v3(sel.lat, sel.lon, 1.01));
    if (face) target = v3(M.max(-80, M.min(80, sel.lat)), sel.lon, camera.position.length());
    readout();
  }
  function resize() {
    var w = canvas.parentNode.clientWidth, hgt = canvas.parentNode.clientHeight || w;
    renderer.setPixelRatio(M.min(2, window.devicePixelRatio || 1)); renderer.setSize(w, hgt, false);
    camera.aspect = w / hgt; camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize); resize();
  function render() { renderer.render(scene, camera); }
  window.RK_RENDER = render;
  (function loop() {
    requestAnimationFrame(loop);
    if (target) {
      var p = camera.position.clone().lerp(target, 0.12).setLength(camera.position.length());
      camera.position.copy(p); camera.lookAt(0, 0, 0);
      if (p.distanceTo(target) < 0.01) target = null;
    }
    controls.update(); render();
  })();

  // tap to read (a drag of more than a few pixels turns the globe instead)
  var ray = new THREE.Raycaster(), down = null;
  canvas.addEventListener('pointerdown', function (e) { down = [e.clientX, e.clientY]; });
  canvas.addEventListener('pointerup', function (e) {
    if (!down || M.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) { down = null; return; }
    down = null;
    var r = canvas.getBoundingClientRect(), p = new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
    ray.setFromCamera(p, camera);
    var hit = ray.intersectObject(ocean)[0];
    if (!hit) return;
    var v = hit.point.clone().normalize();
    sel.lat = M.asin(v.y) / D2R; sel.lon = M.atan2(v.x, v.z) / D2R;
    latIn.value = sel.lat.toFixed(2); lonIn.value = sel.lon.toFixed(2);
    place(false);
  });
  function fromInputs() {
    var la = parseFloat(latIn.value), lo = parseFloat(lonIn.value);
    if (!isFinite(la) || !isFinite(lo)) return;
    sel.lat = M.max(-90, M.min(90, la)); sel.lon = N.wrap180(lo); place(true);
  }
  latIn.addEventListener('change', fromInputs); lonIn.addEventListener('change', fromInputs);
  document.querySelectorAll('[data-ll]').forEach(function (b) {
    b.addEventListener('click', function () { var p = b.getAttribute('data-ll').split(','); latIn.value = p[0]; lonIn.value = p[1]; fromInputs(); });
  });
  place(true);
})();
