"""Plaque de TEST bicolore : 3 capuchons inlay (chevron, smiley, chevron)
espaces de 18 mm, face contre plateau — geometrie de serie (logement 2.3
dans un manchon rallonge, matiere cote face 0.8).

Tranchage : profil 0.20 Standard "orca-like" (voir INLAY_DEPTH),
pause changement couleur->NOIR avant la couche 3 (frontiere a 0.4).
Exporte print/buttons_inlay_test.stl.
"""

from build123d import Compound, Pos, export_stl

import button_cap as bc

TOL, ANG = 0.02, 0.15


def gen():
    caps = [Pos(i * 18.0 - 18.0, 0, 0)
            * bc.make_cap(center=(i == 1), dome=False, inlay=True)
            for i in range(3)]
    export_stl(Compound(children=caps), "print/buttons_inlay_test.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/buttons_inlay_test.stl (3 capuchons serie)")


if __name__ == "__main__":
    gen()
