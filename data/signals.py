"""Signal room data: International Code of Signals flags and single-letter meanings,
Morse code (ITU-R M.1677-1), phonetic alphabets, and sound signals (COLREGs Rules 32-35).

Flag designs follow the ICS (1969 edition, revised 2005), checked against their heraldic
blazons. Colours: r red, y yellow, b blue, w white, k black. Design kinds are drawn by
assets/flags.py-equivalent code in build.py; every flag is 3:2 except pennants/substitutes.
"""

C = {'r': '#c8102e', 'y': '#ffcc00', 'b': '#0b3d91', 'w': '#ffffff', 'k': '#111111'}

# letter: (code word, design kind, colours, meaning, note)
FLAGS = [
    ('A', 'Alfa', ('swallow-pale', 'wb'), 'I have a diver down; keep well clear at slow speed.', ''),
    ('B', 'Bravo', ('swallow', 'r'), 'I am taking in, or discharging, or carrying dangerous goods.', ''),
    ('C', 'Charlie', ('fess5', 'bwrwb'), 'Affirmative: “yes”, or the previous group is to be read as affirmative.', ''),
    ('D', 'Delta', ('fess121', 'yby'), 'Keep clear of me; I am manoeuvring with difficulty.', ''),
    ('E', 'Echo', ('fess2', 'br'), 'I am altering my course to starboard.', ''),
    ('F', 'Foxtrot', ('lozenge', 'wr'), 'I am disabled; communicate with me.', ''),
    ('G', 'Golf', ('paly6', 'yb'), 'I require a pilot.', 'Made by fishing vessels working close together on the fishing grounds: “I am hauling nets”.'),
    ('H', 'Hotel', ('pale2', 'wr'), 'I have a pilot on board.', ''),
    ('I', 'India', ('disc', 'yk'), 'I am altering my course to port.', ''),
    ('J', 'Juliett', ('fess3', 'bwb'), 'I am on fire and have dangerous cargo on board: keep well clear of me, or I am leaking dangerous cargo.', ''),
    ('K', 'Kilo', ('pale2', 'yb'), 'I wish to communicate with you.', ''),
    ('L', 'Lima', ('quarterly', 'ykky'), 'You should stop your vessel instantly.', ''),
    ('M', 'Mike', ('saltire', 'bw'), 'My vessel is stopped and making no way through the water.', ''),
    ('N', 'November', ('chequy', 'bw'), 'Negative: “no”, or the previous group is to be read as negative.', 'Visual or sound signalling only; by voice or radio the signal is “NO”.'),
    ('O', 'Oscar', ('perbend', 'ry'), 'Man overboard.', ''),
    ('P', 'Papa', ('square', 'bw'), 'In harbour: all persons should report on board, as the vessel is about to proceed to sea.',
     'At sea, made by fishing vessels: “My nets have come fast upon an obstruction”. Traditionally called the Blue Peter.'),
    ('Q', 'Quebec', ('plain', 'y'), 'My vessel is “healthy” and I request free pratique.', ''),
    ('R', 'Romeo', ('cross', 'ry'), 'No meaning as a single flag.', 'Before 1969 it meant “The way is off my ship; you may feel your way past me”.'),
    ('S', 'Sierra', ('square', 'wb'), 'I am operating astern propulsion.', ''),
    ('T', 'Tango', ('pale3', 'rwb'), 'Keep clear of me; I am engaged in pair trawling.', ''),
    ('U', 'Uniform', ('quarterly', 'rwwr'), 'You are running into danger.', ''),
    ('V', 'Victor', ('saltire', 'wr'), 'I require assistance.', ''),
    ('W', 'Whiskey', ('square2', 'bwr'), 'I require medical assistance.', ''),
    ('X', 'X-ray', ('cross', 'wb'), 'Stop carrying out your intentions and watch for my signals.', ''),
    ('Y', 'Yankee', ('bendy', 'yr'), 'I am dragging my anchor.', ''),
    ('Z', 'Zulu', ('persaltire', 'ykrb'), 'I require a tug.', 'Made by fishing vessels working close together on the fishing grounds: “I am shooting nets”.'),
]

# numeral pennants (tapered): digit, code word, design
PENNANTS = [
    ('0', 'Nadazero', ('pale3', 'yry')), ('1', 'Unaone', ('disc', 'wr')), ('2', 'Bissotwo', ('disc', 'bw')),
    ('3', 'Terrathree', ('pale3', 'rwb')), ('4', 'Kartefour', ('cross', 'rw')), ('5', 'Pantafive', ('pale2', 'yb')),
    ('6', 'Soxisix', ('fess2', 'kw')), ('7', 'Setteseven', ('fess2', 'yr')), ('8', 'Oktoeight', ('cross', 'wr')),
    ('9', 'Novenine', ('quarterly', 'wkry')),
]
SUBSTITUTES = [
    ('1st', 'First substitute', ('border', 'yb'), 'Repeats the uppermost flag of the same class in the hoist.'),
    ('2nd', 'Second substitute', ('pale2', 'bw'), 'Repeats the second flag of the same class, counting from the top.'),
    ('3rd', 'Third substitute', ('fess3', 'wkw'), 'Repeats the third flag of the same class, counting from the top.'),
]
ANSWERING = ('Answering pennant', ('pale5', 'rwrwr'), 'Hoisted to acknowledge a signal; also used as a decimal point between numeral pennants.')

# ---------------------------------------------------------------- Morse (ITU-R M.1677-1)
MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    '.': '.-.-.-', ',': '--..--', ':': '---...', '?': '..--..', "'": '.----.', '-': '-....-', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '"': '.-..-.', '=': '-...-', '+': '.-.-.', '@': '.--.-.',
}
MORSE_NAMES = {'.': 'full stop', ',': 'comma', ':': 'colon', '?': 'question mark', "'": 'apostrophe', '-': 'hyphen', '/': 'fraction bar',
               '(': 'open bracket', ')': 'close bracket', '"': 'quotation marks', '=': 'double hyphen (break)', '+': 'cross (end of message)',
               '@': 'commercial at (added 2004)'}
PROSIGNS = [
    ('Starting signal', '-.-.-', 'Sent before each transmission.'),
    ('Invitation to transmit (K)', '-.-', 'Over to you.'),
    ('Wait (AS)', '.-...', 'Wait.'),
    ('Understood (SN)', '...-.', 'Message received and understood.'),
    ('Error', '........', 'Eight dots: the last word or group was wrong; it follows corrected.'),
    ('Cross (AR)', '.-.-.', 'End of the message (end of telegram).'),
    ('End of work (SK)', '...-.-', 'End of the whole exchange.'),
]
TIMING = [('dot', 1), ('dash', 3), ('gap inside a letter', 1), ('gap between letters', 3), ('gap between words', 7)]

# ---------------------------------------------------------------- phonetic alphabets
ICAO = ['Alfa', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliett', 'Kilo', 'Lima', 'Mike',
        'November', 'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu']
# spoken as (ITU Radio Regulations, Appendix 14; stress marks omitted)
ICAO_SAY = ['AL FAH', 'BRAH VOH', 'CHAR LEE', 'DELL TAH', 'ECK OH', 'FOKS TROT', 'GOLF', 'HOH TELL', 'IN DEE AH', 'JEW LEE ETT',
            'KEY LOH', 'LEE MAH', 'MIKE', 'NO VEM BER', 'OSS CAH', 'PAH PAH', 'KEH BECK', 'ROW ME OH', 'SEE AIR RAH', 'TANG GO',
            'YOU NEE FORM', 'VIK TAH', 'WISS KEY', 'ECKS RAY', 'YANG KEY', 'ZOO LOO']
FIGURE_WORDS = [('0', 'Nadazero', 'NAH-DAH-ZAY-ROH'), ('1', 'Unaone', 'OO-NAH-WUN'), ('2', 'Bissotwo', 'BEES-SOH-TOO'),
                ('3', 'Terrathree', 'TAY-RAH-TREE'), ('4', 'Kartefour', 'KAR-TAY-FOWER'), ('5', 'Pantafive', 'PAN-TAH-FIVE'),
                ('6', 'Soxisix', 'SOK-SEE-SIX'), ('7', 'Setteseven', 'SAY-TAY-SEVEN'), ('8', 'Oktoeight', 'OK-TOH-AIT'),
                ('9', 'Novenine', 'NO-VAY-NINER'), ('.', 'Decimal', 'DAY-SEE-MAL'), ('stop', 'Stop', 'STOP')]
JAN_1941 = ['Able', 'Baker', 'Charlie', 'Dog', 'Easy', 'Fox', 'George', 'How', 'Item', 'Jig', 'King', 'Love', 'Mike', 'Nan',
            'Oboe', 'Peter', 'Queen', 'Roger', 'Sugar', 'Tare', 'Uncle', 'Victor', 'William', 'X-ray', 'Yoke', 'Zebra']

# ---------------------------------------------------------------- sound signals (COLREGs)
# s = short blast (about 1 s), p = prolonged blast (4 to 6 s); Rule 32
SOUND = [
    ('Manoeuvring (Rule 34 a)', [
        ('s', 'I am altering my course to starboard.'),
        ('ss', 'I am altering my course to port.'),
        ('sss', 'I am operating astern propulsion.')]),
    ('Overtaking in a narrow channel (Rule 34 c)', [
        ('pps', 'I intend to overtake you on your starboard side.'),
        ('ppss', 'I intend to overtake you on your port side.'),
        ('psps', 'Agreement by the vessel being overtaken.')]),
    ('Doubt and bends (Rule 34 d, e)', [
        ('sssss', 'Doubt or warning: I do not understand your intentions or doubt you are taking enough action (at least five short and rapid blasts).'),
        ('p', 'Approaching a bend or an area where other vessels may be hidden; answered with one prolonged blast.')]),
    ('Restricted visibility (Rule 35), at intervals of not more than 2 minutes', [
        ('p', 'Power-driven vessel making way through the water.'),
        ('pp', 'Power-driven vessel under way but stopped and making no way (about 2 s between blasts).'),
        ('pss', 'Vessel not under command, restricted in her ability to manoeuvre, constrained by draught, sailing, fishing, or towing or pushing.'),
        ('psss', 'Manned vessel being towed (sounded immediately after the towing vessel’s signal if possible).')]),
]
