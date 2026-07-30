"""Assembled enclosure with the four M2 countersunk screws + heat-set inserts and
the drop-in wrap bar, to check the lid countersink, shaft/insert engagement, and
the bar seated in its cradle."""

from build123d import Compound, Plane, Pos, Rotation, mirror

import button_cap as bc
import insert as ins
import m2_screw as ps
import speaker_badge as sb
import wrap_bar as wb

L_TOT = ps.SHANK_LEN + ps.HEAD_H
# Seat the countersunk head on the conical seat: the Ø3.8 head meets the Ø4.4
# countersink where their diameters match, recessing the head top by
# (CSK_DIA - HEAD_DIA)/2 below the screen face.
SEAT = (sb.CSK_DIA - ps.HEAD_DIA) / 2


def _corners():
    for sx in (-1, 1):
        for sy in (-1, 1):
            yield sx * (sb.W / 2 - sb.SCREW_INSET), sy * (sb.H / 2 - sb.SCREW_INSET)


def _screws():
    screw = ps.gen_step()
    # flip head-down, head recessed on the counterbore floor, shaft into +z
    return [Pos(cx, cy, SEAT) * Pos(0, 0, L_TOT) * Rotation(180, 0, 0) * screw
            for cx, cy in _corners()]


def _inserts():
    insert = ins.gen_step()
    # seated in each boss, entering at the seam (z=7.25), running into the body
    return [Pos(cx, cy, sb.T_FRONT) * insert for cx, cy in _corners()]


def gen_step():
    """The assembled badge, re-posed for review: standing upright on z=0 with the
    strap header at the top and the screen facing the viewer (the shells' native
    build frame lies flat with the screen face down)."""
    # Bake the pose into each child: the STEP exporter re-roots the assembly and
    # drops a transform left on the root Compound itself.
    pose = Pos(0, 0, sb.H / 2) * Rotation(0, 0, 180) * Rotation(90, 0, 0)
    posed = []
    for child in _children():
        moved = pose * child
        moved.label = child.label
        posed.append(moved)
    return Compound(label="screw_assembly", children=posed)


def _children():
    front = sb.front_shell()
    front.label = "front_shell"
    # Close the case by FLIPPING the back shell about Y (180°), as you would
    # physically — not mirroring it. (x -> -x; the back's ports are pre-mirrored.)
    back = Pos(0, 0, sb.TOTAL_T) * Rotation(0, 180, 0) * sb.back_shell()
    back.label = "back_shell"
    children = [front, back]
    for i, s in enumerate(_screws()):
        s.label = f"screw_{i}"
        children.append(s)
    for i, s in enumerate(_inserts()):
        s.label = f"insert_{i}"
        children.append(s)
    # Drop-in wrap bar, seated in the cradle: axis along X, centered on the seam.
    bar = (Pos(0, sb.STRAP_BAR_Y, sb.TOTAL_T / 2) * Rotation(0, 90, 0)
           * Pos(0, 0, -wb.LEN / 2) * wb.gen_step())
    bar.label = "wrap_bar"
    children.append(bar)
    # Button caps seated in their front-face holes: the head sits proud on the
    # outer face (native z<0 side), the stem passes through the Ø7 hole. The
    # first button_centers() entry is the CENTER (flangeless) cap.
    for i, (bx, by) in enumerate(sb.button_centers()):
        cap = Pos(bx, by, -bc.HEAD_H) * bc.make_cap(center=(i == 0))
        cap.label = f"button_cap_{'center' if i == 0 else i}"
        children.append(cap)
    return children


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "screw_assembly.step")
    print("wrote screw_assembly.step")
