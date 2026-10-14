/* Sound signals (COLREGs Rule 32): short blast about 1 s, prolonged blast 4 to 6 s (5 s used here).
   A low sawtooth stands in for a ship's whistle. "Quick" plays the same rhythm at 40 % of real time. */
(function () {
  'use strict';
  var quick = document.getElementById('hquick');
  document.querySelectorAll('[data-blasts]').forEach(function (b) {
    b.addEventListener('click', function () {
      var p = b.getAttribute('data-blasts'), k = quick && quick.checked ? 0.4 : 1, t = 0, list = [];
      p.split('').forEach(function (c, i) {
        var d = (c === 'p' ? 5 : 1) * k; list.push([t, d]); t += d + (p === 'pp' ? 2 : 1) * k;
      });
      var h = window.RK_AUDIO.tones(list, 160, 0.16, 'sawtooth');
      if (!h) return;
      b.classList.add('lit'); setTimeout(function () { b.classList.remove('lit'); }, (h.end - h.ctx.currentTime) * 1000);
    });
  });
})();
