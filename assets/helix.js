/* Double helix page: a schematic three.js model of A-, B- or Z-DNA built from the helical parameters in RK_FORMS
   (rise and twist per base pair, diameter). 1 unit = 1 nm; the helix axis is vertical. Backbones are tubes through
   the phosphate positions; each base pair is a rung coloured by its two bases. Not an atomic model. */
(function () {
  'use strict';
  var F = window.RK_FORMS, M = Math, D2R = M.PI / 180;
  var canvas = document.getElementById('hx'); if (!canvas) return;
  var q = document.getElementById('hxq'), nIn = document.getElementById('hxn'), form = 'B';
  var SEQ = 'ATGCGTACCATGGCAATCGTAGCTTACGGATCCGATTG', PAIR = { A: 'T', T: 'A', G: 'C', C: 'G' };
  var COL = { A: 0x2f7d4f, T: 0xc8261d, G: 0xe8b500, C: 0x1d4f91 };
  // groove asymmetry: angle (seen down the axis) between the two strands' phosphates at one base pair, minor-groove side
  var GAP = { A: 165, B: 150, Z: 150 }, SHIFT = { A: 0.45, B: 0, Z: 0.1 }, TILT = { A: 20, B: -6, Z: -7 };
  function fm() { for (var i = 0; i < F.length; i++) if (F[i].f === form) return F[i]; }
  function readout() {
    var f = fm(), n = +nIn.value;
    document.getElementById('hxnv').textContent = n;
    q.innerHTML = '<div><span>Hand</span><span>' + f.hand + '</span></div>' +
      '<div><span>Base pairs per turn</span><span>' + f.n + '</span></div>' +
      '<div><span>Rise · twist per bp</span><span>' + f.rise.toFixed(3) + ' nm · ' + f.twist.toFixed(1) + '°</span></div>' +
      '<div><span>Pitch · diameter</span><span>' + f.pitch.toFixed(2) + ' nm · ≈ ' + f.diam.toFixed(1) + ' nm</span></div>' +
      '<div><span>Shown</span><span>' + n + ' bp = ' + (n * f.rise).toFixed(2) + ' nm, ' + (n / f.n).toFixed(2) + ' turns</span></div>';
  }
  if (!window.THREE) { readout(); return; }
  var renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true }); }
  catch (e) { canvas.parentNode.insertAdjacentHTML('beforeend', '<p class="hint">3D view needs WebGL</p>'); readout(); return; }
  var scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(30, 0.75, 0.1, 200);
  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  var dl = new THREE.DirectionalLight(0xffffff, 0.6); dl.position.set(3, 5, 8); scene.add(dl);
  var controls = new THREE.OrbitControls(camera, canvas); controls.enablePan = false; controls.enableDamping = true;
  var group = new THREE.Group(); scene.add(group);
  function css(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function build() {
    while (group.children.length) { var c = group.children.pop(); c.geometry && c.geometry.dispose(); }
    var f = fm(), n = +nIn.value, rP = f.diam / 2 - 0.1, rB = rP * 0.62, gap = GAP[form] * D2R, s1 = [], s2 = [], a = 0;
    var seq = form === 'Z' ? 'CGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCG' : SEQ;
    var ink = new THREE.MeshLambertMaterial({ color: new THREE.Color(css('--ink') || '#14212b') });
    var ink2 = new THREE.MeshLambertMaterial({ color: new THREE.Color(css('--muted') || '#56646d') });
    for (var i = 0; i < n; i++) {
      var z = (i - (n - 1) / 2) * f.rise;
      // Z-DNA: the repeat is two base pairs, so the steps alternate (about −10° and −50°, averaging −30°) and the backbone zigzags
      var zz = form === 'Z' ? (i % 2 ? 0.08 : -0.08) : 0;
      s1.push(new THREE.Vector3((rP + zz) * M.cos(a), z, (rP + zz) * M.sin(a)));
      s2.push(new THREE.Vector3((rP - zz) * M.cos(a + gap), z, (rP - zz) * M.sin(a + gap)));
      var p1 = new THREE.Vector3(rB * M.cos(a), z, rB * M.sin(a)), p2 = new THREE.Vector3(rB * M.cos(a + gap), z, rB * M.sin(a + gap));
      var bis = new THREE.Vector3(M.cos(a + gap / 2), 0, M.sin(a + gap / 2)).multiplyScalar(SHIFT[form]);
      p1.add(bis); p2.add(bis);
      var half = p1.distanceTo(p2) / 2, dz = half * M.sin(TILT[form] * D2R);
      p1.y += dz; p2.y -= dz;
      var mid = p1.clone().add(p2).multiplyScalar(0.5), b1 = seq[i % seq.length], b2 = PAIR[b1];
      [[p1, mid, b1], [mid, p2, b2]].forEach(function (h) {
        var d = h[1].clone().sub(h[0]), L = d.length(), g = new THREE.CylinderGeometry(0.07, 0.07, L, 10);
        var m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: COL[h[2]] }));
        m.position.copy(h[0].clone().add(h[1]).multiplyScalar(0.5));
        m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize());
        group.add(m);
      });
      var step = form === 'Z' ? (i % 2 ? -50 : -10) : f.twist;
      a -= step * D2R;   // x = r cos a, z = r sin a with y up: a decreasing upward is right-handed
    }
    [[s1, ink], [s2, ink2]].forEach(function (s) {
      var curve = new THREE.CatmullRomCurve3(s[0]);
      group.add(new THREE.Mesh(new THREE.TubeGeometry(curve, s[0].length * 6, 0.11, 8, false), s[1]));
      s[0].forEach(function (p) { var b = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 8), s[1]); b.position.copy(p); group.add(b); });
    });
    var ax = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, -n * f.rise / 2 - 0.3, 0), new THREE.Vector3(0, n * f.rise / 2 + 0.3, 0)]);
    group.add(new THREE.Line(ax, new THREE.LineDashedMaterial({ color: new THREE.Color(css('--muted') || '#56646d'), dashSize: 0.15, gapSize: 0.1 })));
    group.children[group.children.length - 1].computeLineDistances();
    var H = M.max(n * f.rise, 3);
    camera.position.set(H * 1.25, H * 0.25, H * 1.7); controls.target.set(0, 0, 0); controls.update();
    readout();
  }
  function size() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== w * devicePixelRatio || canvas.height !== h * devicePixelRatio) { renderer.setPixelRatio(devicePixelRatio); renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
  }
  function frame() { size(); controls.update(); renderer.render(scene, camera); requestAnimationFrame(frame); }
  window.RK_RENDER = function () { size(); renderer.render(scene, camera); return canvas; };
  document.querySelectorAll('.hxf').forEach(function (b) {
    b.addEventListener('click', function () {
      form = b.getAttribute('data-f');
      document.querySelectorAll('.hxf').forEach(function (o) { var on = o === b; o.classList.toggle('ghost', !on); o.setAttribute('aria-pressed', on ? 'true' : 'false'); });
      build();
    });
  });
  nIn.addEventListener('input', build);
  build(); frame();
})();
