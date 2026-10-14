/* Reckoning astronomy core. Pure functions, used by the pages and by tests/check_wave3.js (node).
   Sources:
   - Sun, equation of time, declination: the NOAA solar calculator algorithm (after Meeus, Astronomical
     Algorithms), good to about 1 arcminute and a few seconds of time for 1800-2100.
   - Sidereal time: USNO formula adapted from USNO Circular 179 (2005), accurate to about 0.1 s.
   - Planets: JPL "Approximate positions of the planets" (Standish), Table 1, valid 1800-2050,
     heliocentric, mean ecliptic and equinox of J2000.
   - Constellation from a position: Roman (1987, PASP 99, 695; CDS VI/42) with Delporte's 1930
     boundaries at equinox 1875 and the Herget precession routine distributed with that table.
   Times are UT; TT - UT (about 69 s now) is ignored, which moves the Sun by about 3 arcseconds. */
(function (root) {
  'use strict';
  var M = Math, D2R = M.PI / 180, R2D = 180 / M.PI;
  function norm360(x) { x %= 360; return x < 0 ? x + 360 : x; }
  function sind(x) { return M.sin(x * D2R); }
  function cosd(x) { return M.cos(x * D2R); }

  /* Julian date from a JS Date (UTC) */
  function jd(date) { return date.getTime() / 86400000 + 2440587.5; }
  function dateFromJd(j) { return new Date((j - 2440587.5) * 86400000); }
  /* Julian date from a calendar date (Gregorian), fractional day allowed (Meeus ch. 7) */
  function jdCal(y, m, d) {
    if (m <= 2) { y -= 1; m += 12; }
    var A = M.floor(y / 100), B = 2 - A + M.floor(A / 4);
    return M.floor(365.25 * (y + 4716)) + M.floor(30.6001 * (m + 1)) + d + B - 1524.5;
  }

  /* Sun: NOAA algorithm. Returns apparent longitude, RA, Dec (degrees, of date), distance (au),
     equation of time (minutes, apparent minus mean), and the mean longitude/anomaly. */
  function sun(j) {
    var T = (j - 2451545) / 36525;
    var L0 = norm360(280.46646 + T * (36000.76983 + T * 0.0003032));
    var Ma = 357.52911 + T * (35999.05029 - 0.0001537 * T);
    var e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T);
    var C = sind(Ma) * (1.914602 - T * (0.004817 + 0.000014 * T)) + sind(2 * Ma) * (0.019993 - 0.000101 * T) + sind(3 * Ma) * 0.000289;
    var trueLong = L0 + C, nu = Ma + C;
    var R = 1.000001018 * (1 - e * e) / (1 + e * cosd(nu));
    var om = 125.04 - 1934.136 * T;
    var lam = trueLong - 0.00569 - 0.00478 * sind(om);
    var eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60;
    var eps = eps0 + 0.00256 * cosd(om);
    var ra = norm360(R2D * M.atan2(cosd(eps) * sind(lam), cosd(lam)));
    var dec = R2D * M.asin(sind(eps) * sind(lam));
    var y = M.pow(M.tan(eps * D2R / 2), 2);
    var Eq = 4 * R2D * (y * sind(2 * L0) - 2 * e * sind(Ma) + 4 * e * y * sind(Ma) * cosd(2 * L0) - 0.5 * y * y * sind(4 * L0) - 1.25 * e * e * sind(2 * Ma));
    return { lon: norm360(lam), trueLon: norm360(trueLong), ra: ra, dec: dec, r: R, eot: Eq, eps: eps, eps0: eps0, L0: L0, M: Ma, T: T };
  }

  /* Greenwich mean sidereal time in hours (USNO, assuming TT = UT) */
  function gmst(j) {
    var j0 = M.floor(j - 0.5) + 0.5, H = (j - j0) * 24, D0 = j0 - 2451545, T = (j - 2451545) / 36525;
    var g = 6.697375 + 0.065709824279 * D0 + 1.0027379 * H + 0.0000258 * T * T;
    g %= 24; return g < 0 ? g + 24 : g;
  }

  /* ---------------------------------------------------------------- planets (JPL Table 1) */
  var EL = {
    mercury: [0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593, 0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081],
    venus: [0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255, 0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418],
    earth: [1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0, 0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],
    mars: [1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891, 0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],
    jupiter: [5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909, -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],
    saturn: [9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448, -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],
    uranus: [19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503, -0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589],
    neptune: [30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574, 0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664]
  };
  var EPS_J2000 = 23.43928;
  function kepler(Mdeg, e) {   // eccentric anomaly in degrees (JPL iteration)
    var es = R2D * e, E = Mdeg + es * sind(Mdeg);
    for (var i = 0; i < 50; i++) {
      var dM = Mdeg - (E - es * sind(E)), dE = dM / (1 - e * cosd(E));
      E += dE; if (M.abs(dE) <= 1e-9) break;
    }
    return E;
  }
  /* heliocentric ecliptic J2000 rectangular coordinates (au) */
  function helio(name, j) {
    var p = EL[name], T = (j - 2451545) / 36525;
    var a = p[0] + p[6] * T, e = p[1] + p[7] * T, I = p[2] + p[8] * T, L = p[3] + p[9] * T, w = p[4] + p[10] * T, O = p[5] + p[11] * T;
    var om = w - O, Mm = norm360(L - w); if (Mm > 180) Mm -= 360;
    var E = kepler(Mm, e);
    var xp = a * (cosd(E) - e), yp = a * M.sqrt(1 - e * e) * sind(E);
    var co = cosd(om), so = sind(om), cO = cosd(O), sO = sind(O), cI = cosd(I), sI = sind(I);
    return {
      x: (co * cO - so * sO * cI) * xp + (-so * cO - co * sO * cI) * yp,
      y: (co * sO + so * cO * cI) * xp + (-so * sO + co * cO * cI) * yp,
      z: (so * sI) * xp + (co * sI) * yp, a: a, e: e
    };
  }
  function sph(v) { var r = M.sqrt(v.x * v.x + v.y * v.y + v.z * v.z); return { lon: norm360(R2D * M.atan2(v.y, v.x)), lat: R2D * M.asin(v.z / r), r: r }; }
  function eclToEq(lon, lat, eps) {
    var x = cosd(lat) * cosd(lon), y = cosd(lat) * sind(lon), z = sind(lat);
    var ye = cosd(eps) * y - sind(eps) * z, ze = sind(eps) * y + cosd(eps) * z;
    return { ra: norm360(R2D * M.atan2(ye, x)), dec: R2D * M.asin(ze) };
  }
  /* geocentric position of a planet, J2000 ecliptic and equatorial (light time ignored) */
  function planetGeo(name, j) {
    var p = helio(name, j), E = helio('earth', j), g = { x: p.x - E.x, y: p.y - E.y, z: p.z - E.z };
    var s = sph(g), q = eclToEq(s.lon, s.lat, EPS_J2000);
    var sunLon = norm360(sph(E).lon + 180), el = M.acos(M.max(-1, M.min(1, cosd(s.lat) * cosd(s.lon - sunLon))));
    return { lon: s.lon, lat: s.lat, dist: s.r, ra: q.ra, dec: q.dec, elong: R2D * el, east: norm360(s.lon - sunLon) < 180 };
  }

  /* ---------------------------------------------------------------- constellations (Roman 1987) */
  /* Herget precession of a mean place between two epochs in years (port of the routine shipped with CDS VI/42) */
  function precess(raDeg, decDeg, ep1, ep2) {
    var ra = raDeg * D2R, dec = decDeg * D2R, CSR = D2R / 3600, T = 0.001 * (ep2 - ep1), ST = 0.001 * (ep1 - 1900);
    var A = CSR * T * (23042.53 + ST * (139.75 + 0.06 * ST) + T * (30.23 - 0.27 * ST + 18.0 * T));
    var B = CSR * T * T * (79.27 + 0.66 * ST + 0.32 * T) + A;
    var C = CSR * T * (20046.85 - ST * (85.33 + 0.37 * ST) + T * (-42.67 - 0.37 * ST - 41.8 * T));
    var sA = M.sin(A), sB = M.sin(B), sC = M.sin(C), cA = M.cos(A), cB = M.cos(B), cC = M.cos(C);
    var r = [[cA * cB * cC - sA * sB, -cA * sB - sA * cB * cC, -cB * sC],
             [sA * cB + cA * sB * cC, cA * cB - sA * sB * cC, -sB * sC],
             [cA * sC, -sA * sC, cC]];
    var x1 = [M.cos(dec) * M.cos(ra), M.cos(dec) * M.sin(ra), M.sin(dec)], x2 = [0, 0, 0];
    for (var i = 0; i < 3; i++) x2[i] = r[i][0] * x1[0] + r[i][1] * x1[1] + r[i][2] * x1[2];
    return { ra: norm360(R2D * M.atan2(x2[1], x2[0])), dec: R2D * M.asin(x2[2]) };
  }
  var BOUNDS = null;   // [[raLowHours, raUpHours, decLow, 'Abb'], ...] at equinox 1875
  function setBounds(b) { BOUNDS = b; }
  /* constellation abbreviation for a position (degrees) at the given equinox (year) */
  function constellation(raDeg, decDeg, equinox) {
    var p = precess(raDeg, decDeg, equinox, 1875), raH = p.ra / 15, d = p.dec;
    for (var i = 0; i < BOUNDS.length; i++) {
      var b = BOUNDS[i];
      if (d < b[2] || raH < b[0] || raH >= b[1]) continue;
      return b[3];
    }
    return null;
  }
  function year(j) { return 2000 + (j - 2451545) / 365.25; }

  /* Sun's constellation and the dates it enters each one during a year (days stepped, then bisected) */
  function sunConst(j) { var s = sun(j); return constellation(s.ra, s.dec, year(j)); }
  function sunTransits(y0) {
    var out = [], j = jdCal(y0, 1, 1), end = jdCal(y0 + 1, 1, 1), prev = sunConst(j);
    for (var k = j + 1; k <= end; k += 1) {
      var c = sunConst(k);
      if (c !== prev) {
        var lo = k - 1, hi = k;
        for (var n = 0; n < 20; n++) { var mid = (lo + hi) / 2; if (sunConst(mid) === prev) lo = mid; else hi = mid; }
        out.push({ jd: hi, from: prev, to: c, lon: sun(hi).lon });
        prev = c;
      }
    }
    return out;
  }
  /* date when the Sun's apparent longitude reaches lam (degrees) after jd j0 */
  function sunAtLongitude(lam, j0) {
    var j = j0;
    for (var i = 0; i < 40; i++) {
      var d = norm360(lam - sun(j).lon); if (d > 180) d -= 360;
      j += d / 0.9856474; if (M.abs(d) < 1e-7) break;
    }
    return j;
  }

  var A = { D2R: D2R, R2D: R2D, norm360: norm360, jd: jd, jdCal: jdCal, dateFromJd: dateFromJd, sun: sun, gmst: gmst, helio: helio, sph: sph,
            planetGeo: planetGeo, eclToEq: eclToEq, kepler: kepler, EL: EL, EPS_J2000: EPS_J2000, precess: precess, setBounds: setBounds,
            constellation: constellation, year: year, sunConst: sunConst, sunTransits: sunTransits, sunAtLongitude: sunAtLongitude };
  if (typeof module !== 'undefined' && module.exports) module.exports = A; else root.RK_ASTRO = A;
})(this);
