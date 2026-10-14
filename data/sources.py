"""Primary sources. Every unit, constant and rule on the site cites one of these keys.

Only standards bodies, statutes and official publications are listed here. The
syllabus came from scanned reference books; those books are not named anywhere
in this project (project rule), and none of their text or figures is reused.
"""

SOURCES = {
    'si': {
        'short': 'BIPM SI Brochure',
        'title': 'The International System of Units (SI), 9th edition (2019), with later updates',
        'by': 'Bureau International des Poids et Mesures (BIPM)',
        'url': 'https://www.bipm.org/en/publications/si-brochure',
    },
    'cgpm2022': {
        'short': 'CGPM 2022, Res. 3',
        'title': 'Resolution 3 of the 27th General Conference on Weights and Measures (2022): ronna, quetta, ronto, quecto',
        'by': 'CGPM / BIPM',
        'url': 'https://www.bipm.org/en/cgpm-2022/resolution-3',
    },
    'nist811': {
        'short': 'NIST SP 811',
        'title': 'Guide for the Use of the International System of Units (SP 811, 2008), Appendix B: conversion factors',
        'by': 'National Institute of Standards and Technology (NIST)',
        'url': 'https://www.nist.gov/pml/special-publication-811',
    },
    'nisthb44': {
        'short': 'NIST Handbook 44',
        'title': 'Handbook 44, Appendix C: General Tables of Units of Measurement',
        'by': 'National Institute of Standards and Technology (NIST)',
        'url': 'https://www.nist.gov/pml/owm/nist-handbook-44-current-edition',
    },
    'yp1959': {
        'short': 'Yard and pound, 1959',
        'title': 'Refinement of values for the yard and the pound (international yard and pound agreement, 1959)',
        'by': 'US National Bureau of Standards, Federal Register 24 FR 5348; same values adopted by the UK, Canada, Australia, New Zealand and South Africa',
        'url': 'https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors',
    },
    'wma1985': {
        'short': 'UK Weights and Measures Act 1985',
        'title': 'Weights and Measures Act 1985, Schedule 1 (imperial units defined in metric terms)',
        'by': 'UK Parliament',
        'url': 'https://www.legislation.gov.uk/ukpga/1985/72/schedule/1',
    },
    'usft': {
        'short': 'NIST: US survey foot',
        'title': 'The US survey foot (deprecated from 1 January 2023)',
        'by': 'NIST and the National Geodetic Survey',
        'url': 'https://www.nist.gov/pml/us-surveyfoot',
    },
    'iau2012': {
        'short': 'IAU 2012, Res. B2',
        'title': 'Resolution B2 (2012): re-definition of the astronomical unit of length',
        'by': 'International Astronomical Union',
        'url': 'https://iauarchive.eso.org/static/resolutions/IAU2012_English.pdf',
    },
    'wgs84': {
        'short': 'WGS 84',
        'title': 'World Geodetic System 1984 (WGS 84): equatorial radius a = 6 378 137 m',
        'by': 'US National Geospatial-Intelligence Agency; parameters as registered in the EPSG Geodetic Parameter Dataset (IOGP)',
        'url': 'https://epsg.org/ellipsoid_7030/WGS-84.html',
    },
    'iho': {
        'short': 'IHO 1929 / BIPM',
        'title': 'International nautical mile of 1852 m (International Hydrographic Conference, Monaco, 1929); listed among non-SI units in the SI Brochure',
        'by': 'International Hydrographic Organization / BIPM',
        'url': 'https://www.bipm.org/en/publications/si-brochure',
    },
    'its90': {
        'short': 'BIPM SI Brochure',
        'title': 'Kelvin defined through the Boltzmann constant (2019); degree Celsius t/°C = T/K − 273.15',
        'by': 'BIPM (SI Brochure, section 2.3.1 and Table 4)',
        'url': 'https://www.bipm.org/en/publications/si-brochure',
    },
    'ics': {
        'short': 'IMO International Code of Signals',
        'title': 'International Code of Signals, 1969 edition revised 2005 (US edition: NGA Pub. 102, 2020)',
        'by': 'International Maritime Organization',
        'url': 'https://www.imo.org/en/publications/Pages/Home.aspx',
    },
    'itu1677': {
        'short': 'ITU-R M.1677-1',
        'title': 'Recommendation ITU-R M.1677-1: International Morse code',
        'by': 'International Telecommunication Union',
        'url': 'https://www.itu.int/rec/R-REC-M.1677',
    },
    'iturr': {
        'short': 'ITU Radio Regulations, App. 14',
        'title': 'Radio Regulations, Appendix 14: phonetic alphabet and figure code',
        'by': 'International Telecommunication Union',
        'url': 'https://www.itu.int/pub/R-REG-RR',
    },
    'colregs': {
        'short': 'COLREGs 1972',
        'title': 'Convention on the International Regulations for Preventing Collisions at Sea, 1972, Part D (Rules 32 to 37)',
        'by': 'International Maritime Organization',
        'url': 'https://www.imo.org/en/About/Conventions/Pages/COLREG.aspx',
    },
    'wmo306': {
        'short': 'WMO-No. 306',
        'title': 'Manual on Codes, Volume I.1 (WMO-No. 306): code table 3700 (state of the sea) and 4677 (present weather)',
        'by': 'World Meteorological Organization',
        'url': 'https://community.wmo.int/volume-i1',
    },
    'mobeaufort': {
        'short': 'Met Office: Beaufort scale',
        'title': 'Beaufort wind force scale, with probable wave heights',
        'by': 'Met Office (UK national weather service)',
        'url': 'https://weather.metoffice.gov.uk/guides/coast-and-sea/beaufort-scale',
    },
    'moglossary': {
        'short': 'Met Office: marine glossary',
        'title': 'Coast and sea glossary: visibility terms used in shipping forecasts',
        'by': 'Met Office (UK national weather service)',
        'url': 'https://weather.metoffice.gov.uk/guides/coast-and-sea/glossary',
    },
    'nhc': {
        'short': 'NHC: Saffir-Simpson scale',
        'title': 'Saffir-Simpson Hurricane Wind Scale',
        'by': 'US National Hurricane Center (NOAA)',
        'url': 'https://www.nhc.noaa.gov/aboutsshws.php',
    },
    'hrd': {
        'short': 'NOAA HRD FAQ',
        'title': 'Tropical cyclone FAQ: basins, names and seasons',
        'by': 'NOAA Atlantic Oceanographic and Meteorological Laboratory, Hurricane Research Division',
        'url': 'https://www.aoml.noaa.gov/hrd-faq/',
    },
    'naturalearth': {
        'short': 'Natural Earth',
        'title': 'Natural Earth 1:110m land (public domain), via world-atlas 2.0.2',
        'by': 'Natural Earth',
        'url': 'https://www.naturalearthdata.com/',
    },
    'jan': {
        'short': 'Secondary: Wikipedia',
        'title': 'Allied military phonetic spelling alphabets (secondary source; no primary text found online)',
        'by': 'Wikipedia',
        'url': 'https://en.wikipedia.org/wiki/Allied_military_phonetic_spelling_alphabets',
    },
}
