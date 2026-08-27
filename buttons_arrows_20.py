"""Plaque de PRODUCTION : 20 capuchons chevron inlay (boutons haut/bas —
la meme piece, orientee au montage), grille 5 x 4 espacee de 18 mm.

Tranchage : profil 0.08mm High Quality (premiere couche 0.2 + 0.08),
pause changement couleur->NOIR avant la couche 3 (frontiere a 0.28).
Exporte print/buttons_arrows_20.stl.
"""

from build123d import Compound, Pos, export_stl

import button_cap as bc

TOL, ANG = 0.02, 0.15
PITCH = 18.0
COLS, ROWS = 5, 4


def gen():
    caps = [Pos((c - (COLS - 1) / 2) * PITCH, (r - (ROWS - 1) / 2) * PITCH, 0)
            * bc.make_cap(dome=False, inlay=True)
            for r in range(ROWS) for c in range(COLS)]
    export_stl(Compound(children=caps), "print/buttons_arrows_20.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/buttons_arrows_20.stl (%d capuchons)" % len(caps))


if __name__ == "__main__":
    gen()
