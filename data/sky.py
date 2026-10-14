"""Sky & sea room data: planets and their names, constellations, zodiac signs, ports for the sailing page.

Planet symbols are checked against the Unicode database by tests/check_wave3.py. Orbital data come
from assets/astro.js (JPL elements); physical data below are from the NASA Planetary Fact Sheet.
"""

# (key, name, symbol, Unicode name, Roman figure, Greek counterpart, why the name, IAU 1989 table abbreviation)
PLANETS = [
    ('sun', 'Sun', '☉', 'SUN', 'Sol', 'Helios', 'A circle with a dot at its centre. Astronomers still use it in M☉, the mass of the Sun, as a unit.', ''),
    ('moon', 'Moon', '☾', 'LAST QUARTER MOON', 'Luna', 'Selene', 'A crescent. Our moon has no other English name; the moons of other planets have their own names.', ''),
    ('mercury', 'Mercury', '☿', 'MERCURY', 'Mercury, messenger of the gods', 'Hermes', 'The fastest planet, round the Sun in 88 days, so it bears the messenger’s name; the symbol is his staff.', 'Me'),
    ('venus', 'Venus', '♀', 'FEMALE SIGN', 'Venus, goddess of love and beauty', 'Aphrodite', 'The brightest planet. Its symbol, often read as a hand mirror, became the biologists’ sign for female.', 'V'),
    ('earth', 'Earth', '♁', 'EARTH', 'Terra (Tellus)', 'Gaia', 'The only planet whose English name comes from neither myth: Old English eorþe, “ground”. In formulas the circled cross ⊕ is used, as in M⊕.', 'E'),
    ('mars', 'Mars', '♂', 'MALE SIGN', 'Mars, god of war', 'Ares', 'Its blood-red colour suited the god of war. Its symbol, a shield and spear, became the sign for male.', 'Ma'),
    ('jupiter', 'Jupiter', '♃', 'JUPITER', 'Jupiter, king of the gods', 'Zeus', 'The largest planet takes the name of the chief god.', 'J'),
    ('saturn', 'Saturn', '♄', 'SATURN', 'Saturn, god of sowing, father of Jupiter', 'Kronos', 'The slowest planet known in antiquity, about 29½ years round the Sun; the symbol is his sickle.', 'S'),
    ('uranus', 'Uranus', '♅', 'URANUS', 'none: the name is Greek', 'Ouranos, the sky, father of Kronos', 'Found by William Herschel in 1781, who called it Georgium Sidus after King George III. Johann Bode proposed Uranus, completing the line sky → Saturn → Jupiter. It is the only planet named after a Greek god.', 'U'),
    ('neptune', 'Neptune', '♆', 'NEPTUNE', 'Neptune, god of the sea', 'Poseidon', 'Found by Johann Galle in Berlin on 23 September 1846, close to the position Urbain Le Verrier had calculated from the pull it exerted on Uranus. The symbol is the sea god’s trident.', 'N'),
    ('pluto', 'Pluto', '♇', 'PLUTO', 'Pluto, god of the underworld', 'Hades', 'Found by Clyde Tombaugh in 1930; the name was suggested by Venetia Burney, aged 11. The IAU made it a dwarf planet in 2006.', 'P'),
]
# NASA Planetary Fact Sheet (updated 18 March 2025): (key, diameter km, mass 10^24 kg, sidereal orbit period days, moons)
FACTS = {
    'mercury': (4879, 0.330, 88.0, 0), 'venus': (12104, 4.87, 224.7, 0), 'earth': (12756, 5.97, 365.2, 1), 'mars': (6792, 0.642, 687.0, 2),
    'jupiter': (142984, 1898, 4331, 95), 'saturn': (120536, 568, 10747, 274), 'uranus': (51118, 86.8, 30589, 28), 'neptune': (49528, 102, 59800, 16),
}
# Astronomical words the old handbooks wrote as symbols (IAU 1989 says: write the word)
ASPECTS = [
    ('☌', 'CONJUNCTION', 'Conjunction', 'Two bodies at the same ecliptic longitude as seen from Earth. A planet in conjunction with the Sun is lost in its glare.'),
    ('☍', 'OPPOSITION', 'Opposition', 'An outer planet opposite the Sun in the sky: closest to Earth, brightest, and up all night.'),
    ('□', 'WHITE SQUARE', 'Quadrature', 'An outer planet 90° from the Sun, due south at sunrise or sunset.'),
    ('', '', 'Greatest elongation', 'An inner planet (Mercury or Venus) at its greatest angle from the Sun: about 18–28° for Mercury, 45–47° for Venus.'),
]

# The 88 constellations (IAU names and three-letter abbreviations)
CONSTELLATIONS = {
    'And': 'Andromeda', 'Ant': 'Antlia', 'Aps': 'Apus', 'Aqr': 'Aquarius', 'Aql': 'Aquila', 'Ara': 'Ara', 'Ari': 'Aries', 'Aur': 'Auriga',
    'Boo': 'Boötes', 'Cae': 'Caelum', 'Cam': 'Camelopardalis', 'Cnc': 'Cancer', 'CVn': 'Canes Venatici', 'CMa': 'Canis Major', 'CMi': 'Canis Minor',
    'Cap': 'Capricornus', 'Car': 'Carina', 'Cas': 'Cassiopeia', 'Cen': 'Centaurus', 'Cep': 'Cepheus', 'Cet': 'Cetus', 'Cha': 'Chamaeleon',
    'Cir': 'Circinus', 'Col': 'Columba', 'Com': 'Coma Berenices', 'CrA': 'Corona Australis', 'CrB': 'Corona Borealis', 'Crv': 'Corvus',
    'Crt': 'Crater', 'Cru': 'Crux', 'Cyg': 'Cygnus', 'Del': 'Delphinus', 'Dor': 'Dorado', 'Dra': 'Draco', 'Equ': 'Equuleus', 'Eri': 'Eridanus',
    'For': 'Fornax', 'Gem': 'Gemini', 'Gru': 'Grus', 'Her': 'Hercules', 'Hor': 'Horologium', 'Hya': 'Hydra', 'Hyi': 'Hydrus', 'Ind': 'Indus',
    'Lac': 'Lacerta', 'Leo': 'Leo', 'LMi': 'Leo Minor', 'Lep': 'Lepus', 'Lib': 'Libra', 'Lup': 'Lupus', 'Lyn': 'Lynx', 'Lyr': 'Lyra',
    'Men': 'Mensa', 'Mic': 'Microscopium', 'Mon': 'Monoceros', 'Mus': 'Musca', 'Nor': 'Norma', 'Oct': 'Octans', 'Oph': 'Ophiuchus',
    'Ori': 'Orion', 'Pav': 'Pavo', 'Peg': 'Pegasus', 'Per': 'Perseus', 'Phe': 'Phoenix', 'Pic': 'Pictor', 'Psc': 'Pisces', 'PsA': 'Piscis Austrinus',
    'Pup': 'Puppis', 'Pyx': 'Pyxis', 'Ret': 'Reticulum', 'Sge': 'Sagitta', 'Sgr': 'Sagittarius', 'Sco': 'Scorpius', 'Scl': 'Sculptor',
    'Sct': 'Scutum', 'Ser': 'Serpens', 'Sex': 'Sextans', 'Tau': 'Taurus', 'Tel': 'Telescopium', 'Tri': 'Triangulum', 'TrA': 'Triangulum Australe',
    'Tuc': 'Tucana', 'UMa': 'Ursa Major', 'UMi': 'Ursa Minor', 'Vel': 'Vela', 'Vir': 'Virgo', 'Vol': 'Volans', 'Vul': 'Vulpecula',
}
# The twelve signs: 30° divisions of the ecliptic counted from the March equinox (name, symbol, Unicode name)
SIGNS = [('Aries', '♈', 'ARIES'), ('Taurus', '♉', 'TAURUS'), ('Gemini', '♊', 'GEMINI'), ('Cancer', '♋', 'CANCER'),
         ('Leo', '♌', 'LEO'), ('Virgo', '♍', 'VIRGO'), ('Libra', '♎', 'LIBRA'), ('Scorpius', '♏', 'SCORPIUS'),
         ('Sagittarius', '♐', 'SAGITTARIUS'), ('Capricornus', '♑', 'CAPRICORN'), ('Aquarius', '♒', 'AQUARIUS'), ('Pisces', '♓', 'PISCES')]

# Ports for the sailing page (approximate harbour positions, 0.01°)
PORTS = [
    ('Southampton', 50.90, -1.40), ('Lisbon', 38.70, -9.15), ('Reykjavík', 64.15, -21.94), ('New York', 40.70, -74.02),
    ('Panama (Balboa)', 8.95, -79.57), ('Rio de Janeiro', -22.90, -43.17), ('Valparaíso', -33.03, -71.63), ('Cape Town', -33.91, 18.43),
    ('Mumbai', 18.94, 72.84), ('Singapore', 1.26, 103.84), ('Yokohama', 35.45, 139.65), ('Sydney', -33.86, 151.21),
    ('Wellington', -41.28, 174.78), ('Honolulu', 21.31, -157.87), ('San Francisco', 37.80, -122.42),
]
ROUTES = [('Yokohama', 'San Francisco'), ('New York', 'Southampton'), ('Cape Town', 'Sydney'), ('Valparaíso', 'Wellington'), ('Lisbon', 'Rio de Janeiro')]


def zone_letter(zd):
    """Nautical/military zone letter for a zone description (the hours you add to zone time to get UTC).
    East longitudes have negative descriptions: −1 to −12 = A to M (no J); west: +1 to +12 = N to Y; 0 = Z."""
    if zd == 0:
        return 'Z'
    if zd < 0:
        return 'ABCDEFGHIKLM'[-zd - 1]
    return 'NOPQRSTUVWXY'[zd - 1]
