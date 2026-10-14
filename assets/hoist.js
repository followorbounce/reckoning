/* Flag hoist composer. A ship carries one set of flags, so a letter or figure that already appears
   higher in the same hoist is shown with a substitute: the first substitute repeats the uppermost flag
   of the class (letters or numeral pennants) immediately above it, the second the second, the third
   the third (International Code of Signals, chapter 1). */
(function () {
  'use strict';
  var F = window.RK_FLAGS; if (!F) return;
  var inp = document.getElementById('htext'), mast = document.getElementById('hmast'), out = document.getElementById('hout');
  function cls(c) { return /[0-9]/.test(c) ? 'num' : /[A-Z]/.test(c) ? 'let' : null; }
  function build(text) {
    var chars = text.toUpperCase().replace(/[^A-Z0-9]/g, '').split(''), hoist = [], notes = [];
    var block = [], blockCls = null;
    chars.forEach(function (c) {
      var k = cls(c);
      if (k !== blockCls) { block = []; blockCls = k; }
      var pos = block.indexOf(c), item;
      if (pos >= 0 && pos < 3) item = { sub: pos, ch: c };
      else if (pos >= 3) { item = { ch: c, warn: true }; notes.push(c + ' repeats a flag lower than third in its group; split the signal into two hoists.'); }
      else item = { ch: c };
      block.push(c); hoist.push(item);
    });
    return { hoist: hoist, notes: notes, chars: chars };
  }
  function render() {
    var r = build(inp.value || ''), h = '';
    r.hoist.forEach(function (it) {
      var svg = it.sub !== undefined ? F.subs[it.sub] : (/[0-9]/.test(it.ch) ? F.digits[it.ch] : F.letters[it.ch]);
      var label = it.sub !== undefined ? ['1st', '2nd', '3rd'][it.sub] + ' substitute = ' + it.ch : it.ch + ' · ' + (F.words[it.ch] || '');
      h += '<div class="hflag' + (it.warn ? ' warn' : '') + '">' + svg + '<span>' + label + '</span></div>';
    });
    mast.innerHTML = h || '<p class="small">Type letters or figures to hoist them.</p>';
    var t = '';
    if (r.chars.length === 1 && F.meanings[r.chars[0]]) t = r.chars[0] + ' (' + F.words[r.chars[0]] + '): ' + F.meanings[r.chars[0]];
    else if (r.chars.length) t = 'Spelled: ' + r.chars.map(function (c) { return F.words[c] || c; }).join(' · ');
    if (r.notes.length) t += '  ' + r.notes.join(' ');
    out.textContent = t;
  }
  inp.addEventListener('input', render);
  document.querySelectorAll('[data-hoist]').forEach(function (b) { b.addEventListener('click', function () { inp.value = b.getAttribute('data-hoist'); render(); }); });
  render();
})();
