/* Supercoiling page: a closed ribbon (the DNA axis plus one edge) whose axis coils into an interwound (plectonemic)
   or toroidal supercoil. For a chosen ΔLk the ribbon is given just enough twist to close (dnamath.js ribbon), then
   writhe (Gauss integral of the axis), twist (from the frame) and the linking number of the two edges (Gauss
   integral, computed separately) are shown. Negative ΔLk: right-handed interwound or left-handed toroidal coils. */
(function () {
  'use strict';
  var D = window.RK_DNA, M = Math;
  var canvas = document.getElementById('sc'); if (!canvas) return;
  var lIn = document.getElementById('scl'), sIn = document.getElementById('scs'), q = document.getElementById('scq'), kind = 'plect';
  var N = 240, W = 0.28;
  function f(x, n) { return (x < -1e-9 ? '−' : '') + M.abs(x).toFixed(n === undefined ? 3 : n); }
  function model() {
    var lk = +lIn.value, s = +sIn.value, neg = lk <= 0, c;
    if (kind === 'plect') c = D.plectoneme(N, 6, 0.9, M.max(1, M.abs(lk)), s, neg ? 1 : -1);
    else c = D.toroid(N, 3.2, 1.25 * s, M.max(3, M.abs(lk) + 1), neg ? -1 : 1);
    var r = D.ribbon(c, lk, W);
    var edge2 = c.map(function (p, i) { return [p[0] - W * r.frame[i][0], p[1] - W * r.frame[i][1], p[2] - W * r.frame[i][2]]; });
    r.gauss = D.linking(r.edge, edge2);
    r.curve = c; r.edge2 = edge2; r.lk = lk;
    return r;
  }
  function readout(r) {
    document.getElementById('sclv').textContent = (r.lk > 0 ? '+' : r.lk < 0 ? '−' : '') + M.abs(r.lk);
    document.getElementById('scsv').textContent = M.round(+sIn.value * 100) + ' %';
    var hand = r.lk === 0 ? '' : kind === 'plect' ? (r.lk < 0 ? 'right-handed interwound' : 'left-handed interwound') : (r.lk < 0 ? 'left-handed toroidal' : 'right-handed toroidal');
    q.innerHTML = '<div><span>Linking number ΔLk (set)</span><span>' + f(r.lk, 0) + '</span></div>' +
      '<div><span>Writhe Wr (Gauss integral of the axis)</span><span>' + f(r.Wr) + '</span></div>' +
      '<div><span>Twist Tw (turning of the ribbon)</span><span>' + f(r.Tw) + '</span></div>' +
      '<div><span>Tw + Wr</span><span>' + f(r.Tw + r.Wr) + '</span></div>' +
      '<div><span>Check: linking of the two edges</span><span>' + f(r.gauss) + '</span></div>' +
      (hand ? '<div><span>Shape</span><span>' + hand + '</span></div>' : '');
  }
  if (!window.THREE) { readout(model()); return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }); }
  catch (e) { canvas.parentNode.insertAdjacentHTML('beforeend', '<p class="hint">3D view needs WebGL</p>'); readout(model()); return; }
  var scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(32, 1, 0.1, 400);
  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  var dl = new THREE.DirectionalLight(0xffffff, 0.5); dl.position.set(4, 8, 10); scene.add(dl);
  var controls = new THREE.OrbitControls(camera, canvas); controls.enablePan = false; controls.enableDamping = true;
  var group = new THREE.Group(); scene.add(group);
  function strip(a, b, color) {
    var pos = [], n = a.length;
    for (var i = 0; i < n; i++) {
      var j = (i + 1) % n;
      pos.push.apply(pos, a[i].concat(b[i], a[j], b[i], b[j], a[j]));
    }
    var g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
    return new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: color, side: THREE.DoubleSide }));
  }
  var lastKey = '', fitted = '';
  function build() {
    var r = model();
    readout(r);
    while (group.children.length) { var c = group.children.pop(); c.geometry.dispose(); }
    group.add(strip(r.curve, r.edge, 0xc8261d));
    group.add(strip(r.curve, r.edge2, 0x1d4f91));
    group.rotation.x = kind === 'toroid' ? -M.PI / 2 : 0;   // lay the ring flat so the coils are seen from an angle
    group.updateMatrixWorld(true);
    var key = kind + lIn.value;
    if (key !== fitted) {
      fitted = key;
      var box = new THREE.Box3().setFromObject(group), sph = box.getBoundingSphere(new THREE.Sphere());
      camera.position.set(sph.center.x + sph.radius * 0.6, sph.center.y + sph.radius * 1.8, sph.center.z + sph.radius * 3.4);
      controls.target.copy(sph.center); controls.update();
    }
  }
  function size() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== w * devicePixelRatio || canvas.height !== h * devicePixelRatio) { renderer.setPixelRatio(devicePixelRatio); renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  }
  function frame() { size(); controls.update(); renderer.render(scene, camera); requestAnimationFrame(frame); }
  window.RK_RENDER = function () { size(); renderer.render(scene, camera); return canvas; };
  var pend = 0;
  function sched() { if (!pend) pend = requestAnimationFrame(function () { pend = 0; build(); }); }
  document.querySelectorAll('.scf').forEach(function (b) {
    b.addEventListener('click', function () {
      kind = b.getAttribute('data-f');
      document.querySelectorAll('.scf').forEach(function (o) { var on = o === b; o.classList.toggle('ghost', !on); o.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      build();
    });
  });
  lIn.addEventListener('input', sched); sIn.addEventListener('input', sched);
  build(); frame();
})();
