"""Number room data: mathematical symbols and the Greek alphabet.

Every symbol is stored with its Unicode code point and official Unicode name; tests/check_wave3.py
checks both against Python's unicodedata. "First" is the earliest printed (or manuscript, where
stated) use as documented by Cajori, A History of Mathematical Notations (1928-29); it is left
empty where that history is uncertain or was not checked.
"""

# (char, Unicode name, meaning, example, first use)
SYMBOLS = [
    ('Arithmetic and relations', [
        ('+', 'PLUS SIGN', 'plus, add', '3 + 4 = 7', 'printed by Johann Widman, 1489'),
        ('−', 'MINUS SIGN', 'minus, subtract (not the hyphen)', '7 − 4 = 3', 'printed by Johann Widman, 1489'),
        ('×', 'MULTIPLICATION SIGN', 'times; also the vector product', '3 × 4 = 12', 'William Oughtred, Clavis mathematicae, 1631'),
        ('⋅', 'DOT OPERATOR', 'times; the scalar (dot) product', 'a ⋅ b', ''),
        ('÷', 'DIVISION SIGN', 'divided by', '12 ÷ 4 = 3', 'Johann Heinrich Rahn, Teutsche Algebra, 1659'),
        ('/', 'SOLIDUS', 'divided by, ratio (the IAU and ISO prefer it to ÷)', 'm/s', ''),
        ('=', 'EQUALS SIGN', 'is equal to', '2 + 2 = 4', 'Robert Recorde, The Whetstone of Witte, 1557'),
        ('≠', 'NOT EQUAL TO', 'is not equal to', '1 ≠ 2', ''),
        ('≡', 'IDENTICAL TO', 'is identically equal to; congruent to (modulo)', '−16 ≡ 9 (mod 5)', 'congruence: Carl Friedrich Gauss, 1801'),
        ('≈', 'ALMOST EQUAL TO', 'is approximately equal to', 'π ≈ 3.14', ''),
        ('≅', 'APPROXIMATELY EQUAL TO', 'is congruent to (geometry); also asymptotically equal', '△ABC ≅ △DEF', ''),
        ('∼', 'TILDE OPERATOR', 'is of the order of; is similar to', 'n! ∼ √(2πn)(n/e)ⁿ', ''),
        ('∝', 'PROPORTIONAL TO', 'is proportional to', 'F ∝ 1/r²', ''),
        ('<', 'LESS-THAN SIGN', 'is less than', '2 < 3', 'Thomas Harriot, Artis analyticae praxis, 1631'),
        ('>', 'GREATER-THAN SIGN', 'is greater than', '3 > 2', 'Thomas Harriot, Artis analyticae praxis, 1631'),
        ('≤', 'LESS-THAN OR EQUAL TO', 'is less than or equal to', 'x ≤ 1', ''),
        ('≥', 'GREATER-THAN OR EQUAL TO', 'is greater than or equal to', 'n ≥ 0', ''),
        ('≪', 'MUCH LESS-THAN', 'is much less than', 'm ≪ M', ''),
        ('≫', 'MUCH GREATER-THAN', 'is much greater than', 'R ≫ r', ''),
        ('±', 'PLUS-MINUS SIGN', 'plus or minus', '9.81 ± 0.02', 'Albert Girard 1626 (with “ou”); William Oughtred 1631'),
        ('→', 'RIGHTWARDS ARROW', 'tends to, approaches; maps to', 'x → 0', ''),
        ('∞', 'INFINITY', 'infinity', '1/x → ∞', 'John Wallis, De sectionibus conicis, 1655'),
        ('√', 'SQUARE ROOT', 'square root', '√9 = 3', 'Christoff Rudolff, Coss, 1525'),
        ('!', 'EXCLAMATION MARK', 'factorial: 1 × 2 × … × n', '5! = 120', 'Christian Kramp, 1808'),
        ('%', 'PERCENT SIGN', 'per hundred', '5 % = 0.05', ''),
        ('‰', 'PER MILLE SIGN', 'per thousand (salinity, gradients)', '35 ‰', ''),
    ]),
    ('Analysis', [
        ('∑', 'N-ARY SUMMATION', 'sum of terms', 'Σ k = n(n+1)/2', 'Leonhard Euler, 1755 (as the Greek Σ)'),
        ('∏', 'N-ARY PRODUCT', 'product of terms', 'n! = Π k', ''),
        ('∫', 'INTEGRAL', 'integral (a long S for summa)', '∫ x dx = x²/2 + C', 'Gottfried Leibniz, manuscript of 29 October 1675'),
        ('∂', 'PARTIAL DIFFERENTIAL', 'partial derivative', '∂f/∂x', ''),
        ('∇', 'NABLA', 'gradient (del) operator', '∇T', ''),
        ('∆', 'INCREMENT', 'finite change, difference (written as capital delta)', 'Δt = t₂ − t₁', ''),
    ]),
    ('Geometry', [
        ('∠', 'ANGLE', 'angle', '∠ABC = 90°', 'Pierre Hérigone used < for angle, 1634; the open form ∠ came later'),
        ('⊥', 'UP TACK', 'is perpendicular to', 'AB ⊥ CD', 'Pierre Hérigone, Cursus mathematicus, 1634'),
        ('∥', 'PARALLEL TO', 'is parallel to', 'AB ∥ CD', 'vertical bars for parallel from the 1670s (Kersey and others)'),
        ('△', 'WHITE UP-POINTING TRIANGLE', 'triangle', '△ABC', ''),
        ('°', 'DEGREE SIGN', 'degree of arc (1/360 of a turn)', '45°', ''),
        ('′', 'PRIME', 'minute of arc (1/60 degree)', '12′', ''),
        ('″', 'DOUBLE PRIME', 'second of arc (1/60 minute)', '30″', ''),
        ('∴', 'THEREFORE', 'therefore', '', ''),
        ('∵', 'BECAUSE', 'because', '', ''),
    ]),
    ('Sets and logic', [
        ('∈', 'ELEMENT OF', 'is an element of', '3 ∈ ℕ', ''),
        ('∉', 'NOT AN ELEMENT OF', 'is not an element of', '½ ∉ ℤ', ''),
        ('⊂', 'SUBSET OF', 'is a subset of', 'ℕ ⊂ ℤ', ''),
        ('∪', 'UNION', 'union', 'A ∪ B', ''),
        ('∩', 'INTERSECTION', 'intersection', 'A ∩ B', ''),
        ('∅', 'EMPTY SET', 'the empty set', 'A ∩ ∅ = ∅', ''),
        ('∀', 'FOR ALL', 'for all', '∀x: x² ≥ 0', ''),
        ('∃', 'THERE EXISTS', 'there exists', '∃x: x² = 2', ''),
        ('¬', 'NOT SIGN', 'not', '¬p', ''),
        ('∧', 'LOGICAL AND', 'and', 'p ∧ q', ''),
        ('∨', 'LOGICAL OR', 'or', 'p ∨ q', ''),
        ('⇒', 'RIGHTWARDS DOUBLE ARROW', 'implies', 'p ⇒ q', ''),
        ('⇔', 'LEFT RIGHT DOUBLE ARROW', 'if and only if', 'p ⇔ q', ''),
        ('ℕ', 'DOUBLE-STRUCK CAPITAL N', 'natural numbers', '', ''),
        ('ℤ', 'DOUBLE-STRUCK CAPITAL Z', 'integers (German Zahlen)', '', ''),
        ('ℚ', 'DOUBLE-STRUCK CAPITAL Q', 'rational numbers (quotients)', '', ''),
        ('ℝ', 'DOUBLE-STRUCK CAPITAL R', 'real numbers', '', ''),
        ('ℂ', 'DOUBLE-STRUCK CAPITAL C', 'complex numbers', '', ''),
    ]),
]

# Constants written as letters: (letter, value text, meaning, first use)
CONSTANT_LETTERS = [
    ('π', '3.141 592 653 589 793…', 'ratio of a circle’s circumference to its diameter', 'William Jones, Synopsis palmariorum matheseos, 1706; made standard by Euler'),
    ('e', '2.718 281 828 459 045…', 'base of natural logarithms', 'Leonhard Euler: manuscript of 1727 or 1728, in print 1736'),
    ('i', '√−1', 'imaginary unit', 'Leonhard Euler, memoir of 1777 (published 1794)'),
]

# Greek alphabet: (name, capital, small, variant small forms, uses)
GREEK = [
    ('alpha', 'Α', 'α', '', 'angles; alpha particle; angular acceleration; the fine-structure constant; right ascension (astronomy)'),
    ('beta', 'Β', 'β', 'ϐ', 'angles; beta particle; speed as a fraction of light speed, v/c; ecliptic latitude'),
    ('gamma', 'Γ', 'γ', '', 'photon, gamma ray; Lorentz factor; ratio of heat capacities; Γ the gamma function'),
    ('delta', 'Δ', 'δ', '', 'Δ a change or difference; δ a small change, the Kronecker delta; declination (astronomy)'),
    ('epsilon', 'Ε', 'ε', 'ϵ', 'permittivity ε₀; strain; a small quantity; obliquity of the ecliptic'),
    ('zeta', 'Ζ', 'ζ', '', 'the Riemann zeta function; damping ratio'),
    ('eta', 'Η', 'η', '', 'efficiency; dynamic viscosity'),
    ('theta', 'Θ', 'θ', 'ϑ', 'angles, the polar angle; Θ thermodynamic temperature in some texts'),
    ('iota', 'Ι', 'ι', '', 'rarely used: it is too easily read as i'),
    ('kappa', 'Κ', 'κ', 'ϰ', 'curvature; compressibility; thermal diffusivity in some fields'),
    ('lambda', 'Λ', 'λ', '', 'wavelength; decay constant; ecliptic longitude; Λ the cosmological constant'),
    ('mu', 'Μ', 'μ', '', 'the prefix micro (upright); permeability μ₀; coefficient of friction; mean'),
    ('nu', 'Ν', 'ν', '', 'frequency; neutrino; kinematic viscosity'),
    ('xi', 'Ξ', 'ξ', '', 'ξ a coordinate or random variable; Ξ a family of baryons'),
    ('omicron', 'Ο', 'ο', '', 'almost never used: it looks like o'),
    ('pi', 'Π', 'π', 'ϖ', 'π the circle constant; Π a product of terms'),
    ('rho', 'Ρ', 'ρ', 'ϱ', 'density; resistivity; charge density'),
    ('sigma', 'Σ', 'σ', 'ς', 'Σ a sum; σ standard deviation, the Stefan–Boltzmann constant, conductivity, stress; ς only ends a word'),
    ('tau', 'Τ', 'τ', '', 'torque; time constant, mean life; shear stress'),
    ('upsilon', 'Υ', 'υ', '', 'rarely used: it is too close to u and v'),
    ('phi', 'Φ', 'φ', 'ϕ', 'angles; latitude in navigation and geodesy; Φ magnetic flux; the golden ratio φ'),
    ('chi', 'Χ', 'χ', '', 'χ² statistic; magnetic susceptibility; the Euler characteristic χ of topology'),
    ('psi', 'Ψ', 'ψ', '', 'wave function'),
    ('omega', 'Ω', 'ω', '', 'ω angular frequency; Ω the ohm (unit symbol), solid angle, longitude of an orbit’s ascending node'),
]

# Unicode look-alikes: (char, Unicode name, preferred char, how Unicode relates them: 'compat' NFKC only, 'canon' NFC, 'none', note)
LOOKALIKES = [
    ('\u00b5', 'MICRO SIGN', '\u03bc', 'compat', 'The micro sign is kept only for compatibility with old character sets; Unicode maps it to the Greek small mu. Either way the prefix is printed upright: μm, not 𝜇m.'),
    ('\u2126', 'OHM SIGN', '\u03a9', 'canon', 'The ohm sign is canonically the same character as Greek capital omega; Unicode recommends using omega.'),
    ('\u212b', 'ANGSTROM SIGN', '\u00c5', 'canon', 'The ångström sign is canonically the letter Å.'),
    ('\u2206', 'INCREMENT', '\u0394', 'none', 'A separate operator character; in text the Greek capital delta is normally used.'),
]

# Navigator's compass: 32 points of 11¼° each
POINTS = ['N', 'N by E', 'NNE', 'NE by N', 'NE', 'NE by E', 'ENE', 'E by N', 'E', 'E by S', 'ESE', 'SE by E', 'SE', 'SE by S', 'SSE', 'S by E',
          'S', 'S by W', 'SSW', 'SW by S', 'SW', 'SW by W', 'WSW', 'W by S', 'W', 'W by N', 'WNW', 'NW by W', 'NW', 'NW by N', 'NNW', 'N by W']
