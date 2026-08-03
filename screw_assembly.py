"""Assembled enclosure with the four M2 countersunk screws + heat-set inserts and
the drop-in wrap bar, to check the lid countersink, shaft/insert engagement, and
the bar seated in its cradle."""

from build123d import Box, Compound, Cylinder, Plane, Pos, RectangleRounded, Rotation, extrude, mirror

import button_cap as bc
import insert as ins
import m2_screw as ps
import screw_cap as sc
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
        # au repos, le plongeur porte le capuchon (face externe a cap_seat_z)
        cap = Pos(bx, by, bc.cap_seat_z()) * bc.make_cap(center=(i == 0))
        cap.label = f"button_cap_{'center' if i == 0 else i}"
        children.append(cap)
        if sb.BTN_STYLE == "ring":
            ring = Pos(bx, by, -(bc.RING_H - sb.BTN_RING_SEAT_DEPTH)) * bc.make_ring()
            ring.label = f"button_ring_{i}"
            children.append(ring)
    # capuchons decoratifs colles sur les tetes de vis (dans leurs lamages)
    for i, (cx, cy) in enumerate(_corners()):
        cap = Pos(cx, cy, sb.SCREWCAP_SEAT_DEPTH) * Rotation(0, 180, 0) * sc.make_cap()
        cap.label = f"screw_cap_{i}"
        children.append(cap)
    children += _components()
    return children


def _components():
    """The electronics, as simplified placeholder bodies in their seated
    positions (global frame: front face z=0, seam z=T_FRONT, back z=TOTAL_T).

    FRONT layer stacks off the front-shell floor (z=WALL): the TFT glass
    rests on the bezel lip with its carrier PCB directly behind it; the TP4056
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

    def _rbox(w, h, t, cx, cy, z0, label, r=1.5):
        """Comme _box mais avec des coins arrondis (PCB reels — la TP4056 se
        loge dans le coin arrondi de la cavite grace a eux)."""
        part = Pos(cx, cy, z0) * extrude(RectangleRounded(w, h, r), t)
        part.label = label
        return part

    board_t, esp_t, bat_t = 4.0, 4.8, 5.0
    back_floor = sb.TOTAL_T - sb.WALL

    # 2.1" TFT module: glass disc bonded on a round PCB with a connector tab.
    glass = (Pos(0, sb.SCREEN_CY, sb.WALL + sb.TFT_GLASS_T / 2)
             * Cylinder(sb.TFT_GLASS_DIA / 2, sb.TFT_GLASS_T))
    glass.label = "tft_glass"
    pcb_z = sb.WALL + sb.TFT_GLASS_T
    pcb = (Pos(0, sb.SCREEN_CY, pcb_z + sb.TFT_PCB_T / 2)
           * Cylinder(sb.TFT_PCB_DIA / 2, sb.TFT_PCB_T))
    tab_h = sb.TFT_PCB_H - sb.TFT_PCB_DIA
    tab_cy = sb.SCREEN_CY - sb.TFT_PCB_DIA / 2 - tab_h / 2 + 1.0  # 1 mm overlap into the disc
    pcb += (Pos(0, tab_cy, pcb_z + sb.TFT_PCB_T / 2)
            * Box(sb.TFT_TAB_W, tab_h + 2.0, sb.TFT_PCB_T))
    pcb.label = "tft_pcb"
    return [
        glass,
        pcb,
        # largeur reduite a la poche resserree (cloison -x rapprochee de 1.5) :
        # la carte reelle s'y ajuste serree entre -16.5 et +7.0
        # PCB sureleve de 2.2 (il repose sur le muret support + le bord bas de
        # l'ouverture USB) ; l'espace dessous loge connecteur et composants
        _rbox(sb.TP_W - 1.5, sb.TP_H, 1.6, sb.TP_CXY[0] + 0.75,
              sb.TP_CXY[1], sb.WALL + 2.2, "tp4056_boost"),
        _box(sb.ESP_W, sb.ESP_H, esp_t, *sb.ESP_CXY, back_floor - esp_t, "esp32_s3"),
        # batterie reelle : legerement plus etroite que la poche centree de
        # BAT_POCKET_W (34.5) entre les deux nervures symetriques
        _box(sb.BAT_POCKET_W - 1.0, sb.BAT_H, bat_t, *sb.BAT_CXY,
             back_floor - bat_t, "lipo_503040"),
    ]


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "screw_assembly.step")
    print("wrote screw_assembly.step")
