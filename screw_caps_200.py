"""Plaque de PRODUCTION : 200 capuchons decoratifs de vis (50 badges x 4,
dont 10 badges de marge), grille 15 x 14 au pas de 12 mm (~176 x 164 mm,
plateau P2S 256). Monochromes COULEUR (meme filament que la face des
boutons), imprimes a plat carre vers le haut, sans pause ni support.

Tranchage : profil 0.20 Standard "orca-like" (print/bambu/).
Exporte print/screw_caps_200.stl.
"""

from build123d import Compound, Pos, export_stl

import screw_cap as sc

TOL, ANG = 0.02, 0.15
PITCH = 12.0
COLS, ROWS = 15, 14
N = 200


def gen():
    caps = []
    for k in range(N):
        r, c = divmod(k, COLS)
        caps.append(Pos((c - (COLS - 1) / 2) * PITCH,
                        (r - (ROWS - 1) / 2) * PITCH, 0) * sc.make_cap())
    export_stl(Compound(children=caps), "print/screw_caps_200.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/screw_caps_200.stl (%d capuchons)" % len(caps))


if __name__ == "__main__":
    gen()
