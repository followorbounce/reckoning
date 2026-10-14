/* Ship structure page: tap a part of the midship section (or its name) to highlight it and read what it does;
   switch between the transverse and the longitudinal framing system. */
(function () {
  'use strict';
  var svg = document.getElementById('mid'); if (!svg) return;
  var P = window.RK_PARTS, nm = document.getElementById('pname'), ds = document.getElementById('pdesc'), note = document.getElementById('sysnote');
  var btns = document.querySelectorAll('.pbtn'), sel = null;
  // a wide invisible copy of every thin stroke, so a finger can hit it
  svg.querySelectorAll('.part path.ps').forEach(function (p) { var h = p.cloneNode(); h.setAttribute('class', 'hit'); h.removeAttribute('style'); p.parentNode.insertBefore(h, p); });
  function show(k) {
    sel = k;
    svg.querySelectorAll('.part').forEach(function (g) { g.classList.toggle('on', g.getAttribute('data-part') === k); });
    btns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-part') === k ? 'true' : 'false'); });
    svg.classList.toggle('picking', !!k);
    if (!k) return;
    var i = Object.keys(P).indexOf(k) + 1;
    nm.textContent = i + ' · ' + P[k][0]; ds.textContent = P[k][1];
  }
  svg.addEventListener('click', function (e) {
    var g = e.target.closest && e.target.closest('.part');
    show(g ? g.getAttribute('data-part') : null);
  });
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-part');
      if (b.classList.contains('lg') && svg.classList.contains('sys-tr')) sys('lg');
      if (k === 'frame' && svg.classList.contains('sys-lg')) sys('tr');
      show(k);
      if (window.innerWidth < 760) svg.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
  var NOTE = { tr: 'Transverse: a frame, a floor and a beam at every frame space, about 0.6 m to 0.9 m apart, form closed rings.',
               lg: 'Longitudinal: fore-and-aft stiffeners (dots) along bottom, tank top, side and deck, held by deep web frames a few metres apart.' };
  function sys(s) {
    svg.classList.remove('sys-tr', 'sys-lg'); svg.classList.add('sys-' + s);
    document.querySelectorAll('.sysb').forEach(function (b) { var on = b.getAttribute('data-sys') === s; b.classList.toggle('ghost', !on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    note.textContent = NOTE[s];
    if (sel && ((s === 'tr' && (sel === 'long' || sel === 'web')) || (s === 'lg' && sel === 'frame'))) show(null);
  }
  document.querySelectorAll('.sysb').forEach(function (b) { b.addEventListener('click', function () { sys(b.getAttribute('data-sys')); }); });
  sys('tr');
})();
