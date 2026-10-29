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

## 2026-10-14: Wave 4 (Ship + Code of life), glossary, naming page, homepage card
- Ship: tappable midship section (25 parts, transverse/longitudinal framing, strakes lettered); buoyancy and
  load line (displacement, TPC, FWA = Δ/40 TPC, dock water, the mark drawn to Annex I sizes); stability
  simulator computed from the section polygon (three hulls, KG, off-centre G, slack tank, GZ curve to 90°,
  IMO 2008 IS Code A 2.2 criteria).
- Code of life: bases as skeletal formulas (formulas re-derived from the drawing at build time), WC pairs,
  nucleotide; IUPAC decoder with expansion, complements, two-strand pattern search; A/B/Z helix in 3D;
  supercoiling with Lk, Tw and Wr each computed independently on a coiled ribbon.
- Glossary (61 terms EN/ES/FR + same-word-different-meaning cards) and Names from the sky (gods, moon
  themes, dwarf planets, weekdays, months, elements). Nav gains Ship, Code of life, Glossary.
- Homepage: "Signal of the day" card on followorbounce.github.io reads reckoning/assets/signal-of-day.json.
- Found while checking: B-DNA in solution is 10.4 ± 0.1 bp/turn (Wang 1979), not the often-quoted 10.5;
  the old "1/48 of the draught" fresh-water rule survives in the 1966 Convention only as the fallback when
  the displacement cannot be certified (reg. 40(8)); a common gods table pairs Apollo with Sol, but Rome
  kept Apollo's Greek name.
- Not verified on a real iPhone: dragging the 3D views and sliders (headless screenshots only).

## Next
- Wave 2 leftovers: semaphore; bell and gong signals; the other 80 present-weather symbols.
- Wave 4 leftovers: hull ends and a 3D hull; weather criterion (wind heel); RNA secondary structure;
  codon table / genetic code; more glossary terms.
- Wave 3 leftovers: Moon phases; star chart; sight reduction; log-table page for sines.
- Known gaps: foreign national units of the old handbook (vara, arroba…) are left out because
  they varied by country; density/specific-gravity explorer not built yet.

## 2026-10-14: Wave 5 (Light) built
- Owner request: an interactive explanation of light going through lenses, prisms and other objects ("call science team").
- assets/optics.js: exact 2D ray tracer (Snell at the real surface, Fresnel split for unpolarised light, TIR), five materials from published
  dispersion formulas (N-BK7, N-F2, fused silica, water 20 °C, diamond), lenses from signed radii, prisms, blocks, half-cylinder, drop,
  plane/spherical/parabolic/convex mirrors, ideal thin lens. tests/check_wave5.js: 110 checks against published indices, IAPWS 1997 and
  closed forms (see CLAUDE.md).
- Pages: Refraction and total reflection, Lenses, Prisms and colour, Mirrors, The rainbow (with a deviation chart), Free bench (sandbox).
- Found while checking: handbook indices (water n_D = 1.3330) are relative to air, while the Daimon-Masumura and IAPWS water formulas give
  the absolute index (1.33335); they agree with each other to 1e-6. Water is now divided by the index of air so every material is
  relative to air, as the bench (air = 1) needs. N-F2 has v_d = 36.43; the often-quoted 36.37 is the old lead glass F2.
- Primary rainbow 42.08° (589 nm), red 42.49° / violet 40.62°; secondary 50.1°-53.5°; 60° N-BK7 prism minimum deviation 38.65°.
- Not verified on a real iPhone: dragging on the bench (headless screenshots at 390 px only).
- Science-team review (independent reviewer as Optical Physicist / Science Communicator / Historian, per AGENTS.md): approve-with-changes,
  no blocks. Fixed: spectacles sermon was preached in Florence (by Giordano da Pisa), not Pisa; only F and C are Fraunhofer's letters
  (d is helium, found 1868); most large modern telescopes are Ritchey-Chretien (hyperbolic), not parabolic; "each refraction" (not each
  pass) turns the ray by i − r; coma described as the bench shows it; Newton's Opticks link is the 1730 4th edition; readouts no longer
  print double negatives and say where distances are measured from; labels follow the chosen material; air index scaled to 20 °C.
  Tests: prism and drop formulas now written out in the test (were compared with the page's own functions), added Fresnel R_s/R_p at 45°,
  rotated lens and prism, two internal reflections, front focal distance, off-axis convex mirror (110 → 123 checks).

## 2026-10-28 — Reach plan F4: structured data
Article on 100 pages, breadcrumbs on 101, glossary DefinedTermSet (JSON-LD in build.py).
