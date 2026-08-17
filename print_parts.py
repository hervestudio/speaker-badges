"""Export STL files for the 3D-PRINTED parts, ready to slice (Bambu A1).

Printed parts: front_shell, back_shell, the button caps (2 side + 1 center),
and (optionally) wrap_bar.
NOT printed: the M2 socket-screws and the brass heat-set inserts (bought hardware).

Each shell is exported in its native pose, which is also the recommended print
orientation: OUTER FACE DOWN, cavity opening up. In that pose the USB / SD
cutouts and the strap slot are all open notches at the seam (top), and the
front-face button holes are plain through-holes, so the print needs NO supports.
The caps print head-DOWN (their native pose); the wrap bar is laid flat (print
with a brim, or just use a Ø3 mm steel rod instead).
"""

import os

from build123d import Pos, Rotation, export_stl

import button_cap as bc


def _cap_print(cap):
    """Oriente un capuchon pour l'impression : dome vers le haut, repose sur
    le bout du nub (supports auto combleront sous la couronne)."""
    flipped = Rotation(180, 0, 0) * cap
    return Pos(0, 0, -flipped.bounding_box().min.Z) * flipped
import screw_cap as sc
import speaker_badge as sb
import wrap_bar as wb

# Fine tessellation so the round bulge / fillets print smooth.
TOL, ANG = 0.02, 0.15


def gen():
    os.makedirs("print", exist_ok=True)
    # Coques suffixees par variante : "_short" (64x124, l'originale),
    # "_medium" (66x134, +10 en haut, ESP remonte, 505060 paysage),
    # "_long" (66x144, +10 haut et bas, 505060 paysage).
    variant = sb.VARIANT
    parts = {
        f"front_shell_{variant}": sb.front_shell(),      # screen face down, cavity up
        f"back_shell_{variant}": sb.back_shell(),        # back face down, cavity up
        # (wrap_bar retire des impressions : Romain utilise une barre metal
        # Ø3 coupee a ~29.4 mm — le modele wrap_bar.py reste disponible)
        # capuchons PLATS (production serie) : face contre plateau, SANS
        # supports — gravures cote plateau. Icones (designs Figma) : chevron ∨
        # identique pour les DEUX lateraux, smiley au centre
        "button_cap_side": bc.make_cap(dome=False),                 # print x2
        "button_cap_center": bc.make_cap(center=True, dome=False),  # print x1
        # variante BOMBEE (option) : dome en haut, nub sur le plateau,
        # supports auto sous la couronne
        "button_cap_side_dome": _cap_print(bc.make_cap()),
        "button_cap_center_dome": _cap_print(bc.make_cap(center=True)),
        # variante INLAY BICOLORE (plate, face contre plateau) : icone gravee
        # de DEUX couches (0.4) — trancher a 0.2. Recette 1 pause : couleur
        # couches 1-2, noir du debut de la couche 3 a la fin (tranche/dos
        # noirs). Recette 2 pauses : retour couleur debut couche 5.
        # Bicolore net, zero support, zero remplissage manuel
        "button_cap_side_inlay": bc.make_cap(dome=False, inlay=True),
        "button_cap_center_inlay": bc.make_cap(center=True, dome=False,
                                               inlay=True),
        "screw_cap": sc.make_cap(),                      # a plat; print x4
    }
    for name, part in parts.items():
        path = f"print/{name}.stl"
        export_stl(part, path, tolerance=TOL, angular_tolerance=ANG)
        print(f"wrote {path}")

    # Plaque combinee des petites pieces (un seul print) :
    # 3 capuchons de boutons + 4 capuchons de vis, a plat, espaces.
    from build123d import Compound, Pos
    small = []
    for i in range(3):
        small.append(Pos(i * 18.0 - 18.0, 0, 0)
                     * bc.make_cap(center=(i == 0), dome=False))
    for i in range(4):
        small.append(Pos(i * 12.0 - 18.0, 22.0, 0) * sc.make_cap())
    export_stl(Compound(children=small), "print/small_parts.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/small_parts.stl")


if __name__ == "__main__":
    import subprocess
    import sys

    gen()
    if sb.VARIANT == "short" and not os.environ.get("BADGE_VARIANT"):
        # regenere aussi les coques Medium et Long en sous-processus
        for v in ("medium", "long"):
            subprocess.run([sys.executable, __file__],
                           env={**os.environ, "BADGE_VARIANT": v}, check=True)
