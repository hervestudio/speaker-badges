"""Plaque de PRODUCTION serie complete : 100 capuchons chevron inlay
(40 badges + 10 de perte = 50 badges x 2 boutons haut/bas — la meme piece,
orientee au montage), grille 10 x 10 espacee de 18 mm (~175 mm de cote,
plateau P2S 256).

Tranchage : profil 0.08mm High Quality (premiere couche 0.2 + 0.08),
pause changement couleur->NOIR avant la couche 3 (frontiere a 0.28).
Exporte print/buttons_arrows_100.stl.
"""

from build123d import Compound, Pos, export_stl

import button_cap as bc

TOL, ANG = 0.02, 0.15
PITCH = 18.0
COLS, ROWS = 10, 10


def gen():
    caps = [Pos((c - (COLS - 1) / 2) * PITCH, (r - (ROWS - 1) / 2) * PITCH, 0)
            * bc.make_cap(dome=False, inlay=True)
            for r in range(ROWS) for c in range(COLS)]
    export_stl(Compound(children=caps), "print/buttons_arrows_100.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/buttons_arrows_100.stl (%d capuchons)" % len(caps))


if __name__ == "__main__":
    gen()
