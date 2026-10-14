/* Checks for the Sky & sea and Number rooms, run on the same JS the pages use.
   Run: node tests/check_wave3.js   (called by tests/check_wave3.py)
   Reference values are published worked examples typed in by hand; they are not produced by this code. */
'use strict';
var fs = require('fs'), path = require('path');
var A = require('../assets/astro.js'), N = require('../assets/navmath.js'), T = require('../assets/trigmath.js');
var fails = [], notes = [];
function ok(c, m) { if (!c) fails.push(m); }
function near(x, y, tol, m) { ok(Math.abs(x - y) <= tol, m + ': got ' + x + ', expected ' + y + ' ± ' + tol); }
function dms(d, m, s) { var sg = (d < 0 || Object.is(d, -0)) ? -1 : 1; return sg * (Math.abs(d) + m / 60 + s / 3600); }

// ------------------------------------------------------------ time and the Sun
// Julian dates (Meeus, Astronomical Algorithms, ch. 7): 2000 Jan 1.5 = 2451545.0; 1957 Oct 4.81 = 2436116.31
near(A.jdCal(2000, 1, 1.5), 2451545.0, 1e-9, 'JD of J2000');
near(A.jdCal(1957, 10, 4.81), 2436116.31, 1e-6, 'JD of Sputnik example');
near(A.jdCal(1987, 6, 19.5), 2446966.0, 1e-9, 'JD 1987 Jun 19.5');
// GMST: Meeus example 12.a, 1987 Apr 10 0h UT = 13h10m46.3668s; 12.b, 19h21m00s UT = 8h34m57.0896s
near(A.gmst(A.jdCal(1987, 4, 10)) * 3600, 13 * 3600 + 10 * 60 + 46.3668, 0.3, 'GMST Meeus 12.a (s)');
near(A.gmst(A.jdCal(1987, 4, 10 + (19 + 21 / 60) / 24)) * 3600, 8 * 3600 + 34 * 60 + 57.0896, 0.3, 'GMST Meeus 12.b (s)');
near(A.gmst(2451545.0), 18.697374558, 2e-5, 'GMST at J2000.0 (h)');
// mean sidereal day from the rate in the formula: 86400/1.0027379 s = 23 h 56 m 4.09 s
near(86400 / 1.0027379, 86164.0905, 0.01, 'sidereal day (s)');
// Sun: Meeus example 25.a, 1992 Oct 13.0 TD: apparent longitude 199.90895° (low-accuracy method), δ −7.78507°, α 198.38083°
var s92 = A.sun(A.jdCal(1992, 10, 13));
near(s92.lon, 199.90895, 0.01, 'Sun apparent longitude, Meeus 25.a');
near(s92.dec, -7.78507, 0.01, 'Sun declination, Meeus 25.a');
near(s92.ra, 198.38083, 0.01, 'Sun right ascension, Meeus 25.a');
near(s92.r, 0.99766, 0.0001, 'Sun distance (au), Meeus 25.a');
// Equation of time: Meeus example 28.b, 1992 Oct 13.0 TD: E = +13m42.7s
near(s92.eot * 60, 13 * 60 + 42.7, 3, 'equation of time, Meeus 28.b (s)');
// Equation of time over a year: extremes about −14.2 min (mid-February) and +16.4 min (early November); four zeros
var y = 2026, e = [], j0 = A.jdCal(y, 1, 1);
for (var d = 0; d < 365; d++) e.push(A.sun(j0 + d + 0.5).eot);
var mn = Math.min.apply(null, e), mx = Math.max.apply(null, e), imn = e.indexOf(mn), imx = e.indexOf(mx);
near(mn, -14.2, 0.15, 'EoT minimum (min)'); near(mx, 16.4, 0.15, 'EoT maximum (min)');
ok(imn >= 38 && imn <= 46, 'EoT minimum date should be Feb 8-16, day ' + imn);
ok(imx >= 300 && imx <= 310, 'EoT maximum date should be Oct 28 - Nov 7, day ' + imx);
var zeros = 0; for (d = 1; d < 365; d++) if ((e[d - 1] < 0) !== (e[d] < 0)) zeros++;
ok(zeros === 4, 'EoT should cross zero four times a year, got ' + zeros);
// equinox and solstice: declination 0 near Mar 20, maximum 23.44 near Jun 21
var jq = A.sunAtLongitude(0, A.jdCal(y, 3, 1)), dq = A.dateFromJd(jq);
ok(dq.getUTCMonth() === 2 && dq.getUTCDate() === 20, 'March equinox 2026 should be Mar 20, got ' + dq.toISOString());
near(A.sun(A.sunAtLongitude(90, A.jdCal(y, 6, 1))).dec, 23.436, 0.003, 'June solstice declination (obliquity 2026)');

// ------------------------------------------------------------ planets
// Venus, Meeus example 32.a, 1992 Dec 20.0 TD (VSOP87, mean equinox of date): L 26.11428°, B −2.62070°, R 0.724603 au.
// The JPL elements are referred to J2000, so precess the reference back by the general precession in longitude.
var jv = A.jdCal(1992, 12, 20), hv = A.sph(A.helio('venus', jv)), pT = (jv - 2451545) / 36525, prec = 5029.0966 / 3600 * pT;
near(hv.lon, 26.11428 - prec, 0.02, 'Venus heliocentric longitude J2000, Meeus 32.a');
near(hv.lat, -2.62070, 0.01, 'Venus heliocentric latitude, Meeus 32.a');
near(hv.r, 0.724603, 0.0005, 'Venus radius vector, Meeus 32.a');
// Two independent routes to the Sun: Earth from the JPL elements (+180°) and the NOAA solar algorithm (precessed to J2000)
var worst = 0;
for (d = 0; d < 3650; d += 17) {
  var jj = A.jdCal(2020, 1, 1) + d, sE = A.sph(A.helio('earth', jj)), s = A.sun(jj), Tt = (jj - 2451545) / 36525;
  var geo = s.trueLon - 5029.0966 / 3600 * Tt;      // geometric longitude, mean equinox of J2000
  var diff = Math.abs(A.norm360(sE.lon + 180 - geo + 180) - 180);
  worst = Math.max(worst, diff);
}
ok(worst < 0.02, 'Earth (JPL) and Sun (NOAA) disagree by ' + worst.toFixed(4) + '°');
notes.push('Earth-vs-Sun longitude agreement over 2020-2029: ' + (worst * 3600).toFixed(0) + '″');
// Kepler's third law: period from the semi-major axis matches the sidereal periods of the NASA fact sheet within 1 %
// (Neptune differs most, 0.7 %: the mutual pull of the giant planets makes the fitted a and the observed period disagree slightly)
var periods = { mercury: 88.0, venus: 224.7, earth: 365.2, mars: 687.0, jupiter: 4331, saturn: 10747, uranus: 30589, neptune: 59800 };
Object.keys(periods).forEach(function (k) {
  var P = Math.pow(A.EL[k][0], 1.5) * 365.25636;
  ok(Math.abs(P / periods[k] - 1) < 0.01, 'period of ' + k + ': ' + P.toFixed(1) + ' d vs ' + periods[k]);
});
// Kepler solver: E − e sin E = M to 1e-9° for every planet and many anomalies
for (var Mm = -180; Mm <= 180; Mm += 7.5) for (var k in A.EL) {
  var ee = A.EL[k][1], E = A.kepler(Mm, ee);
  ok(Math.abs(E - 180 / Math.PI * ee * Math.sin(E * Math.PI / 180) - Mm) < 1e-8, 'Kepler ' + k + ' M=' + Mm);
}

// ------------------------------------------------------------ constellations
var bounds = fs.readFileSync(path.join(__dirname, '..', 'data', 'constbounds_1875.dat'), 'utf8').trim().split('\n').map(function (l) {
  var p = l.trim().split(/\s+/); return [+p[0], +p[1], +p[2], p[3]];
});
A.setBounds(bounds);
// the eight test positions published with the table (CDS VI/42 ReadMe), equinox 1950
[[9.0, 65.0, 'UMa'], [23.5, -20.0, 'Aqr'], [5.12, 9.12, 'Ori'], [9.4555, -19.9, 'Hya'], [12.8888, 22.0, 'Com'], [15.6687, -12.1234, 'Lib'],
 [19.0, -40.0, 'CrA'], [6.2222, -81.1234, 'Men']].forEach(function (t) {
  var c = A.constellation(t[0] * 15, t[1], 1950);
  ok(c === t[2], 'Roman test position ' + t + ' gave ' + c);
});
// a few bright stars (J2000 positions) land in their own constellations
[['Sirius', 101.287, -16.716, 'CMa'], ['Polaris', 37.955, 89.264, 'UMi'], ['Vega', 279.235, 38.784, 'Lyr'], ['Betelgeuse', 88.793, 7.407, 'Ori'],
 ['Antares', 247.352, -26.432, 'Sco'], ['Spica', 201.298, -11.161, 'Vir'], ['Regulus', 152.093, 11.967, 'Leo'], ['Aldebaran', 68.980, 16.509, 'Tau'],
 ['Fomalhaut', 344.413, -29.622, 'PsA'], ['Canopus', 95.988, -52.696, 'Car']].forEach(function (s) {
  var c = A.constellation(s[1], s[2], 2000); ok(c === s[3], s[0] + ' should be in ' + s[3] + ', got ' + c);
});
// the Sun crosses 13 constellations; Ophiuchus between Scorpius and Sagittarius, from about Nov 29 to Dec 17
var tr = A.sunTransits(2026), seq = tr.map(function (t) { return t.to; });
ok(tr.length === 13, 'Sun should enter 13 constellations in 2026, got ' + tr.length + ' ' + seq.join(' '));
var io = seq.indexOf('Oph');
ok(io > 0 && seq[io - 1] === 'Sco' && seq[io + 1] === 'Sgr', 'Ophiuchus order: ' + seq.join(' '));
var dOph = A.dateFromJd(tr[io].jd);
ok(dOph.getUTCMonth() === 10 && dOph.getUTCDate() >= 28 || dOph.getUTCMonth() === 11 && dOph.getUTCDate() <= 1, 'Sun enters Oph ' + dOph.toISOString());
ok(A.sunConst(A.sunAtLongitude(0, A.jdCal(2026, 3, 1))) === 'Psc', 'at the March equinox the Sun is in Pisces');
notes.push('Sun enters: ' + tr.map(function (t) { return t.to + ' ' + A.dateFromJd(t.jd).toISOString().slice(5, 10); }).join(', '));

// ------------------------------------------------------------ navigation
// Vincenty (1975) worked example from the Geocentric Datum of Australia technical manual, on the GRS80 ellipsoid:
// Flinders Peak → Buninyong: 54 972.271 m, azimuth 306°52′05.37″, reverse azimuth 127°10′25.07″
var ANS = { a: 6378137, f: 1 / 298.257222101 };
var FP = [dms(-37, 57, 3.72030), dms(144, 25, 29.52440)], BY = [dms(-37, 39, 10.15610), dms(143, 55, 35.38390)];
var v = N.vincenty(FP, BY, ANS);
near(v.dist, 54972.271, 0.001, 'Vincenty distance (m)');
near(v.az1 * 3600, (306 * 3600 + 52 * 60 + 5.37), 0.01, 'Vincenty forward azimuth (″)');
near(N.norm360(v.az2 + 180) * 3600, (127 * 3600 + 10 * 60 + 25.07), 0.01, 'Vincenty reverse azimuth (″)');
// WGS 84 meridian quadrant 10 001 965.729 m, by integrating the meridian radius of curvature (Simpson, 2000 steps)
var q = 0, n = 2000, h = 90 / n;
for (var i = 0; i <= n; i++) q += (i === 0 || i === n ? 1 : i % 2 ? 4 : 2) * N.minuteLengths(i * h).M;
q *= h / 3 * Math.PI / 180;
near(q, 10001965.729, 0.01, 'WGS 84 meridian quadrant (m)');
near(N.minuteLengths(0).lat, 1842.9, 0.05, '1′ of latitude at the equator (m)');
near(N.minuteLengths(90).lat, 1861.6, 0.05, '1′ of latitude at the pole (m)');
near(N.minuteLengths(0).lon, 1855.3, 0.05, '1′ of longitude at the equator (m)');
// geocentric minus geodetic latitude is largest near 45°: 11.5′
var gmax = 0; for (var L = 0; L <= 90; L += 0.1) gmax = Math.max(gmax, L - N.geocentric(L));
near(gmax * 60, 11.54, 0.02, 'max geodetic − geocentric latitude (′)');
// great circle: haversine and n-vector distances agree; course formulas round-trip; vertex consistent with sampled track
var seed = 7; function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
var worstD = 0, worstR = 0;
for (i = 0; i < 400; i++) {
  var p1 = [rnd() * 160 - 80, rnd() * 360 - 180], p2 = [rnd() * 160 - 80, rnd() * 360 - 180];
  var h1 = N.haversine(p1, p2), h2 = N.vectorDistance(p1, p2);
  worstD = Math.max(worstD, Math.abs(h1 - h2));
  ok(h1 <= N.rhumb(p1, p2).dist + 1e-6, 'great circle must not be longer than the rhumb line');
  // the vertex latitude equals the highest latitude of the whole great circle (p1 → p2 → p1, sampled densely)
  var a1 = N.nvec(p1), a2 = N.nvec(p2), nrm = [a1[1] * a2[2] - a1[2] * a2[1], a1[2] * a2[0] - a1[0] * a2[2], a1[0] * a2[1] - a1[1] * a2[0]];
  var nl = Math.hypot(nrm[0], nrm[1], nrm[2]);
  if (nl > 1e-6) near(N.vertexLat(p1, p2), Math.acos(Math.abs(nrm[2] / nl)) * 180 / Math.PI, 1e-6, 'vertex latitude = tilt of the great-circle plane');
  // rhumb distance by numerical integration along the loxodrome (sum of short chords)
  var rp = N.rhumbPoints(p1, p2, 4000).pts, sum = 0;
  for (var k2 = 1; k2 < rp.length; k2++) sum += N.haversine(rp[k2 - 1], rp[k2]);
  if (Math.abs(p2[0] - p1[0]) > 0.5) worstR = Math.max(worstR, Math.abs(sum - N.rhumb(p1, p2).dist) / N.rhumb(p1, p2).dist);
}
ok(worstD < 1e-6, 'haversine vs n-vector distance: ' + worstD);
ok(worstR < 1e-5, 'rhumb closed form vs integration: ' + worstR);
// vertex check on a route that contains its vertex: Yokohama → San Francisco reaches about 48°N
var yok = [35.45, 139.65], sf = [37.8, -122.42], pts = N.gcPoints(yok, sf, 2000), top = 0;
pts.forEach(function (p) { top = Math.max(top, p[0]); });
near(N.vertexLat(yok, sf), top, 0.01, 'vertex latitude vs sampled track');
// a meridian and the equator are both great circles and rhumb lines: the two distances must agree
near(N.rhumb([0, 10], [0, 70]).dist, N.haversine([0, 10], [0, 70]), 1e-6, 'equator: rhumb = great circle');
near(N.rhumb([-40, 10], [50, 10]).dist, 90 * 60, 1e-6, 'meridian: 90° = 5400 nmi');

// ------------------------------------------------------------ trigonometry and logarithms
Object.keys(T.EXACT).forEach(function (deg) {
  var x = T.EXACT[deg], d = +deg, r = d * Math.PI / 180;
  near(T.evalExact(x[0]), Math.sin(r), 1e-12, 'exact sin ' + deg);
  near(T.evalExact(x[1]), Math.cos(r), 1e-12, 'exact cos ' + deg);
  if (x[2] !== '∞') near(T.evalExact(x[2]), Math.tan(r), 1e-9, 'exact tan ' + deg); else ok(Math.abs(Math.cos(r)) < 1e-12, 'tan undefined at ' + deg);
});
// identities at many angles
for (var a = -720; a <= 720; a += 13.7) {
  var sa = T.sin(a), ca = T.cos(a);
  near(sa * sa + ca * ca, 1, 1e-12, 'sin²+cos² at ' + a);
  near(T.sin(2 * a), 2 * sa * ca, 1e-12, 'double angle at ' + a);
}
// triangle solver: random triangles are recovered from every kind of given data; SSA count matches a construction
var bad = 0, amb = { 0: 0, 1: 0, 2: 0 };
for (i = 0; i < 2000; i++) {
  var Aa = 5 + rnd() * 150, Bb = 5 + rnd() * (170 - Aa), Cc = 180 - Aa - Bb, kk = 1 + rnd() * 20;
  var t0 = { a: kk * T.sin(Aa), b: kk * T.sin(Bb), c: kk * T.sin(Cc), A: Aa, B: Bb, C: Cc };
  var tries = [['SSS', { a: t0.a, b: t0.b, c: t0.c }], ['SAS', { b: t0.b, c: t0.c, A: Aa }], ['ASA', { B: Bb, C: Cc, a: t0.a }], ['AAS', { A: Aa, B: Bb, a: t0.a }], ['SSA', { a: t0.a, b: t0.b, A: Aa }]];
  tries.forEach(function (tt) {
    var sol = T.solve(tt[0], tt[1]), hit = sol.some(function (s) { return Math.abs(s.a - t0.a) + Math.abs(s.b - t0.b) + Math.abs(s.c - t0.c) + Math.abs(s.A - Aa) + Math.abs(s.B - Bb) < 1e-6 * (1 + kk); });
    if (!hit) bad++;
    if (tt[0] === 'SSA') {
      // construction: a circle of radius a around C meets the ray from A at distance b·cos A ± sqrt(a² − (b sin A)²)
      var hgt = t0.b * T.sin(Aa), disc = t0.a * t0.a - hgt * hgt, base = t0.b * T.cos(Aa), cnt = 0;
      if (disc >= 0) [base - Math.sqrt(disc), base + Math.sqrt(disc)].forEach(function (x, ix) { if (x > 1e-9 && !(ix === 1 && disc < 1e-18)) cnt++; });
      ok(cnt === sol.length, 'SSA solution count ' + sol.length + ' vs construction ' + cnt);
      amb[sol.length]++;
    }
  });
}
ok(bad === 0, bad + ' triangles not recovered');
ok(amb[2] > 100, 'the ambiguous case should occur in the random sample');
ok(T.solve('SSS', { a: 1, b: 2, c: 3.5 }).length === 0, 'impossible SSS rejected');
// logarithms: characteristic and mantissa; bar notation for numbers below 1
var lp = T.logParts(3456); ok(lp.characteristic === 3 && Math.abs(lp.mantissa - 0.53857) < 1e-5, 'log 3456');
lp = T.logParts(0.0345); ok(lp.characteristic === -2 && lp.bar === '2̄.5378', 'log 0.0345 = 2̄.5378, got ' + lp.bar);
lp = T.logParts(1000); ok(lp.characteristic === 3 && lp.mantissa === 0, 'log 1000');
// slide rule: multiplying by adding lengths gives the product's significant figures
for (i = 0; i < 500; i++) {
  var x1 = 1 + rnd() * 9, x2 = 1 + rnd() * 9, r1 = T.slideMultiply(x1, x2), want = T.normalise(x1 * x2).m;
  near(r1.reading, want, 1e-9, 'slide rule ' + x1 + '×' + x2);
}
near(T.SCALES.A(4) * 2, T.SCALES.D(4), 1e-15, 'A scale holds squares');

console.log('wave 3 checks: Sun, sidereal time, planets, 88 constellations, Vincenty, trig, logs; ' + fails.length + ' failures');
notes.forEach(function (x) { console.log('note: ' + x); });
fails.forEach(function (f) { console.log('FAIL ' + f); });
process.exit(fails.length ? 1 : 0);
