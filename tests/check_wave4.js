/* Wave 4 checks of the code the Ship and Code of life pages run (assets/stability.js, assets/dnamath.js).
   Closed-form results are written out here independently of the code under test. Exit code 1 on any failure. */
'use strict';
var path = require('path'), M = Math;
var S = require(path.join(__dirname, '..', 'assets', 'stability.js'));
var D = require(path.join(__dirname, '..', 'assets', 'dnamath.js'));
var fails = 0, n = 0, notes = [];
function ok(c, msg) { n++; if (!c) { fails++; console.log('FAIL ' + msg); } }
function near(a, b, tol, msg) { ok(M.abs(a - b) <= tol, msg + ': got ' + a + ', expected ' + b + ' ± ' + tol); }
var R = M.PI / 180;

// ---------------------------------------------------------------- stability
var box = S.box(12, 6), ob = { T: 3, KG: 4.2 }, ub = S.upright(box, 3);
near(ub.KB, 1.5, 1e-12, 'box KB = T/2');
near(ub.BM, 12 * 12 / (12 * 3), 1e-12, 'box BM = B²/12T');
near(ub.KM, 5.5, 1e-12, 'box KM');
var GMb = 5.5 - 4.2, deckEdge = M.atan((6 - 3) / 6) / R;
for (var d = 1; d < deckEdge; d += 1) near(S.gz(box, ob, d * R), M.sin(d * R) * (GMb + 4 / 2 * M.tan(d * R) * M.tan(d * R)), 1e-6, 'box GZ = wall-sided formula at ' + d + '°');
near(S.edgeAngle(box, ob, [6, 6], true), deckEdge, 0.25, 'deck-edge immersion angle');
var circ = S.circle(5), oc = { T: 4, KG: 3 };
[10, 30, 60, 90, 120, 150, 170].forEach(function (d) { near(S.gz(circ, oc, d * R), (5 - 3) * M.sin(d * R), 2e-4, 'circular section GZ = (KM − KG) sin θ at ' + d + '°'); });
var loll = S.equilibrium(box, { T: 3, KG: 5.8 });
near(loll, M.atan(M.sqrt(2 * 0.3 / 4)) / R, 0.01, 'angle of loll tan θ = √(2|GM|/BM)');
Object.keys(S.HULLS).forEach(function (k) {
  var h = S.HULLS[k], o = { T: h.T, KG: h.KG }, u = S.upright(h.poly, h.T);
  [5, 25, 45, 75].forEach(function (d) { near(S.gz(h.poly, o, -d * R), -S.gz(h.poly, o, d * R), 1e-6, k + ': GZ(−θ) = −GZ(θ) at ' + d + '°'); });
  for (var d2 = 0; d2 <= 90; d2 += 15) near(S.waterline(h.poly, u.A, d2 * R).B && S.areaCentroid(S.waterline(h.poly, u.A, d2 * R).sub).A, u.A, 1e-6 * u.A, k + ': displaced area constant at ' + d2 + '°');
  near(S.gz(h.poly, o, 0.2 * R) / M.sin(0.2 * R), u.KM - h.KG, 2e-3, k + ': GZ/sin θ → GM at small heel');
  ok(u.KM - h.KG > 0.15, k + ': default loading meets GM ≥ 0.15 m');
});
// free surface: the liquid in a half-full tank, heeled a little, moves sideways as if its weight were raised by i/a
(function () {
  var b = 8, hgt = 2, tank = [[-b / 2, 0], [b / 2, 0], [b / 2, hgt], [-b / 2, hgt]], aLiq = b * hgt / 2, th = 0.5 * R;
  var w0 = S.waterline(tank, aLiq, 0).B, w1 = S.waterline(tank, aLiq, th).B;
  var shift = (w1.y - w0.y) * M.cos(th) + (w1.z - w0.z) * M.sin(th);   // horizontal move of the liquid's centroid (earth frame)
  var rise = shift / M.sin(th);   // a solid weight would not move relative to the ship; the liquid's sideways move per sin θ is its virtual rise
  near(rise * aLiq, b * b * b / 12, 0.01 * b * b * b / 12, 'free surface: liquid shift equals i = b³/12 (per unit length)');
  near(S.freeSurface(b, 1, S.RHO_SW, 100), b * b * b / 12 / 100, 1e-12, 'free-surface correction formula');
})();
// hydrostatics and the load line
var hb = S.hydro(100, 10, 4, 1, 1);
near(hb.fwa, 100 * 4 / 40, 1e-9, 'box: fresh water allowance = T/40');
near(hb.disp, 1.025 * 4000, 1e-9, 'box displacement');
near(S.dwa(10, 1.000), 10, 1e-12, 'dock water allowance in fresh water = FWA');
near(S.dwa(10, 1.025), 0, 1e-12, 'dock water allowance in sea water = 0');
near(S.dwa(10, 1.0125), 5, 1e-9, 'dock water allowance is proportional');
var cr = S.criteria(box, ob, S.curve(box, ob)).map(function (r) { return r.min; });
ok(JSON.stringify(cr) === JSON.stringify([0.055, 0.09, 0.03, 0.20, 25, 0.15]), 'IMO 2008 IS Code A 2.2 limits as published');

// ---------------------------------------------------------------- IUPAC letters
var PAIRS = { A: 'T', C: 'G', G: 'C', T: 'A' };
D.ORDER.forEach(function (c) {
  ok(D.complement(D.complement(c)) === c, 'complement is an involution: ' + c);
  var want = D.SETS[c].split('').map(function (b) { return PAIRS[b]; }).sort().join('');
  ok(D.SETS[D.complement(c)].split('').sort().join('') === want, 'complement of ' + c + ' is the complemented set');
});
ok(D.ORDER.length === 15 && new Set(D.ORDER.map(function (c) { return D.SETS[c].split('').sort().join(''); })).size === 15, '15 letters for the 15 non-empty sets');
ok(D.revcomp('GTYRAC') === 'GTYRAC', 'HincII site is its own reverse complement');
ok(D.revcomp('AUGC', true) === 'GCAU', 'RNA reverse complement');
ok(D.count('GTYRAC') === 4 && D.expand('GTYRAC').length === 4, 'GTYRAC stands for 4 sequences');
D.expand('GTYRAC').forEach(function (s) { ok(D.matches('GTYRAC', s).length === 1, 'each expansion matches its pattern: ' + s); });
ok(JSON.stringify(D.matches('GTYRAC', 'ATGGTCAACGCTAGTTAACCGGTCGACATTGTTGACGGAGTCAACTAG')) === JSON.stringify([3, 13, 21, 30, 39]), 'pattern search finds the 5 sites in the demo sequence');
ok(M.abs(D.gc('GGCCAT') - 4 / 6) < 1e-12, 'GC content');

// ---------------------------------------------------------------- topology
var ca = [], cb = [], cc = [];
for (var i = 0; i < 240; i++) { var t = 2 * M.PI * i / 240; ca.push([M.cos(t), M.sin(t), 0]); cb.push([1 + M.cos(t), 0, M.sin(t)]); cc.push([5 + M.cos(t), 0, M.sin(t)]); }
near(M.abs(D.linking(ca, cb)), 1, 1e-9, 'Hopf link: |Lk| = 1');
near(D.linking(ca, cc), 0, 1e-9, 'unlinked circles: Lk = 0');
near(D.writhe(ca), 0, 1e-12, 'plane curve: Wr = 0');
var shapes = [['interwound', function (s, h) { return D.plectoneme(200, 6, 0.9, 4, s, h); }], ['toroidal', function (s, h) { return D.toroid(200, 3.2, 1.25 * s, 5, h); }]];
shapes.forEach(function (sh) {
  [0, 0.4, 1].forEach(function (s) {
    [-4, -1, 0, 2].forEach(function (lk) {
      var r = D.ribbon(sh[1](s, lk <= 0 ? (sh[0] === 'interwound' ? 1 : -1) : (sh[0] === 'interwound' ? -1 : 1)), lk, 0.25);
      near(r.Tw + r.Wr, M.round(r.Tw + r.Wr), 2e-3, sh[0] + ' s=' + s + ': Tw + Wr is an integer (Fuller: writhe ≡ holonomy)');
      near(r.Tw + r.Wr, lk, 2e-3, sh[0] + ' s=' + s + ': Tw + Wr = Lk');
      var c = sh[1](s, lk <= 0 ? (sh[0] === 'interwound' ? 1 : -1) : (sh[0] === 'interwound' ? -1 : 1));
      near(D.linking(c, r.edge), lk, 2e-3, sh[0] + ' s=' + s + ': Gauss linking of axis and edge = Lk = ' + lk);
    });
  });
});
var rp = D.writhe(D.plectoneme(200, 6, 0.9, 4, 1, 1)), lt = D.writhe(D.toroid(200, 3.2, 1.25, 5, -1));
ok(rp < -2, 'right-handed interwound supercoil has negative writhe (' + rp.toFixed(3) + ')');
ok(lt < -1, 'left-handed toroidal supercoil has negative writhe (' + lt.toFixed(3) + ')');
notes.push('interwound, 4 turns: Wr = ' + rp.toFixed(3) + '; toroidal, 5 turns: Wr = ' + lt.toFixed(3));

notes.forEach(function (s) { console.log('note: ' + s); });
console.log(fails ? fails + ' of ' + n + ' JS checks FAILED' : 'wave 4 JS: ' + n + ' checks passed');
process.exit(fails ? 1 : 0);
