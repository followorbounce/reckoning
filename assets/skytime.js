/* Kinds of time page: live clocks for a chosen longitude, the equation of time over the current year,
   and the analemma. Sun and sidereal time from astro.js. */
(function () {
  'use strict';
  var A = window.RK_ASTRO, M = Math;
  var lonIn = document.getElementById('tlon'), box = document.getElementById('clocks'), dev = document.getElementById('tdev');
  if (!box) return;
  var LET = { 0: 'Z' }; 'ABCDEFGHIKLM'.split('').forEach(function (c, i) { LET[-(i + 1)] = c; }); 'NOPQRSTUVWXY'.split('').forEach(function (c, i) { LET[i + 1] = c; });
  function hms(h, secs) {
    h = ((h % 24) + 24) % 24;
    var t = M.floor(h * 3600 + 1e-6), s = t % 60, m = M.floor(t / 60) % 60, hh = M.floor(t / 3600);
    return String(hh).padStart(2, '0') + ':' + String(m).padStart(2, '0') + (secs === false ? '' : ':' + String(s).padStart(2, '0'));
  }
  function minsec(x) { var s = M.round(M.abs(x) * 60); return (x < 0 ? '−' : '+') + M.floor(s / 60) + ' min ' + String(s % 60).padStart(2, '0') + ' s'; }
  // A guess at the device longitude from its UTC offset (only to pre-fill the box)
  var guess = -new Date().getTimezoneOffset() / 60 * 15;
  if (M.abs(guess) <= 180) lonIn.value = guess;

  function tick() {
    var now = new Date(), j = A.jd(now), s = A.sun(j), lon = parseFloat(lonIn.value);
    if (!isFinite(lon)) lon = 0;
    lon = M.max(-180, M.min(180, lon));
    var ut = now.getUTCHours() + now.getUTCMinutes() / 60 + now.getUTCSeconds() / 3600 + now.getUTCMilliseconds() / 3.6e6;
    var zd = -M.round(lon / 15); if (zd === -12 && lon < 0) zd = 12;
    var lmt = ut + lon / 15, lat = lmt + s.eot / 60, g = A.gmst(j), lst = g + lon / 15;
    var dayShift = function (h) { var d = M.floor((h) / 24); return d > 0 ? ' (+1 day)' : d < 0 ? ' (−1 day)' : ''; };
    var rows = [
      ['UTC', hms(ut), now.toISOString().slice(0, 10)],
      ['Zone time', hms(ut - zd) + dayShift(ut - zd), 'zone ' + (zd > 0 ? '+' : zd < 0 ? '−' : '') + M.abs(zd) + ' (' + LET[zd] + '), central meridian ' + M.abs(zd * 15) + '°' + (zd > 0 ? 'W' : zd < 0 ? 'E' : '')],
      ['Local mean time', hms(lmt) + dayShift(lmt), 'UTC ' + (lon >= 0 ? '+' : '−') + ' ' + M.floor(M.abs(lon) / 15) + ' h ' + String(M.round(M.abs(lon) % 15 * 4)).padStart(2, '0') + ' min (4 min per degree)'],
      ['Apparent solar time', hms(lat) + dayShift(lat), 'what a sundial here shows: mean time ' + minsec(s.eot)],
      ['Greenwich sidereal', hms(g), 'mean sidereal time at Greenwich'],
      ['Local sidereal', hms(lst), 'right ascension now on your meridian'],
    ];
    box.innerHTML = rows.map(function (r) { return '<div class="clock"><span class="ck">' + r[0] + '</span><span class="cv">' + r[1] + '</span><span class="cn">' + r[2] + '</span></div>'; }).join('') +
      '<div class="clock"><span class="ck">The Sun</span><span class="cv sm">δ ' + s.dec.toFixed(2) + '°</span><span class="cn">declination; right ascension ' + hms(s.ra / 15, false) + '</span></div>';
    dev.textContent = now.toString().replace(/ \(.*\)$/, '');
  }
  lonIn.addEventListener('input', tick);
  document.querySelectorAll('[data-lon]').forEach(function (b) { b.addEventListener('click', function () { lonIn.value = b.getAttribute('data-lon'); tick(); }); });
  tick(); setInterval(tick, 1000);

  // ---------------------------------------------------------------- the year
  var y = new Date().getUTCFullYear(), j0 = A.jdCal(y, 1, 1), days = M.round(A.jdCal(y + 1, 1, 1) - j0), pts = [];
  for (var d = 0; d < days; d++) { var sn = A.sun(j0 + d + 0.5); pts.push([d, sn.eot, sn.dec]); }
  var today = M.floor(A.jd(new Date()) - j0), MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var eot = document.getElementById('eot');
  if (eot) {
    var W = 720, H = 300, x0 = 46, x1 = 706, ymin = -16, ymax = 18;
    var X = function (dd) { return x0 + dd / days * (x1 - x0); }, Y = function (v) { return 20 + (ymax - v) / (ymax - ymin) * (H - 50); };
    var g = '';
    for (var v = -15; v <= 15; v += 5) g += '<line class="aux" x1="' + x0 + '" x2="' + x1 + '" y1="' + Y(v) + '" y2="' + Y(v) + '"/><text x="' + (x0 - 6) + '" y="' + (Y(v) + 4) + '" text-anchor="end" font-size="11">' + (v > 0 ? '+' : '') + String(v).replace('-', '−') + '</text>';
    g += '<line x1="' + x0 + '" x2="' + x1 + '" y1="' + Y(0) + '" y2="' + Y(0) + '" stroke="var(--ink)"/>';
    for (var m = 0; m < 12; m++) { var dm = A.jdCal(y, m + 1, 1) - j0; g += '<line class="aux" x1="' + X(dm) + '" x2="' + X(dm) + '" y1="' + Y(ymax) + '" y2="' + Y(ymin) + '"/><text x="' + (X(dm) + 4) + '" y="' + (H - 12) + '" font-size="11">' + MON[m] + '</text>'; }
    g += '<path d="' + pts.map(function (p, i) { return (i ? 'L' : 'M') + X(p[0]).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('') + '" fill="none" stroke="var(--flag-b)" stroke-width="2.5"/>';
    if (today >= 0 && today < days) g += '<circle cx="' + X(today) + '" cy="' + Y(pts[today][1]) + '" r="6" fill="var(--signal)"/><text x="' + (X(today) + 9) + '" y="' + (Y(pts[today][1]) - 8) + '" class="lbl" font-size="12">today ' + minsec(pts[today][1]) + '</text>';
    g += '<text x="' + (x0 + 6) + '" y="16" font-size="11">minutes: sundial ahead of the clock (+) or behind (−), ' + y + '</text>';
    eot.innerHTML = g;
  }
  var ana = document.getElementById('ana');
  if (ana) {
    var AX = function (v) { return 150 + v * 7.5; }, AY = function (dd) { return 200 - dd * 7.6; }, a = '';
    a += '<line class="aux" x1="150" x2="150" y1="10" y2="390"/><line class="aux" x1="20" x2="280" y1="200" y2="200"/>';
    a += '<text x="154" y="22" font-size="11">δ +23.4°</text><text x="154" y="388" font-size="11">δ −23.4°</text><text x="282" y="196" text-anchor="end" font-size="11">sundial fast →</text>';
    a += '<path d="' + pts.map(function (p, i) { return (i ? 'L' : 'M') + AX(p[1]).toFixed(1) + ' ' + AY(p[2]).toFixed(1); }).join('') + 'Z" fill="none" stroke="var(--flag-b)" stroke-width="2.5"/>';
    for (var mm = 0; mm < 12; mm++) { var p0 = pts[M.round(A.jdCal(y, mm + 1, 1) - j0)]; a += '<circle cx="' + AX(p0[1]) + '" cy="' + AY(p0[2]) + '" r="3" fill="var(--ink)"/><text x="' + (AX(p0[1]) + (p0[1] > 0 ? 6 : -6)) + '" y="' + (AY(p0[2]) + 4) + '" font-size="10" text-anchor="' + (p0[1] > 0 ? 'start' : 'end') + '">' + MON[mm] + '</text>'; }
    if (today >= 0 && today < days) a += '<circle cx="' + AX(pts[today][1]) + '" cy="' + AY(pts[today][2]) + '" r="6" fill="var(--signal)"/>';
    ana.innerHTML = a;
  }
})();
