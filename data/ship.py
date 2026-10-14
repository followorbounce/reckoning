"""Ship room data: the named parts of a midship section, and the load-line rules.

Part descriptions are original text. Definitions follow standard naval-architecture usage; the
load-line numbers are quoted from the International Convention on Load Lines, 1966, Annex I.
Each part: (id, name, group, description). Groups order the legend.
"""

PARTS = [
    # bottom
    ('keel', 'Keel (flat plate keel)', 'Bottom',
     'The backbone of the hull: a heavy strip of plating along the centreline of the bottom, thicker than the plates beside it. '
     'Everything else is built up from it, and in dry dock the ship rests on it.'),
    ('garboard', 'Garboard strake', 'Bottom',
     'The strake of bottom plating next to the keel, one on each side. Strakes are lettered from the keel outwards: '
     'the garboard is strake A.'),
    ('bottom', 'Bottom shell plating', 'Bottom',
     'The outer skin of the flat bottom. With the deck it forms the two flanges of the hull girder, so it carries the largest '
     'bending stresses when the ship hogs or sags on a wave.'),
    ('cgirder', 'Centre girder', 'Bottom',
     'A continuous vertical plate on the centreline inside the double bottom, from the keel to the tank top. '
     'Older ships had a vertical keel or keelson in the same place.'),
    ('sgirder', 'Side girder', 'Bottom',
     'Vertical fore-and-aft plates in the double bottom, parallel to the centre girder. They stiffen the bottom and divide the tanks.'),
    ('floor', 'Plate floor', 'Bottom',
     'A transverse plate across the double bottom, from the centre girder to the bilge. Lightening holes save weight and let a worker '
     'pass through. In a transversely framed ship there is a floor at every frame.'),
    ('tanktop', 'Tank top (inner bottom)', 'Bottom',
     'The plating over the double bottom. It is the floor of the hold and the roof of the tanks below. If the outer bottom is holed '
     'in a grounding, the tank top keeps the sea out of the hold.'),
    ('margin', 'Margin plate', 'Bottom',
     'The plate that closes the outer edge of the double bottom where it meets the turn of the bilge.'),
    # side
    ('bilge', 'Bilge strake', 'Side',
     'The curved strake at the turn of the bilge, where the bottom becomes the side.'),
    ('bilgekeel', 'Bilge keel', 'Side',
     'A fin fitted along the turn of the bilge for part of the ship’s length. It does not support anything: it damps rolling by '
     'stirring up the water as the ship rolls.'),
    ('bracket', 'Tank-side bracket', 'Side',
     'A triangular plate joining the foot of each frame to the margin plate and tank top, so the side and the bottom act as one frame.'),
    ('shell', 'Side shell plating', 'Side',
     'The outer skin of the side, laid in long horizontal strakes. Plates in neighbouring strakes have their joints staggered so that '
     'no weak line runs round the ship.'),
    ('frame', 'Frame', 'Side',
     'A rib: a bent section bar (or, in welded ships, a flat bulb bar) running up the inside of the shell from the bilge to the deck. '
     'Transverse frames are typically 0.6 m to 0.9 m apart.'),
    ('sheer', 'Sheerstrake', 'Side',
     'The top strake of the side shell, where the side meets the deck. Like the deck stringer it is highly stressed and is made thicker.'),
    # decks
    ('deck', 'Upper deck plating', 'Decks',
     'The weather deck, the top flange of the hull girder. It closes the hull, and its edge is the reference for the freeboard and the load line.'),
    ('stringer', 'Deck stringer plate', 'Decks',
     'The outermost strake of deck plating, joined to the sheerstrake. It is the thickest plate of the deck.'),
    ('beam', 'Deck beam', 'Decks',
     'A transverse girder under the deck, one at every frame, curved to give the deck its camber so that water runs off to the sides.'),
    ('knee', 'Beam knee', 'Decks',
     'A bracket that joins the end of each deck beam to the top of its frame, making frame and beam a single stiff ring.'),
    ('tween', 'Tween deck', 'Decks',
     'An intermediate deck between the upper deck and the tank top, dividing the hold so cargo can be stowed in layers.'),
    ('pillar', 'Pillar (stanchion)', 'Decks',
     'A column under the deck girders that carries deck loads down to the double bottom.'),
    ('coaming', 'Hatch coaming', 'Decks',
     'The vertical plating round a hatchway. It stiffens the edge of the opening and keeps water on deck from running into the hold.'),
    ('bulwark', 'Bulwark', 'Decks',
     'A light plate wall above the deck edge that keeps people and gear from going over the side. It is not part of the hull girder, '
     'and freeing ports in it let water on deck escape.'),
    ('stay', 'Bulwark stay', 'Decks',
     'A bracket from the deck to the top of the bulwark, holding it up.'),
    # longitudinal system only
    ('long', 'Longitudinal', 'Longitudinal framing',
     'In the longitudinal system, stiffeners run fore and aft along the bottom, side and deck, close together, instead of transverse frames. '
     'They add to the strength of the hull girder as well as stiffening the plating.'),
    ('web', 'Web frame', 'Longitudinal framing',
     'A deep transverse frame, spaced several metres apart, that supports the longitudinals.'),
]

# Load Line Convention 1966, Annex I (sizes in mm, reg. 4-7; freeboard rules, reg. 40)
LOADLINE = {
    'deck_line': (300, 25),       # reg. 4: length, breadth
    'ring_outer': 300,            # reg. 5: outside diameter
    'ring_width': 25,
    'ring_bar': (450, 25),        # reg. 5: horizontal line; its upper edge passes through the centre of the ring
    'line': (230, 25),            # reg. 6: lines used with the mark
    'vertical_from_ring': 540,    # reg. 6: vertical line forward of the ring centre
    'letters': (115, 75),         # reg. 7: letters of the assigning authority, height and width
    'wna_add_mm': 50,             # reg. 40(6): Winter North Atlantic, ships of not more than 100 m
    'wna_max_length_m': 100,
    'tropical_fraction': 48,      # reg. 40(3) and (5): 1/48 of summer draught
}
