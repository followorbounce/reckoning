/* Shared audio for Reckoning: one AudioContext, unlocked from a user gesture (iOS Safari needs
   the context resumed and a silent buffer played inside the tap; the ringer switch can still mute it). */
(function () {
  'use strict';
  var ctx = null;
  function get() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === 'suspended') ctx.resume();
    try { var b = ctx.createBuffer(1, 1, 22050), s = ctx.createBufferSource(); s.buffer = b; s.connect(ctx.destination); s.start(0); } catch (e) { /* ignore */ }
    return ctx;
  }
  /* schedule tones: list of [startSeconds, durationSeconds]; returns end time */
  function tones(list, freq, vol, type) {
    var c = get(); if (!c) return 0;
    var t0 = c.currentTime + 0.06, g = c.createGain(); g.gain.value = 0; g.connect(c.destination);
    var o = c.createOscillator(); o.type = type || 'sine'; o.frequency.value = freq || 650; o.connect(g); o.start(t0);
    var end = t0;
    list.forEach(function (p) {
      var a = t0 + p[0], b = a + p[1], r = Math.min(0.006, p[1] / 4);
      g.gain.setValueAtTime(0, a); g.gain.linearRampToValueAtTime(vol || 0.25, a + r);
      g.gain.setValueAtTime(vol || 0.25, b - r); g.gain.linearRampToValueAtTime(0, b);
      end = Math.max(end, b);
    });
    o.stop(end + 0.05);
    return { start: t0, end: end, osc: o, gain: g, ctx: c };
  }
  window.RK_AUDIO = { get: get, tones: tones };
})();
