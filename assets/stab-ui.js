/* Stability page: the heeled section with G, B, M and Z, the righting-lever curve and the IMO criteria.
   All numbers come from stability.js (the code the build checks). Earth frame: w = y cosθ + z sinθ across,
   h = −y sinθ + z cosθ − c up from the water. The ship is drawn as seen from aft: starboard on the right. */
(function () {
  'use strict';
  var St = window.RK_STAB, M = Math, D2R = M.PI / 180;
  var svg = document.getElementById('stsvg'); if (!svg) return;
  var gsv = document.getElementById('gzsvg'), crit = document.getElementById('crit'), q = document.getElementById('sq');
  var hs = document.getElementById('shull'), el = {};
  ['sT', 'sKG', 'sGy', 'sFs', 'sH'].forEach(function (k) { el[k] = document.getElementById(k); });
  Object.keys(St.HULLS).forEach(function (k) { var o = document.createElement('option'); o.value = k; o.textContent = St.HULLS[k].name; hs.appendChild(o); });
  var TANK_LEN = 0.3, RHO_TANK = 1.025;
  function f(x, n) { return (x < 0 ? '−' : '') + M.abs(x).toFixed(n === undefined ? 2 : n); }
  function setHull(k) {
    var h = St.HULLS[k];
    el.sT.min = (0.15 * h.D).toFixed(2); el.sT.max = (0.85 * h.D).toFixed(2); el.sT.value = h.T;
    el.sKG.min = (0.2 * h.D).toFixed(2); el.sKG.max = (1.1 * h.D).toFixed(2); el.sKG.value = h.KG;
    el.sGy.min = (-0.12 * h.B).toFixed(2); el.sGy.max = (0.12 * h.B).toFixed(2); el.sGy.value = 0;
    el.sFs.max = (0.9 * h.B).toFixed(1); el.sFs.value = 0;
  }
  function opts(h) {
    var T = +el.sT.value, A0 = St.upright(h.poly, T).A, b = +el.sFs.value;
    return { T: T, KG: +el.sKG.value, Gy: +el.sGy.value, fsc: b ? St.freeSurface(b, TANK_LEN, RHO_TANK, A0) : 0 };
  }
  function draw() {
    var h = St.HULLS[hs.value], o = opts(h), p = h.poly, u = St.upright(p, o.T), th = +el.sH.value * D2R;
    ['sT', 'sKG', 'sGy'].forEach(function (k) { document.getElementById(k + 'v').textContent = f(+el[k].value) + ' m'; });
    document.getElementById('sFsv').textContent = +el.sFs.value ? f(+el.sFs.value, 1) + ' m' : 'none';
    document.getElementById('sHv').textContent = (+el.sH.value).toFixed(1) + '°';
    var GM = u.KM - o.KG - o.fsc, cv = St.curve(p, o, 90, 1);
    var full = St.curve(p, o, 180, 1), mx = cv.reduce(function (m, r) { return r[1] > m[1] ? r : m; }, [0, -Infinity]), van = null;
    for (var i = 1; i < full.length; i++) if (full[i][0] > mx[0] && full[i - 1][1] > 0 && full[i][1] <= 0) { van = full[i - 1][0] + full[i - 1][1] / (full[i - 1][1] - full[i][1]); break; }
    var eq = St.equilibrium(p, o), de = St.edgeAngle(p, o, [h.B / 2, h.D], true);
    q.innerHTML = '<div><span>Displacement per metre of length</span><span>' + f(u.A * St.RHO_SW, 1) + ' t</span></div>' +
      '<div><span>KB · BM · KM</span><span>' + f(u.KB) + ' · ' + f(u.BM) + ' · ' + f(u.KM) + ' m</span></div>' +
      (o.fsc ? '<div><span>Free-surface rise of G</span><span>' + f(o.fsc, 3) + ' m</span></div>' : '') +
      '<div><span>GM' + (o.fsc ? ' (fluid)' : '') + '</span><span' + (GM < 0 ? ' class="warn"' : '') + '>' + f(GM, 3) + ' m</span></div>' +
      '<div><span>Roll period, rough (k = 0.4 B)</span><span>' + (GM > 0.01 ? f(2 * M.PI * 0.4 * h.B / M.sqrt(9.81 * GM), 1) + ' s' : '—') + '</span></div>' +
      '<div><span>Lies at</span><span' + (eq === null || M.abs(eq) > 0.05 ? ' class="warn"' : '') + '>' + (eq === null ? 'capsizes' : M.abs(eq) < 0.05 ? 'upright' : f(M.abs(eq), 1) + '° to ' + (eq > 0 ? 'starboard' : 'port') + (o.Gy === 0 ? ' (loll)' : ' (list)')) + '</span></div>' +
      '<div><span>Deck edge immerses at</span><span>' + (de === null ? 'beyond 90°' : f(de, 1) + '°') + '</span></div>' +
      '<div><span>Maximum GZ</span><span>' + f(mx[1], 3) + ' m at ' + mx[0] + '°</span></div>' +
      '<div><span>Vanishing stability</span><span>' + (van === null ? (mx[1] <= 0 ? '—' : 'beyond 180°') : f(van, 1) + '°') + '</span></div>';

    // ---------------------------------------------------------------- the section
    var A0 = u.A, w = St.waterline(p, A0, th), sn = M.sin(th), cs = M.cos(th), c = w.c;
    function E(pt) { return [pt[0] * cs + pt[1] * sn, -pt[0] * sn + pt[1] * cs - c]; }
    var Gp = [o.Gy, o.KG + o.fsc], Ge = E(Gp), s = M.min(380 / h.B, 300 / h.D) * 0.8, ox = 300 - Ge[0] * s, wy = 250;
    function P(pt) { var e = E(pt); return [ox + e[0] * s, wy - e[1] * s]; }
    function poly(pp) { return pp.map(function (q2) { var r = P(q2); return r[0].toFixed(1) + ',' + r[1].toFixed(1); }).join(' '); }
    var g = '<rect x="0" y="' + wy + '" width="600" height="' + (450 - wy) + '" class="sea"/><line x1="0" x2="600" y1="' + wy + '" y2="' + wy + '" class="wl"/>';
    g += '<polygon points="' + poly(p) + '" class="hullp"/><polygon points="' + poly(w.sub) + '" class="subp"/>';
    var k0 = P([0, -0.05 * h.D]), k1 = P([0, 1.2 * h.D]);
    g += '<line x1="' + k0[0] + '" y1="' + k0[1] + '" x2="' + k1[0] + '" y2="' + k1[1] + '" class="cl"/>';
    if (o.fsc) {   // the slack tank: a box low in the hull with a horizontal liquid surface
      var tb = +el.sFs.value / 2, tz0 = 0.06 * h.D, tz1 = 0.24 * h.D, tank = [[-tb, tz0], [tb, tz0], [tb, tz1], [-tb, tz1]];
      var mid = [0, (tz0 + tz1) / 2], hm = -mid[0] * sn + mid[1] * cs;
      var liq = St.clipBelow(tank, 0, hm, th);
      g += '<polygon points="' + poly(tank) + '" class="tankp"/><polygon points="' + poly(liq) + '" class="liqp"/>';
    }
    var Bp = P([w.B.y, w.B.z]), Gs = P(Gp), Ms = P([0, u.KM]), Zs = [Bp[0], Gs[1]];
    g += '<line x1="' + Bp[0] + '" y1="' + Bp[1] + '" x2="' + Bp[0] + '" y2="' + (Bp[1] - 90) + '" class="fup"/>' +
      '<line x1="' + Gs[0] + '" y1="' + Gs[1] + '" x2="' + Gs[0] + '" y2="' + (Gs[1] + 90) + '" class="fdn"/>' +
      '<line x1="' + Gs[0] + '" y1="' + Gs[1] + '" x2="' + Zs[0] + '" y2="' + Zs[1] + '" class="gzl"/>';
    if (th < 25 * D2R) g += '<circle cx="' + Ms[0] + '" cy="' + Ms[1] + '" r="5" class="pm"/><text x="' + (Ms[0] + 8) + '" y="' + (Ms[1] - 6) + '" class="lbl">M</text>';
    g += '<circle cx="' + Bp[0] + '" cy="' + Bp[1] + '" r="6" class="pb"/><text x="' + (Bp[0] + 9) + '" y="' + (Bp[1] + 16) + '" class="lbl">B</text>' +
      '<circle cx="' + Gs[0] + '" cy="' + Gs[1] + '" r="6" class="pg"/><text x="' + (Gs[0] - 18) + '" y="' + (Gs[1] - 8) + '" class="lbl">G</text>' +
      '<circle cx="' + Zs[0] + '" cy="' + Zs[1] + '" r="3.5" class="pz"/><text x="' + (Zs[0] + 6) + '" y="' + (Zs[1] - 6) + '" class="lbl">Z</text>';
    var gzNow = St.gz(p, o, th);
    g += '<text x="12" y="22" class="lbl">heel ' + (+el.sH.value).toFixed(1) + '° · GZ = ' + f(gzNow, 3) + ' m ' + (gzNow >= 0 ? '(rights the ship)' : '(capsizing lever)') + '</text>' +
      '<text x="588" y="440" text-anchor="end" class="small-t">seen from aft · starboard to the right</text>';
    svg.innerHTML = g;

    // ---------------------------------------------------------------- the GZ curve
    var hi = M.max(0.2, mx[1], GM > 0 ? GM : 0) * 1.12, lo = M.max(M.min(-0.1, M.min.apply(null, cv.map(function (r) { return r[1]; }))), -0.8 * hi);
    function gx(d) { return 60 + d / 90 * 680; }
    function gy(v) { return 290 - (v - lo) / (hi - lo) * 260; }
    var gg = '<defs><clipPath id="gzclip"><rect x="60" y="30" width="680" height="260"/></clipPath></defs>';
    for (var d = 0; d <= 90; d += 10) gg += '<line x1="' + gx(d) + '" x2="' + gx(d) + '" y1="30" y2="290" class="grid"/><text x="' + gx(d) + '" y="308" text-anchor="middle">' + d + '°</text>';
    var stp = (hi - lo) > 2 ? 0.5 : (hi - lo) > 0.8 ? 0.2 : 0.1;
    for (var v = M.ceil(lo / stp) * stp; v <= hi; v += stp) gg += '<line x1="60" x2="740" y1="' + gy(v) + '" y2="' + gy(v) + '" class="grid"/><text x="54" y="' + (gy(v) + 4) + '" text-anchor="end">' + f(v, stp < 0.2 ? 1 : 1) + '</text>';
    gg += '<line x1="60" x2="740" y1="' + gy(0) + '" y2="' + gy(0) + '" class="axis"/><text x="18" y="22">GZ (m)</text>';
    function area(a, b, cls) {
      var pp = [[gx(a), gy(0)]]; cv.forEach(function (r) { if (r[0] >= a && r[0] <= b) pp.push([gx(r[0]), gy(M.max(0, r[1]))]); }); pp.push([gx(b), gy(0)]);
      return '<polygon points="' + pp.map(function (z) { return z[0].toFixed(1) + ',' + z[1].toFixed(1); }).join(' ') + '" class="' + cls + '"/>';
    }
    gg += area(0, 30, 'ar1') + area(30, 40, 'ar2');
    if (GM > 0) gg += '<line x1="' + gx(0) + '" y1="' + gy(0) + '" x2="' + gx(57.3) + '" y2="' + gy(GM) + '" class="tan"/><circle cx="' + gx(57.3) + '" cy="' + gy(GM) + '" r="3.5" class="pm"/><text x="' + (gx(57.3) + 6) + '" y="' + (gy(GM) - 6) + '">GM at 57.3°</text>';
    gg += '<polyline points="' + cv.map(function (r) { return gx(r[0]).toFixed(1) + ',' + gy(r[1]).toFixed(1); }).join(' ') + '" class="gzc" clip-path="url(#gzclip)"/>';
    var hd = +el.sH.value; gg += '<line x1="' + gx(hd) + '" x2="' + gx(hd) + '" y1="30" y2="290" class="now"/><circle cx="' + gx(hd) + '" cy="' + gy(gzNow) + '" r="5" class="pg"/>';
    if (eq !== null && eq > 0.05) gg += '<text x="' + gx(eq) + '" y="' + (gy(0) + 16) + '" text-anchor="middle">list</text>';
    gsv.innerHTML = gg;

    crit.innerHTML = St.criteria(p, o, cv).map(function (r) {
      var d = r.unit === '°' ? 0 : 3;
      return '<tr><td>' + r.name + '</td><td class="num">≥ ' + r.min + (d ? ' ' : '') + r.unit + '</td><td class="num">' + (isFinite(r.value) ? f(r.value, d) : '—') + (d ? ' ' : '') + r.unit + '</td><td>' + (r.ok ? '<span class="tag exact">meets</span>' : '<span class="tag warn">fails</span>') + '</td></tr>';
    }).join('');
  }
  var raf = 0;
  function sched() { if (!raf) raf = requestAnimationFrame(function () { raf = 0; draw(); }); }
  hs.addEventListener('change', function () { setHull(hs.value); draw(); });
  ['sT', 'sKG', 'sGy', 'sFs', 'sH'].forEach(function (k) { el[k].addEventListener('input', sched); });
  hs.value = 'cargo'; setHull('cargo'); draw();
})();
