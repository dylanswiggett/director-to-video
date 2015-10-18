#!/usr/bin/python

AI = "AI.jpg"
CDG = "CDGKNRSThYZ.jpg"
E = "E.jpg"
FV = "FV.jpg"
L = "L.jpg"
MBP = "MBP.jpg"
O = "O.jpg"
U = "U.jpg"
WQ = "WQ.jpg"

REST = "Rest.jpg"

phonemes = {
    # Consonants
    'p': MBP,
    't': CDG,
    'tS': CDG, # ?
    'k': CDG,
    'f': FV,
    'T': CDG,
    's': CDG,
    'S': REST, # ?
    'h': CDG, # ?
    'm': MBP,
    'N': CDG, # ?
    'l': L,
    'j': E, # ?
    'b': MBP,
    'd': CDG,
    'dZ': REST, # ?
    'g': CDG,
    'v': FV,
    'D': L, # ?
    'z': CDG,
    'Z': REST, # ?
    'n': CDG,
    'r': CDG,
    'w': WQ,

    # Additional consonants
    'C': CDG, # ?
    'l^': L, # ?
    'x': CDG, # ?
    'n^': CDG, # ?

    # Vowels
    '@': U, # ?
    '3': CDG, # ?
    '3:': CDG, # ?
    '@L': L,
    '@2': CDG,
    '@5': O,
    'a': AI,
    'aa': AI,
    'a#': U,
    'A:': O, # ?
    'A@': CDG, # ?
    'E': E,
    'e@': CDG, # ?
    'I': AI,
    'I2': AI,
    'i': AI,
    'i:': AI,
    'i@': CDG, # ?
    '0': O,
    'V': U,
    'u:': U,
    'U': U,
    'U@': U, # ?
    'O:': O, # ?
    'O@': O,
    'o@': O,
    'aI': CDG, # ?
    'eI': AI, # ?
    'OI': O,
    'aU': AI, # ?
    'oU': O,
    'aI@': AI,
    'aU@': CDG, # ?

    # Additional vowels
    'e': E,
    'o': O,
    'y': O, # ?
    'Y': O, # ?

    # Misc?
    'Q': O, # ?

    # Break
    '_': REST
    }
