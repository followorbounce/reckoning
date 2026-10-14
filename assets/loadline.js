/* Buoyancy page: displacement, TPC and fresh water allowance from the sliders (stability.js hydro/dwa), and the load-line
   mark drawn to the Convention's sizes (RK_LL, from data/ship.py). Scale: S px per millimetre. The bow is to the right. */
(function () {
  'use strict';
  var St = window.RK_STAB, LL = window.RK_LL, svg = document.getElementById('llsvg'); if (!svg) return;
  var ids = ['lL', 'lB', 'lT', 'lCb', 'lCw', 'lrho'], el = {}, q = document.getElementById('lq');
  ids.forEach(function (k) { el[k] = document.getElementById(k); });
  var S;
  function fmt(x, n) { return x.toLocaleString('en-US', { minimumFractionDigits: n, maximumFractionDigits: n }); }
  function draw() {
    var L = +el.lL.value, B = +el.lB.value, T = +el.lT.value, Cb = +el.lCb.value, Cw = +el.lCw.value, rho = +el.lrho.value;
    document.getElementById('lLv').textContent = L + ' m'; document.getElementById('lBv').textContent = B + ' m';
    document.getElementById('lTv').textContent = T.toFixed(1) + ' m'; document.getElementById('lCbv').textContent = Cb.toFixed(2);
    document.getElementById('lCwv').textContent = Cw.toFixed(2); document.getElementById('lrhov').textContent = rho.toFixed(3);
    var h = St.hydro(L, B, T, Cb, Cw), fwa = h.fwa * 10, d48 = T * 1000 / LL.tropical_fraction, dwaMm = St.dwa(h.fwa, rho) * 10;
    var wna = L <= LL.wna_max_length_m;
    q.innerHTML = '<div><span>Volume displaced ∇</span><span>' + fmt(h.V, 0) + ' m³</span></div>' +
      '<div><span>Displacement Δ (sea water)</span><span>' + fmt(h.disp, 0) + ' t</span></div>' +
      '<div><span>Waterplane area</span><span>' + fmt(h.Aw, 0) + ' m²</span></div>' +
      '<div><span>TPC</span><span>' + fmt(h.tpc, 2) + ' t/cm</span></div>' +
      '<div><span>Fresh water allowance</span><span>' + fmt(fwa, 0) + ' mm</span></div>' +
      '<div><span>1/48 of summer draught</span><span>' + fmt(d48, 0) + ' mm</span></div>' +
      '<div><span>Allowance in water of ' + rho.toFixed(3) + '</span><span>' + fmt(dwaMm, 0) + ' mm</span></div>';
    // levels of the upper edges, mm above the summer line (positive up)
    var lv = { S: 0, T: d48, W: -d48, F: fwa, TF: d48 + fwa };
    if (wna) lv.WNA = -d48 - LL.wna_add_mm;
    var top = Math.max(lv.TF, dwaMm), bot = wna ? lv.WNA : lv.W;
    S = Math.min(0.55, 330 / (top - Math.min(bot, -LL.ring_outer / 2) + 40));
    var yS = 120 + top * S, x0 = 165, xv = x0 + LL.vertical_from_ring * S, ln = LL.line[0] * S, lw = LL.line[1] * S;
    function Y(mm) { return yS - mm * S; }
    var g = '';
    // water: loaded to the summer line in sea water, then moved to water of the chosen density
    var yw = Y(dwaMm);
    g += '<rect x="0" y="' + yw.toFixed(1) + '" width="640" height="' + (520 - yw).toFixed(1) + '" class="llsea"/>' +
      '<line x1="0" x2="640" y1="' + yw.toFixed(1) + '" y2="' + yw.toFixed(1) + '" class="llwl"/>';
    // deck line, with a break: the summer freeboard comes from the Convention's tables and is not drawn to scale
    var dl = LL.deck_line[0] * S;
    g += '<rect x="' + (x0 - dl / 2) + '" y="22" width="' + dl + '" height="' + (LL.deck_line[1] * S) + '" class="llm"/>' +
      '<text x="' + (x0 + dl / 2 + 10) + '" y="34" class="lltx">deck line</text>' +
      '<path d="M' + (x0 - 30) + ' 62 l10 -8 l10 16 l10 -16 l10 16 l10 -16 l10 8" class="llbrk"/>' +
      '<line x1="' + x0 + '" x2="' + x0 + '" y1="40" y2="56" class="llbrk"/><line x1="' + x0 + '" x2="' + x0 + '" y1="72" y2="' + (Y(0) - LL.ring_outer * S / 2 - 6) + '" class="llbrk"/>' +
      '<text x="' + (x0 + 10) + '" y="96" class="lltx">summer freeboard (not to scale)</text>';
    // ring and bar
    var R = LL.ring_outer * S / 2, rw = LL.ring_width * S;
    g += '<circle cx="' + x0 + '" cy="' + Y(0) + '" r="' + (R - rw / 2) + '" class="llring" style="stroke-width:' + rw + '"/>' +
      '<rect x="' + (x0 - LL.ring_bar[0] * S / 2) + '" y="' + Y(0) + '" width="' + (LL.ring_bar[0] * S) + '" height="' + (LL.ring_bar[1] * S) + '" class="llm"/>';
    var lh = LL.letters[0] * S;
    g += '<text x="' + (x0 - R - 8) + '" y="' + (Y(0) - 8) + '" text-anchor="end" class="llauth" style="font-size:' + lh + 'px">A</text>' +
      '<text x="' + (x0 + R + 8) + '" y="' + (Y(0) - 8) + '" class="llauth" style="font-size:' + lh + 'px">B</text>';
    // vertical line and the load lines
    g += '<rect x="' + (xv - lw / 2) + '" y="' + Y(lv.TF) + '" width="' + lw + '" height="' + (Y(bot) - Y(lv.TF) + lw) + '" class="llm"/>';
    Object.keys(lv).forEach(function (k) {
      var aft = k === 'F' || k === 'TF', xa = aft ? xv - ln : xv;
      g += '<rect x="' + xa + '" y="' + Y(lv[k]) + '" width="' + ln + '" height="' + lw + '" class="llm"/>' +
        '<text x="' + (aft ? xa - 8 : xa + ln + 8) + '" y="' + (Y(lv[k]) + 12) + '" text-anchor="' + (aft ? 'end' : 'start') + '" class="llk">' + k + '</text>';
    });
    g += '<text x="12" y="' + (Y(bot) + 46) + '" class="lltx">← aft · forward → · to scale except the freeboard · ' + (wna ? 'L ≤ 100 m: WNA line marked' : 'L > 100 m: no WNA line') + '</text>' +
      '<text x="12" y="' + (Y(bot) + 64) + '" class="lltx">dashed: waterline in water of ' + rho.toFixed(3) + ' t/m³ when loaded to S in the sea</text>';
    svg.innerHTML = g;
  }
  ids.forEach(function (k) { el[k].addEventListener('input', draw); });
  draw();
})();
