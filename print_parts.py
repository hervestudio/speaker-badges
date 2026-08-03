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

from build123d import Rotation, export_stl

import button_cap as bc
import screw_cap as sc
import speaker_badge as sb
import wrap_bar as wb

# Fine tessellation so the round bulge / fillets print smooth.
TOL, ANG = 0.02, 0.15


def gen():
    os.makedirs("print", exist_ok=True)
    parts = {
        "front_shell": sb.front_shell(),                 # screen face down, cavity up
        "back_shell": sb.back_shell(),                   # back face down, cavity up
        # (wrap_bar retire des impressions : Romain utilise une barre metal
        # Ø3 coupee a ~29.4 mm — le modele wrap_bar.py reste disponible)
        "button_cap_side": bc.make_cap(center=False),    # head down; print x2
        "button_cap_center": bc.make_cap(center=True),   # head down; print x1
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
        small.append(Pos(i * 18.0 - 18.0, 0, 0) * bc.make_cap(center=(i == 0)))
    for i in range(4):
        small.append(Pos(i * 12.0 - 18.0, 22.0, 0) * sc.make_cap())
    export_stl(Compound(children=small), "print/small_parts.stl",
               tolerance=TOL, angular_tolerance=ANG)
    print("wrote print/small_parts.stl")


if __name__ == "__main__":
    gen()
