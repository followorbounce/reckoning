/* IUPAC letters page: decode a sequence with ambiguity letters, and search a pattern on both strands (dnamath.js). */
(function () {
  'use strict';
  var D = window.RK_DNA, inp = document.getElementById('iseq'); if (!inp) return;
  var rna = document.getElementById('irna'), q = document.getElementById('iq');
  function esc(s) { return s.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
  function decode() {
    var raw = inp.value, s = D.clean(raw), r = rna.checked, show = function (x) { return r ? x.replace(/T/g, 'U') : x; };
    var bad = raw.toUpperCase().replace(/[\sACGTURYSWKMBDHVN]/g, '');
    var n = D.count(s), list = D.expand(s, 64);
    q.innerHTML = '<div><span>Sequence (' + s.length + ' letters)</span><span>' + esc(show(s)) + '</span></div>' +
      (bad ? '<div><span class="warn">Not IUPAC letters, ignored</span><span class="warn">' + esc(bad) + '</span></div>' : '') +
      '<div><span>Complement</span><span>' + esc(show(s.split('').map(D.complement).join(''))) + '</span></div>' +
      '<div><span>Reverse complement (5′→3′)</span><span>' + esc(D.revcomp(s, r)) + '</span></div>' +
      '<div><span>Concrete sequences it stands for</span><span>' + n.toLocaleString('en-US') + '</span></div>' +
      '<div><span>' + (n > 64 ? 'First 64' : 'They are') + '</span><span class="wrapnum">' + list.map(show).join(' ') + (n > 64 ? ' …' : '') + '</span></div>' +
      (n === 1 && s.length ? '<div><span>GC content</span><span>' + (100 * D.gc(s)).toFixed(1) + ' %</span></div>' : '');
  }
  inp.addEventListener('input', decode); rna.addEventListener('change', function () { decode(); search(); });
  document.querySelectorAll('[data-iseq]').forEach(function (b) { b.addEventListener('click', function () { inp.value = b.getAttribute('data-iseq'); decode(); }); });

  var pat = document.getElementById('ipat'), tgt = document.getElementById('itgt'), out = document.getElementById('ihits');
  function search() {
    var p = D.clean(pat.value), t = D.clean(tgt.value), rc = D.revcomp(p), r = rna.checked;
    var fw = D.matches(p, t), rv = rc === p ? [] : D.matches(rc, t), mark = new Array(t.length).fill(0);
    fw.forEach(function (i) { for (var k = 0; k < p.length; k++) mark[i + k] |= 1; });
    rv.forEach(function (i) { for (var k = 0; k < p.length; k++) mark[i + k] |= 2; });
    var h = '';
    for (var i = 0; i < t.length; i++) { var c = r ? t[i].replace('T', 'U') : t[i]; h += mark[i] ? '<mark class="m' + mark[i] + '">' + c + '</mark>' : c; }
    out.innerHTML = '<p class="mono seq">' + h + '</p><p class="small">' + fw.length + ' on this strand' + (rc === p ? ' (the pattern is its own reverse complement, so every hit is on both strands)' : ', ' + rv.length + ' on the other strand (shown where its reverse complement ' + esc(rc) + ' reads on this one)') +
      (fw.length ? '. Positions: ' + fw.concat(rv).sort(function (a, b) { return a - b; }).map(function (x) { return x + 1; }).join(', ') : '') + '.</p>';
  }
  pat.addEventListener('input', search); tgt.addEventListener('input', search);
  decode(); search();
})();
