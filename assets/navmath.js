/* Reckoning navigation maths. Pure functions, used by the pages and by tests/check_wave3.js (node).
   Angles in degrees, distances in the unit of the radius given (default: the navigator's sphere on
   which one minute of arc is one nautical mile, R = 10800/π nmi).
   - Great circle: haversine distance, and the same distance again from n-vectors (two independent methods).
   - Rhumb line (Mercator sailing): constant course, from the difference of meridional parts.
   - Vincenty (1975) inverse solution on an ellipsoid (default WGS 84) for the true distance. */
(function (root) {
  'use strict';
  var M = Math, D2R = M.PI / 180, R2D = 180 / M.PI;
  var R_NM = 10800 / M.PI;            // nautical miles; 1' of arc = 1 nmi on this sphere
  var WGS84 = { a: 6378137, f: 1 / 298.257223563 };
  function wrap180(x) { x = ((x + 180) % 360 + 360) % 360 - 180; return x; }
  function norm360(x) { x %= 360; return x < 0 ? x + 360 : x; }

  function haversine(p1, p2, R) {
    R = R || R_NM;
    var f1 = p1[0] * D2R, f2 = p2[0] * D2R, df = f2 - f1, dl = (p2[1] - p1[1]) * D2R;
    var h = M.pow(M.sin(df / 2), 2) + M.cos(f1) * M.cos(f2) * M.pow(M.sin(dl / 2), 2);
    return 2 * R * M.asin(M.min(1, M.sqrt(h)));
  }
  function nvec(p) { var f = p[0] * D2R, l = p[1] * D2R; return [M.cos(f) * M.cos(l), M.cos(f) * M.sin(l), M.sin(f)]; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function len(a) { return M.sqrt(dot(a, a)); }
  function vectorDistance(p1, p2, R) {
    var a = nvec(p1), b = nvec(p2);
    return (R || R_NM) * M.atan2(len(cross(a, b)), dot(a, b));
  }
  function initialCourse(p1, p2) {
    var f1 = p1[0] * D2R, f2 = p2[0] * D2R, dl = (p2[1] - p1[1]) * D2R;
    return norm360(R2D * M.atan2(M.sin(dl) * M.cos(f2), M.cos(f1) * M.sin(f2) - M.sin(f1) * M.cos(f2) * M.cos(dl)));
  }
  function finalCourse(p1, p2) { return norm360(initialCourse(p2, p1) + 180); }
  /* points along the great circle (spherical linear interpolation of n-vectors) */
  function gcPoints(p1, p2, n) {
    var a = nvec(p1), b = nvec(p2), w = M.atan2(len(cross(a, b)), dot(a, b)), out = [];
    for (var i = 0; i <= n; i++) {
      var t = i / n, v;
      if (w < 1e-12) v = a;
      else { var s1 = M.sin((1 - t) * w) / M.sin(w), s2 = M.sin(t * w) / M.sin(w); v = [s1 * a[0] + s2 * b[0], s1 * a[1] + s2 * b[1], s1 * a[2] + s2 * b[2]]; }
      out.push([R2D * M.atan2(v[2], M.sqrt(v[0] * v[0] + v[1] * v[1])), R2D * M.atan2(v[1], v[0])]);
    }
    return out;
  }
  /* latitude of the vertex (highest latitude of the whole great circle): cos(lat_v) = |sin C · cos lat1| */
  function vertexLat(p1, p2) { return R2D * M.acos(M.abs(M.sin(initialCourse(p1, p2) * D2R) * M.cos(p1[0] * D2R))); }

  /* meridional part on the sphere, in minutes of arc: 10800/π · ln tan(45° + φ/2) */
  function meridionalParts(lat) { return R_NM * M.log(M.tan(M.PI / 4 + lat * D2R / 2)); }
  function rhumb(p1, p2, R) {
    R = R || R_NM;
    var f1 = p1[0] * D2R, f2 = p2[0] * D2R, df = f2 - f1, dl = wrap180(p2[1] - p1[1]) * D2R;
    var dpsi = M.log(M.tan(M.PI / 4 + f2 / 2) / M.tan(M.PI / 4 + f1 / 2));
    var q = M.abs(dpsi) > 1e-12 ? df / dpsi : M.cos(f1);
    return { dist: M.sqrt(df * df + q * q * dl * dl) * R, course: norm360(R2D * M.atan2(dl, dpsi)) };
  }
  function rhumbPoints(p1, p2, n) {
    var r = rhumb(p1, p2), out = [], f1 = p1[0], dl = wrap180(p2[1] - p1[1]);
    var m1 = meridionalParts(p1[0]), m2 = meridionalParts(p2[0]);
    for (var i = 0; i <= n; i++) {
      var t = i / n, lat = f1 + (p2[0] - f1) * t, lon;
      if (M.abs(m2 - m1) > 1e-9) lon = p1[1] + dl * (meridionalParts(lat) - m1) / (m2 - m1); else lon = p1[1] + dl * t;
      out.push([lat, wrap180(lon)]);
    }
    return { pts: out, course: r.course };
  }
  /* the classic mid-latitude shortcut: departure = d.long · cos(mean latitude) */
  function midLatitude(p1, p2) {
    var dlat = (p2[0] - p1[0]) * 60, dlon = wrap180(p2[1] - p1[1]) * 60, dep = dlon * M.cos((p1[0] + p2[0]) / 2 * D2R);
    return { dist: M.sqrt(dlat * dlat + dep * dep), course: norm360(R2D * M.atan2(dep, dlat)) };
  }

  /* Vincenty inverse (Survey Review 23, 1975). Returns metres and azimuths in degrees. */
  function vincenty(p1, p2, ell) {
    ell = ell || WGS84;
    var a = ell.a, f = ell.f, b = a * (1 - f);
    var L = wrap180(p2[1] - p1[1]) * D2R, U1 = M.atan((1 - f) * M.tan(p1[0] * D2R)), U2 = M.atan((1 - f) * M.tan(p2[0] * D2R));
    var sU1 = M.sin(U1), cU1 = M.cos(U1), sU2 = M.sin(U2), cU2 = M.cos(U2);
    var lam = L, lamP, it = 0, sS, cS, sig, sA, c2A, c2Sm, C;
    do {
      var sL = M.sin(lam), cL = M.cos(lam);
      sS = M.sqrt(M.pow(cU2 * sL, 2) + M.pow(cU1 * sU2 - sU1 * cU2 * cL, 2));
      if (sS === 0) return { dist: 0, az1: 0, az2: 0, iter: it };
      cS = sU1 * sU2 + cU1 * cU2 * cL; sig = M.atan2(sS, cS);
      sA = cU1 * cU2 * sL / sS; c2A = 1 - sA * sA;
      c2Sm = c2A !== 0 ? cS - 2 * sU1 * sU2 / c2A : 0;
      C = f / 16 * c2A * (4 + f * (4 - 3 * c2A));
      lamP = lam;
      lam = L + (1 - C) * f * sA * (sig + C * sS * (c2Sm + C * cS * (-1 + 2 * c2Sm * c2Sm)));
    } while (M.abs(lam - lamP) > 1e-12 && ++it < 200);
    if (it >= 200) return null;   // nearly antipodal: no convergence
    var u2 = c2A * (a * a - b * b) / (b * b);
    var A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)));
    var B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)));
    var dS = B * sS * (c2Sm + B / 4 * (cS * (-1 + 2 * c2Sm * c2Sm) - B / 6 * c2Sm * (-3 + 4 * sS * sS) * (-3 + 4 * c2Sm * c2Sm)));
    var s = b * A * (sig - dS);
    var sL2 = M.sin(lam), cL2 = M.cos(lam);
    var az1 = M.atan2(cU2 * sL2, cU1 * sU2 - sU1 * cU2 * cL2), az2 = M.atan2(cU1 * sL2, -sU1 * cU2 + cU1 * sU2 * cL2);
    return { dist: s, az1: norm360(az1 * R2D), az2: norm360(az2 * R2D), iter: it };
  }

  /* WGS 84 lengths of one minute of latitude and longitude (metres) at geodetic latitude φ */
  function minuteLengths(lat, ell) {
    ell = ell || WGS84;
    var e2 = ell.f * (2 - ell.f), s = M.sin(lat * D2R), w = 1 - e2 * s * s;
    var Mr = ell.a * (1 - e2) / M.pow(w, 1.5), N = ell.a / M.sqrt(w);
    return { lat: Mr * D2R / 60, lon: N * M.cos(lat * D2R) * D2R / 60, M: Mr, N: N };
  }
  /* geocentric latitude from geodetic latitude */
  function geocentric(lat, ell) { ell = ell || WGS84; var e2 = ell.f * (2 - ell.f); return R2D * M.atan((1 - e2) * M.tan(lat * D2R)); }

  function fmtDM(x, pos, neg) {   // 51°28.7′N
    var h = x < 0 ? neg : pos, a = M.abs(x), d = M.floor(a), m = (a - d) * 60;
    if (m >= 59.95) { d += 1; m = 0; }
    return d + '°' + m.toFixed(1).padStart(4, '0') + '′' + h;
  }
  function fmtDMS(x, pos, neg) {
    var h = x < 0 ? neg : pos, a = M.abs(x), t = M.round(a * 3600), d = M.floor(t / 3600), m = M.floor(t % 3600 / 60), s = t % 60;
    return d + '°' + String(m).padStart(2, '0') + '′' + String(s).padStart(2, '0') + '″' + h;
  }

  var N = { R_NM: R_NM, WGS84: WGS84, wrap180: wrap180, norm360: norm360, haversine: haversine, vectorDistance: vectorDistance,
            initialCourse: initialCourse, finalCourse: finalCourse, gcPoints: gcPoints, vertexLat: vertexLat, meridionalParts: meridionalParts,
            rhumb: rhumb, rhumbPoints: rhumbPoints, midLatitude: midLatitude, vincenty: vincenty, minuteLengths: minuteLengths,
            geocentric: geocentric, fmtDM: fmtDM, fmtDMS: fmtDMS, nvec: nvec };
  if (typeof module !== 'undefined' && module.exports) module.exports = N; else root.RK_NAV = N;
})(this);
