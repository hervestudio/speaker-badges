"""Plaque de PRODUCTION : 50 capuchons smiley inlay (boutons centraux —
40 badges + 10 de marge), grille 10 x 5 au pas de 18 mm (~175 x 85 mm,
plateau P2S 256).

Tranchage : profil 0.20 Standard "orca-like" (print/bambu/), pause
changement couleur->NOIR avant la couche 3 (frontiere a 0.4).
Exporte print/buttons_smiley_50.stl.
"""

from build123d import Compound, Pos, export_stl

import button_cap as bc

TOL, ANG = 0.02, 0.15
PITCH = 18.0
COLS, ROWS = 10, 5


def gen():
    caps = [Pos((c - (COLS - 1) / 2) * PITCH, (r - (ROWS - 1) / 2) * PITCH, 0)
            * bc.make_cap(center=True, dome=False, inlay=True)
            for r in range(ROWS) for c in range(COLS)]
    export_stl(Compound(children=caps), "print/buttons_smiley_50.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/buttons_smiley_50.stl (%d capuchons)" % len(caps))


if __name__ == "__main__":
    gen()
