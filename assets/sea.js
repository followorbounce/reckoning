/* Beaufort sea: a side view at a fixed scale (6 px = 1 m) with a 10 m boat for reference.
   Wave height = probable wave height for the force (Met Office / WMO table); wavelength is set
   from a typical wind-sea steepness (height/length about 1/10), and each component moves at the
   deep-water speed sqrt(g L / 2π). Whitecaps from force 3, foam streaks and spray from force 8.
   It is an illustration of scale and character, not a forecast. */
(function () {
  'use strict';
  var D = window.RK_BEAUFORT; if (!D) return;
  var cv = document.getElementById('seacv'), sl = document.getElementById('bf'), cap = document.getElementById('bfout');
  var ctx = cv.getContext('2d'), PX = 6, g = 9.81, M = Math;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var force = +sl.value, t = 0, last = 0, comps = [], foam = [];
  function css(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function setup() {
    var b = D[force], H = b.h ? b.h[0] : 0;
    comps = [];
    if (H > 0) {
      var L = M.max(H * 10, 1.2);
      [[1, 0], [0.55, 1.7], [0.3, 4.1], [0.18, 2.6]].forEach(function (p, i) {
        var len = L * [1, 0.62, 0.37, 0.21][i], k = 2 * M.PI / len;
        comps.push({ a: H / 2 * p[0] * (i ? 0.6 : 1), k: k, w: M.sqrt(g * k), ph: p[1] });
      });
    }
    var s = D[force];
    cap.innerHTML = '<b>Force ' + force + ' · ' + s.name + '</b> · ' + s.kn + ' kn · ' + s.ms + ' m/s' + (s.h ? ' · probable wave height ' + s.h[0] + ' m' + (s.h[1] ? ' (max ' + s.h[1] + ' m)' : '') : '') +
      '<br>' + s.sea;
  }
  function surf(x) {   // height in metres at position x (metres), time t
    var y = 0;
    for (var i = 0; i < comps.length; i++) { var c = comps[i]; y += c.a * M.cos(c.k * x - c.w * t + c.ph); }
    // sharpen crests a little (trochoid-like) for stronger forces
    return y;
  }
  function frame(now) {
    requestAnimationFrame(frame);
    var dt = M.min(0.05, (now - last) / 1000 || 0); last = now;
    if (!reduce) t += dt;
    var w = cv.clientWidth, h = cv.clientHeight, dpr = M.min(2, window.devicePixelRatio || 1);
    if (cv.width !== M.round(w * dpr)) { cv.width = M.round(w * dpr); cv.height = M.round(h * dpr); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var dark = M.min(1, force / 12), sea0 = h * 0.58;
    var sky = ctx.createLinearGradient(0, 0, 0, sea0);
    sky.addColorStop(0, 'hsl(205,' + (40 - 25 * dark) + '%,' + (78 - 45 * dark) + '%)');
    sky.addColorStop(1, 'hsl(205,' + (30 - 20 * dark) + '%,' + (88 - 40 * dark) + '%)');
    ctx.fillStyle = sky; ctx.fillRect(0, 0, w, h);
    // wind streaks in the air
    if (force >= 2) {
      ctx.strokeStyle = 'rgba(255,255,255,' + (0.15 + 0.03 * force) + ')'; ctx.lineWidth = 1;
      var n = force * 3, sp = D[force].mid * PX;
      for (var i = 0; i < n; i++) {
        var yy = (i * 37 % 100) / 100 * sea0 * 0.85, xx = ((i * 131 + t * sp * (0.6 + (i % 5) / 8)) % (w + 80)) - 40;
        ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx + 10 + force * 3, yy); ctx.stroke();
      }
    }
    // sea surface
    var pts = [];
    for (var x = 0; x <= w; x += 3) pts.push([x, sea0 - surf(x / PX) * PX]);
    var seaG = ctx.createLinearGradient(0, sea0 - 60, 0, h);
    seaG.addColorStop(0, 'hsl(200,' + (55 - 25 * dark) + '%,' + (38 - 14 * dark) + '%)');
    seaG.addColorStop(1, 'hsl(205,60%,' + (16 - 6 * dark) + '%)');
    ctx.beginPath(); ctx.moveTo(0, h); pts.forEach(function (p) { ctx.lineTo(p[0], p[1]); }); ctx.lineTo(w, h); ctx.closePath();
    ctx.fillStyle = seaG; ctx.fill();
    // ripples for light airs
    if (force >= 1 && force <= 3) {
      ctx.strokeStyle = 'rgba(255,255,255,0.25)';
      for (var r = 0; r < 30; r++) { var rx = (r * 53 + t * 20) % w, ry = sea0 + 8 + (r * 29 % 60); ctx.beginPath(); ctx.moveTo(rx, ry); ctx.lineTo(rx + 8, ry); ctx.stroke(); }
    }
    // whitecaps on crests that are high enough
    if (force >= 3) {
      var thr = force >= 8 ? 0.15 : force >= 5 ? 0.35 : 0.6, amp = comps.reduce(function (s, c) { return s + c.a; }, 0);
      ctx.fillStyle = 'rgba(255,255,255,0.9)';
      for (var j = 2; j < pts.length - 2; j++) {
        var p = pts[j], hgt = (sea0 - p[1]) / PX;
        if (hgt > amp * (1 - thr) && pts[j - 1][1] >= p[1] && pts[j + 1][1] >= p[1]) {
          ctx.beginPath(); ctx.ellipse(p[0] + 4, p[1] + 1, 6 + force, 2 + force / 4, 0, 0, 2 * M.PI); ctx.fill();
          if (force >= 8 && !reduce && M.random() < 0.3) foam.push({ x: p[0], y: p[1], vx: D[force].mid * PX * 0.5, life: 1 });
        }
      }
    }
    // spray and spindrift
    for (var f = foam.length - 1; f >= 0; f--) {
      var q = foam[f]; q.x += q.vx * dt; q.y -= 6 * dt; q.life -= dt * 0.8;
      if (q.life <= 0 || q.x > w) { foam.splice(f, 1); continue; }
      ctx.fillStyle = 'rgba(255,255,255,' + (q.life * 0.7) + ')'; ctx.fillRect(q.x, q.y, 3, 1.5);
    }
    if (foam.length > 400) foam.splice(0, foam.length - 400);
    // 10 m boat at x = 40 % of width, riding the surface
    var bx = w * 0.4, by = sea0 - surf(bx / PX) * PX, ang = M.atan2(-(surf((bx + 15) / PX) - surf((bx - 15) / PX)) * PX, 30);
    ctx.save(); ctx.translate(bx, by); ctx.rotate(ang);
    ctx.fillStyle = css('--ink') || '#14212b';
    ctx.beginPath(); ctx.moveTo(-30, -4); ctx.lineTo(30, -4); ctx.lineTo(24, 4); ctx.lineTo(-26, 4); ctx.closePath(); ctx.fill();
    ctx.fillRect(-10, -12, 16, 8); ctx.fillRect(-1, -34, 2, 22);
    ctx.restore();
    // scale bar: 10 m
    ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.font = '12px "IBM Plex Mono", monospace';
    ctx.fillRect(12, h - 18, 10 * PX, 2); ctx.fillText('10 m', 12, h - 24);
  }
  sl.addEventListener('input', function () { force = +sl.value; foam = []; setup(); });
  setup();
  requestAnimationFrame(frame);
})();
