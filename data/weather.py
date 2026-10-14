"""Weather room data. Beaufort scale (WMO; speeds and probable wave heights as published
by WMO and national services), WMO sea-state code 3700, swell (Douglas) scale, marine
visibility terms, Saffir-Simpson hurricane wind scale, tropical cyclone basins."""

# force, name, knots (lo, hi), m/s (lo, hi), probable wave height m (typical, max) or None, sea, land
BEAUFORT = [
    (0, 'Calm', (0, 0), (0.0, 0.2), None, 'Sea like a mirror.', 'Smoke rises straight up.'),
    (1, 'Light air', (1, 3), (0.3, 1.5), (0.1, 0.1), 'Ripples like scales, no foam crests.', 'Smoke drifts; vanes do not move.'),
    (2, 'Light breeze', (4, 6), (1.6, 3.3), (0.2, 0.3), 'Small wavelets with glassy crests that do not break.', 'Wind felt on the face; leaves rustle.'),
    (3, 'Gentle breeze', (7, 10), (3.4, 5.4), (0.6, 1.0), 'Large wavelets; crests begin to break; scattered white horses.', 'Leaves and twigs in constant motion; light flags extended.'),
    (4, 'Moderate breeze', (11, 16), (5.5, 7.9), (1.0, 1.5), 'Small waves becoming longer; fairly frequent white horses.', 'Dust and loose paper lifted; small branches move.'),
    (5, 'Fresh breeze', (17, 21), (8.0, 10.7), (2.0, 2.5), 'Moderate, longer waves; many white horses; some spray.', 'Small trees in leaf begin to sway.'),
    (6, 'Strong breeze', (22, 27), (10.8, 13.8), (3.0, 4.0), 'Large waves form; white foam crests everywhere; probably some spray.', 'Large branches move; umbrellas hard to use.'),
    (7, 'Near gale', (28, 33), (13.9, 17.1), (4.0, 5.5), 'Sea heaps up; white foam from breaking waves blown in streaks.', 'Whole trees in motion; hard to walk against the wind.'),
    (8, 'Gale', (34, 40), (17.2, 20.7), (5.5, 7.5), 'Moderately high, longer waves; crests break into spindrift; well-marked foam streaks.', 'Twigs break off trees.'),
    (9, 'Strong gale', (41, 47), (20.8, 24.4), (7.0, 10.0), 'High waves; dense foam streaks; crests topple and roll over; spray may reduce visibility.', 'Slight structural damage; slates blown off.'),
    (10, 'Storm', (48, 55), (24.5, 28.4), (9.0, 12.5), 'Very high waves with long overhanging crests; sea surface white; heavy tumbling; visibility affected.', 'Trees uprooted; considerable structural damage.'),
    (11, 'Violent storm', (56, 63), (28.5, 32.6), (11.5, 16.0), 'Exceptionally high waves that can hide small and medium ships; sea covered in white foam.', 'Widespread damage (rare inland).'),
    (12, 'Hurricane', (64, None), (32.7, None), (14.0, None), 'Air filled with foam and spray; sea completely white; visibility very seriously affected.', 'Devastation.'),
]
# the old names some handbooks used before the WMO names
BEAUFORT_OLD_NAMES = {7: 'Moderate gale', 8: 'Fresh gale', 9: 'Strong gale', 10: 'Whole gale', 11: 'Storm', 12: 'Hurricane'}

# WMO code 3700: state of the sea (total wave height, m)
SEA_STATE = [
    (0, 'Calm (glassy)', 0, 0), (1, 'Calm (rippled)', 0, 0.1), (2, 'Smooth (wavelets)', 0.1, 0.5), (3, 'Slight', 0.5, 1.25),
    (4, 'Moderate', 1.25, 2.5), (5, 'Rough', 2.5, 4), (6, 'Very rough', 4, 6), (7, 'High', 6, 9), (8, 'Very high', 9, 14),
    (9, 'Phenomenal', 14, None),
]
# marine forecast visibility terms (as used in UK shipping forecasts)
VISIBILITY = [
    ('Very poor', 'less than 1000 metres'), ('Poor', '1000 metres to 2 nautical miles'),
    ('Moderate', '2 to 5 nautical miles'), ('Good', 'more than 5 nautical miles'),
]
FOG_TERMS = [
    ('Fog', 'Visibility below 1000 m because of water droplets in the air.'),
    ('Mist', 'Visibility reduced by droplets but still 1000 m or more, with high humidity.'),
    ('Haze', 'Visibility reduced by dry particles such as dust or smoke.'),
]

# Saffir-Simpson hurricane wind scale (1-minute sustained wind): category, knots lo/hi, km/h lo/hi as published by NHC
SAFFIR = [(1, 64, 82, 119, 153), (2, 83, 95, 154, 177), (3, 96, 112, 178, 208), (4, 113, 136, 209, 251), (5, 137, None, 252, None)]

# tropical cyclone basins: name, local term, season, peak, approximate box (lon0, lat0, lon1, lat1)
BASINS = [
    ('North Atlantic', 'hurricane', '1 June to 30 November (official)', 'September', (-100, 8, -15, 40)),
    ('Eastern North Pacific', 'hurricane', '15 May to 30 November', 'August to September', (-140, 8, -85, 28)),
    ('Western North Pacific', 'typhoon', 'all year', 'August to September', (100, 5, 180, 35)),
    ('North Indian Ocean', 'cyclonic storm', 'April to June and October to December', 'May and November', (50, 5, 100, 25)),
    ('South-West Indian Ocean', 'tropical cyclone', 'November to April', 'January to March', (30, -30, 90, -5)),
    ('Australian region', 'tropical cyclone', 'November to April', 'January to March', (90, -30, 160, -5)),
    ('South Pacific', 'tropical cyclone', 'November to April', 'February to March', (160, -30, -120, -5)),
]
