/* Reckoning converter. Unit sizes arrive as exact fractions (numerator/denominator strings,
   from data/units.py); conversion is done in exact rational arithmetic with BigInt, so a result
   is either printed in full (it terminates) or rounded to 15 significant figures and marked so. */
(function () {
  'use strict';
  var D = window.RK_UNITS; if (!D) return;
  var byId = {}; D.units.forEach(function (u) { byId[u.id] = u; });

  function gcd(a, b) { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) { var t = a % b; a = b; b = t; } return a; }
  function fr(n, d) { if (d < 0n) { n = -n; d = -d; } var g = gcd(n, d) || 1n; return [n / g, d / g]; }
  function mul(a, b) { return fr(a[0] * b[0], a[1] * b[1]); }
  function div(a, b) { return fr(a[0] * b[1], a[1] * b[0]); }
  function add(a, b) { return fr(a[0] * b[1] + b[0] * a[1], a[1] * b[1]); }
  function sub(a, b) { return add(a, [-b[0], b[1]]); }
  function parse(s) {
    s = String(s).trim().replace(/\s/g, '').replace(',', '.');
    var m = /^([+-]?)(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(s);
    if (!m || (m[2] === '' && (m[3] === undefined || m[3] === ''))) return null;
    var digits = (m[2] || '') + (m[3] || ''), scale = (m[3] || '').length - parseInt(m[4] || '0', 10);
    var n = BigInt(digits || '0'), d = 1n;
    if (scale > 0) d = 10n ** BigInt(scale); else n = n * 10n ** BigInt(-scale);
    if (m[1] === '-') n = -n;
    return fr(n, d);
  }
  function terminates(d) { while (d % 2n === 0n) d /= 2n; while (d % 5n === 0n) d /= 5n; return d === 1n; }
  function group(s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  function groupFrac(s) { return s.replace(/(\d{3})(?=\d)/g, '$1 '); }
  function fmt(f) {
    var n = f[0], d = f[1], neg = n < 0n; if (neg) n = -n;
    var ip = n / d, rem = n % d, out;
    if (terminates(d)) {
      var frac = ''; var guard = 0;
      while (rem && guard++ < 60) { rem *= 10n; frac += (rem / d).toString(); rem %= d; }
      out = group(ip.toString()) + (frac ? '.' + groupFrac(frac) : '');
      return { text: (neg ? '−' : '') + out, exact: true };
    }
    // 15 significant figures
    var x = Number(n) / Number(d);
    var t = x.toPrecision(15);
    if (/e/.test(t)) { out = t.replace('e+', ' × 10^').replace('e-', ' × 10^-'); }
    else { var p = t.split('.'); out = group(p[0]) + (p[1] ? '.' + groupFrac(p[1].replace(/0+$/, '')) : ''); out = out.replace(/\.$/, ''); }
    return { text: (neg ? '−' : '') + out + '…', exact: false };
  }
  function F(u) { return [BigInt(u.n), BigInt(u.d)]; }
  function O(u) { return [BigInt(u.on || '0'), BigInt(u.od || '1')]; }
  function convert(x, a, b) {
    if (a.kind === 'temperature') { var k = add(mul(F(a), x), O(a)); return div(sub(k, O(b)), F(b)); }
    return div(mul(x, F(a)), F(b));
  }
  function opt(sel, u) { var o = document.createElement('option'); o.value = u.id; o.textContent = u.name + (u.sym ? ' (' + u.sym + ')' : ''); sel.appendChild(o); }

  document.querySelectorAll('.converter').forEach(function (root) {
    var fixedKind = root.getAttribute('data-kind');
    var kindSel = root.querySelector('.ck'), amt = root.querySelector('.ca'), fromSel = root.querySelector('.cf'), toSel = root.querySelector('.ct');
    var out = root.querySelector('.out'), prov = root.querySelector('.prov'), swap = root.querySelector('.cs');
    function fill(kind, a, b) {
      [fromSel, toSel].forEach(function (s) { s.innerHTML = ''; });
      D.units.filter(function (u) { return u.kind === kind; }).forEach(function (u) { opt(fromSel, u); opt(toSel, u); });
      fromSel.value = a || D.kinds[kind].pair[0]; toSel.value = b || D.kinds[kind].pair[1];
    }
    if (kindSel) {
      Object.keys(D.kinds).forEach(function (k) { var o = document.createElement('option'); o.value = k; o.textContent = D.kinds[k].name; kindSel.appendChild(o); });
      kindSel.addEventListener('change', function () { fill(kindSel.value); run(); });
    }
    var start = root.getAttribute('data-pair'); var p = start ? start.split(',') : [];
    var k0 = fixedKind || (p[0] && byId[p[0]] ? byId[p[0]].kind : 'length');
    if (kindSel) kindSel.value = k0;
    fill(k0, p[0], p[1]);
    function run() {
      var a = byId[fromSel.value], b = byId[toSel.value], x = parse(amt.value);
      if (!x) { out.textContent = 'Enter a number, for example 12 or 0.5'; prov.textContent = ''; return; }
      var r = fmt(convert(x, a, b)), shown = fmt(x).text;
      out.textContent = shown + ' ' + (a.sym || a.name) + ' = ' + r.text + ' ' + (b.sym || b.name);
      var exactUnits = a.exact && b.exact;
      var status = r.exact && exactUnits ? 'Exact: both units are defined exactly and the result terminates.'
        : (exactUnits ? 'Both units are exact; the result is a repeating decimal, shown to 15 significant figures.'
          : 'One of the units is approximate or conventional; treat the result as approximate.');
      prov.innerHTML = '';
      [status, '1 ' + a.name + ': ' + a.by + ' (' + D.sources[a.src] + ')', '1 ' + b.name + ': ' + b.by + ' (' + D.sources[b.src] + ')']
        .forEach(function (t, i) { var dv = document.createElement('div'); dv.textContent = t; if (!i) dv.style.color = r.exact && exactUnits ? 'var(--flag-b)' : ''; prov.appendChild(dv); });
    }
    [amt, fromSel, toSel].forEach(function (el) { el.addEventListener('input', run); el.addEventListener('change', run); });
    if (swap) swap.addEventListener('click', function () { var t = fromSel.value; fromSel.value = toSel.value; toSel.value = t; run(); });
    run();
  });
})();
