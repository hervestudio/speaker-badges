"""Plaque de REPRISE : 30 capuchons chevron inlay (15 badges x 2 boutons
haut/bas), grille 6 x 5 au pas de 18 mm — geometrie manchon 0.9 /
logement 1.5 (revue montage 2026-08-27).

Tranchage : profil 0.20 Standard "orca-like" (print/bambu/), pause
changement couleur->NOIR avant la couche 3 (frontiere a 0.4).
Exporte print/buttons_arrows_30.stl.
"""

from build123d import Compound, Pos, export_stl

import button_cap as bc

TOL, ANG = 0.02, 0.15
PITCH = 18.0
COLS, ROWS = 6, 5


def gen():
    caps = [Pos((c - (COLS - 1) / 2) * PITCH, (r - (ROWS - 1) / 2) * PITCH, 0)
            * bc.make_cap(dome=False, inlay=True)
            for r in range(ROWS) for c in range(COLS)]
    export_stl(Compound(children=caps), "print/buttons_arrows_30.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/buttons_arrows_30.stl (%d capuchons)" % len(caps))


if __name__ == "__main__":
    gen()
