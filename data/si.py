"""The SI as defined since 20 May 2019: seven defining constants, seven base units,
22 derived units with special names, and the prefixes (24 since 2022). Source: BIPM
SI Brochure, 9th edition (Tables 1, 2, 4 and 7) and CGPM 2022 Resolution 3."""

CONSTANTS = [
    # symbol, name, exact value text, unit, which base unit it fixes
    ('ΔνCs', 'hyperfine transition frequency of caesium-133', '9 192 631 770', 'Hz', 's'),
    ('c', 'speed of light in vacuum', '299 792 458', 'm/s', 'm'),
    ('h', 'Planck constant', '6.626 070 15 × 10⁻³⁴', 'J s', 'kg'),
    ('e', 'elementary charge', '1.602 176 634 × 10⁻¹⁹', 'C', 'A'),
    ('k', 'Boltzmann constant', '1.380 649 × 10⁻²³', 'J/K', 'K'),
    ('NA', 'Avogadro constant', '6.022 140 76 × 10²³', 'mol⁻¹', 'mol'),
    ('Kcd', 'luminous efficacy of 540 THz radiation', '683', 'lm/W', 'cd'),
]

BASE = [
    # symbol, name, quantity, how it is fixed (plain words), what it replaced
    ('s', 'second', 'time', 'Fixed by taking the caesium frequency ΔνCs to be exactly 9 192 631 770 Hz.',
     'Defined from the caesium atom since 1967; before that, as a fraction of the year 1900, and earlier of the mean solar day.'),
    ('m', 'metre', 'length', 'The distance light travels in vacuum in 1/299 792 458 of a second, because c is fixed.',
     'Since 1983. Before: a wavelength of krypton-86 light (1960), and before that a platinum-iridium bar in Sèvres (1889).'),
    ('kg', 'kilogram', 'mass', 'Fixed by taking the Planck constant h to be exactly 6.626 070 15 × 10⁻³⁴ J s, with the metre and second.',
     'Since 2019. From 1889 to 2019 it was the mass of one metal cylinder, the International Prototype, kept near Paris.'),
    ('A', 'ampere', 'electric current', 'Fixed by taking the elementary charge e to be exactly 1.602 176 634 × 10⁻¹⁹ C: one ampere is that many charges per second, inverted.',
     'Since 2019. Before: the current giving a set force between two long parallel wires (1948).'),
    ('K', 'kelvin', 'thermodynamic temperature', 'Fixed by taking the Boltzmann constant k to be exactly 1.380 649 × 10⁻²³ J/K.',
     'Since 2019. From 1954 to 2019: 1/273.16 of the temperature of the triple point of water.'),
    ('mol', 'mole', 'amount of substance', 'Exactly 6.022 140 76 × 10²³ specified entities (atoms, molecules, ions…).',
     'Since 2019. Before: as many entities as atoms in 12 g of carbon-12.'),
    ('cd', 'candela', 'luminous intensity', 'Fixed by taking the luminous efficacy of green light at 540 × 10¹² Hz to be exactly 683 lm/W.',
     'Since 1979, restated in 2019. Earlier definitions used a glowing platinum surface and, before that, candles.'),
]

DERIVED = [
    # symbol, name, quantity, in other SI units, in base units
    ('rad', 'radian', 'plane angle', 'm/m', '1'),
    ('sr', 'steradian', 'solid angle', 'm²/m²', '1'),
    ('Hz', 'hertz', 'frequency', '', 's⁻¹'),
    ('N', 'newton', 'force', '', 'kg m s⁻²'),
    ('Pa', 'pascal', 'pressure, stress', 'N/m²', 'kg m⁻¹ s⁻²'),
    ('J', 'joule', 'energy, work, heat', 'N m', 'kg m² s⁻²'),
    ('W', 'watt', 'power', 'J/s', 'kg m² s⁻³'),
    ('C', 'coulomb', 'electric charge', '', 'A s'),
    ('V', 'volt', 'electric potential difference', 'W/A', 'kg m² s⁻³ A⁻¹'),
    ('F', 'farad', 'capacitance', 'C/V', 'kg⁻¹ m⁻² s⁴ A²'),
    ('Ω', 'ohm', 'electric resistance', 'V/A', 'kg m² s⁻³ A⁻²'),
    ('S', 'siemens', 'electric conductance', 'A/V', 'kg⁻¹ m⁻² s³ A²'),
    ('Wb', 'weber', 'magnetic flux', 'V s', 'kg m² s⁻² A⁻¹'),
    ('T', 'tesla', 'magnetic flux density', 'Wb/m²', 'kg s⁻² A⁻¹'),
    ('H', 'henry', 'inductance', 'Wb/A', 'kg m² s⁻² A⁻²'),
    ('°C', 'degree Celsius', 'Celsius temperature', '', 'K'),
    ('lm', 'lumen', 'luminous flux', 'cd sr', 'cd sr'),
    ('lx', 'lux', 'illuminance', 'lm/m²', 'cd sr m⁻²'),
    ('Bq', 'becquerel', 'activity of a radionuclide', '', 's⁻¹'),
    ('Gy', 'gray', 'absorbed dose', 'J/kg', 'm² s⁻²'),
    ('Sv', 'sievert', 'dose equivalent', 'J/kg', 'm² s⁻²'),
    ('kat', 'katal', 'catalytic activity', '', 'mol s⁻¹'),
]

PREFIXES = [
    # exponent, name, symbol, year adopted
    (30, 'quetta', 'Q', 2022), (27, 'ronna', 'R', 2022), (24, 'yotta', 'Y', 1991), (21, 'zetta', 'Z', 1991),
    (18, 'exa', 'E', 1975), (15, 'peta', 'P', 1975), (12, 'tera', 'T', 1960), (9, 'giga', 'G', 1960),
    (6, 'mega', 'M', 1960), (3, 'kilo', 'k', 1795), (2, 'hecto', 'h', 1795), (1, 'deca', 'da', 1795),
    (-1, 'deci', 'd', 1795), (-2, 'centi', 'c', 1795), (-3, 'milli', 'm', 1795), (-6, 'micro', 'µ', 1960),
    (-9, 'nano', 'n', 1960), (-12, 'pico', 'p', 1960), (-15, 'femto', 'f', 1964), (-18, 'atto', 'a', 1964),
    (-21, 'zepto', 'z', 1991), (-24, 'yocto', 'y', 1991), (-27, 'ronto', 'r', 2022), (-30, 'quecto', 'q', 2022),
]
