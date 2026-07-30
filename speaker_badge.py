"""Speaker badge enclosure — portrait two-piece shell. v2: 2.1" screen.

Outer: 64 x 124 x 14.5 mm — scaled from v1 (54 x 105) with the bigger screen to
keep the same visual balance (H/W ~1.94, same relative bezel frame and margins).
Round body bulge follows the screen. A webbing strap threads through a slot on
the top face and loops around an internal bar (no clips or screws). USB-C exits
the right edge, the micro SD slot the left edge. Three buttons sit on the front
face, on an arc below the screen.

The shell splits evenly at the mid-plane: the FRONT shell holds the front
layer (screen module, TP4056, SD); the BACK shell holds the back layer
(ESP32, battery). No internal shelf is needed. The mid-plane split also lets
the USB-C opening and the strap slot/bar sit centered in the thickness.

Bill of materials (see component_layout.py for the in-case fit check):
  - 2.1" round TFT, 360x360, on its own round PCB: glass Ø55.92, active area
    Ø52.92, PCB Ø59.24 + connector tab (67.47 total) — replaces v1's 1.73"
    AMOLED + separate 50x50 adapter board
  - ESP32-S3 N16R8 devkit, 28.2 x 64.4 x 4.8 mm
  - LiPo 503040, 40 x 30 x 5 mm, 600 mAh
  - TP4056 + 5V boost, USB-C, 18 x 23.6 mm  (the charge port)
  - micro SD module, 17.8 x 17.9 mm
  - 3 tactile buttons with printed caps (button_cap.py)
"""

import math

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Compound,
    Cone,
    Cylinder,
    Plane,
    Pos,
    Rectangle,
    RectangleRounded,
    Rotation,
    chamfer,
    extrude,
    fillet,
    mirror,
    offset,
)

# --- Outer envelope (portrait, with body bulge around screen) ---
W = 64.0                   # base width (X); floor set by the Ø59.24 screen PCB +
                           # walls (~0.3 mm/side — snug, like v1's adapter fit)
H = 124.0                  # body height (Y); scaled with the 2.1" screen to keep
                           # the v1 proportions (H/W ≈ 1.94). The ESP + battery
                           # stack (95.7) now has slack in the 115.2 mm cavity.
HEADER_H = 7.0             # solid top strip housing the strap slot + internal bar
BULGE_DIA = 72.0           # body bulges 4 mm proud of the base around the screen —
                           # same frame width beyond the bezel as v1 (~7.7 mm),
                           # scaled with the screen; base still 64 (holds the PCB)
CORNER_R = 4.0             # smoothing radius for outer silhouette
WALL = 1.8                 # thinned from 2.0 in v1 for module clearance; kept
T_FRONT = 7.25             # even split at the mid-plane (total 14.5 mm)
T_BACK = 7.25
TOTAL_T = T_FRONT + T_BACK
CAVITY_TOP = H / 2 - HEADER_H   # cavity stops here; header above stays solid

# --- Screen (2.1" round TFT 360x360 module: glass bonded on its own PCB) ---
# Per the "foot position chart": PCB Ø59.24 disc + a ~30.5 mm connector tab at
# the bottom (total PCB height 67.47); LCM glass Ø55.92; active area Ø52.92.
# AA / glass / PCB disc are concentric (side offsets are equal), so everything
# centers on (0, SCREEN_CY); only the tab hangs below the disc.
SCREEN_CUTOUT_DIA = 53.7   # covers the Ø52.92 active area + small margin
SCREEN_CY = 8.0            # below lanyard, sized to fit bulge (v1 forehead ratio)

# --- Bezel: 45° chamfer around the screen opening ---
# A chamfer (not a flat recess) so the front shell prints FACE-DOWN with no
# support: the bevel backs the lip the glass rests on, instead of leaving it
# floating over an undercut recess. 45° (= printable overhang); Ø48 at the face
# tapering to the Ø45 viewable opening.
BEZEL_CHAMFER = 1.5        # 45° chamfer leg: 1.5 mm deep and 1.5 mm radial

# --- Exterior edge fillet (rounded outer edges, mating face stays flat) ---
EDGE_FILLET = 1.5

# --- Strap mount (through-slot on the top face + SEPARATE drop-in wrap bar) ---
# The webbing drops through the slot, loops under the bar, and folds back up
# (sewn into a loop) — no clips or screws. The wrap bar is a SEPARATE part
# (wrap_bar.py — print it OR cut a Ø3 steel rod) that drops into a half-round
# cradle groove; each shell carries half the cradle, so closing the enclosure
# captures the bar. STRAP_FLOOR_Y keeps a thin floor above the cavity; the load
# runs bar -> cradle -> thick header side walls, not the floor.
STRAP_SLOT_X = 22.0        # along width, for ~20 mm webbing + threading tolerance
STRAP_SLOT_Z = 8.0         # along thickness — room for two strap passes + the bar
STRAP_FLOOR_Y = CAVITY_TOP + 1.0   # chamber floor, 1 mm above the cavity ceiling
STRAP_RIM_CHAMFER = 0.8    # ease the top-face entry edge (anti-wear)
STRAP_BAR_D = 3.0          # wrap-bar diameter (Ø3 printed bar or steel rod/pin)
STRAP_BAR_SPAN = 30.0      # cradle socket length (X); the ends (outboard of the
                           # Ø22 slot) groove ~4 mm into each header side wall
STRAP_BAR_Y = 49.3         # bar height (Y), suspended in the slot chamber
BAR_CRADLE_CLEAR = 0.2     # radial clearance: Ø3 bar in a Ø3.4 socket (drop-in fit)
BAR_LEN = STRAP_BAR_SPAN - 0.6     # separate bar part length (0.6 mm axial play)
STRAP_HEADER_W = 36.0      # the solid header is only this central block (carries the
                           # strap mount); top corners stay open so all 4 bosses match

# --- Closure: M2 countersunk (90° flat) head screw + M2 brass heat-set insert.
#     Lid (front): Ø2.4 clearance through-hole + Ø4.4 × 90° countersink so the
#       Ø3.8 flat head seats flush on the conical seat (self-centering; m2_screw.py).
#       Use an M2 × 10 mm screw (length includes the flush head).
#     Body (back): Ø3.2 blind hole for the insert (OD ~3.5, len 4.0), pressed in
#       from the seam; the screw threads into the insert's metal M2 bore. ---
SCREW_INSET = 4.0          # countersink rim (Ø4.4) sits ~1.8 mm off the edge; the
                           # Ø5.0 insert boss clears the 40 mm battery by ~0.5 mm.
                           # NB: a countersink wedges the thin corner wall outward
                           # (hoop stress) — drive to moderate torque, don't crank.
M2_CLEAR_DIA = 2.4         # M2 shaft clearance through the lid (ISO normal fit)
CSK_DIA = 4.4              # countersink rim Ø at the screen face (head Ø3.8 + margin
                           # → flush / slightly recessed flat head)
CSK_DEPTH = (CSK_DIA - M2_CLEAR_DIA) / 2   # 1.0 mm: 90° cone meets the clearance hole
INSERT_HOLE_DIA = 3.2      # melt hole for the M2 heat-set insert (insert OD ~3.5)
INSERT_HOLE_DEPTH = 5.0    # blind (stops ~0.45 mm short of the outer wall); insert is
                           # 4.0 mm, the rest is shaft clearance
INSERT_LEADIN_DIA = 3.8    # shallow lead-in counterbore so the insert starts square
INSERT_LEADIN_DEPTH = 0.6
BOSS_OD = 5.0              # ≥0.9 mm wall around the insert; merges into the perimeter wall

# Edge ports/buttons are given in GLOBAL z (0 = front face); they straddle the
# mid-plane seam so each shell cuts its own portion. The back shell is FLIPPED
# about the vertical (Y) axis to close the case, which swaps X (left<->right), so
# its cuts are mirrored in X and use native z = TOTAL_T - global z. (A flip, not a
# reflection — you can't print a mirrored part.)
USB_GZ = TOTAL_T / 2       # centered in the thickness (straddles the seam)
USB_CY = -41.5             # height on the RIGHT (+X) edge — follows the TP4056 center
                           # (the USB-C connector is on that board).
USB_W = 11.0               # opening width (now along Y — the connector width)
USB_H = 6.5                # opening height (along Z) — clears the plug overmold

SD_GZ = 5.0                # SD card-slot height (SD module seats near the front)
SD_CY = -41.5              # aligned to the SD module center (SD_CXY[1])
SD_SLOT_W = 13.0           # along Y (card width)
SD_SLOT_H = 3.0            # along Z

# --- Front-face buttons (3 equal caps on an arc following the screen curve) ---
# THROUGH-HOLES only; the caps print separately and drop in (see button_cap.py).
# Through-holes don't bridge, so the lid still prints face-down with no support.
# Centers lie on a circle of radius BTN_ARC_R about the screen center; the side
# pair sits BTN_ARC_ANG up from bottom-dead-center, so the trio follows the curve.
# Fit check (component_layout / the design notes): the two side buttons clear the
# TP4056 + SD boards by ~2 mm with a full 6x6 switch; the CENTER button sits over
# the TP4056 corner, so the board is nudged down (TP_CXY) and the center wants a
# compact (<=4x4) switch behind it.
BTN_HOLE_DIA = 7.0         # cap-stem through-hole (the visible opening)
BTN_CAP_HEAD = 9.0         # proud cap head Ø (identical for all three)
BTN_ARC_R = 42.0           # arc radius measured from the screen center (0, SCREEN_CY).
                           # Wider than a pure visual scale of v1: the 2.1" module's
                           # PCB tab reaches y=-29.9, so the center button (and the
                           # switch behind it) must sit fully below the tab.
BTN_ARC_ANG = 38.0         # side buttons sit this many degrees up from bottom
BTN_FLANGE_CLEAR = 9.0     # pocket walls are notched to this Ø around the SIDE caps
                           # so their Ø8 snap flange (button_cap.py) clears — the SD
                           # +y wall otherwise grazes the left flange by ~0.7 mm

# --- Internal retention (printed pockets/ribs; screen on a ledge + foam) ---
RIB_T = 1.6                # pocket / rib wall thickness
FIT_CLEAR = 0.5            # clearance around each module
POCKET_GAP = 0.8           # stop pocket walls short of the seam so the front and
                           # back shells' walls never butt together at the mid-plane
FRONT_POCKET_TOP = T_FRONT - POCKET_GAP
BACK_POCKET_TOP = T_BACK - POCKET_GAP

# Screen module (2.1" TFT). Thicknesses are ASSUMED (the foot-position chart
# gives no Z data) — confirm against the full datasheet before printing:
TFT_GLASS_DIA = 55.92      # LCM glass Ø (the bottom ledge to 57.58 is ignored by
                           # the placeholder; the bezel lip only meets the circle)
TFT_GLASS_T = 2.5          # ASSUMED typical TFT LCM thickness
TFT_PCB_DIA = 59.24        # round PCB the glass is bonded to
TFT_PCB_T = 1.6            # ASSUMED standard PCB
TFT_PCB_H = 67.47          # total PCB height incl. the bottom connector tab
TFT_TAB_W = 30.5           # tab width (23.88 connector zone + 2x3.3 shoulders)
TFT_RING_ID = TFT_PCB_DIA + 0.56        # PCB locating-ring inner diameter
# NB: the module's 10-pin P2.54 header solders through the tab — pin tails
# protrude past the seam into the back cavity's ESP<->battery gap (open space).
# Use a low-profile header or trim the tails.

# Module footprints (X, Y) and pocket centers (shared by both shells in XY)
ESP_W, ESP_H, ESP_CXY = 28.2, 64.4, (0.0, 22.3)      # back layer; top registers on header ceiling (4.8 mm thick)
BAT_W, BAT_H, BAT_CXY = 40.0, 30.0, (0.0, -45.2)     # back layer; bottom rests on perimeter wall
TP_W, TP_H, TP_CXY = 23.6, 18.0, (17.9, -41.5)       # front layer, lower-right, ROTATED 90°
                                                     # so its USB-C faces the right edge;
                                                     # +x registers on the perimeter wall.
                                                     # Low enough that the pocket's +y wall
                                                     # (top + 2.1) clears the screen PCB's
                                                     # tab, which hangs to y=-29.85.
SD_W, SD_H, SD_CXY = 17.8, 17.9, (-20.8, -41.5)      # front layer; -x registers on left perimeter
                                                     # (+y wall clears the PCB tab, as above)


def _outer_sketch():
    """Body silhouette: rounded base rectangle unioned with the screen bulge."""
    base = Rectangle(W, H)
    bulge = Pos(0, SCREEN_CY) * Circle(BULGE_DIA / 2)
    return fillet((base + bulge).vertices(), radius=CORNER_R)


def _cavity_sketch():
    """Interior cavity: inset silhouette. The solid header is only a CENTRAL block
    (STRAP_HEADER_W wide) that carries the strap mount; the top corners stay open
    so all four screw bosses stand in the cavity alike."""
    cav = offset(_outer_sketch(), -WALL)
    remove = Pos(0, CAVITY_TOP + H / 2) * Rectangle(STRAP_HEADER_W, H)
    return cav - remove


def _corners():
    for sx in (-1, 1):
        for sy in (-1, 1):
            yield sx * (W / 2 - SCREW_INSET), sy * (H / 2 - SCREW_INSET)


def _walls(w, h, center, z0, z1, sides, t=RIB_T, clear=FIT_CLEAR):
    """Pocket wall segments around a w*h footprint; `sides` picks which to add."""
    cx, cy = center
    iw, ih = w + 2 * clear, h + 2 * clear
    mid, dz = (z0 + z1) / 2, z1 - z0
    segs = []
    if "+x" in sides:
        segs.append(Pos(cx + iw / 2 + t / 2, cy, mid) * Box(t, ih + 2 * t, dz))
    if "-x" in sides:
        segs.append(Pos(cx - iw / 2 - t / 2, cy, mid) * Box(t, ih + 2 * t, dz))
    if "+y" in sides:
        segs.append(Pos(cx, cy + ih / 2 + t / 2, mid) * Box(iw + 2 * t, t, dz))
    if "-y" in sides:
        segs.append(Pos(cx, cy - ih / 2 - t / 2, mid) * Box(iw + 2 * t, t, dz))
    out = segs[0]
    for s in segs[1:]:
        out += s
    return out


def _pcb_ring():
    """Locating ring on the front-shell inner face around the screen module's
    Ø59.24 PCB disc (the glass is bonded to it, so locating the PCB locates the
    screen). Full pocket height so it captures the PCB at its seated depth. The
    bottom is opened for the connector tab, and the caller clips to the cavity
    (the disc is only ~0.3 mm/side off the perimeter wall, which registers X —
    this ring mostly survives as top/bottom arcs handling Y)."""
    h = FRONT_POCKET_TOP - WALL
    outer = Pos(0, SCREEN_CY, WALL) * extrude(Circle(TFT_RING_ID / 2 + RIB_T), h)
    inner = Pos(0, SCREEN_CY, WALL) * extrude(Circle(TFT_RING_ID / 2), h + 0.02)
    ring = outer - inner
    # Open the ring across the connector tab (plus clearance) at the disc bottom.
    ring -= Pos(0, SCREEN_CY - TFT_PCB_DIA / 2, WALL + h / 2) * Box(
        TFT_TAB_W + 2 * FIT_CLEAR + 2 * RIB_T, 16.0, h + 1.0
    )
    return ring


def _usb_cut(z):
    """USB-C opening through the RIGHT (+X) edge, at local z (thickness). Moved off
    the bottom edge so the wraparound label can run across the bottom + back."""
    return Pos(W / 2, USB_CY, z) * extrude(
        Plane.YZ * RectangleRounded(USB_W, USB_H, 1.0), WALL * 2, both=True
    )


def _sd_cut(z):
    """micro SD slot through the left edge, centered at local z."""
    return Pos(-W / 2, SD_CY, z) * extrude(
        Plane.YZ * RectangleRounded(SD_SLOT_W, SD_SLOT_H, 0.4), WALL * 2, both=True
    )


def button_centers():
    """The three button-cap centers (XY), on an arc below the screen: center button
    at bottom-dead-center, side pair BTN_ARC_ANG up from it. Shared by the shell
    holes and the cap placement (button_cap.py / the assembled views)."""
    a = math.radians(BTN_ARC_ANG)
    cx, cy = 0.0, SCREEN_CY
    return [
        (cx, cy - BTN_ARC_R),                                          # center (lowest)
        (cx + BTN_ARC_R * math.sin(a), cy - BTN_ARC_R * math.cos(a)),   # right
        (cx - BTN_ARC_R * math.sin(a), cy - BTN_ARC_R * math.cos(a)),   # left
    ]


def _button_holes():
    """Three equal Ø7 cap through-holes on the arc (front face, native z=0)."""
    holes = [Pos(bx, by, 0) * extrude(Circle(BTN_HOLE_DIA / 2), T_FRONT)
             for bx, by in button_centers()]
    out = holes[0]
    for h in holes[1:]:
        out += h
    return out


def _cavity_solid(thickness):
    """The hollow interior volume (the region subtracted to form the cavity). Used
    both to carve the shell and to CLIP internal pocket walls/ribs, so no internal
    feature can ever extend past the perimeter wall to the outer surface."""
    return Pos(0, 0, WALL) * extrude(_cavity_sketch(), thickness - WALL + 0.01)


def _shell_body(thickness):
    """Outer block with rounded exterior edge and a header-clipped cavity."""
    solid = extrude(_outer_sketch(), thickness)
    solid = fillet(solid.edges().group_by(Axis.Z)[0], radius=EDGE_FILLET)
    return solid - _cavity_solid(thickness)


def _add_strap_mount(solid, t):
    """Cut the top-face strap slot and the wrap-bar cradle, for a shell whose seam
    is at z=t. Slot and cradle are symmetric about the seam, so identical local
    coords serve both shells (the back is mirrored later). The wrap bar itself is a
    SEPARATE drop-in part (wrap_bar.py) — not split between the halves."""
    top = H / 2
    slot = Pos(0, (STRAP_FLOOR_Y + top + 1) / 2, t) * Box(
        STRAP_SLOT_X, (top + 1) - STRAP_FLOOR_Y, STRAP_SLOT_Z
    )
    slot = fillet(slot.edges().filter_by(Axis.Y), radius=3.0)   # rounded slot section
    solid -= slot

    # Ease the slot entry on the top face — the edge the strap folds over.
    rim = (
        solid.edges()
        .group_by(Axis.Y)[-1]                       # top face (y = H/2)
        .filter_by_position(Axis.X, -12, 12)        # the slot, not the outer
        .filter_by_position(Axis.Z, 2.5, t + 0.5)   # top-face perimeter
    )
    if rim:
        solid = chamfer(rim, length=STRAP_RIM_CHAMFER)

    # Wrap-bar cradle: a half-round groove along X at the seam. The separate bar
    # drops into this shell's half-trough; the other shell caps it into a full
    # socket. Cutting a full cylinder centered on the seam leaves each shell its
    # own half automatically. Only the ends (outboard of the open slot) have
    # header material to groove — the central span stays clear for the strap.
    cradle = Pos(0, STRAP_BAR_Y, t) * Rotation(0, 90, 0) * Cylinder(
        STRAP_BAR_D / 2 + BAR_CRADLE_CLEAR, STRAP_BAR_SPAN
    )
    return solid - cradle


def front_shell():
    """Front shell (z=0 exterior .. z=T_FRONT seam): screen + TP4056 + SD."""
    solid = _shell_body(T_FRONT)

    # Screen cutout + 45° chamfered bezel. The chamfer (not a flat recess) leaves
    # the glass-retaining lip backed by solid wall, so the shell prints face-down
    # with no support; the bevel also reads as a clean screen surround.
    solid -= Pos(0, SCREEN_CY, 0) * extrude(Circle(SCREEN_CUTOUT_DIA / 2), T_FRONT)
    solid -= Pos(0, SCREEN_CY, 0) * Cone(
        SCREEN_CUTOUT_DIA / 2 + BEZEL_CHAMFER, SCREEN_CUTOUT_DIA / 2, BEZEL_CHAMFER,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )

    # M2 clearance through-holes & 90° head countersinks
    for x, y in _corners():
        solid -= Pos(x, y, 0) * extrude(Circle(M2_CLEAR_DIA / 2), T_FRONT)
        # countersink: cone wide (Ø4.4) at the screen face, narrowing to the
        # clearance hole at CSK_DEPTH — a flush conical seat for the flat head.
        solid -= Pos(x, y, 0) * Cone(
            CSK_DIA / 2, M2_CLEAR_DIA / 2, CSK_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Screen locating ring + front-layer module pockets (walls stop short of seam).
    # Pocket walls are CLIPPED to the cavity so the corner-overlap padding can't push
    # a wall past the perimeter and poke out the outer edge face.
    cav = _cavity_solid(T_FRONT)
    solid += _pcb_ring() & cav
    solid += _walls(TP_W, TP_H, TP_CXY, WALL, FRONT_POCKET_TOP, ["-x", "+y", "-y"]) & cav  # USB exits +X; bracketed inboard + top/bottom
    solid += _walls(SD_W, SD_H, SD_CXY, WALL, FRONT_POCKET_TOP, ["+x", "+y", "-y"]) & cav  # card exits -X (left perimeter)
    # Notch the pocket walls around the SIDE caps so their snap flange (which
    # springs past the Ø7 hole onto the inner wall face) has room to seat. The
    # notch cylinders start above the floor and stay clear of the glass ring and
    # perimeter wall, so only wall material in the flange's path is removed.
    # (NB: subtract from `solid`, not from the `& cav` result — that is a
    # ShapeList, whose -= is a list set-difference, not a boolean cut.)
    for bx, by in button_centers()[1:]:
        solid -= Pos(bx, by, WALL) * extrude(
            Circle(BTN_FLANGE_CLEAR / 2), FRONT_POCKET_TOP - WALL
        )

    # Edge ports (this shell's portion; local z = global z)
    solid -= _usb_cut(USB_GZ)
    solid -= _sd_cut(SD_GZ)

    # Three button cap holes on an arc below the screen (caps drop in — button_cap.py).
    solid -= _button_holes()

    # Top-face strap slot + wrap-bar cradle
    solid = _add_strap_mount(solid, T_FRONT)

    return solid


def back_shell():
    """Back shell (z=0 exterior .. z=T_BACK seam): ESP32 + battery."""
    solid = _shell_body(T_BACK)

    cavity_depth = T_BACK - WALL
    for x, y in _corners():
        # Boss + blind hole for an M2 heat-set insert, pressed in from the seam.
        solid += Pos(x, y, WALL) * extrude(Circle(BOSS_OD / 2), cavity_depth)
        solid -= Pos(x, y, T_BACK - INSERT_HOLE_DEPTH) * extrude(
            Circle(INSERT_HOLE_DIA / 2), INSERT_HOLE_DEPTH + 0.01
        )
        solid -= Pos(x, y, T_BACK - INSERT_LEADIN_DEPTH) * extrude(
            Circle(INSERT_LEADIN_DIA / 2), INSERT_LEADIN_DEPTH + 0.01
        )

    # Back-layer module pockets (walls stop short of seam). ESP and battery
    # face each other across a clear gap with no divider — the gap doubles as
    # the JST-lead route. ESP top registers on the header ceiling; the battery
    # bottom rests on the perimeter wall. Walls/ribs are CLIPPED to the cavity so
    # the corner-overlap padding can't poke through the perimeter to the outside.
    cav = _cavity_solid(T_BACK)
    solid += _walls(ESP_W, ESP_H, ESP_CXY, WALL, BACK_POCKET_TOP, ["+x", "-x"]) & cav
    # Trim the ESP walls' -y corner padding out of the battery zone: _walls pads
    # wall ends by FIT_CLEAR + RIB_T (2.1 mm) but the ESP<->battery gap is only
    # 1.3 mm, so the stubs would poke ~0.8 mm into the battery footprint. Cut
    # them flush with the ESP clearance edge (keeps full corner support, leaves
    # the battery side ribs at x=±21.3 untouched).
    esp_wall_end = ESP_CXY[1] - ESP_H / 2 - FIT_CLEAR
    solid -= Pos(0, esp_wall_end - 1.5, (WALL + BACK_POCKET_TOP) / 2) * Box(
        2 * (ESP_W / 2 + FIT_CLEAR + RIB_T + 1.0), 3.0, BACK_POCKET_TOP - WALL
    )

    # Battery side ribs (+x / -x). Built explicitly rather than via _walls, and
    # stopped ~4 mm ABOVE the bottom insert bosses so the ribs don't run down
    # alongside the inserts (per the design review) — the bosses stand free for
    # clean heat-set access. The rib backs the upper ~2/3 of the battery's sides;
    # the bottom corners are located by the bosses + the perimeter wall. (Free rib
    # ends just add footprint loops to the floor face — verified NOT through-holes.)
    rib_x = BAT_W / 2 + FIT_CLEAR + RIB_T / 2
    rib_top = BAT_CXY[1] + BAT_H / 2 + FIT_CLEAR + RIB_T          # +y end (matches _walls)
    rib_bot = -(H / 2 - SCREW_INSET) + BOSS_OD / 2 + 4.0          # ~4 mm above the bosses
    for sx in (-1, 1):
        rib = Pos(sx * rib_x, (rib_top + rib_bot) / 2, (WALL + BACK_POCKET_TOP) / 2) * Box(
            RIB_T, rib_top - rib_bot, BACK_POCKET_TOP - WALL
        )
        solid += rib & cav

    # Edge ports. The back shell is flipped about Y when the case closes (x -> -x),
    # so its cuts are MIRRORED in X (about the YZ plane) to line up with the front
    # shell's ports after the flip. Native z = TOTAL_T - global z.
    solid -= mirror(_usb_cut(TOTAL_T - USB_GZ), about=Plane.YZ)
    solid -= mirror(_sd_cut(TOTAL_T - SD_GZ), about=Plane.YZ)

    # Top-face strap slot + wrap-bar cradle
    solid = _add_strap_mount(solid, T_BACK)

    return solid


def gen_step():
    front = front_shell()
    front.label = "front_shell"

    back = back_shell()
    back = Pos(BULGE_DIA + 8, 0, 0) * back
    back.label = "back_shell"

    return Compound(label="speaker_badge", children=[front, back])


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "speaker_badge.step")
    print("wrote speaker_badge.step")
