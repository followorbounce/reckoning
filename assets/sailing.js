/* Sailing page: great circle against rhumb line between two ports, on a Mercator chart (rhumb line
   straight) and on a gnomonic chart centred on the route (great circle straight). Maths in navmath.js. */
(function () {
  'use strict';
  var N = window.RK_NAV, P = window.RK_PORTS, M = Math, D2R = M.PI / 180;
  var sf = document.getElementById('sfrom'), st = document.getElementById('sto'), out = document.getElementById('sout');
  var merc = document.getElementById('mmerc'), gno = document.getElementById('mgno');
  if (!sf) return;
  var land = null;
  fetch('../../assets/land.json').then(function (r) { return r.json(); }).then(function (d) { land = d; draw(); }).catch(function () { /* charts work without coastlines */ });

  // ---------------------------------------------------------------- projections
  function mercProj(lon0, W, H) {   // centred on lon0, latitudes ±80°
    var ymax = M.log(M.tan(M.PI / 4 + 80 * D2R / 2)), k = W / (2 * M.PI);
    return function (lat, lon) {
      var x = N.wrap180(lon - lon0) * D2R * k + W / 2, la = M.max(-85, M.min(85, lat));
      var y = H / 2 - M.log(M.tan(M.PI / 4 + la * D2R / 2)) * (H / 2) / ymax;
      return [x, y];
    };
  }
  function gnoProj(c, scale, W, H) {   // centre c = [lat, lon]; returns null for points more than ~80° from the centre
    var f0 = c[0] * D2R, l0 = c[1] * D2R, sf0 = M.sin(f0), cf0 = M.cos(f0);
    return function (lat, lon) {
      var f = lat * D2R, l = lon * D2R, cosc = sf0 * M.sin(f) + cf0 * M.cos(f) * M.cos(l - l0);
      if (cosc < 0.17) return null;
      var x = M.cos(f) * M.sin(l - l0) / cosc, y = (cf0 * M.sin(f) - sf0 * M.cos(f) * M.cos(l - l0)) / cosc;
      return [W / 2 + x * scale, H / 2 - y * scale];
    };
  }
  function path(pts, proj, W, breakJump) {
    var d = '', prev = null;
    pts.forEach(function (p) {
      var q = proj(p[0], p[1]);
      if (!q) { prev = null; return; }
      var jump = !prev || (breakJump && M.abs(q[0] - prev[0]) > W / 2);
      d += (jump ? 'M' : 'L') + q[0].toFixed(1) + ' ' + q[1].toFixed(1);
      prev = q;
    });
    return d;
  }
  function landPath(proj, W, wrap) {   // whole rings are filled; rings cut by the chart edge are only outlined
    if (!land) return '';
    var fill = '', edge = '';
    land.forEach(function (ring) {
      var d = path(ring.map(function (p) { return [p[1], p[0]]; }), proj, W, wrap);
      if (!d) return;
      if (d.indexOf('M', 1) < 0) fill += d + 'Z'; else edge += d;
    });
    return '<path class="mland" d="' + fill + '"/><path class="mland edge" d="' + edge + '"/>';
  }
  function graticule(proj, W, wrap, step) {
    var d = '';
    for (var la = -80; la <= 80; la += step) { var p = []; for (var lo = -180; lo <= 180; lo += 2) p.push([la, lo]); d += path(p, proj, W, wrap); }
    for (var lo2 = -180; lo2 < 180; lo2 += step) { var q = []; for (var la2 = -80; la2 <= 80; la2 += 2) q.push([la2, lo2]); d += path(q, proj, W, wrap); }
    return '<path class="mgrat" d="' + d + '"/>';
  }
  function dot(proj, p, label) {
    var q = proj(p[0], p[1]); if (!q) return '';
    return '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="5" class="mport"/><text x="' + (q[0] + 8).toFixed(1) + '" y="' + (q[1] - 8).toFixed(1) + '" class="mlbl">' + label + '</text>';
  }

  function fmtC(c) { return String(M.round(c)).padStart(3, '0') + '°'; }
  function nm(x) { return M.round(x).toLocaleString('en-US') + ' nmi'; }
  function draw() {
    var a = P[+sf.value], b = P[+st.value], p1 = [a[1], a[2]], p2 = [b[1], b[2]];
    if (sf.value === st.value) { out.innerHTML = '<tr><td>Choose two different ports.</td></tr>'; return; }
    var gc = N.gcPoints(p1, p2, 240), rl = N.rhumbPoints(p1, p2, 240).pts;
    // Mercator, centred midway in longitude
    var lon0 = p1[1] + N.wrap180(p2[1] - p1[1]) / 2, mp = mercProj(lon0, 720, 520);
    merc.innerHTML = graticule(mp, 720, true, 20) + landPath(mp, 720, true) +
      '<path class="mrl" d="' + path(rl, mp, 720, true) + '"/><path class="mgc" d="' + path(gc, mp, 720, true) + '"/>' + dot(mp, p1, a[0]) + dot(mp, p2, b[0]);
    // gnomonic, centred on the great-circle midpoint, scaled to fit both ports
    var mid = gc[120], g0 = gnoProj(mid, 1, 0, 0), e1 = g0(p1[0], p1[1]), e2 = g0(p2[0], p2[1]);
    var ext = M.max(0.2, e1 ? M.hypot(e1[0], e1[1]) : 3, e2 ? M.hypot(e2[0], e2[1]) : 3), gp = gnoProj(mid, 165 / ext, 520, 520);
    gno.innerHTML = graticule(gp, 520, false, 10) + landPath(gp, 520, false) +
      '<path class="mrl" d="' + path(rl, gp, 520, false) + '"/><path class="mgc" d="' + path(gc, gp, 520, false) + '"/>' + dot(gp, p1, a[0]) + dot(gp, p2, b[0]);
    // numbers
    var dg = N.haversine(p1, p2), r = N.rhumb(p1, p2), ml = N.midLatitude(p1, p2), v = N.vincenty(p1, p2), vlat = N.vertexLat(p1, p2);
    var top = 0; gc.forEach(function (p) { if (M.abs(p[0]) > M.abs(top)) top = p[0]; });
    var inside = M.abs(M.abs(top) - vlat) < 0.05;
    out.innerHTML =
      '<tr><th></th><th>Great circle</th><th>Rhumb line</th></tr>' +
      '<tr><td>Distance (sphere, 1′ = 1 nmi)</td><td class="num"><b>' + nm(dg) + '</b></td><td class="num"><b>' + nm(r.dist) + '</b></td></tr>' +
      '<tr><td>Course</td><td class="num">starts ' + fmtC(N.initialCourse(p1, p2)) + ', ends ' + fmtC(N.finalCourse(p1, p2)) + '</td><td class="num">' + fmtC(r.course) + ' all the way</td></tr>' +
      '<tr><td>Saving by great circle</td><td class="num" colspan="2">' + nm(r.dist - dg) + ' (' + ((r.dist - dg) / r.dist * 100).toFixed(1) + ' %)</td></tr>' +
      '<tr><td>Highest latitude on the route</td><td class="num">' + N.fmtDM(top, 'N', 'S') + (inside ? ' (the vertex)' : ' (at a port; the vertex ' + N.fmtDM(vlat, '', '') + ' lies beyond)') + '</td><td class="num">' + N.fmtDM(M.abs(p1[0]) > M.abs(p2[0]) ? p1[0] : p2[0], 'N', 'S') + '</td></tr>' +
      '<tr><td>On the WGS 84 ellipsoid (Vincenty)</td><td class="num">' + (v ? nm(v.dist / 1852) + ' (' + ((v.dist / 1852 - dg) / dg * 100).toFixed(2) + ' % vs sphere)' : 'nearly antipodal: no solution') + '</td><td></td></tr>' +
      '<tr class="hist"><td>Mid-latitude sailing (old shortcut)</td><td></td><td class="num">' + nm(ml.dist) + ', ' + fmtC(ml.course) + ' (' + ((ml.dist - r.dist) / r.dist * 100).toFixed(1) + ' % off)</td></tr>';
  }
  sf.addEventListener('change', draw); st.addEventListener('change', draw);
  function byName(n) { for (var i = 0; i < P.length; i++) if (P[i][0] === n) return i; return 0; }
  document.querySelectorAll('[data-route]').forEach(function (b) {
    b.addEventListener('click', function () { var p = b.getAttribute('data-route').split('|'); sf.value = byName(p[0]); st.value = byName(p[1]); draw(); });
  });
  sf.value = byName('Yokohama'); st.value = byName('San Francisco');
  draw();
})();
