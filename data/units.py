"""Units of measurement with exact definitions.

Each unit's `f` is its size in the coherent SI unit of its kind, as an exact
Fraction whenever the unit is defined exactly (most are, since 1959 and 2019).
`exact` False marks a conventional or approximate value; `status` says whether a
unit is in current use, legal but old, or historical only.

`by` is the human-readable definition chain the site prints ("12 inches",
"231 cubic inches"); tests check that every chain reproduces `f` exactly.
"""
import math
from fractions import Fraction as F

KINDS = {
    'length': {'si': 'm', 'name': 'Length', 'unit': 'metre'},
    'mass': {'si': 'kg', 'name': 'Mass', 'unit': 'kilogram'},
    'area': {'si': 'm²', 'name': 'Area', 'unit': 'square metre'},
    'volume': {'si': 'm³', 'name': 'Volume', 'unit': 'cubic metre'},
    'speed': {'si': 'm/s', 'name': 'Speed', 'unit': 'metre per second'},
    'force': {'si': 'N', 'name': 'Force', 'unit': 'newton'},
    'pressure': {'si': 'Pa', 'name': 'Pressure', 'unit': 'pascal'},
    'energy': {'si': 'J', 'name': 'Energy', 'unit': 'joule'},
    'power': {'si': 'W', 'name': 'Power', 'unit': 'watt'},
    'temperature': {'si': 'K', 'name': 'Temperature', 'unit': 'kelvin'},
}

# exact building blocks
IN = F(254, 10000)              # inch, 1959
FT = 12 * IN
YD = 3 * FT
MI = 5280 * FT
NMI = F(1852)
LB = F(45359237, 100000000)     # pound, 1959
GR = LB / 7000
OZ = LB / 16
G0 = F(980665, 100000)          # standard gravity, m/s² (CGPM 1901)
LBF = LB * G0
KGF = G0
GAL_US = 231 * IN ** 3
GAL_IMP = F(454609, 100000000)  # 4.546 09 L, UK 1985
BU_US = F(215042, 100) * IN ** 3
CAL_TH = F(4184, 1000)
CAL_IT = F(41868, 10000)
MMHG = F(133322387415, 1000000000)   # conventional millimetre of mercury
ATM = F(101325)


def U(id, name, kind, f, by, src, exact=True, status='current', sym='', note='', system=''):
    return {'id': id, 'name': name, 'kind': kind, 'f': F(f), 'by': by, 'src': src, 'exact': exact,
            'status': status, 'sym': sym, 'note': note, 'system': system}


UNITS = [
    # ---------------------------------------------------------------- length
    U('m', 'metre', 'length', 1, 'SI base unit: the length light travels in vacuum in 1/299 792 458 s', 'si', sym='m', system='SI'),
    U('km', 'kilometre', 'length', 1000, '1000 m', 'si', sym='km', system='SI'),
    U('cm', 'centimetre', 'length', F(1, 100), '1/100 m', 'si', sym='cm', system='SI'),
    U('mm', 'millimetre', 'length', F(1, 1000), '1/1000 m', 'si', sym='mm', system='SI'),
    U('um', 'micrometre', 'length', F(1, 10 ** 6), '10⁻⁶ m (once called the micron)', 'si', sym='µm', system='SI'),
    U('in', 'inch', 'length', IN, 'exactly 25.4 mm', 'yp1959', sym='in', system='Imperial / US',
      note='Before 1959 the US inch was 1/39.37 m and the British inch differed in the sixth figure.'),
    U('ft', 'foot', 'length', FT, '12 inches = 0.3048 m', 'yp1959', sym='ft', system='Imperial / US'),
    U('yd', 'yard', 'length', YD, '3 feet = 0.9144 m', 'yp1959', sym='yd', system='Imperial / US'),
    U('mi', 'mile (statute)', 'length', MI, '5280 feet = 1609.344 m', 'yp1959', sym='mi', system='Imperial / US'),
    U('thou', 'thou (mil)', 'length', IN / 1000, '1/1000 inch', 'nisthb44', sym='mil', system='Imperial / US'),
    U('line', 'line', 'length', IN / 12, '1/12 inch', 'nisthb44', status='historical', system='Imperial / US'),
    U('pt', 'point (desktop publishing)', 'length', IN / 72, '1/72 inch', 'nist811', sym='pt', system='Typography',
      note='Older printers’ points were slightly smaller (about 1/72.27 inch).'),
    U('palm', 'palm', 'length', 3 * IN, '3 inches', 'nisthb44', status='historical', system='Old English'),
    U('hand', 'hand', 'length', 4 * IN, '4 inches (still used for the height of horses)', 'nisthb44', system='Old English'),
    U('nail', 'nail (cloth)', 'length', F(9, 4) * IN, '2¼ inches = 1/16 yard', 'nisthb44', status='historical', system='Old English'),
    U('span', 'span', 'length', 9 * IN, '9 inches', 'nisthb44', status='historical', system='Old English'),
    U('cubit', 'cubit', 'length', 18 * IN, '18 inches (traditional English value)', 'nisthb44', exact=False, status='historical',
      system='Old English', note='The cubit varied widely between peoples and periods.'),
    U('link', 'link (Gunter’s)', 'length', F(66, 100) * FT, '7.92 inches = 1/100 chain', 'nisthb44', status='historical', system='Surveying'),
    U('rod', 'rod (pole, perch)', 'length', F(33, 2) * FT, '16½ feet', 'nisthb44', status='historical', system='Surveying'),
    U('chain', 'chain (Gunter’s)', 'length', 66 * FT, '66 feet = 4 rods = 100 links', 'nisthb44', status='historical', system='Surveying'),
    U('furlong', 'furlong', 'length', 660 * FT, '10 chains = 220 yards', 'nisthb44', system='Surveying', note='Still used in horse racing.'),
    U('pace', 'pace (military)', 'length', F(5, 2) * FT, '2½ feet', 'nisthb44', exact=False, status='historical', system='Old English'),
    U('league', 'league (statute)', 'length', 3 * MI, '3 statute miles', 'nisthb44', status='historical', system='Old English'),
    U('usft', 'US survey foot', 'length', F(1200, 3937), '1200/3937 m', 'usft', status='obsolete', system='US surveying',
      note='Withdrawn on 1 January 2023; it was 2 parts in a million longer than the international foot.'),
    U('fathom', 'fathom', 'length', 6 * FT, '6 feet = 1.8288 m', 'nisthb44', sym='ftm', system='Nautical'),
    U('shackle', 'shackle (of anchor cable)', 'length', 90 * FT, '15 fathoms = 90 feet', 'nisthb44', system='Nautical'),
    U('cable', 'cable (international)', 'length', NMI / 10, '1/10 international nautical mile = 185.2 m', 'iho', system='Nautical',
      note='The British cable was 608 feet (1/10 of the old Admiralty mile); the US Navy cable was 120 fathoms.'),
    U('nmi', 'nautical mile', 'length', NMI, 'exactly 1852 m', 'iho', sym='NM', system='Nautical',
      note='Chosen as close to one minute of latitude, which varies from about 1843 m at the equator to 1862 m at the poles.'),
    U('admmi', 'Admiralty nautical mile', 'length', 6080 * FT, '6080 feet = 1853.184 m', 'nisthb44', status='obsolete', system='Nautical',
      note='Used in Britain until 1970.'),
    U('usnmi', 'US nautical mile (before 1954)', 'length', F(185324800, 100000), '1853.248 m', 'nisthb44', status='obsolete', system='Nautical'),
    U('geomi', 'geographical mile', 'length', F(2 * math.pi * 6378137 / 21600).limit_denominator(10 ** 6),
      'one minute of longitude on the equator of the WGS 84 ellipsoid, about 1855.32 m', 'wgs84', exact=False,
      status='historical', system='Nautical'),
    U('nleague', 'league (nautical)', 'length', 3 * NMI, '3 nautical miles', 'nisthb44', status='historical', system='Nautical'),
    U('au', 'astronomical unit', 'length', 149597870700, 'exactly 149 597 870 700 m', 'iau2012', sym='au', system='Astronomy'),

    # ---------------------------------------------------------------- mass
    U('kg', 'kilogram', 'mass', 1, 'SI base unit: fixed by the Planck constant h = 6.626 070 15 × 10⁻³⁴ J s', 'si', sym='kg', system='SI'),
    U('g', 'gram', 'mass', F(1, 1000), '1/1000 kg', 'si', sym='g', system='SI'),
    U('mg', 'milligram', 'mass', F(1, 10 ** 6), '1/1000 g', 'si', sym='mg', system='SI'),
    U('t', 'tonne (metric ton)', 'mass', 1000, '1000 kg', 'si', sym='t', system='SI (accepted)'),
    U('gr', 'grain', 'mass', GR, '64.798 91 mg = 1/7000 pound', 'yp1959', sym='gr', system='Imperial / US',
      note='The grain is shared by the avoirdupois, troy and apothecaries’ systems.'),
    U('dr', 'dram (avoirdupois)', 'mass', OZ / 16, '1/16 ounce = 27.343 75 grains', 'nisthb44', sym='dr', system='Avoirdupois'),
    U('oz', 'ounce (avoirdupois)', 'mass', OZ, '1/16 pound = 437.5 grains', 'yp1959', sym='oz', system='Avoirdupois'),
    U('lb', 'pound (avoirdupois)', 'mass', LB, 'exactly 0.453 592 37 kg = 7000 grains', 'yp1959', sym='lb', system='Avoirdupois'),
    U('st', 'stone', 'mass', 14 * LB, '14 pounds', 'wma1985', sym='st', system='Imperial'),
    U('qtr', 'quarter (British)', 'mass', 28 * LB, '28 pounds', 'nisthb44', status='historical', system='Imperial'),
    U('cwt', 'hundredweight (long)', 'mass', 112 * LB, '112 pounds', 'nisthb44', sym='cwt', system='Imperial'),
    U('scwt', 'hundredweight (short)', 'mass', 100 * LB, '100 pounds', 'nisthb44', system='US'),
    U('lton', 'ton (long)', 'mass', 2240 * LB, '2240 pounds = 20 long hundredweight', 'nisthb44', system='Imperial'),
    U('ston', 'ton (short)', 'mass', 2000 * LB, '2000 pounds', 'nisthb44', system='US'),
    U('ozt', 'troy ounce', 'mass', 480 * GR, '480 grains = 31.103 476 8 g', 'nisthb44', sym='oz t', system='Troy',
      note='Precious metals are still priced by the troy ounce.'),
    U('dwt', 'pennyweight', 'mass', 24 * GR, '24 grains', 'nisthb44', sym='dwt', system='Troy'),
    U('lbt', 'troy pound', 'mass', 5760 * GR, '12 troy ounces = 5760 grains', 'nisthb44', status='historical', system='Troy'),
    U('scruple', 'scruple', 'mass', 20 * GR, '20 grains', 'nisthb44', status='historical', system='Apothecaries’'),
    U('drap', 'dram (apothecaries’)', 'mass', 60 * GR, '3 scruples = 60 grains', 'nisthb44', status='historical', system='Apothecaries’'),
    U('ct', 'carat (metric)', 'mass', F(2, 10000), 'exactly 200 mg', 'nisthb44', sym='ct', system='Gemstones',
      note='Before the metric carat (1907 onward) the carat varied from about 188 to 213 mg by country.'),
    U('slug', 'slug', 'mass', LBF / FT, 'the mass that 1 pound-force accelerates at 1 ft/s²', 'nist811', status='historical', system='US engineering'),

    # ---------------------------------------------------------------- area
    U('m2', 'square metre', 'area', 1, '1 m × 1 m', 'si', sym='m²', system='SI'),
    U('cm2', 'square centimetre', 'area', F(1, 10 ** 4), '1 cm × 1 cm', 'si', sym='cm²', system='SI'),
    U('km2', 'square kilometre', 'area', 10 ** 6, '1 km × 1 km', 'si', sym='km²', system='SI'),
    U('are', 'are', 'area', 100, '100 m²', 'si', sym='a', system='Metric'),
    U('ha', 'hectare', 'area', 10 ** 4, '100 ares = 10 000 m²', 'si', sym='ha', system='Metric (accepted)'),
    U('in2', 'square inch', 'area', IN ** 2, '1 in × 1 in', 'nisthb44', sym='in²', system='Imperial / US'),
    U('ft2', 'square foot', 'area', FT ** 2, '144 square inches', 'nisthb44', sym='ft²', system='Imperial / US'),
    U('yd2', 'square yard', 'area', YD ** 2, '9 square feet', 'nisthb44', sym='yd²', system='Imperial / US'),
    U('rod2', 'square rod (perch)', 'area', (F(33, 2) * FT) ** 2, '30¼ square yards', 'nisthb44', status='historical', system='Surveying'),
    U('rood', 'rood', 'area', 10890 * FT ** 2, '1/4 acre = 40 square rods', 'nisthb44', status='historical', system='Surveying'),
    U('acre', 'acre', 'area', 43560 * FT ** 2, '43 560 square feet = 160 square rods', 'nisthb44', sym='ac', system='Imperial / US'),
    U('mi2', 'square mile', 'area', MI ** 2, '640 acres', 'nisthb44', sym='mi²', system='Imperial / US'),

    # ---------------------------------------------------------------- volume
    U('m3', 'cubic metre', 'volume', 1, '1 m × 1 m × 1 m', 'si', sym='m³', system='SI'),
    U('L', 'litre', 'volume', F(1, 1000), 'exactly 1 dm³ (since 1964)', 'si', sym='L', system='SI (accepted)',
      note='From 1901 to 1964 the litre was the volume of 1 kg of water, about 1.000 028 dm³.'),
    U('mL', 'millilitre', 'volume', F(1, 10 ** 6), '1/1000 L = 1 cm³', 'si', sym='mL', system='SI (accepted)'),
    U('in3', 'cubic inch', 'volume', IN ** 3, '1 in × 1 in × 1 in', 'nisthb44', sym='in³', system='Imperial / US'),
    U('ft3', 'cubic foot', 'volume', FT ** 3, '1728 cubic inches', 'nisthb44', sym='ft³', system='Imperial / US'),
    U('yd3', 'cubic yard', 'volume', YD ** 3, '27 cubic feet', 'nisthb44', sym='yd³', system='Imperial / US'),
    U('bdft', 'board foot', 'volume', 144 * IN ** 3, '144 cubic inches (1 ft × 1 ft × 1 in of timber)', 'nisthb44', system='Timber'),
    U('cord', 'cord (of wood)', 'volume', 128 * FT ** 3, '128 cubic feet (a stack 8 × 4 × 4 ft)', 'nisthb44', system='Timber'),
    U('regton', 'register ton', 'volume', 100 * FT ** 3, '100 cubic feet of enclosed ship space', 'nisthb44', status='historical', system='Shipping',
      note='Replaced for ship measurement by the dimensionless gross tonnage of the 1969 Tonnage Convention.'),
    U('frton', 'freight ton (measurement ton)', 'volume', 40 * FT ** 3, '40 cubic feet', 'nisthb44', status='historical', system='Shipping'),
    U('galus', 'US gallon', 'volume', GAL_US, '231 cubic inches = 3.785 411 784 L', 'nisthb44', sym='gal', system='US liquid',
      note='231 in³ is the old English wine gallon of 1707, kept by the United States.'),
    U('qtus', 'US quart', 'volume', GAL_US / 4, '1/4 US gallon', 'nisthb44', sym='qt', system='US liquid'),
    U('ptus', 'US pint', 'volume', GAL_US / 8, '1/8 US gallon', 'nisthb44', sym='pt', system='US liquid'),
    U('cupus', 'US cup', 'volume', GAL_US / 16, '8 US fluid ounces', 'nisthb44', system='US liquid'),
    U('gius', 'US gill', 'volume', GAL_US / 32, '4 US fluid ounces', 'nisthb44', status='historical', system='US liquid'),
    U('flozus', 'US fluid ounce', 'volume', GAL_US / 128, '1/128 US gallon', 'nisthb44', sym='fl oz', system='US liquid'),
    U('tbsp', 'tablespoon (US)', 'volume', GAL_US / 256, '1/2 US fluid ounce', 'nisthb44', sym='tbsp', system='US kitchen'),
    U('tsp', 'teaspoon (US)', 'volume', GAL_US / 768, '1/3 tablespoon', 'nisthb44', sym='tsp', system='US kitchen'),
    U('drus', 'US fluid dram', 'volume', GAL_US / 1024, '1/8 US fluid ounce', 'nisthb44', status='historical', system='US apothecaries’'),
    U('minim', 'minim (US)', 'volume', GAL_US / 61440, '1/60 US fluid dram', 'nisthb44', status='historical', system='US apothecaries’'),
    U('bbl', 'barrel (petroleum)', 'volume', 42 * GAL_US, '42 US gallons', 'nisthb44', sym='bbl', system='Oil industry'),
    U('buus', 'US bushel', 'volume', BU_US, '2150.42 cubic inches (the old Winchester bushel)', 'nisthb44', sym='bu', system='US dry'),
    U('pkus', 'US peck', 'volume', BU_US / 4, '1/4 US bushel', 'nisthb44', sym='pk', system='US dry'),
    U('dqtus', 'US dry quart', 'volume', BU_US / 32, '1/32 US bushel', 'nisthb44', system='US dry'),
    U('galimp', 'imperial gallon', 'volume', GAL_IMP, 'exactly 4.546 09 L', 'wma1985', sym='gal', system='Imperial',
      note='Defined in 1824 as the volume of 10 lb of water; fixed in litres in 1985.'),
    U('qtimp', 'imperial quart', 'volume', GAL_IMP / 4, '1/4 imperial gallon', 'wma1985', system='Imperial'),
    U('ptimp', 'imperial pint', 'volume', GAL_IMP / 8, '1/8 imperial gallon = 568.261 25 mL', 'wma1985', sym='pt', system='Imperial'),
    U('giimp', 'imperial gill', 'volume', GAL_IMP / 32, '1/4 imperial pint', 'wma1985', system='Imperial'),
    U('flozimp', 'imperial fluid ounce', 'volume', GAL_IMP / 160, '1/20 imperial pint', 'wma1985', system='Imperial'),
    U('pkimp', 'imperial peck', 'volume', 2 * GAL_IMP, '2 imperial gallons', 'nisthb44', status='historical', system='Imperial dry'),
    U('buimp', 'imperial bushel', 'volume', 8 * GAL_IMP, '8 imperial gallons', 'nisthb44', system='Imperial dry'),
    U('wtun', 'tun (wine)', 'volume', 252 * GAL_US, '252 wine gallons of 231 in³', 'nisthb44', status='historical', system='Wine casks'),
    U('wpipe', 'pipe or butt (wine)', 'volume', 126 * GAL_US, '126 wine gallons', 'nisthb44', status='historical', system='Wine casks'),
    U('wpunch', 'puncheon (wine)', 'volume', 84 * GAL_US, '84 wine gallons', 'nisthb44', status='historical', system='Wine casks'),
    U('whhd', 'hogshead (wine)', 'volume', 63 * GAL_US, '63 wine gallons', 'nisthb44', status='historical', system='Wine casks'),
    U('wtierce', 'tierce (wine)', 'volume', 42 * GAL_US, '42 wine gallons', 'nisthb44', status='historical', system='Wine casks'),
    U('wbbl', 'barrel (wine)', 'volume', F(63, 2) * GAL_US, '31½ wine gallons', 'nisthb44', status='historical', system='Wine casks'),
    U('bbutt', 'butt (beer)', 'volume', 108 * GAL_IMP, '108 imperial gallons', 'nisthb44', status='historical', system='Beer casks'),
    U('bhhd', 'hogshead (beer)', 'volume', 54 * GAL_IMP, '54 imperial gallons', 'nisthb44', status='historical', system='Beer casks'),
    U('bbbl', 'barrel (beer)', 'volume', 36 * GAL_IMP, '36 imperial gallons', 'nisthb44', status='historical', system='Beer casks'),
    U('kild', 'kilderkin', 'volume', 18 * GAL_IMP, '18 imperial gallons', 'nisthb44', status='historical', system='Beer casks'),
    U('firkin', 'firkin', 'volume', 9 * GAL_IMP, '9 imperial gallons', 'nisthb44', status='historical', system='Beer casks'),
    U('pin', 'pin', 'volume', F(9, 2) * GAL_IMP, '4½ imperial gallons', 'nisthb44', status='historical', system='Beer casks'),

    # ---------------------------------------------------------------- speed
    U('mps', 'metre per second', 'speed', 1, '1 m in 1 s', 'si', sym='m/s', system='SI'),
    U('kmh', 'kilometre per hour', 'speed', F(1000, 3600), '1000 m in 3600 s', 'si', sym='km/h', system='SI (accepted)'),
    U('mph', 'mile per hour', 'speed', MI / 3600, '1 statute mile in 1 hour', 'nisthb44', sym='mph', system='Imperial / US'),
    U('fps', 'foot per second', 'speed', FT, '1 foot in 1 s', 'nist811', sym='ft/s', system='Imperial / US'),
    U('kn', 'knot', 'speed', NMI / 3600, '1 nautical mile per hour', 'iho', sym='kn', system='Nautical',
      note='A speed, never a distance: “knots per hour” is wrong.'),

    # ---------------------------------------------------------------- force
    U('N', 'newton', 'force', 1, '1 kg · m/s²', 'si', sym='N', system='SI'),
    U('kgf', 'kilogram-force', 'force', KGF, '9.806 65 N (1 kg under standard gravity)', 'nist811', sym='kgf', status='historical', system='Gravitational metric'),
    U('lbf', 'pound-force', 'force', LBF, '4.448 221 615 260 5 N (1 lb under standard gravity)', 'nist811', sym='lbf', system='US engineering'),
    U('dyn', 'dyne', 'force', F(1, 10 ** 5), '1 g · cm/s²', 'nist811', sym='dyn', status='historical', system='CGS'),

    # ---------------------------------------------------------------- pressure
    U('Pa', 'pascal', 'pressure', 1, '1 N/m²', 'si', sym='Pa', system='SI'),
    U('kPa', 'kilopascal', 'pressure', 1000, '1000 Pa', 'si', sym='kPa', system='SI'),
    U('bar', 'bar', 'pressure', 10 ** 5, '100 000 Pa', 'si', sym='bar', system='Metric'),
    U('atm', 'standard atmosphere', 'pressure', ATM, 'exactly 101 325 Pa', 'nist811', sym='atm', system='Conventional'),
    U('torr', 'torr', 'pressure', ATM / 760, '1/760 standard atmosphere', 'nist811', sym='Torr', system='Conventional'),
    U('mmHg', 'millimetre of mercury', 'pressure', MMHG, '133.322 387 415 Pa (conventional)', 'nist811', sym='mmHg', system='Medicine',
      note='Still used for blood pressure. It differs from the torr in the seventh figure.'),
    U('inHg', 'inch of mercury', 'pressure', MMHG * F(254, 10), '25.4 conventional millimetres of mercury', 'nist811', sym='inHg', system='Aviation / weather'),
    U('psi', 'pound per square inch', 'pressure', LBF / IN ** 2, '1 pound-force on 1 square inch', 'nist811', sym='psi', system='US engineering'),

    # ---------------------------------------------------------------- energy
    U('J', 'joule', 'energy', 1, '1 N · m', 'si', sym='J', system='SI'),
    U('kJ', 'kilojoule', 'energy', 1000, '1000 J', 'si', sym='kJ', system='SI'),
    U('kWh', 'kilowatt-hour', 'energy', 3600000, '1000 W for 3600 s', 'si', sym='kWh', system='Electricity'),
    U('calth', 'calorie (thermochemical)', 'energy', CAL_TH, 'exactly 4.184 J', 'nist811', sym='cal', system='Chemistry'),
    U('calIT', 'calorie (International Table)', 'energy', CAL_IT, 'exactly 4.1868 J', 'nist811', sym='cal_IT', system='Engineering'),
    U('kcal', 'kilocalorie (food Calorie)', 'energy', 1000 * CAL_TH, '1000 thermochemical calories', 'nist811', sym='kcal', system='Nutrition',
      note='Food labels usually use the thermochemical value; some use the International Table value.'),
    U('btu', 'British thermal unit (IT)', 'energy', CAL_IT * 1000 * LB * F(5, 9), 'the IT calorie per gram per kelvin, scaled to the pound and degree Fahrenheit', 'nist811', sym='BTU', system='Engineering'),
    U('ftlbf', 'foot-pound', 'energy', FT * LBF, '1 pound-force acting through 1 foot', 'nist811', sym='ft·lbf', system='US engineering'),
    U('erg', 'erg', 'energy', F(1, 10 ** 7), '1 dyne · cm', 'nist811', status='historical', system='CGS'),

    # ---------------------------------------------------------------- power
    U('W', 'watt', 'power', 1, '1 J/s', 'si', sym='W', system='SI'),
    U('kW', 'kilowatt', 'power', 1000, '1000 W', 'si', sym='kW', system='SI'),
    U('hp', 'horsepower (mechanical)', 'power', 550 * FT * LBF, '550 foot-pounds per second', 'nist811', sym='hp', system='Imperial / US'),
    U('PS', 'metric horsepower (cheval vapeur)', 'power', 75 * KGF, '75 kilogram-force metres per second', 'nist811', sym='PS', system='Gravitational metric'),
    U('btuh', 'BTU per hour', 'power', CAL_IT * 1000 * LB * F(5, 9) / 3600, '1 BTU (IT) in 1 hour', 'nist811', sym='BTU/h', system='Engineering'),

    # ---------------------------------------------------------------- temperature (affine: K = f·x + o)
    U('K', 'kelvin', 'temperature', 1, 'SI base unit: fixed by the Boltzmann constant k = 1.380 649 × 10⁻²³ J/K', 'its90', sym='K', system='SI'),
    U('degC', 'degree Celsius', 'temperature', 1, 'T/K = t/°C + 273.15', 'its90', sym='°C', system='SI'),
    U('degF', 'degree Fahrenheit', 'temperature', F(5, 9), 't/°F = 1.8 · t/°C + 32', 'nist811', sym='°F', system='US'),
    U('degR', 'degree Rankine', 'temperature', F(5, 9), 'T/°R = 1.8 · T/K', 'nist811', sym='°R', status='historical', system='US engineering'),
]

# offsets for temperature: K = f * x + OFFSET
TEMP_OFFSET = {'K': F(0), 'degC': F(27315, 100), 'degF': F(27315, 100) - F(5, 9) * 32, 'degR': F(0)}

BY_ID = {u['id']: u for u in UNITS}
