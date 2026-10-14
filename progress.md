# Progress

## 2026-10-14: Wave 1 (Measure + Shape) built
- Proposal approved by the owner (name Reckoning; keep the never-name-the-books rule; start
  with Wave 1; scope: no wartime appendix, no hand photos, zodiac as astronomy only).
- Measure: 144 units in 10 kinds (141 exact), SI constants/base/derived/prefixes, fractions of
  an inch, a converter on every page with exact rational arithmetic and per-unit sources.
- Shape: 20 plane figures + 22 solids, live figures (SVG / three.js), formulas in KaTeX,
  then-and-now notes, topology lens page.
- Checks: 61 unit values vs NIST, temperature fixed points, all 42 area/volume formulas vs
  Monte Carlo, 9 perimeters/surfaces by integration, Euler characteristics.
- Found while checking: the old handbook ellipse perimeter rule overestimates by 2.54 % at 2:1
  (text says "about 2.5 %"); two source URLs were dead and were replaced (IAU archive, EPSG).

## 2026-10-14: Wave 2 (Signal + Weather) built
- Signal: 26 code flags + 10 numeral pennants + 3 substitutes + answering pennant, drawn from
  their blazons; single-letter meanings (ICS 1969/2005); hoist composer with substitute rules;
  Morse player (ITU timing, PARIS wpm, Farnsworth, lamp, older 5-unit gap toggle) and ear drill;
  ICAO/ITU alphabet + figure code words + 1941 Able-Baker list (secondary source, labelled);
  COLREGs sound signals played at real length.
- Weather: Beaufort 0-12 with an animated sea at a fixed scale beside a 10 m boat; WMO sea-state
  code 3700 (verified against the 2010 WMO-No. 306 text); marine visibility terms; 20 present-
  weather symbols (ww meanings verified in WMO-No. 306); cyclone basins map + Saffir-Simpson.
- Found while checking: the Beaufort knot and m/s limits are separately rounded tables and
  disagree by up to ~0.5 m/s at forces 4-6; stated on the page, check allows 0.6.
- Dropped: the swell (Douglas) table, because no primary source was found.

## 2026-10-14: Wave 3 (Number + Sky & sea) built
- Number: 59 symbols with Unicode names and first uses checked in Cajori (dates left blank where not
  verified; Hérigone's 1634 angle sign was "<", noted); Greek alphabet with uses, look-alikes and a
  drill; unit circle, exact values (from the tested JS), angle units, 32 points, triangle solver with
  the ambiguous case; logarithms (characteristic, mantissa, bar notation) and a 7-scale slide rule.
- Sky & sea: three.js globe (tap to read, WGS 84 minute lengths, geocentric latitude); great circle vs
  rhumb line on Mercator + gnomonic charts with Vincenty and the mid-latitude shortcut; live clocks
  (UTC, zone, LMT, apparent, GMST, LST), equation of time and analemma, zone letters; celestial
  sphere in 3D, signs vs the 13 ecliptic constellations with this year's dates; planets with names,
  symbols, IAU 1989 rule against symbols, Pluto 2006, and a JPL-element orrery.
- Found while checking: the Vincenty worked example is on GRS80, not the ANS; Neptune's period from
  Kepler's law with the JPL a is 0.7 % longer than NASA's sidereal period (planetary perturbations;
  check tolerance 1 %). The IAU 1989 manual (scanned) was read page by page for 5.15/5.223/5.25.

## Next
- Wave 2 leftovers: semaphore; bell and gong signals; the other 80 present-weather symbols.
- Wave 4: Ship + Code of life (and glossary/naming pages, homepage widget).
- Wave 3 leftovers: Moon phases; star chart; sight reduction; log-table page for sines.
- Known gaps: foreign national units of the old handbook (vara, arroba…) are left out because
  they varied by country; density/specific-gravity explorer not built yet.
