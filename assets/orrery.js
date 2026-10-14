/* Planets page: a top-down orrery (heliocentric, ecliptic J2000) for any date within ±10 years of today,
   with each planet's elongation, configuration and the constellation it stands in front of. */
(function () {
  'use strict';
  var A = window.RK_ASTRO, M = Math, PL = window.RK_PL, NAMES = window.RK_CNAMES;
  A.setBounds(window.RK_CONST);
  var svg = document.getElementById('orr'); if (!svg) return;
  var sl = document.getElementById('odate'), slv = document.getElementById('odatev'), tab = document.getElementById('otab'), play = document.getElementById('oplay'), trueSc = document.getElementById('oscale');
  var KEYS = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune'];
  var COL = { mercury: '#8a8f94', venus: '#d9a441', earth: '#2f6fb3', mars: '#c8461d', jupiter: '#b5835a', saturn: '#c9a95c', uranus: '#4fb3c4', neptune: '#3b5bd6' };
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var jNow = A.jd(new Date()), orbits = {};
  function R(r) { return trueSc.checked ? r / 30.1 * 270 : M.sqrt(r / 30.1) * 270; }
  KEYS.forEach(function (k) {   // one revolution of each orbit, sampled from the elements
    var P = M.pow(A.EL[k][0], 1.5) * 365.25, pts = [];
    for (var i = 0; i <= 160; i++) { var v = A.helio(k, jNow + P * i / 160); pts.push([v.x, v.y]); }
    orbits[k] = pts;
  });
  function config(k, j, g) {
    if (k === 'earth') return '';
    var inner = k === 'mercury' || k === 'venus', e = g.elong;
    if (e < 6) return inner ? (g.dist < 1 ? 'inferior conjunction' : 'superior conjunction') : 'conjunction with the Sun';
    if (!inner && e > 174) return 'opposition';
    if (!inner && M.abs(e - 90) < 3) return (g.east ? 'eastern' : 'western') + ' quadrature';
    if (inner) {
      var a = A.planetGeo(k, j - 1).elong, b = A.planetGeo(k, j + 1).elong;
      if (e >= a && e >= b) return 'greatest ' + (g.east ? 'eastern' : 'western') + ' elongation';
    }
    return g.east ? 'evening sky (east of the Sun)' : 'morning sky (west of the Sun)';
  }
  function draw() {
    var j = jNow + (+sl.value), d = A.dateFromJd(j), g = '';
    slv.textContent = d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear();
    g += '<line x1="0" y1="0" x2="290" y2="0" class="aux"/><text x="290" y="16" text-anchor="end" font-size="12">♈︎ March equinox →</text>';
    KEYS.forEach(function (k) {
      g += '<path d="' + orbits[k].map(function (p, i) { var r = M.hypot(p[0], p[1]), s = R(r) / r; return (i ? 'L' : 'M') + (p[0] * s).toFixed(1) + ' ' + (-p[1] * s).toFixed(1); }).join('') + '" fill="none" stroke="var(--rule)" stroke-width="1"/>';
    });
    g += '<circle r="9" fill="var(--flag-y)"/>';
    var E = A.helio('earth', j), ex = E.x * R(M.hypot(E.x, E.y)) / M.hypot(E.x, E.y), ey = -E.y * R(M.hypot(E.x, E.y)) / M.hypot(E.x, E.y);
    var rows = '';
    KEYS.forEach(function (k) {
      var v = A.helio(k, j), r = M.hypot(v.x, v.y), x = v.x * R(r) / r, y = -v.y * R(r) / r;
      if (k !== 'earth') g += '<line x1="' + ex.toFixed(1) + '" y1="' + ey.toFixed(1) + '" x2="' + x.toFixed(1) + '" y2="' + y.toFixed(1) + '" stroke="' + COL[k] + '" stroke-opacity="0.35" stroke-dasharray="3 4"/>';
      g += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + (k === 'jupiter' || k === 'saturn' ? 8 : 6) + '" fill="' + COL[k] + '" stroke="var(--sheet)" stroke-width="1.5"/>' +
        '<text x="' + (x + 10).toFixed(1) + '" y="' + (y + 4).toFixed(1) + '" font-size="13">' + PL[k][1] + '︎ ' + PL[k][0] + '</text>';
      if (k === 'earth') return;
      var geo = A.planetGeo(k, j), con = A.constellation(geo.ra, geo.dec, 2000);
      rows += '<tr><td><span class="pdot" style="background:' + COL[k] + '"></span><b>' + PL[k][0] + '</b></td><td class="num">' + geo.elong.toFixed(0) + '° ' + (geo.east ? 'E' : 'W') +
        '</td><td class="small">' + config(k, j, geo) + '</td><td>' + (NAMES[con] || con) + '</td><td class="num">' + geo.dist.toFixed(2) + ' au</td></tr>';
    });
    svg.innerHTML = g;
    tab.innerHTML = rows;
  }
  var timer = null;
  play.addEventListener('click', function () {
    if (timer) { clearInterval(timer); timer = null; play.textContent = 'Play'; return; }
    play.textContent = 'Pause';
    timer = setInterval(function () { var v = +sl.value + 2; if (v > +sl.max) v = +sl.min; sl.value = v; draw(); }, 40);
  });
  document.getElementById('otoday').addEventListener('click', function () { sl.value = 0; draw(); });
  sl.addEventListener('input', draw); trueSc.addEventListener('change', draw);
  draw();
})();
