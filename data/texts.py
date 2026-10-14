"""Page text for the Measure room. Plain statements of fact; each topic page also prints
the unit table with sources, so claims here stay general and checkable."""

KIND_PAGES = {
    'length': {
        'lede': 'Since 1983 the metre has been defined by the speed of light, and since 1959 the inch, foot, yard and mile have been '
                'defined as exact fractions of the metre. Every length unit below is therefore exact unless it is marked otherwise.',
        'then': 'Before the 1959 agreement the American and British inches differed slightly, and the US kept a separate survey foot '
                '(1200/3937 m) for land measurement until 2023. Nautical miles also differed: Britain used 6080 feet until 1970.',
        'pair': ('nmi', 'km'),
    },
    'mass': {
        'lede': 'The kilogram is fixed by the Planck constant (2019). The pound has been exactly 0.453 592 37 kg since 1959, and the '
                'grain, 1/7000 pound, is shared by the avoirdupois, troy and apothecaries’ systems, which is how those three relate.',
        'then': 'For 130 years the kilogram was the mass of one metal cylinder kept near Paris; copies drifted from it by tens of '
                'micrograms. The carat once varied by country between about 188 and 213 mg before settling on 200 mg.',
        'pair': ('lb', 'kg'),
    },
    'area': {
        'lede': 'Areas are squares of lengths, so every area unit here is exact once its length is. The acre is a chain by a furlong '
                '(66 by 660 feet): a strip of ploughland one furlong long.',
        'then': 'Land measures varied from place to place for centuries; the rood and the square perch survive only in old deeds.',
        'pair': ('acre', 'ha'),
    },
    'volume': {
        'lede': 'The litre is exactly one cubic decimetre. The US gallon (231 cubic inches) and the imperial gallon (4.546 09 L) are '
                'different units with the same name: an imperial gallon is about 1.2 US gallons, and so are its pints and quarts.',
        'then': 'The US gallon is the English wine gallon of 1707; Britain replaced its wine, ale and corn gallons with the imperial '
                'gallon in 1824. Casks such as the hogshead meant different volumes for wine and for beer, and the litre itself was '
                'about 28 parts per million larger from 1901 to 1964.',
        'pair': ('galus', 'L'),
    },
    'speed': {
        'lede': 'Speed is length over time. The knot is one nautical mile per hour, exactly 1852/3600 m/s, which is why it is the '
                'natural unit wherever positions are given in degrees and minutes of latitude.',
        'then': 'The name comes from the log line: a line knotted at regular intervals was paid out astern and the knots counted '
                'against a sand-glass.',
        'pair': ('kn', 'kmh'),
    },
    'force': {
        'lede': 'A force is mass times acceleration; the newton is 1 kg m/s². The kilogram-force and pound-force are the weights of '
                '1 kg and 1 lb under standard gravity, 9.806 65 m/s², a conventional value adopted in 1901.',
        'then': 'Engineering once measured force in kilograms and pounds, which blurs mass and weight; the SI keeps them apart.',
        'pair': ('lbf', 'N'),
    },
    'pressure': {
        'lede': 'Pressure is force per area; the pascal is 1 N/m². Weather maps use hectopascals (equal to millibars), medicine uses '
                'millimetres of mercury, and tyre gauges in the US use pounds per square inch.',
        'then': 'Mercury columns gave the old units their names: the torr and the conventional millimetre of mercury differ by about '
                'one part in seven million.',
        'pair': ('psi', 'kPa'),
    },
    'energy': {
        'lede': 'Energy, work and heat share one unit, the joule. The calorie comes in two exact versions (4.184 J and 4.1868 J), and '
                'the food Calorie is a kilocalorie.',
        'then': 'Heat was measured as warmth given to water long before it was understood as energy; the calorie and the British '
                'thermal unit come from that time.',
        'pair': ('kWh', 'kJ'),
    },
    'power': {
        'lede': 'Power is energy per time; the watt is 1 J/s. The horsepower comes from James Watt’s figure of 33 000 foot-pounds '
                'per minute for a working horse; the metric horsepower is a slightly smaller, rounded metric version.',
        'then': 'Car engines in Europe were rated in PS (metric horsepower) and in the US in hp; both are now officially given in kW.',
        'pair': ('hp', 'kW'),
    },
    'temperature': {
        'lede': 'Temperature scales are not simple multiples of each other: they have different zeros. The kelvin starts at absolute '
                'zero, the Celsius degree is the same size with its zero at 273.15 K, and the Fahrenheit degree is 5/9 as large.',
        'then': 'Anders Celsius’s scale of 1742 ran backwards, with 0 at boiling and 100 at freezing; it was reversed soon after '
                'his death. Since 2019 the kelvin is fixed through the Boltzmann constant rather than the triple point of water.',
        'pair': ('degF', 'degC'),
    },
}

SYSTEM_ORDER = ['SI', 'SI (accepted)', 'Metric', 'Metric (accepted)', 'Imperial / US', 'US', 'Imperial', 'Avoirdupois', 'Troy',
                'Apothecaries’', 'Gemstones', 'US liquid', 'US kitchen', 'US apothecaries’', 'US dry', 'Imperial dry',
                'Nautical', 'Surveying', 'US surveying', 'Old English', 'Typography', 'Timber', 'Shipping', 'Oil industry',
                'Wine casks', 'Beer casks', 'Astronomy', 'Electricity', 'Chemistry', 'Engineering', 'Nutrition', 'Medicine',
                'Aviation / weather', 'US engineering', 'Gravitational metric', 'Conventional', 'CGS']
