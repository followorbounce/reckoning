/* Light room: the optical bench. One canvas engine (draw, drag, trace with assets/optics.js) and one setup per page,
   chosen by data-page on the .bench figure. Every number shown comes from the tracer or from the closed forms that
   tests/check_wave5.js checks against it. World units are millimetres, y up. */
(function () {
  'use strict';
  var O = window.RK_OPTICS, M = Math, R2D = 180 / M.PI;
  var fig = document.querySelector('.figure.bench');
  if (!fig || !O) return;
  var cv = fig.querySelector('canvas'), ctx = cv.getContext('2d');
  var $ = function (id) { return document.getElementById(id); };
  var PAGE = fig.getAttribute('data-page');

  // colour weights so that the traced "white" wavelengths add up to white
  var WSUM = [0, 0, 0];
  O.WHITE.forEach(function (l) { var c = O.rgb(l); WSUM[0] += c[0]; WSUM[1] += c[1]; WSUM[2] += c[2]; });
  function rayColour(lam, white) {
    var c = O.rgb(lam);
    if (white) return [c[0] * 765 / WSUM[0], c[1] * 765 / WSUM[1], c[2] * 765 / WSUM[2]];   // 3× so a split spectrum stays visible; overlaps saturate to white
    var m = M.max(c[0], c[1], c[2], 1);
    return [c[0] * 255 / m, c[1] * 255 / m, c[2] * 255 / m];
  }

  // ---------------------------------------------------------------- bench state
  var B = { scene: [], sources: [], view: { cx: 0, cy: 0, w: 300 }, minI: 0.02, gain: 1, overlay: null, readout: null,
    filter: null, sel: null, locked: false, lastRes: [] };
  var W = 0, H = 0, DPR = 1, S = 1;   // canvas px, device pixel ratio, px per mm
  function size() {
    var r = cv.getBoundingClientRect();
    DPR = M.min(window.devicePixelRatio || 1, 2);
    W = M.max(1, M.round(r.width * DPR)); H = M.max(1, M.round(r.height * DPR));
    cv.width = W; cv.height = H; S = W / B.view.w;
  }
  function px(x, y) { return [W / 2 + (x - B.view.cx) * S, H / 2 - (y - B.view.cy) * S]; }
  function world(X, Y) { return [B.view.cx + (X - W / 2) / S, B.view.cy - (Y - H / 2) / S]; }
  function box() { var a = world(0, H), b = world(W, 0); return [a[0] - 5, a[1] - 5, b[0] + 5, b[1] + 5]; }

  // rays of a source: {type: beam|point|laser, x, y, ang (deg), width, spread (deg), n, white, lam}
  function emit(s) {
    var out = [], a = s.ang / R2D, d = [M.cos(a), M.sin(a)], k;
    if (s.type === 'laser') out.push([s.x, s.y, d[0], d[1]]);
    else if (s.type === 'beam') for (k = 0; k < s.n; k++) {
      var off = s.n === 1 ? 0 : -s.width / 2 + s.width * k / (s.n - 1);
      out.push([s.x - d[1] * off, s.y + d[0] * off, d[0], d[1]]);
    } else for (k = 0; k < s.n; k++) {
      var b = a + (s.n === 1 ? 0 : (-s.spread / 2 + s.spread * k / (s.n - 1)) / R2D);
      out.push([s.x, s.y, M.cos(b), M.sin(b)]);
    }
    return out;
  }
  function traceAll() {
    var res = [], bx = box();
    B.sources.forEach(function (s, si) {
      var lams = s.white ? O.WHITE : [s.lam];
      emit(s).forEach(function (r, ri) {
        lams.forEach(function (lam) {
          var t = O.trace(B.scene, { x: r[0], y: r[1], dx: r[2], dy: r[3], lam: lam }, { box: bx, minI: B.minI });
          t.lam = lam; t.white = s.white; t.src = si; t.ray = ri; res.push(t);
        });
      });
    });
    return res;
  }

  // ---------------------------------------------------------------- drawing
  function pathOf(o) {   // outline of an object as a canvas path (world → px)
    var a = (o.rot || 0) / R2D, ca = M.cos(a), sa = M.sin(a);
    function T(p) { return px(o.x + ca * p[0] - sa * p[1], o.y + sa * p[0] + ca * p[1]); }
    var pts = [];
    o._g.prims.forEach(function (q) {
      if (q.t === 'seg') { pts.push(T(q.a), T(q.b)); return; }
      if (q.t === 'thin') { pts.push(T([0, -q.h / 2]), T([0, q.h / 2])); return; }
      var i, N = 64, p;
      if (q.t === 'par') { for (i = 0; i <= N; i++) { var y = -q.h / 2 + q.h * i / N; pts.push(T([-y * y / (4 * q.f), y])); } return; }
      var a0, a1;
      if (q.y0 === null) { a0 = 0; a1 = 2 * M.PI; }
      else {
        var s0 = M.asin(M.max(-1, M.min(1, q.y0 / q.r))), s1 = M.asin(M.max(-1, M.min(1, q.y1 / q.r)));
        if (q.side > 0) { a0 = s0; a1 = s1; } else { a0 = M.PI - s0; a1 = M.PI - s1; }
      }
      for (i = 0; i <= N; i++) { var t = a0 + (a1 - a0) * i / N; p = [q.c[0] + q.r * M.cos(t), q.c[1] + q.r * M.sin(t)]; pts.push(T(p)); }
    });
    return pts;
  }
  function regionPath(o) {   // closed outline for glass: chain the primitives end to start
    var a = (o.rot || 0) / R2D, ca = M.cos(a), sa = M.sin(a);
    function T(p) { return px(o.x + ca * p[0] - sa * p[1], o.y + sa * p[0] + ca * p[1]); }
    var pieces = o._g.prims.map(function (q) {
      if (q.t === 'seg') return [q.a, q.b];
      var a0, a1, i, N = 72, pts = [];
      if (q.y0 === null) { for (i = 0; i <= N; i++) { var t0 = 2 * M.PI * i / N; pts.push([q.c[0] + q.r * M.cos(t0), q.c[1] + q.r * M.sin(t0)]); } return pts; }
      var s0 = M.asin(M.max(-1, M.min(1, q.y0 / q.r))), s1 = M.asin(M.max(-1, M.min(1, q.y1 / q.r)));
      if (q.side > 0) { a0 = s0; a1 = s1; } else { a0 = M.PI - s0; a1 = M.PI - s1; }
      for (i = 0; i <= N; i++) { var t = a0 + (a1 - a0) * i / N; pts.push([q.c[0] + q.r * M.cos(t), q.c[1] + q.r * M.sin(t)]); }
      return pts;
    });
    // order the pieces into a loop by nearest endpoints
    var loop = pieces.shift().slice(), guard = 0;
    while (pieces.length && guard++ < 20) {
      var end = loop[loop.length - 1], bi = 0, rev = false, bd = 1e18;
      pieces.forEach(function (p, i) {
        var d0 = M.hypot(p[0][0] - end[0], p[0][1] - end[1]), d1 = M.hypot(p[p.length - 1][0] - end[0], p[p.length - 1][1] - end[1]);
        if (d0 < bd) { bd = d0; bi = i; rev = false; }
        if (d1 < bd) { bd = d1; bi = i; rev = true; }
      });
      var nx = pieces.splice(bi, 1)[0]; if (rev) nx = nx.slice().reverse();
      loop = loop.concat(nx);
    }
    return loop.map(T);
  }
  function grid() {
    ctx.fillStyle = '#0b1218'; ctx.fillRect(0, 0, W, H);
    var step = B.view.w > 500 ? 50 : 10, bx = box();
    ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(140,170,190,0.08)'; ctx.beginPath();
    for (var x = M.ceil(bx[0] / step) * step; x < bx[2]; x += step) { var p = px(x, 0); ctx.moveTo(p[0], 0); ctx.lineTo(p[0], H); }
    for (var y = M.ceil(bx[1] / step) * step; y < bx[3]; y += step) { var q = px(0, y); ctx.moveTo(0, q[1]); ctx.lineTo(W, q[1]); }
    ctx.stroke();
  }
  function drawObjects() {
    B.scene.forEach(function (o) {
      if (!o._g) return;
      var sel = B.sel === o;
      if (o._g.region) {
        var pts = regionPath(o);
        ctx.beginPath(); pts.forEach(function (p, i) { if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); }); ctx.closePath();
        ctx.fillStyle = o.mat === 'diamond' ? 'rgba(220,235,255,0.20)' : o.mat === 'water' ? 'rgba(90,160,230,0.20)' : 'rgba(150,200,230,0.16)';
        ctx.fill(); ctx.lineWidth = (sel ? 2.5 : 1.5) * DPR; ctx.strokeStyle = sel ? 'rgba(242,197,61,0.95)' : 'rgba(190,225,250,0.75)'; ctx.stroke();
      } else {
        var p2 = pathOf(o);
        ctx.beginPath(); p2.forEach(function (p, i) { if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); });
        if (o._g.thin) {
          ctx.lineWidth = 2 * DPR; ctx.strokeStyle = sel ? 'rgba(242,197,61,0.95)' : 'rgba(190,225,250,0.85)'; ctx.setLineDash([6 * DPR, 4 * DPR]); ctx.stroke(); ctx.setLineDash([]);
          var e0 = p2[0], e1 = p2[p2.length - 1], ux = (e1[0] - e0[0]), uy = (e1[1] - e0[1]), L = M.hypot(ux, uy); ux /= L; uy /= L;
          var k = 8 * DPR, sgn = o.f > 0 ? 1 : -1;
          [[e0, -1], [e1, 1]].forEach(function (e) {
            var tip = e[0], dir = e[1] * sgn;
            ctx.beginPath(); ctx.moveTo(tip[0] - uy * k - ux * k * dir, tip[1] + ux * k - uy * k * dir); ctx.lineTo(tip[0], tip[1]);
            ctx.lineTo(tip[0] + uy * k - ux * k * dir, tip[1] - ux * k - uy * k * dir); ctx.stroke();
          });
        } else {   // mirror: bright face, hatched back
          ctx.lineWidth = 3 * DPR; ctx.strokeStyle = sel ? 'rgba(242,197,61,0.95)' : 'rgba(225,232,238,0.95)'; ctx.stroke();
          var a = (o.rot || 0) / R2D, back = [M.cos(a) * 6 * DPR, -M.sin(a) * 6 * DPR];
          ctx.lineWidth = 1 * DPR; ctx.strokeStyle = 'rgba(225,232,238,0.45)'; ctx.beginPath();
          for (var i = 0; i < p2.length; i += 6) { ctx.moveTo(p2[i][0], p2[i][1]); ctx.lineTo(p2[i][0] + back[0] + back[1] * 0.6, p2[i][1] + back[1] - back[0] * 0.6); }
          ctx.stroke();
        }
      }
    });
  }
  function drawRays(res) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
    var lw = M.max(1.2, 1.6 * DPR);
    res.forEach(function (t) {
      var c = rayColour(t.lam, t.white);
      t.segs.forEach(function (s) {
        if (B.filter && !B.filter(s, t)) return;
        var a = M.min(1, M.sqrt(s.I) * B.gain);
        if (a < 0.02) return;
        var p = px(s.x0, s.y0), q = px(s.x1, s.y1);
        ctx.strokeStyle = 'rgba(' + M.round(c[0]) + ',' + M.round(c[1]) + ',' + M.round(c[2]) + ',' + a.toFixed(3) + ')';
        ctx.lineWidth = lw; ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke();
      });
    });
    ctx.restore();
  }
  function drawSources() {
    B.sources.forEach(function (s) {
      if (s.hidden) return;
      var p = px(s.x, s.y), a = s.ang / R2D, hp = px(s.x + M.cos(a) * 18 / S * DPR * 2, s.y + M.sin(a) * 18 / S * DPR * 2);
      ctx.fillStyle = '#f2c53d'; ctx.strokeStyle = '#f2c53d'; ctx.lineWidth = 2 * DPR;
      ctx.beginPath(); ctx.arc(p[0], p[1], 7 * DPR, 0, 2 * M.PI); ctx.fill();
      if (!s.fixedAngle) { ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(hp[0], hp[1]); ctx.stroke(); ctx.beginPath(); ctx.arc(hp[0], hp[1], 5 * DPR, 0, 2 * M.PI); ctx.stroke(); }
    });
  }
  function mark(x, y, label, col) {   // small labelled marker on the bench
    var p = px(x, y);
    ctx.fillStyle = col || '#f2c53d'; ctx.beginPath(); ctx.arc(p[0], p[1], 3.5 * DPR, 0, 2 * M.PI); ctx.fill();
    ctx.font = (12 * DPR) + 'px "IBM Plex Mono", monospace'; ctx.fillText(label, p[0] + 6 * DPR, p[1] - 6 * DPR);
  }
  function dashed(x0, y0, x1, y1, col) {
    var p = px(x0, y0), q = px(x1, y1);
    ctx.save(); ctx.setLineDash([5 * DPR, 5 * DPR]); ctx.strokeStyle = col || 'rgba(200,215,225,0.35)'; ctx.lineWidth = 1 * DPR;
    ctx.beginPath(); ctx.moveTo(p[0], p[1]); ctx.lineTo(q[0], q[1]); ctx.stroke(); ctx.restore();
  }
  var pending = false;
  function render() {
    if (pending) return; pending = true;
    requestAnimationFrame(function () {
      pending = false; size(); O.prepare(B.scene);
      var res = traceAll(); B.lastRes = res;
      grid(); if (B.under) B.under(); drawObjects(); drawRays(res); drawSources();
      if (B.overlay) B.overlay(res);
      if (B.readout) B.readout(res);
    });
  }
  window.addEventListener('resize', render);

  // ---------------------------------------------------------------- dragging (objects, sources, a source's direction handle)
  var drag = null;
  function objRadius(o) {
    var r = 0; o._g && o._g.prims.forEach(function (q) {
      if (q.t === 'seg') r = M.max(r, M.hypot(q.a[0], q.a[1]), M.hypot(q.b[0], q.b[1]));
      else if (q.t === 'arc') r = M.max(r, q.y0 === null ? q.r : M.max(M.abs(q.y0), M.abs(q.y1)));
      else r = M.max(r, q.h / 2);
    });
    return r;
  }
  cv.addEventListener('pointerdown', function (e) {
    var r = cv.getBoundingClientRect(), X = (e.clientX - r.left) * DPR, Y = (e.clientY - r.top) * DPR, w = world(X, Y), tol = 16 * DPR / S;
    var hit = null;
    B.sources.forEach(function (s) {
      if (s.hidden || hit) return;
      var a = s.ang / R2D, hl = 18 / S * DPR * 2, hx = s.x + M.cos(a) * hl, hy = s.y + M.sin(a) * hl;
      if (!s.fixedAngle && M.hypot(w[0] - hx, w[1] - hy) < tol) hit = { kind: 'aim', s: s };
      else if (!s.fixed && M.hypot(w[0] - s.x, w[1] - s.y) < tol) hit = { kind: 'src', s: s, dx: s.x - w[0], dy: s.y - w[1] };
    });
    if (!hit) B.scene.forEach(function (o) {
      if (hit || o.fixed) return;
      if (M.hypot(w[0] - o.x, w[1] - o.y) < M.max(objRadius(o), 12 / S * DPR)) hit = { kind: 'obj', o: o, dx: o.x - w[0], dy: o.y - w[1] };
    });
    if (!hit) return;
    drag = hit; cv.setPointerCapture(e.pointerId); e.preventDefault();
    if (hit.kind === 'obj' && B.onSelect) B.onSelect(hit.o);
  });
  cv.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var r = cv.getBoundingClientRect(), w = world((e.clientX - r.left) * DPR, (e.clientY - r.top) * DPR);
    if (drag.kind === 'aim') drag.s.ang = M.atan2(w[1] - drag.s.y, w[0] - drag.s.x) * R2D;
    else if (drag.kind === 'src') { drag.s.x = w[0] + drag.dx; if (!drag.s.lockY) drag.s.y = w[1] + drag.dy; }
    else { drag.o.x = w[0] + drag.dx; if (!drag.o.lockY) drag.o.y = w[1] + drag.dy; }
    if (B.onDrag) B.onDrag(drag);
    render();
  });
  function end() { drag = null; }
  cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);

  // ---------------------------------------------------------------- small UI helpers
  function bindRange(id, fmt, cb) {
    var el = $(id), out = $(id + 'v');
    function upd() { if (out) out.textContent = fmt ? fmt(+el.value) : el.value; cb && cb(+el.value); render(); }
    el.addEventListener('input', upd); upd();
    return el;
  }
  function onChange(id, cb) { var el = $(id); el.addEventListener('change', function () { cb(el.value); render(); }); cb(el.value); return el; }
  function qty(rows) {   // rows: [label, value] -> html
    return rows.map(function (r) { return '<div><span>' + r[0] + '</span><span>' + r[1] + '</span></div>'; }).join('');
  }
  function f1(x, d) { return isFinite(x) ? x.toFixed(d === undefined ? 1 : d) : '∞'; }
  function deg(x, d) { return f1(x, d === undefined ? 2 : d) + '°'; }
  function matName(m) { return O.MATERIALS[m].name; }

  var P = {};

  // ================================================================= refraction: a half-cylinder of glass
  P.refraction = function () {
    var st = { mat: 'bk7', lam: 589.3, ang: 40, out: false };
    var blk = { kind: 'half', x: 0, y: 0, rot: 0, r: 80, mat: 'bk7', fixed: true }, src = { type: 'laser', x: 0, y: 0, ang: 0, white: false, lam: 589.3, fixed: true, fixedAngle: true };
    B.scene = [blk]; B.sources = [src]; B.view = { cx: 10, cy: 0, w: 280 }; B.minI = 0.004; B.gain = 1.3;
    function place() {
      blk.mat = st.mat; blk.rot = st.out ? 180 : 0; src.lam = st.lam;
      var a = -st.ang / R2D;   // ray goes down and to the right, meeting the flat face's centre at st.ang from the normal
      src.ang = a * R2D; src.x = -125 * M.cos(a); src.y = -125 * M.sin(a);
    }
    onChange('rmat', function (v) { st.mat = v; place(); });
    bindRange('rang', function (v) { return v.toFixed(1) + '°'; }, function (v) { st.ang = v; place(); });
    bindRange('rlam', function (v) { return v.toFixed(0) + ' nm'; }, function (v) { st.lam = v; place(); });
    document.querySelectorAll('[data-dir]').forEach(function (b) {
      b.addEventListener('click', function () {
        st.out = b.getAttribute('data-dir') === 'out';
        document.querySelectorAll('[data-dir]').forEach(function (c) { c.setAttribute('aria-pressed', c === b); c.classList.toggle('ghost', c !== b); });
        place(); render();
      });
    });
    place();
    B.overlay = function () {
      dashed(-120, 0, 120, 0);
      var n = O.index(st.mat, st.lam), crit = O.criticalDeg(n, 1);
      if (st.out && crit !== null) {   // the critical angle as a faint guide
        var c = crit / R2D; dashed(0, 0, -110 * M.cos(c), 110 * M.sin(c), 'rgba(255,106,92,0.45)');
      }
      ctx.fillStyle = 'rgba(200,215,225,0.7)'; ctx.font = (12 * DPR) + 'px "IBM Plex Mono", monospace';
      var p = px(st.out ? 70 : -110, 6); ctx.fillText('normal', p[0], p[1]);
      var g = px(st.out ? -60 : 40, -70); ctx.fillText(matName(st.mat).toLowerCase(), g[0], g[1]);
      var aa = px(st.out ? 40 : -60, -70); ctx.fillText('air', aa[0], aa[1]);
    };
    B.readout = function (res) {
      var ev = res[0].events.filter(function (e) { return M.abs(e.x) < 1e-6; })[0];
      var n = O.index(st.mat, st.lam), n1 = st.out ? n : 1, n2 = st.out ? 1 : n, rows;
      var what = st.mat === 'water' ? 'water' : st.mat === 'diamond' ? 'diamond' : 'glass';
      rows = [['Index of the ' + (st.out ? what : 'air') + ', n₁', f1(n1, 4)], ['Index of the ' + (st.out ? 'air' : what) + ', n₂', f1(n2, 4)],
        ['Angle of incidence θ₁', deg(st.ang)]];
      if (ev && ev.type === 'refract') {
        rows.push(['Angle of refraction θ₂', deg(ev.thT)], ['n₁ sin θ₁', f1(n1 * M.sin(st.ang / R2D), 5)], ['n₂ sin θ₂', f1(n2 * M.sin(ev.thT / R2D), 5)],
          ['Reflected (unpolarised)', f1(100 * ev.R, 1) + ' %'], ['Transmitted', f1(100 * (1 - ev.R), 1) + ' %']);
      } else if (ev) rows.push(['Angle of refraction θ₂', 'none'], ['Total internal reflection', '100 % reflected']);
      rows.push([n1 > n2 ? 'Critical angle' : 'Critical angle (only from the ' + what + ' side)', n1 > n2 ? deg(O.criticalDeg(n1, n2)) : deg(O.criticalDeg(n2, n1))],
        ['Brewster’s angle', deg(O.brewsterDeg(n1, n2))]);
      $('rq').innerHTML = qty(rows);
      $('rnote').textContent = ev && ev.type === 'tir' ? 'Past the critical angle no light gets out: the flat face is a perfect mirror.' :
        st.out ? 'Light leaving the ' + what + ' bends away from the normal. Tilt it further and watch the reflected ray brighten.' : 'Light entering the ' + what + ' bends towards the normal. A little is always reflected.';
    };
  };

  // ================================================================= lenses
  P.lenses = function () {
    var st = { type: 'biconvex', R: 100, D: 50, mat: 'bk7', light: 'beam', tilt: 0, n: 11, u: 220, white: false, lam: 587.6, f: 100 };
    var lens = { kind: 'lens', x: 0, y: 0, rot: 0, fixed: true }, src = { type: 'beam', x: -170, y: 0, ang: 0, width: 40, n: 11, white: false, lam: 587.6, fixed: true, fixedAngle: true };
    B.scene = [lens]; B.sources = [src]; B.view = { cx: 60, cy: 0, w: 460 }; B.minI = 0.06;
    var geo;
    function place() {
      var R = st.R, t = st.type;
      var r1 = { biconvex: R, 'plano-convex': R, meniscus: R, biconcave: -R, 'plano-concave': Infinity }[t];
      var r2 = { biconvex: -R, 'plano-convex': Infinity, meniscus: 2.5 * R, biconcave: R, 'plano-concave': R }[t];
      if (t === 'ideal') { lens.kind = 'thin'; lens.f = st.f; lens.D = st.D; geo = null; }
      else {
        var D = M.min(st.D, 1.9 * R), tc = M.max(O.minThickness(r1, r2, D), t === 'biconcave' || t === 'plano-concave' ? 3 : 1);
        lens.kind = 'lens'; lens.R1 = r1; lens.R2 = r2; lens.tc = tc; lens.D = D; lens.mat = st.mat; geo = { r1: r1, r2: r2, tc: tc, D: D };
      }
      src.white = st.white; src.lam = st.lam; src.n = st.n;
      if (st.light === 'beam') { src.type = 'beam'; src.x = -100; src.y = -100 * M.tan(st.tilt / R2D); src.ang = st.tilt; src.width = st.D * 0.9; }
      else { src.type = 'point'; src.x = -st.u; src.y = 0; src.ang = 0; src.spread = 2 * M.atan(st.D * 0.45 / st.u) * R2D; }
      var I0 = info(), reach = isFinite(I0.f) ? M.min(M.abs(I0.bfd), 420) : 200, left = st.light === 'point' ? st.u + 20 : 120;
      if (st.light === 'beam') src.x = -100;
      B.view = { cx: (reach + 40 - left) / 2, cy: 0, w: M.max(220, reach + 40 + left) };
      $('lRrow').hidden = st.type === 'ideal'; $('lfrow').hidden = st.type !== 'ideal'; $('lmatrow').hidden = st.type === 'ideal';
      $('ltiltrow').hidden = st.light !== 'beam'; $('lurow').hidden = st.light !== 'point';
    }
    onChange('ltype', function (v) { st.type = v; place(); });
    bindRange('lR', function (v) { return v + ' mm'; }, function (v) { st.R = v; place(); });
    bindRange('lf', function (v) { return v + ' mm'; }, function (v) { st.f = v; place(); });
    bindRange('lD', function (v) { return v + ' mm'; }, function (v) { st.D = v; place(); });
    onChange('lmat', function (v) { st.mat = v; place(); });
    onChange('llight', function (v) { st.light = v; place(); });
    bindRange('ltilt', function (v) { return v.toFixed(1) + '°'; }, function (v) { st.tilt = v; place(); });
    bindRange('lu', function (v) { return v + ' mm'; }, function (v) { st.u = v; place(); });
    bindRange('ln', null, function (v) { st.n = v; place(); });
    onChange('lcol', function (v) { st.white = v === 'white'; place(); });
    place();
    function info() {   // focal quantities at the current wavelength (d line for white light)
      var lam = st.white ? O.LINES.d : st.lam;
      if (st.type === 'ideal') return { f: st.f, bfd: st.f, ffd: st.f, back: 0, front: 0, n: null, lam: lam };
      var n = O.index(st.mat, lam), tl = O.thickLens(n, geo.r1, geo.r2, geo.tc), rev = O.thickLens(n, -geo.r2, -geo.r1, geo.tc);
      return { f: tl.f, bfd: tl.bfd, ffd: rev.bfd, back: geo.tc / 2, front: geo.tc / 2, n: n, lam: lam };
    }
    function crossAt(h, lam) {   // where a ray parallel to the axis at height h meets the axis after the lens
      var t = O.trace(B.scene, { x: -300, y: h, dx: 1, dy: 0, lam: lam }, { minI: 1 });
      return O.axisCrossing(O.finalRay(t));
    }
    B.overlay = function () {
      dashed(-400, 0, 600, 0);
      var I = info();
      if (isFinite(I.f)) { mark(I.back + I.bfd, 0, 'F′'); mark(-I.front - I.ffd, 0, 'F'); }
      if (st.light === 'point') {
        mark(-st.u, 0, 'object', '#f2c53d');
        var im = imagePoint(); if (im) mark(im, 0, im > 0 ? 'image' : 'virtual image', '#6cc790');
      }
    };
    function imagePoint() {   // paraxial image of the axial object point, found by tracing two near-axis rays
      var lam = st.white ? O.LINES.d : st.lam, a = 1e-4;
      var t = O.trace(B.scene, { x: -st.u, y: 0, dx: M.cos(a), dy: M.sin(a), lam: lam }, { minI: 1 });
      var fr = O.finalRay(t);
      return O.axisCrossing(fr);
    }
    B.readout = function () {
      var I = info(), rows = [];
      rows.push(['Focal length f', f1(I.f, 1) + ' mm'], ['Power', f1(1000 / I.f, 2) + ' dioptres']);
      if (st.type !== 'ideal') {
        rows.push(['Glass index n (' + I.lam.toFixed(1) + ' nm)', f1(I.n, 4)], ['Centre thickness', f1(geo.tc, 1) + ' mm'], ['Back focal distance', f1(I.bfd, 1) + ' mm']);
        if (I.f > 0) {
          var par = crossAt(1e-3, I.lam), mar = crossAt(0.45 * geo.D, I.lam);
          rows.push(['Rim ray (h = ' + f1(0.45 * geo.D, 0) + ' mm) meets the axis', f1(mar - I.back, 1) + ' mm']);
          rows.push(['Spherical aberration', f1(par - mar, 2) + ' mm']);
        }
        if (st.white) {
          var nF = O.index(st.mat, O.LINES.F), nC = O.index(st.mat, O.LINES.C);
          rows.push(['Blue (F) − red (C) focus', f1(O.thickLens(nF, geo.r1, geo.r2, geo.tc).bfd - O.thickLens(nC, geo.r1, geo.r2, geo.tc).bfd, 2) + ' mm']);
        }
      }
      if (st.light === 'point') {
        var im = imagePoint();
        var ref = st.type === 'ideal' ? 0 : (im > 0 ? geo.tc / 2 : -geo.tc / 2);
        rows.push(['Object distance u (to the ' + (st.type === 'ideal' ? 'lens' : 'lens centre') + ')', st.u + ' mm'],
          ['Image (paraxial rays), from the ' + (st.type === 'ideal' ? 'lens' : im > 0 ? 'back surface' : 'front surface'), isFinite(im) ? f1(M.abs(im - ref), 1) + ' mm ' + (im > 0 ? 'behind' : 'in front (virtual)') : 'at infinity']);
        if (st.type === 'ideal' && isFinite(im)) rows.push(['1/u + 1/v', f1(1 / st.u + 1 / im, 5)], ['1/f', f1(1 / st.f, 5)], ['Magnification −v/u', f1(-im / st.u, 2)]);
      }
      $('lq').innerHTML = qty(rows);
    };
  };

  // ================================================================= prism
  P.prism = function () {
    var st = { A: 60, mat: 'bk7', i: 50, white: true, lam: 589.3 };
    var pr = { kind: 'prism', x: 0, y: 0, rot: 0, A: 60, L: 120, mat: 'bk7', fixed: true }, src = { type: 'laser', x: 0, y: 0, ang: 0, white: true, lam: 589.3, fixed: true, fixedAngle: true };
    B.scene = [pr]; B.sources = [src]; B.view = { cx: 30, cy: -10, w: 380 }; B.minI = 0.04;
    var face;
    function place() {
      pr.A = st.A; pr.mat = st.mat; O.prepare(B.scene);
      var g = pr._g.prims[2]; face = { c: [(g.a[0] + g.b[0]) / 2, (g.a[1] + g.b[1]) / 2], n: M.atan2(g.n[1], g.n[0]) };
      var da = face.n + M.PI + st.i / R2D;
      src.ang = da * R2D; src.x = face.c[0] - 130 * M.cos(da); src.y = face.c[1] - 130 * M.sin(da); src.white = st.white; src.lam = st.lam;
    }
    bindRange('pA', function (v) { return v + '°'; }, function (v) { st.A = v; place(); });
    onChange('pmat', function (v) { st.mat = v; place(); });
    var ir = bindRange('pi', function (v) { return v.toFixed(1) + '°'; }, function (v) { st.i = v; place(); });
    onChange('pcol', function (v) { st.white = v === 'white'; place(); });
    bindRange('plam', function (v) { return v.toFixed(0) + ' nm'; }, function (v) { st.lam = v; place(); });
    $('pmin').addEventListener('click', function () {
      var mn = O.prismMin(st.A, O.index(st.mat, st.white ? O.LINES.d : st.lam));
      if (mn) { ir.value = mn.i.toFixed(1); ir.dispatchEvent(new Event('input')); }
    });
    place();
    B.overlay = function () {
      var da = src.ang / R2D; dashed(face.c[0], face.c[1], face.c[0] + 220 * M.cos(da), face.c[1] + 220 * M.sin(da));
      var nn = face.n; dashed(face.c[0] - 30 * M.cos(nn), face.c[1] - 30 * M.sin(nn), face.c[0] + 30 * M.cos(nn), face.c[1] + 30 * M.sin(nn), 'rgba(200,215,225,0.5)');
    };
    function dev(lam) {
      var n = O.index(st.mat, lam); return O.prismDeviation(st.A, n, st.i);
    }
    B.readout = function () {
      var lam = st.white ? O.LINES.d : st.lam, n = O.index(st.mat, lam), d = dev(lam), mn = O.prismMin(st.A, n), rows = [];
      rows.push(['Glass index n (' + lam.toFixed(1) + ' nm)', f1(n, 4)], ['Angle of incidence i', deg(st.i, 1)]);
      rows.push(['Deviation δ', d === null ? 'no exit (total reflection)' : deg(d)]);
      if (st.white) {
        var dF = dev(O.LINES.F), dC = dev(O.LINES.C);
        rows.push(['Blue F line, 486 nm', dF === null ? '—' : deg(dF)], ['Red C line, 656 nm', dC === null ? '—' : deg(dC)], ['Spread F − C', dF === null || dC === null ? '—' : deg(dF - dC)]);
      }
      if (mn) rows.push(['Minimum deviation', deg(mn.D)], ['… reached at i =', deg(mn.i, 1)], ['n = sin((A + δmin)/2) / sin(A/2)', f1(O.nFromMinDev(st.A, mn.D), 4)]);
      else rows.push(['Minimum deviation', 'none: light cannot pass this prism']);
      $('pq').innerHTML = qty(rows);
    };
  };

  // ================================================================= mirrors
  P.mirrors = function () {
    var st = { shape: 'spherical', f: 100, D: 160, tilt: 0, n: 15 };
    var mir = { kind: 'mirror', shape: 'spherical', x: 150, y: 0, rot: 0, fixed: true }, src = { type: 'beam', x: -170, y: 0, ang: 0, width: 140, n: 15, white: false, lam: 560, fixed: true, fixedAngle: true };
    B.scene = [mir]; B.sources = [src]; B.view = { cx: 30, cy: 0, w: 420 }; B.minI = 0.5;
    function place() {
      mir.shape = st.shape; mir.R = 2 * st.f; mir.f = st.f; mir.D = M.min(st.D, st.shape === 'parabolic' ? 4 * st.f : 1.9 * st.f * 2);
      src.n = st.n; src.width = mir.D * 0.92; src.ang = st.tilt; src.y = -320 * M.tan(st.tilt / R2D);
      $('mfrow').hidden = st.shape === 'plane';
    }
    onChange('mshape', function (v) { st.shape = v; place(); });
    bindRange('mf', function (v) { return v + ' mm'; }, function (v) { st.f = v; place(); });
    bindRange('mD', function (v) { return v + ' mm'; }, function (v) { st.D = v; place(); });
    bindRange('mtilt', function (v) { return v.toFixed(1) + '°'; }, function (v) { st.tilt = v; place(); });
    bindRange('mn', null, function (v) { st.n = v; place(); });
    place();
    function cross(h) { var t = O.trace(B.scene, { x: -300, y: h, dx: 1, dy: 0, lam: 560 }, { minI: 1 }); return O.axisCrossing(O.finalRay(t)) - mir.x; }
    B.overlay = function () {
      dashed(-300, 0, 300, 0);
      if (st.shape === 'plane') return;
      mark(mir.x + (st.shape === 'convex' ? st.f : -st.f), 0, st.shape === 'convex' ? 'F (virtual)' : 'F');
      if (st.shape !== 'parabolic') mark(mir.x + (st.shape === 'convex' ? 2 * st.f : -2 * st.f), 0, 'C', 'rgba(200,215,225,0.8)');
    };
    B.readout = function () {
      var rows = [];
      if (st.shape === 'plane') rows.push(['Angle in = angle out', 'always'], ['Image', 'as far behind as the object is in front']);
      else {
        rows.push(['Focal length f', f1(st.f, 0) + ' mm'], [st.shape === 'parabolic' ? 'Focal length of the parabola' : 'Radius R = 2f', st.shape === 'parabolic' ? f1(st.f, 0) + ' mm' : f1(2 * st.f, 0) + ' mm']);
        var h = 0.46 * mir.D, par = cross(1e-3), mar = cross(h);
        var side = st.shape === 'convex' ? ' behind (virtual)' : ' in front';
        rows.push(['Ray near the axis meets it, from the mirror', f1(M.abs(par), 2) + ' mm' + side]);
        rows.push(['Ray at h = ' + f1(h, 0) + ' mm meets it', f1(M.abs(mar), 2) + ' mm' + side]);
        rows.push(['Spherical aberration', st.shape === 'parabolic' ? f1(M.abs(par - mar), 6) + ' mm (none)' : f1(M.abs(par - mar), 2) + ' mm']);
      }
      $('mq').innerHTML = qty(rows);
    };
  };

  // ================================================================= rainbow: one drop of water
  P.rainbow = function () {
    var st = { mode: 'one', b: 0.86, only: true };
    var drop = { kind: 'drop', x: 0, y: 0, rot: 0, r: 70, mat: 'water', fixed: true }, src = { type: 'beam', x: -160, y: 0, ang: 0, width: 0, n: 1, white: true, lam: 589, fixed: true, fixedAngle: true };
    B.scene = [drop]; B.sources = [src]; B.view = { cx: 0, cy: 0, w: 340 }; B.minI = 0.002; B.gain = 2.2;
    function place() {
      if (st.mode === 'one') { src.n = 1; src.width = 0; src.y = 70 * st.b; }
      else { src.n = 41; src.width = 2 * 70 * 0.98; src.y = 0; }
      B.gain = st.mode === 'one' ? 7 : 2.5;
    }
    onChange('rbmode', function (v) { st.mode = v; place(); $('rbbrow').hidden = v !== 'one'; });
    bindRange('rbb', function (v) { return v.toFixed(3); }, function (v) { st.b = v; place(); });
    var only = $('rbonly'); only.addEventListener('change', function () { st.only = only.checked; render(); }); st.only = only.checked;
    B.filter = function (s) { return !st.only || s.k === 1 || (s.k === 0 && (s.n > 1 || !s.end)); };
    place();
    B.overlay = function () {
      if (st.mode !== 'one') return;
      dashed(-160, 70 * st.b, 160, 70 * st.b);
    };
    var ch = $('rbchart');
    drawChart();
    B.readout = function () {
      var lams = [[700, 'Red, 700 nm'], [589.29, 'Yellow, 589 nm'], [400, 'Violet, 400 nm']], h = '';
      if (st.mode === 'one') h += '<p class="small">This ray leaves at, from the antisolar point:</p>' + qty(lams.map(function (l) {
        return [l[1], deg(180 - O.dropDeviation(O.index('water', l[0]), st.b, 1))];
      }));
      h += '<p class="small">Bow radius, primary · secondary:</p>' + qty(lams.map(function (l) {
        var n = O.index('water', l[0]); return [l[1], deg(O.rainbowDeg(n, 1).angle) + ' · ' + deg(O.rainbowDeg(n, 2).angle)];
      }));
      $('rbq').innerHTML = h;
      chartMark();
    };
    function drawChart() {   // deviation 180° − D (the angle from the antisolar point) against b, for red and violet
      var w = 600, h = 260, pad = 40, s = '', y0 = 0, y1 = 45;
      function X(b) { return pad + (w - pad - 10) * b; }
      function Y(a) { return h - 26 - (h - 40) * (a - y0) / (y1 - y0); }
      for (var g = 0; g <= 45; g += 15) s += '<line x1="' + pad + '" x2="' + (w - 10) + '" y1="' + Y(g) + '" y2="' + Y(g) + '" class="gl"/><text x="' + (pad - 6) + '" y="' + (Y(g) + 4) + '" text-anchor="end">' + g + '°</text>';
      for (var bb = 0; bb <= 1.0001; bb += 0.25) s += '<text x="' + X(bb) + '" y="' + (h - 8) + '" text-anchor="middle">' + bb.toFixed(2) + '</text>';
      [[700, '#d9412b'], [400, '#7a4fd6']].forEach(function (c) {
        var n = O.index('water', c[0]), d = '';
        for (var i = 0; i <= 200; i++) { var b = i / 200, a = 180 - O.dropDeviation(n, b, 1); d += (i ? 'L' : 'M') + X(b).toFixed(1) + ',' + Y(a).toFixed(1); }
        var rb = O.rainbowDeg(n, 1);
        s += '<path d="' + d + '" fill="none" stroke="' + c[1] + '" stroke-width="2"/><circle cx="' + X(rb.b) + '" cy="' + Y(rb.angle) + '" r="4" fill="' + c[1] + '"/>';
      });
      s += '<line id="rbcur" x1="0" x2="0" y1="' + Y(y1) + '" y2="' + Y(0) + '" class="cur"/>';
      s += '<text x="' + X(0.02) + '" y="' + Y(43.5) + '">angle from the antisolar point, one reflection inside</text><text x="' + (w - 12) + '" y="' + (h - 22) + '" text-anchor="end">b (impact parameter)</text>';
      ch.innerHTML = s;
      ch.X = X;
    }
    function chartMark() { var c = $('rbcur'); if (!c) return; var x = st.mode === 'one' ? ch.X(st.b) : -10; c.setAttribute('x1', x); c.setAttribute('x2', x); }
  };

  // ================================================================= free bench
  P.bench = function () {
    var MAKE = {
      biconvex: function () { return { kind: 'lens', R1: 90, R2: -90, tc: 12, D: 50, mat: 'bk7' }; },
      biconcave: function () { return { kind: 'lens', R1: -90, R2: 90, tc: 4, D: 50, mat: 'bk7' }; },
      prism: function () { return { kind: 'prism', A: 60, L: 70, mat: 'bk7' }; },
      rprism: function () { return { kind: 'prism', A: 90, L: 60, mat: 'bk7' }; },
      slab: function () { return { kind: 'slab', w: 30, h: 80, mat: 'bk7' }; },
      half: function () { return { kind: 'half', r: 40, mat: 'bk7' }; },
      drop: function () { return { kind: 'drop', r: 30, mat: 'water' }; },
      plane: function () { return { kind: 'mirror', shape: 'plane', D: 80 }; },
      concave: function () { return { kind: 'mirror', shape: 'spherical', R: 160, D: 90 }; },
      parabolic: function () { return { kind: 'mirror', shape: 'parabolic', f: 60, D: 100 }; },
      thin: function () { return { kind: 'thin', f: 80, D: 70 }; }
    };
    B.view = { cx: 0, cy: 0, w: 520 }; B.minI = 0.06;
    var src = { type: 'beam', x: -230, y: 0, ang: 0, width: 36, spread: 30, n: 9, white: true, lam: 589 };
    B.sources = [src];
    function add(k, x, y, rot) { var o = MAKE[k](); o.x = x; o.y = y; o.rot = rot || 0; o.tag = k; B.scene.push(o); return o; }
    add('biconvex', -150, 0); add('prism', 10, -6, 0); add('concave', 175, -75, 35);
    var sel = null;
    function setSel(o) {
      sel = o; B.sel = o; $('bsel').hidden = !o;
      if (!o) return;
      $('bname').textContent = { biconvex: 'Converging lens', biconcave: 'Diverging lens', prism: 'Prism', rprism: 'Right-angle prism', slab: 'Glass block', half: 'Half-cylinder', drop: 'Drop',
        plane: 'Plane mirror', concave: 'Concave mirror', parabolic: 'Parabolic mirror', thin: 'Ideal thin lens' }[o.tag];
      $('brot').value = o.rot; $('brotv').textContent = M.round(o.rot) + '°';
      $('bmatrow').hidden = !o.mat; if (o.mat) $('bmat').value = o.mat;
      $('bsize').value = 100; $('bsizev').textContent = '100 %'; o.base = o.base || JSON.parse(JSON.stringify(o));
      var sz = o.scale ? M.round(o.scale * 100) : 100; $('bsize').value = sz; $('bsizev').textContent = sz + ' %';
    }
    B.onSelect = function (o) { setSel(o); };
    document.querySelectorAll('[data-add]').forEach(function (b) {
      b.addEventListener('click', function () { setSel(add(b.getAttribute('data-add'), B.view.cx + (M.random() - 0.5) * 60, B.view.cy + (M.random() - 0.5) * 60)); render(); });
    });
    $('brot').addEventListener('input', function () { if (!sel) return; sel.rot = +$('brot').value; $('brotv').textContent = sel.rot + '°'; render(); });
    $('bsize').addEventListener('input', function () {
      if (!sel) return; var k = +$('bsize').value / 100, b = sel.base; sel.scale = k; $('bsizev').textContent = M.round(k * 100) + ' %';
      ['R1', 'R2', 'tc', 'D', 'L', 'w', 'h', 'r', 'R', 'f'].forEach(function (p) { if (b[p] !== undefined) sel[p] = b[p] * k; });
      render();
    });
    $('bmat').addEventListener('change', function () { if (sel && sel.mat) { sel.mat = $('bmat').value; render(); } });
    $('bdel').addEventListener('click', function () { if (!sel) return; B.scene.splice(B.scene.indexOf(sel), 1); setSel(null); render(); });
    $('bclear').addEventListener('click', function () { B.scene = []; setSel(null); render(); });
    onChange('bsrc', function (v) { src.type = v; $('bwrow').hidden = v !== 'beam'; $('bsprow').hidden = v !== 'point'; $('bnrow').hidden = v === 'laser'; });
    onChange('bcol', function (v) { src.white = v === 'white'; $('blamrow').hidden = v === 'white'; });
    bindRange('blam', function (v) { return v + ' nm'; }, function (v) { src.lam = v; });
    bindRange('bw', function (v) { return v + ' mm'; }, function (v) { src.width = v; });
    bindRange('bsp', function (v) { return v + '°'; }, function (v) { src.spread = v; });
    bindRange('bn', null, function (v) { src.n = v; });
    setSel(null);
    B.readout = function (res) {
      var segs = 0; res.forEach(function (t) { segs += t.segs.length; });
      $('bq').textContent = B.scene.length + ' objects · ' + res.length + ' rays traced · ' + segs + ' straight pieces drawn';
    };
  };

  if (P[PAGE]) P[PAGE]();
  render();
  window.RK_RENDER = function () { size(); O.prepare(B.scene); var res = traceAll(); grid(); if (B.under) B.under(); drawObjects(); drawRays(res); drawSources(); if (B.overlay) B.overlay(res); if (B.readout) B.readout(res); };
})();
