"""Assembled enclosure with the four M2 countersunk screws + heat-set inserts and
the drop-in wrap bar, to check the lid countersink, shaft/insert engagement, and
the bar seated in its cradle."""

from build123d import Box, Compound, Cylinder, Plane, Pos, Rotation, mirror

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
    children += _components()
    return children


def _components():
    """The electronics, as simplified placeholder bodies in their seated
    positions (global frame: front face z=0, seam z=T_FRONT, back z=TOTAL_T).

    FRONT layer stacks off the front-shell floor (z=WALL): the AMOLED glass
    rests on the bezel lip, its adapter board directly behind it; the TP4056
    and SD boards sit on the floor. BACK layer stacks off the back-shell
    floor, which lands at z = TOTAL_T - WALL once the shell is flipped: the
    ESP32 and battery hang from it toward the seam. XY centers come straight
    from the pocket layout in speaker_badge.py (all the flip-sensitive ones
    are on x=0, so the back shell's x-mirror changes nothing).
    """

    def _box(w, h, t, cx, cy, z0, label):
        part = Pos(cx, cy, z0 + t / 2) * Box(w, h, t)
        part.label = label
        return part

    glass_t, adapter_t, board_t, esp_t, bat_t = 2.21, 3.1, 4.0, 4.8, 5.0
    back_floor = sb.TOTAL_T - sb.WALL

    glass = Pos(0, sb.SCREEN_CY, sb.WALL + glass_t / 2) * Cylinder(48.4 / 2, glass_t)
    glass.label = "amoled_glass"
    return [
        glass,
        _box(50, 50, adapter_t, 0, sb.SCREEN_CY, sb.WALL + glass_t, "screen_adapter"),
        _box(sb.TP_W, sb.TP_H, board_t, *sb.TP_CXY, sb.WALL, "tp4056_boost"),
        _box(sb.SD_W, sb.SD_H, board_t, *sb.SD_CXY, sb.WALL, "sd_module"),
        _box(sb.ESP_W, sb.ESP_H, esp_t, *sb.ESP_CXY, back_floor - esp_t, "esp32_s3"),
        _box(sb.BAT_W, sb.BAT_H, bat_t, *sb.BAT_CXY, back_floor - bat_t, "lipo_503040"),
    ]


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "screw_assembly.step")
    print("wrote screw_assembly.step")
