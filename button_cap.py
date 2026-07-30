"""Drop-in button caps — print separately. Two variants:

SIDE caps (x2): a flat Ø9 head sits slightly proud of the front face; a Ø6.6 stem
passes through the Ø7 panel hole; a Ø8.0 snap flange with a 45° lead-in springs
past the hole and catches on the inner wall face, retaining the cap while it
presses the tactile switch behind it.

CENTER cap (x1): SAME Ø9 head and stem, but NO retention flange. The TP4056 sits
~2.5 mm behind this hole — too close for any flange wider than the Ø7 hole — so the
center cap is GLUED at the head rim (or trapped by a non-springing switch carrier).
A short Ø6 nub on the back contacts the switch. If you want the center to snap-fit
like the sides, the TP4056 has to drop another ~2 mm (to ~-37) and one pocket wall
gets trimmed — say the word.

Print orientation: head-DOWN on the bed (the head's flat top is the only fully
flat face). The flange's lead-in cone then prints as a self-supporting overhang.
"""

from build123d import Align, Compound, Cone, Cylinder, Pos

import speaker_badge as sb

HEAD_DIA = sb.BTN_CAP_HEAD          # 9.0  proud head
HEAD_H = 1.6
STEM_DIA = sb.BTN_HOLE_DIA - 0.4    # 6.6  (0.2 mm clearance per side in the Ø7 hole)
STEM_H = sb.WALL + 0.4              # through the 1.8 mm wall + a touch of float
FLANGE_DIA = 8.0                    # side caps: snaps behind the inner wall face
FLANGE_H = 1.0
LEADIN = 0.6                        # 45° lead-in under the flange (snap-in ramp)
NUB_DIA = 6.0                       # center cap: switch-contact nub (no retention)
NUB_H = 1.0

MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def make_cap(center=False):
    z = 0.0
    head = Pos(0, 0, z) * Cylinder(HEAD_DIA / 2, HEAD_H, align=MIN)
    z += HEAD_H
    stem = Pos(0, 0, z) * Cylinder(STEM_DIA / 2, STEM_H, align=MIN)
    z += STEM_H
    if center:
        # No flange (TP4056 too close) — just a switch-contact nub; glued at the rim.
        nub = Pos(0, 0, z) * Cylinder(NUB_DIA / 2, NUB_H, align=MIN)
        cap = head + stem + nub
        cap.label = "button_cap_center"
        return cap
    flange = Pos(0, 0, z) * Cylinder(FLANGE_DIA / 2, FLANGE_H, align=MIN)
    z += FLANGE_H
    # 45° lead-in cone (flange Ø -> stem Ø) so the flange presses through the hole
    leadin = Pos(0, 0, z) * Cone(FLANGE_DIA / 2, STEM_DIA / 2, LEADIN, align=MIN)
    cap = head + stem + flange + leadin
    cap.label = "button_cap"
    return cap


def gen_step():
    """Both cap variants side by side: the side-button cap (full Ø8.5 snap flange)
    and the center cap (reduced Ø6 flange)."""
    side = make_cap(center=False)
    center = Pos(HEAD_DIA + 3, 0, 0) * make_cap(center=True)
    return Compound(label="button_caps", children=[side, center])


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "button_cap.step")
    print("wrote button_cap.step")
