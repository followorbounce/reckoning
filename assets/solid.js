/* Reckoning solids: three.js r128 geometry built from the live parameters. Solids of
   revolution are lathed from their profile; polyhedra are built from their vertices.
   Hollow solids are shown with a quarter cut away so the cavity or hole is visible. */
(function () {
  'use strict';
  var host = document.getElementById('fig3d');
  if (!host || !window.THREE) return;
  var T = THREE, M = Math, PI = M.PI;
  var renderer;
  try { renderer = new T.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true }); }
  catch (e) { host.innerHTML = '<p class="hint">3D view needs WebGL.</p>'; return; }
  renderer.setPixelRatio(M.min(2, window.devicePixelRatio || 1));
  host.appendChild(renderer.domElement);
  var scene = new T.Scene(), camera = new T.PerspectiveCamera(30, 4 / 3, 0.1, 200);
  var controls = new T.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.enablePan = false;
  scene.add(new T.HemisphereLight(0xffffff, 0x8899aa, 0.85));
  var key = new T.DirectionalLight(0xffffff, 0.75); key.position.set(4, 6, 5); scene.add(key);
  var group = new T.Group(); scene.add(group);
  function css(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function mats() {
    var c = new T.Color(css('--flag-b') || '#1d4f91');
    return {
      body: new T.MeshStandardMaterial({ color: c, roughness: 0.55, metalness: 0.05, side: T.DoubleSide, transparent: true, opacity: 0.9, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }),
      cut: new T.MeshStandardMaterial({ color: new T.Color(css('--flag-y') || '#e8b500'), roughness: 0.8, side: T.DoubleSide }),
      edge: new T.LineBasicMaterial({ color: new T.Color(css('--ink') || '#14212b') })
    };
  }
  var MAT = mats();
  function lathe(profile, phi0, phiLen, n) {
    return new T.LatheGeometry(profile.map(function (p) { return new T.Vector2(p[0], p[1]); }), n || 96, phi0 || 0, phiLen === undefined ? 2 * PI : phiLen);
  }
  function arc(r, a0, a1, n, cy) { var p = []; n = n || 48; for (var i = 0; i <= n; i++) { var a = a0 + (a1 - a0) * i / n; p.push([r * M.sin(a), (cy || 0) - r * M.cos(a)]); } return p; }
  function polyGeo(verts, faces) {
    var pos = [];
    faces.forEach(function (f) { for (var i = 1; i < f.length - 1; i++) [f[0], f[i], f[i + 1]].forEach(function (k) { pos.push(verts[k][0], verts[k][1], verts[k][2]); }); });
    var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); g.computeVertexNormals(); return g;
  }
  function halfDisc(profile, phi) {
    // flat face in the plane at angle phi from a closed (r, y) profile
    var s = new T.Shape(profile.map(function (p) { return new T.Vector2(p[0], p[1]); }));
    var g = new T.ShapeGeometry(s, 48); g.rotateY(phi - PI / 2); return g;   /* lathe angle phi = rotation + 90° */
  }
  function add(g, mat, edges) {
    var m = new T.Mesh(g, mat); group.add(m);
    if (edges) group.add(new T.LineSegments(new T.EdgesGeometry(g, 25), MAT.edge));
    return m;
  }
  function box(a, b, c) { return new T.BoxGeometry(a, c, b); }

  function build(slug, v) {
    while (group.children.length) { var o = group.children.pop(); if (o.geometry) o.geometry.dispose(); }
    var g, h, R, r;
    switch (slug) {
      case 'cube': add(box(v.a, v.a, v.a), MAT.body, true); break;
      case 'cuboid': add(box(v.a, v.b, v.c), MAT.body, true); break;
      case 'prism': R = v.s / (2 * M.sin(PI / M.round(v.n))); add(new T.CylinderGeometry(R, R, v.h, M.round(v.n)), MAT.body, true); break;
      case 'pyramid': g = new T.ConeGeometry(v.a / M.SQRT2, v.h, 4); g.rotateY(PI / 4); add(g, MAT.body, true); break;
      case 'frustum-pyramid': g = new T.CylinderGeometry(v.b / M.SQRT2, v.a / M.SQRT2, v.h, 4); g.rotateY(PI / 4); add(g, MAT.body, true); break;
      case 'wedge': (function () { var a = v.a / 2, b = v.b / 2, c = v.c / 2, H = v.h, y0 = -H / 2;
        var P = [[-a, y0, -b], [a, y0, -b], [a, y0, b], [-a, y0, b], [-c, y0 + H, 0], [c, y0 + H, 0]];
        add(polyGeo(P, [[0, 1, 2, 3], [0, 4, 5, 1], [3, 2, 5, 4], [0, 3, 4], [1, 5, 2]]), MAT.body, true); })(); break;
      case 'prismoid': (function () { var y0 = -v.h / 2, y1 = v.h / 2, A = v.a1 / 2, B = v.b1 / 2, C = v.a2 / 2, D = v.b2 / 2;
        var P = [[-A, y0, -B], [A, y0, -B], [A, y0, B], [-A, y0, B], [-C, y1, -D], [C, y1, -D], [C, y1, D], [-C, y1, D]];
        add(polyGeo(P, [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]), MAT.body, true); })(); break;
      case 'cylinder': add(new T.CylinderGeometry(v.r, v.r, v.h, 96), MAT.body, false); break;
      case 'tube': R = v.R; r = M.min(v.r, v.R * 0.98); h = v.h / 2;
        add(lathe([[R, -h], [R, h], [r, h], [r, -h], [R, -h]], PI / 2, 1.5 * PI), MAT.body);
        [PI / 2, 2 * PI].forEach(function (ph) { add(halfDisc([[r, -h], [R, -h], [R, h], [r, h]], ph), MAT.cut); }); break;
      case 'truncated-cylinder': (function () { g = new T.CylinderGeometry(v.r, v.r, 1, 96, 1, false); var p = g.attributes.position;
        for (var i = 0; i < p.count; i++) { var x = p.getX(i), y = p.getY(i); var top = (v.h1 + v.h2) / 2 + (v.h2 - v.h1) / 2 * x / v.r; p.setY(i, y > 0 ? top - (v.h1 + v.h2) / 4 : -(v.h1 + v.h2) / 4); }
        g.computeVertexNormals(); add(g, MAT.body); })(); break;
      case 'cone': add(new T.ConeGeometry(v.r, v.h, 96), MAT.body); break;
      case 'frustum-cone': add(new T.CylinderGeometry(v.r, v.R, v.h, 96), MAT.body); break;
      case 'sphere': add(new T.SphereGeometry(v.r, 96, 64), MAT.body); break;
      case 'spherical-cap': (function () { var y0 = v.r - M.min(v.h, 2 * v.r), a0 = M.acos(M.max(-1, M.min(1, y0 / v.r))), prof = [[0, y0]];
        for (var i = 0; i <= 48; i++) { var a = a0 - a0 * i / 48; prof.push([v.r * M.sin(a), v.r * M.cos(a)]); }
        add(lathe(prof), MAT.body);
        add(new T.SphereGeometry(v.r, 48, 32), new T.MeshBasicMaterial({ color: new T.Color(css('--muted')), wireframe: true, transparent: true, opacity: 0.12 })); })(); break;
      case 'spherical-zone': (function () { var z1 = M.max(-v.r, M.min(v.r, v.z1)), z2 = M.max(-v.r, M.min(v.r, v.z2)), prof = [[0, z1]];
        for (var i = 0; i <= 48; i++) { var z = z1 + (z2 - z1) * i / 48; prof.push([M.sqrt(M.max(v.r * v.r - z * z, 0)), z]); }
        add(lathe(prof.concat([[0, z2]])), MAT.body);
        add(new T.SphereGeometry(v.r, 48, 32), new T.MeshBasicMaterial({ color: new T.Color(css('--muted')), wireframe: true, transparent: true, opacity: 0.12 })); })(); break;
      case 'spherical-sector': (function () { var c = M.max(-1, M.min(1, (v.r - v.h) / v.r)), a0 = M.acos(c), prof = [[0, 0]];
        for (var i = 0; i <= 48; i++) { var a = a0 - a0 * i / 48; prof.push([v.r * M.sin(a), v.r * M.cos(a)]); }
        add(lathe(prof), MAT.body); })(); break;
      case 'spherical-wedge': (function () { var t = v.t * PI / 180, prof = [];
        for (var i = 0; i <= 64; i++) { var a = PI * i / 64; prof.push([v.r * M.sin(a), -v.r * M.cos(a)]); }
        add(lathe(prof, 0, t), MAT.body);
        var half = prof.concat([[0, v.r], [0, -v.r]]);
        add(halfDisc(half, 0), MAT.cut); add(halfDisc(half, t), MAT.cut);
        group.rotation.y = M.atan2(0.55, 0.72) - (t / 2 + 1.25); })(); break;
      case 'hollow-sphere': (function () { R = v.R; r = M.min(v.r, v.R * 0.98); var outer = [], inner = [];
        for (var i = 0; i <= 64; i++) { var a = PI * i / 64; outer.push([R * M.sin(a), -R * M.cos(a)]); inner.push([r * M.sin(a), -r * M.cos(a)]); }
        add(lathe(outer, PI / 2, 1.5 * PI), MAT.body); add(lathe(inner, PI / 2, 1.5 * PI), MAT.body);
        var face = outer.concat(inner.slice().reverse());
        [PI / 2, 2 * PI].forEach(function (ph) { add(halfDisc(face, ph), MAT.cut); }); })(); break;
      case 'ellipsoid': g = new T.SphereGeometry(1, 96, 64); g.scale(v.a, v.c, v.b); add(g, MAT.body); break;
      case 'torus': add(new T.TorusGeometry(v.R, M.min(v.r, v.R * 0.99), 48, 128), MAT.body); group.rotation.x = -PI / 2.6; break;
      case 'square-ring': (function () { var w = v.w / 2, a = M.max(v.R - w, 0.01), b = v.R + w;
        add(lathe([[a, -w], [b, -w], [b, w], [a, w], [a, -w]], PI / 2, 1.5 * PI), MAT.body);
        [PI / 2, 2 * PI].forEach(function (ph) { add(halfDisc([[a, -w], [b, -w], [b, w], [a, w]], ph), MAT.cut); }); })(); break;
      case 'barrel': (function () { var prof = [[0, -v.h / 2]];
        for (var i = 0; i <= 48; i++) { var z = -v.h / 2 + v.h * i / 48; prof.push([v.D / 2 - (v.D - v.d) / 2 * M.pow(2 * z / v.h, 2), z]); }
        add(lathe(prof.concat([[0, v.h / 2]])), MAT.body); })(); break;
    }
    if (slug !== 'torus') group.rotation.x = 0;
    if (slug !== 'spherical-wedge') group.rotation.y = 0;
  }
  var fitted = false;
  function fit() {
    var bb = new T.Box3().setFromObject(group), sph = bb.getBoundingSphere(new T.Sphere()), c = sph.center;
    var d = sph.radius / M.sin(camera.fov * PI / 360) * 1.08;
    var dir = new T.Vector3(0.55, 0.42, 0.72).normalize();
    camera.position.copy(c).addScaledVector(dir, d); controls.target.copy(c); controls.update();
  }
  function size() { var w = host.clientWidth, h = host.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  window.RK_SOLID = function (slug, v, ok) {
    build(slug, v);
    group.children.forEach(function (m) { if (m.material && m.material.opacity !== undefined && m.material === MAT.body) m.material.opacity = ok ? 0.9 : 0.3; });
    if (!fitted) { size(); fit(); fitted = true; }
  };
  window.addEventListener('resize', size);
  var refit = document.getElementById('refit');
  if (refit) refit.addEventListener('click', fit);
  window.RK_RENDER = function () { controls.update(); renderer.render(scene, camera); };
  (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
})();
