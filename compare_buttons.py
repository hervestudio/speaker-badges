"""Comparatif des deux traitements de boutons, cote a cote :

  GAUCHE  — option 1 "ring"  : puits a collerette rapportee, capuchon en retrait
  DROITE  — option 2 "flush" : lamage direct Ø14 x 1.0, tete 1.2 quasi affleurante

Chaque variante = coque avant + capuchons en position repos (+ collerettes pour
l'option 1), posee debout ecran vers le spectateur.
"""

from build123d import Compound, Pos, Rotation

import button_cap as bc
import speaker_badge as sb

GAP = 76.0  # entraxe des deux facades


def _variant(style, dx):
    sb.BTN_STYLE = style
    front = sb.front_shell()
    parts = [(front, f"front_{style}")]
    for i, (bx, by) in enumerate(sb.button_centers()):
        cap = Pos(bx, by, bc.cap_seat_z(style)) * bc.make_cap(style=style)
        parts.append((cap, f"cap_{style}_{i}"))
        if style == "ring":
            ring = Pos(bx, by, -(bc.RING_H - sb.BTN_RING_SEAT_DEPTH)) * bc.make_ring()
            parts.append((ring, f"ring_{style}_{i}"))
    # pose debout, ecran vers le spectateur, decale en x
    pose = Pos(dx, 0, sb.H / 2) * Rotation(0, 0, 180) * Rotation(90, 0, 0)
    out = []
    for p, label in parts:
        moved = pose * p
        moved.label = label
        out.append(moved)
    return out


def gen_step():
    children = _variant("ring", -GAP / 2) + _variant("flush", GAP / 2)
    sb.BTN_STYLE = "ring"  # remet le defaut
    return Compound(label="compare_buttons", children=children)


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "compare_buttons.step")
    print("wrote compare_buttons.step")
