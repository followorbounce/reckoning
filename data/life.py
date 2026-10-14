"""Code of life data.

IUPAC letters: only the names and the mnemonic are stored here. The SETS (what each letter means)
live once, in assets/dnamath.js, and the tests check this table against them.
Helix parameters are from the fibre models (Arnott & Hukins 1972) and the Z-DNA crystal structure
(Wang et al. 1979), with the solution value for B-DNA from Wang 1979; see data/sources.py.
"""

# letter, meaning, mnemonic (the reason for the letter)
IUPAC = [
    ('A', 'adenine', 'Adenine'),
    ('C', 'cytosine', 'Cytosine'),
    ('G', 'guanine', 'Guanine'),
    ('T', 'thymine (U, uracil, in RNA)', 'Thymine'),
    ('R', 'A or G', 'puRine'),
    ('Y', 'C or T', 'pYrimidine'),
    ('S', 'G or C', 'Strong: three hydrogen bonds'),
    ('W', 'A or T', 'Weak: two hydrogen bonds'),
    ('K', 'G or T', 'Keto'),
    ('M', 'A or C', 'aMino'),
    ('B', 'C, G or T', 'not A: B comes after A'),
    ('D', 'A, G or T', 'not C: D comes after C'),
    ('H', 'A, C or T', 'not G: H comes after G'),
    ('V', 'A, C or G', 'not T (not U): V comes after U'),
    ('N', 'any base', 'aNy'),
]

# The bases. Ring atoms are numbered by the standard scheme; exocyclic groups are listed by the atom they hang on.
BASES = [
    # key, name, kind, letter, formula, groups, in
    ('A', 'Adenine', 'purine', 'A', 'C5H5N5', 'amino group on C6', 'DNA and RNA'),
    ('G', 'Guanine', 'purine', 'G', 'C5H5N5O', 'C6=O (keto), amino group on C2', 'DNA and RNA'),
    ('C', 'Cytosine', 'pyrimidine', 'C', 'C4H5N3O', 'amino group on C4, C2=O', 'DNA and RNA'),
    ('T', 'Thymine', 'pyrimidine', 'T', 'C5H6N2O2', 'C2=O, C4=O, methyl group on C5', 'DNA'),
    ('U', 'Uracil', 'pyrimidine', 'U', 'C4H4N2O2', 'C2=O, C4=O', 'RNA'),
]

# form, hand, bp per turn, rise per bp (nm), twist per bp (deg), pitch (nm), diameter (nm, approx.), base-pair tilt (deg), grooves, where found, source key
FORMS = [
    ('A', 'right', 11, 0.256, 32.7, 2.82, 2.3, 20, 'major deep and narrow; minor wide and shallow',
     'dehydrated DNA; RNA double helices and DNA–RNA hybrids take this shape', 'arnott1972'),
    ('B', 'right', 10, 0.338, 36.0, 3.38, 2.0, -6, 'major wide; minor narrow',
     'the usual form in water and in cells; in solution 10.4 ± 0.1 bp per turn', 'arnott1972'),
    ('Z', 'left', 12, 0.372, -30.0, 4.46, 1.8, -7, 'no real major groove; minor narrow and deep',
     'alternating purine–pyrimidine runs such as (CG)n, at high salt or under negative supercoiling', 'wang1979z'),
]
B_SOLUTION_BP_PER_TURN = 10.4   # Wang 1979 (PNAS 76:200): 10.4 ± 0.1 bp per turn under physiological conditions

# Structural graphs of the free bases, used to draw them and checked against their formulas (tests/check_wave4.py):
# hydrogens are not stored; they are implied by valence (C 4, N 3, O 2), as in a skeletal formula.
RING = {
    'purine': (['N1', 'C2', 'N3', 'C4', 'C5', 'C6', 'N7', 'C8', 'N9'],
               [('N1', 'C2'), ('C2', 'N3'), ('N3', 'C4'), ('C4', 'C5'), ('C5', 'C6'), ('C6', 'N1'), ('C5', 'N7'), ('N7', 'C8'), ('C8', 'N9'), ('N9', 'C4')]),
    'pyrimidine': (['N1', 'C2', 'N3', 'C4', 'C5', 'C6'],
                   [('N1', 'C2'), ('C2', 'N3'), ('N3', 'C4'), ('C4', 'C5'), ('C5', 'C6'), ('C6', 'N1')]),
}
# key: (ring, ring double bonds, exocyclic groups as (ring atom, group, bond order)), sugar attaches at N9 (purines) or N1 (pyrimidines)
STRUCT = {
    'A': ('purine', [('N1', 'C6'), ('C2', 'N3'), ('C4', 'C5'), ('N7', 'C8')], [('C6', 'NH2', 1)]),
    'G': ('purine', [('C2', 'N3'), ('C4', 'C5'), ('N7', 'C8')], [('C6', 'O', 2), ('C2', 'NH2', 1)]),
    'C': ('pyrimidine', [('N3', 'C4'), ('C5', 'C6')], [('C4', 'NH2', 1), ('C2', 'O', 2)]),
    'T': ('pyrimidine', [('C5', 'C6')], [('C2', 'O', 2), ('C4', 'O', 2), ('C5', 'CH3', 1)]),
    'U': ('pyrimidine', [('C5', 'C6')], [('C2', 'O', 2), ('C4', 'O', 2)]),
}
# Watson-Crick hydrogen bonds: (purine atom or group, pyrimidine atom or group, donor side 'pu' or 'py')
HBONDS = {
    'AT': [('C6', 'C4', 'pu'), ('N1', 'N3', 'py')],
    'GC': [('C6', 'C4', 'py'), ('N1', 'N3', 'pu'), ('C2', 'C2', 'pu')],
}
