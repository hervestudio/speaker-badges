"""Exploded view of the current design — all parts pulled apart along Z in
assembly order.

Bottom to top: back shell, 4 heat-set inserts (into the bosses), drop-in wrap bar
(into the header cradle), ESP32 + LiPo (back layer), TP4056 + SD (front layer),
screen adapter, AMOLED glass, front shell (lid, screen up), 4 M2 countersunk
screws (drop in from the screen face). Component bodies are simplified placeholders.
"""

from build123d import Box, Compound, Cylinder, Plane, Pos, Rotation, mirror

import button_cap as bc
import insert as ins
import m2_screw as ms
import speaker_badge as sb
import wrap_bar as wb

SCY = sb.SCREEN_CY


def _corners():
    for sx in (-1, 1):
        for sy in (-1, 1):
            yield sx * (sb.W / 2 - sb.SCREW_INSET), sy * (sb.H / 2 - sb.SCREW_INSET)


def _box(w, h, d, center, label):
    part = Pos(*center) * Box(w, h, d)
    part.label = label
    return part


def gen_step():
    parts = []

    # Back shell (native orientation, cavity opening up) at the bottom
    back = sb.back_shell()
    back.label = "back_shell"
    parts.append(back)

    # Heat-set inserts, lifted just above their bosses
    insert = ins.gen_step()
    for i, (cx, cy) in enumerate(_corners()):
        part = Pos(cx, cy, 13) * insert
        part.label = f"insert_{i}"
        parts.append(part)

    # Drop-in wrap bar, lifted above the header cradle (axis along X)
    bar = (Pos(0, sb.STRAP_BAR_Y, 18) * Rotation(0, 90, 0)
           * Pos(0, 0, -wb.LEN / 2) * wb.gen_step())
    bar.label = "wrap_bar"
    parts.append(bar)

    # Back layer
    parts.append(_box(sb.ESP_W, sb.ESP_H, 5.0, (0, 10, 26), "esp32_s3"))
    parts.append(_box(sb.BAT_W, sb.BAT_H, 5.0, (0, -32, 26), "lipo_503040"))

    # Front layer
    parts.append(_box(sb.TP_W, sb.TP_H, 5.0, (1.5, -35, 42), "tp4056_boost"))
    parts.append(_box(sb.SD_W, sb.SD_H, 4.0, (-16, -32, 42), "sd_module"))
    parts.append(_box(50, 50, 3.1, (0, SCY, 56), "screen_adapter"))

    glass = Pos(0, SCY, 64) * Cylinder(48.4 / 2, 2.21)
    glass.label = "amoled_glass"
    parts.append(glass)

    # Front shell, flipped about Y (as it closes onto the back) so the screen faces up
    front = Pos(0, 0, 82) * Rotation(0, 180, 0) * sb.front_shell()
    front.label = "front_shell"
    parts.append(front)

    # M2 cap screws above the screen face (head up, tip pointing down into the lid)
    screw = ms.gen_step()
    for i, (cx, cy) in enumerate(_corners()):
        part = Pos(cx, cy, 88) * screw
        part.label = f"screw_{i}"
        parts.append(part)

    # Button caps above their holes (head up, stem pointing down into the lid).
    # The shell is flipped about Y, so hole x flips too; first entry = CENTER cap.
    for i, (bx, by) in enumerate(sb.button_centers()):
        cap = Pos(-bx, by, 88) * Rotation(0, 180, 0) * bc.make_cap(center=(i == 0))
        cap.label = f"button_cap_{'center' if i == 0 else i}"
        parts.append(cap)

    return Compound(label="badge_exploded", children=parts)


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "exploded_view.step")
    print("wrote exploded_view.step")
