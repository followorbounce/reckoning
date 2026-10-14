/* Reckoning Morse: timing from units (ITU-R M.1677-1: dot 1, dash 3, gaps 1 / 3 / 7), speed in words per
   minute by the PARIS standard (50 units per word, so one unit = 1.2 / wpm seconds), optional Farnsworth
   spacing (characters at full speed, extra space between them), a lamp, and a listen-and-type drill. */
(function () {
  'use strict';
  var M = window.RK_MORSE; if (!M) return;
  var $ = function (id) { return document.getElementById(id); };
  var txt = $('mtext'), wpm = $('mwpm'), fwpm = $('mfwpm'), oldgap = $('moldgap'), bar = $('mbar'), lamp = $('mlamp'), info = $('minfo');
  var playing = null;

  function seq(text, wordGap) {
    var s = [], words = text.toUpperCase().trim().split(/\s+/).filter(Boolean);
    words.forEach(function (w, wi) {
      var chars = w.split('').filter(function (c) { return M.code[c]; });
      chars.forEach(function (c, ci) {
        var code = M.code[c];
        code.split('').forEach(function (e, ei) {
          s.push({ on: true, u: e === '.' ? 1 : 3, ch: c });
          if (ei < code.length - 1) s.push({ on: false, u: 1, kind: 'el' });
        });
        if (ci < chars.length - 1) s.push({ on: false, u: 3, kind: 'ch' });
      });
      if (wi < words.length - 1 && chars.length) s.push({ on: false, u: wordGap, kind: 'wd' });
    });
    return s;
  }
  function timing() {
    var c = +wpm.value, f = Math.min(+fwpm.value, c), unit = 1.2 / c, gap = oldgap && oldgap.checked ? 5 : 7;
    var ch = 3 * unit, wd = gap * unit;
    if (f < c) {   // Farnsworth: stretch only the gaps between characters and words
      var ta = (60 * c - 37.2 * f) / (f * c);
      ch = 3 * ta / 19; wd = gap * ta / 19;
    }
    return { unit: unit, ch: ch, wd: wd, gap: gap, c: c, f: f };
  }
  function draw() {
    var T = timing(), s = seq(txt.value, T.gap), units = 0, secs = 0;
    bar.innerHTML = '';
    s.forEach(function (x, i) {
      var d = x.on ? x.u * T.unit : (x.kind === 'ch' ? T.ch : x.kind === 'wd' ? T.wd : T.unit);
      x.d = d; units += x.u; secs += d;
      var sp = document.createElement('span');
      sp.style.width = Math.max(2, x.u * 6) + 'px';
      sp.className = x.on ? 'on' : 'off';
      bar.appendChild(sp);
    });
    info.textContent = units + ' units · ' + secs.toFixed(1) + ' s at ' + T.c + ' wpm' + (T.f < T.c ? ' (Farnsworth ' + T.f + ' wpm)' : '') +
      ' · word gap ' + T.gap + ' units' + (T.gap === 5 ? ' (older practice)' : ' (ITU)');
    return s;
  }
  function stop() {
    if (playing) { try { playing.osc.stop(); } catch (e) { /* ignore */ } playing.timers.forEach(clearTimeout); playing = null; }
    lamp.classList.remove('lit'); bar.querySelectorAll('.lit').forEach(function (e) { e.classList.remove('lit'); });
    $('mplay').textContent = 'Play';
  }
  function play(s, freq) {
    stop();
    var list = [], t = 0;
    s.forEach(function (x) { if (x.on) list.push([t, x.d]); t += x.d; });
    var h = window.RK_AUDIO.tones(list, freq || +$('mtone').value, 0.22, 'sine');
    if (!h) return;
    var timers = [], spans = bar.children, base = (h.start - h.ctx.currentTime) * 1000, acc = 0;
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    s.forEach(function (x, i) {
      if (x.on && !reduce && spans[i]) {
        (function (el, a, b) {
          timers.push(setTimeout(function () { el.classList.add('lit'); lamp.classList.add('lit'); }, a));
          timers.push(setTimeout(function () { el.classList.remove('lit'); lamp.classList.remove('lit'); }, b));
        })(spans[i], base + acc * 1000, base + (acc + x.d) * 1000);
      }
      acc += x.d;
    });
    timers.push(setTimeout(stop, base + acc * 1000 + 100));
    playing = { osc: h.osc, timers: timers };
    $('mplay').textContent = 'Stop';
  }
  [txt, wpm, fwpm, oldgap].forEach(function (el) { if (el) el.addEventListener('input', function () { $('mwpmv').textContent = wpm.value; $('mfwpmv').textContent = Math.min(+fwpm.value, +wpm.value); draw(); }); });
  $('mplay').addEventListener('click', function () { if (playing) stop(); else play(draw()); });
  document.querySelectorAll('[data-say]').forEach(function (b) {
    b.addEventListener('click', function () { txt.value = b.getAttribute('data-say'); play(draw()); });
  });
  draw();

  /* drill: listen, type what you heard */
  var dset = $('dset'), dlen = $('dlen'), dans = $('dans'), dres = $('dres'), score = { ok: 0, n: 0 }, current = '';
  function pool() {
    var v = dset.value;
    if (v === 'letters') return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (v === 'digits') return '0123456789';
    if (v === 'all') return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    return 'ETIANMSUWDKRGO';   /* the letters with the shortest codes, a gentle start */
  }
  function newGroup() {
    var p = pool(), n = +dlen.value, g = '';
    for (var i = 0; i < n; i++) g += p.charAt(Math.floor(Math.random() * p.length));
    return g;
  }
  $('dlisten').addEventListener('click', function () {
    if (!current) current = newGroup();
    var keep = txt.value; txt.value = current; var s = draw(); txt.value = keep; play(s); dans.focus();
  });
  $('dcheck').addEventListener('click', check);
  dans.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); check(); } });
  function check() {
    if (!current) return;
    var a = dans.value.toUpperCase().replace(/\s/g, ''), ok = a === current;
    score.n++; if (ok) score.ok++;
    dres.textContent = (ok ? 'Right: ' : 'It was ' ) + current.split('').map(function (c) { return c + ' ' + M.code[c]; }).join('   ') + '  ·  ' + score.ok + ' of ' + score.n;
    dres.className = ok ? 'out good' : 'out bad';
    current = ''; dans.value = '';
  }
})();
