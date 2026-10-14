"""Naming page: gods and the names they left in the sky, the calendar and the periodic table.

All text original. Sources: the IAU Gazetteer of Planetary Nomenclature (naming rules and themes), the Carnegie
note on Jupiter's moon names, the OED for days and months, the RSC periodic table for element names.
"""

# Greek, Roman, domain, what carries the name today
GODS = [
    ('Zeus', 'Jupiter (Iuppiter)', 'king of the gods, sky and thunder', 'the largest planet; Thursday in Romance languages (jueves, jeudi)'),
    ('Hera', 'Juno', 'queen of the gods, marriage', 'asteroid 3 Juno; probably the month of June'),
    ('Poseidon', 'Neptune', 'the sea', 'the eighth planet; its moon Triton is Poseidon’s son'),
    ('Hades', 'Pluto (Dis)', 'the underworld', 'the dwarf planet Pluto and plutonium; Pluto’s moons carry underworld names'),
    ('Demeter', 'Ceres', 'grain and harvest', 'the dwarf planet Ceres, cerium, and the word cereal'),
    ('Hestia', 'Vesta', 'hearth and home', 'asteroid 4 Vesta'),
    ('Ares', 'Mars', 'war', 'the red planet, its moons Phobos and Deimos (his sons, Fear and Dread), the month of March, Tuesday in Romance languages'),
    ('Aphrodite', 'Venus', 'love and beauty', 'the brightest planet; Friday in Romance languages (viernes, vendredi)'),
    ('Hermes', 'Mercury', 'messenger, trade, travellers', 'the innermost planet, the metal, Wednesday in Romance languages'),
    ('Athena', 'Minerva', 'wisdom, crafts', 'asteroid 2 Pallas (Pallas Athena) and, through it, palladium'),
    ('Artemis', 'Diana', 'the hunt; linked with the Moon', 'NASA’s Artemis programme, named as Apollo’s twin sister'),
    ('Apollo', 'Apollo', 'light, music, prophecy; linked with the Sun', 'the Apollo programme. Rome kept his Greek name; the Sun itself is Helios in Greek and Sol in Latin'),
    ('Hephaestus', 'Vulcan', 'fire and the forge', 'Vulcan, a planet inside Mercury’s orbit predicted in 1859 and never found; Einstein’s relativity explained the motion it was invented for (1915). Also the word volcano'),
    ('Kronos', 'Saturn', 'sowing and time; father of Zeus', 'the ringed planet and Saturday'),
    ('Ouranos', 'Caelus', 'the sky; father of Kronos', 'the seventh planet (the only one with a Greek name) and uranium'),
    ('Gaia', 'Terra (Tellus)', 'the Earth', 'tellurium; the Earth itself has an English name from Old English eorþe'),
    ('Eros', 'Cupid (Amor)', 'love', 'asteroid 433 Eros, the first asteroid orbited and landed on by a spacecraft (NEAR Shoemaker, 2000–2001)'),
    ('Helios', 'Sol', 'the Sun', 'helium (found in the Sun’s spectrum before it was found on Earth), heliocentric, solar'),
    ('Selene', 'Luna', 'the Moon', 'selenium, selenography (mapping the Moon), lunar'),
    ('Eos', 'Aurora', 'the dawn', 'the aurora, the polar lights'),
    ('Prometheus', 'Prometheus', 'the Titan who stole fire', 'promethium, and Prometheus, a moon of Saturn that shepherds its F ring'),
]

# Who names what in the Solar System (IAU)
MOON_THEMES = [
    ('Mars', 'Phobos, Deimos', 'The sons of Ares who drove his chariot: Fear and Dread. Found by Asaph Hall in 1877.'),
    ('Jupiter', 'Io, Europa, Ganymede, Callisto and dozens more',
     'Lovers, favourites and descendants of Zeus. Galileo found the four large moons in 1610; their names were proposed by Simon Marius. '
     'Under the present convention the names of prograde moons end in -a and of retrograde moons in -e.'),
    ('Saturn', 'Titan, Rhea, Iapetus, Dione, Tethys, Enceladus, Mimas, Hyperion…',
     'Titans and giants, named by John Herschel in 1847; the many small outer moons are grouped by giants of Inuit, Gallic and Norse myth.'),
    ('Uranus', 'Titania, Oberon, Ariel, Umbriel, Miranda…',
     'An exception: characters from Shakespeare and Alexander Pope, not myth. Titania and Oberon rule the fairies in A Midsummer Night’s Dream.'),
    ('Neptune', 'Triton, Nereid, Proteus…', 'Gods and spirits of the sea. Triton was found 17 days after Neptune itself, in 1846.'),
    ('Pluto', 'Charon, Nix, Hydra, Kerberos, Styx', 'The underworld: its ferryman, river, guard dog and monsters.'),
]

DWARF = [
    ('Ceres', 'Roman goddess of grain; patron of Sicily, where Giuseppe Piazzi found it on 1 January 1801'),
    ('Pluto', 'Roman god of the underworld; a planet from 1930 to 2006'),
    ('Eris', 'Greek goddess of strife: its discovery in 2005 started the debate that led the IAU to define “planet” in 2006'),
    ('Haumea', 'Hawaiian goddess of childbirth; its moons are her daughters Hiʻiaka and Namaka'),
    ('Makemake', 'creator god of the people of Rapa Nui (Easter Island)'),
]

# English, Old English form and who it honours, Latin, Spanish, French
WEEKDAYS = [
    ('Sunday', 'sunnandæg: the Sun', 'dies Solis', 'domingo', 'dimanche', 'Romance languages took the Christian “Lord’s day” (dies Dominica).'),
    ('Monday', 'mōnandæg: the Moon', 'dies Lunae', 'lunes', 'lundi', ''),
    ('Tuesday', 'Tīwesdæg: Tiw, a Germanic war god equated with Mars', 'dies Martis', 'martes', 'mardi', ''),
    ('Wednesday', 'Wōdnesdæg: Woden, equated with Mercury', 'dies Mercurii', 'miércoles', 'mercredi', ''),
    ('Thursday', 'Þunresdæg: Thunor (Thor), the thunder god, equated with Jupiter', 'dies Iovis', 'jueves', 'jeudi', ''),
    ('Friday', 'Frīgedæg: Frig, equated with Venus', 'dies Veneris', 'viernes', 'vendredi', ''),
    ('Saturday', 'Sæternesdæg: Saturn, the only Roman god kept in English', 'dies Saturni', 'sábado', 'samedi', 'Spanish and French took the Sabbath.'),
]

MONTHS = [
    ('January', 'Janus, the two-faced god of doorways and beginnings'),
    ('February', 'Februa, a Roman festival of purification held in that month'),
    ('March', 'Mars; the first month of the oldest Roman year'),
    ('April', 'uncertain; perhaps from Latin aperire, “to open”'),
    ('May', 'Maia, a goddess of growth'),
    ('June', 'probably Juno'),
    ('July', 'Julius Caesar, renamed in 44 BC (before: Quintilis, “fifth”)'),
    ('August', 'the emperor Augustus, 8 BC (before: Sextilis, “sixth”)'),
    ('September to December', 'seventh to tenth (septem, octo, novem, decem), counting from March'),
]

# element, symbol, named after, year named (approx.)
ELEMENTS = [
    ('Helium', 'He', 'Helios, the Sun: seen as a yellow line in the solar spectrum in 1868, found on Earth in 1895'),
    ('Selenium', 'Se', 'Selene, the Moon: named in 1817 as the companion of tellurium'),
    ('Tellurium', 'Te', 'Tellus, the Earth'),
    ('Mercury', 'Hg', 'the planet and god; the symbol is Latin hydrargyrum, “water-silver”'),
    ('Uranium', 'U', 'the planet Uranus, found eight years before it (1789)'),
    ('Neptunium', 'Np', 'Neptune, the planet after Uranus, as element 93 comes after uranium (1940)'),
    ('Plutonium', 'Pu', 'Pluto, the next “planet” out, as element 94 follows neptunium (made 1940–41)'),
    ('Cerium', 'Ce', 'the dwarf planet Ceres, discovered two years earlier (1803)'),
    ('Palladium', 'Pd', 'the asteroid Pallas, discovered the year before (1803)'),
    ('Titanium', 'Ti', 'the Titans, sons of the Earth'),
    ('Promethium', 'Pm', 'Prometheus, who stole fire from the gods'),
    ('Thorium', 'Th', 'Thor, the Norse thunder god'),
    ('Vanadium', 'V', 'Vanadís, a name of the Norse goddess Freyja'),
]
