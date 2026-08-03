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
STRAP_BAR_Y = H / 2 - 3.2  # bar height (Y), suspended in the slot chamber, 3.2 mm
                           # under the top face (v1 relation). Was hardcoded 49.3
                           # (a v1 value): after the v2 rescale (H 105 -> 124) the
                           # cradle was cutting BELOW the chamber, into the cavity
                           # void — the sockets had silently vanished.
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
SCREW_INSET = 7.0          # rentre de 4.0 -> 7.0 (revue capuchons decoratifs) :
                           # les faux-caps Ø10 doivent reposer sur la zone PLATE de
                           # la face (le conge d'arete EDGE_FILLET=1.5 mange 1.5 mm
                           # au bord). La poche batterie resserree (34.5) laisse
                           # largement la place aux bosses d'inserts plus interieurs.
                           # Bonus : plus de matiere autour du fraisage (hoop stress).
# --- Capuchons decoratifs de vis (facon mockup : cercle + carre en relief) ---
# Colles par-dessus les tetes M2 apres montage ; un lamage de centrage Ø10.2
# est fraise dans la face avant autour de chaque fraisage de vis.
SCREWCAP_DIA = 8.0         # reduit de 20% (revue : Ø10 trop grand)
SCREWCAP_SEAT_DIA = 8.2    # lamage d'encastrement (capuchon Ø8 legerement rentre)
SCREWCAP_SEAT_DEPTH = 0.3
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
USB_CX = 0.0               # ouverture CENTREE sur la tranche basse du badge.
                           # La carte TP4056 (horizontale, USB-C sur le long bord
                           # bas) se decale en consequence : son connecteur est a
                           # +5.5 mm du centre de la carte (il commence a 13 mm du
                           # bord gauche, largeur ~9 mm — cotes mesurees).
TP_USB_OFF = 5.5           # centre du connecteur - centre de la carte (le long du bord)
USB_W = 9.0                # largeur d'ouverture (X) — retrecie de 2 mm depuis la
                           # DROITE vue de face (revue impression : trop de jeu a
                           # droite du connecteur reel)
USB_OPEN_CX = USB_CX + 1.0 # centre de l'OUVERTURE : 2 mm repris sur le bord cote
                           # x negatif uniquement (verifie par Romain sur piece) ;
                           # la carte TP reste calee sur USB_CX
USB_H = 6.5                # opening height (along Z) — clears the plug overmold

# (module SD supprime — plus de fente sur le bord gauche ; le stockage interne
# de 16 Mo suffit. Seule subsiste la paroi +y de son ancienne poche, qui sert
# aussi de butee basse a l'ecran.)

# --- Front-face buttons (3 equal caps on an arc following the screen curve) ---
# THROUGH-HOLES only; the caps print separately and drop in (see button_cap.py).
# Through-holes don't bridge, so the lid still prints face-down with no support.
# Centers lie on a circle of radius BTN_ARC_R about the screen center; the side
# pair sits BTN_ARC_ANG up from bottom-dead-center, so the trio follows the curve.
# Fit check (component_layout / the design notes): the two side buttons clear the
# TP4056 + SD boards by ~2 mm with a full 6x6 switch; the CENTER button sits over
# the TP4056 corner, so the board is nudged down (TP_CXY) and the center wants a
# compact (<=4x4) switch behind it.
BTN_HOLE_DIA = 8.8         # front-face through-hole. Sized so the 6x6 switch
                           # itself (diagonal 8.49) inserts THROUGH it from the
                           # outside into its cradle; the Ø13.5 cap head covers
                           # the opening. Wall thickness only — the cradle's
                           # backer plate behind stays solid.
BTN_CAP_HEAD = 13.5        # cap head Ø (identical for all three; 1.5x the v2 Ø9)
# Puits anti-arrachement : une collerette RAPPORTEE (anneau imprime a plat,
# button_cap.py make_ring) se colle dans un lamage de centrage autour de chaque
# trou. Le capuchon affleure le sommet de l'anneau (0.05 en retrait) : rien ne
# depasse, aucune prise pour l'arracher. (Un anneau integre a la coque rendrait
# l'impression face-contre-plateau impossible sans supports.)
BTN_RING_SEAT_DIA = 16.7   # lamage de centrage (anneau Ø16.5 + 0.1/cote)
BTN_RING_SEAT_DEPTH = 0.3  # laisse 1.5 mm de paroi sous le lamage
# Style RETENU (revue 2026-07-31) : "flush" — pas de collerette, lamage Ø14 x 1.0
# directement dans la paroi (anneau restant 0.8) + tete amincie a 1.2 qui ne
# depasse que de ~0.55 mm de la facade (bord arrondi, aucune prise d'arrachement).
# L'alternative "ring" (puits a collerette rapportee) reste disponible via ce
# parametre — voir compare_buttons.py pour le comparatif.
BTN_STYLE = "flush"
BTN_FLUSH_CB_DIA = 14.0
BTN_FLUSH_CB_DEPTH = 1.0
BTN_ARC_R = 41.5           # arc radius measured from the screen center (0, SCREEN_CY).
                           # Wider than a pure visual scale of v1: the 2.1" module's
                           # PCB tab reaches y=-29.9, so the center button (and the
                           # switch behind it) must sit fully below the tab.
BTN_ARC_ANG = 28.5         # side buttons sit this many degrees up from bottom.
                           # Narrower than v1's 38° to compensate for the larger R:
                           # neighbor spacing 2*R*sin(ANG/2) ~ 20.4 mm, matching
                           # v1's tight cluster (20.2). Sides land at (±19.8,-28.5)
                           # — switches (6x6) clear the PCB tab (|x|>16.8, and the
                           # center trio sits fully below y=-29.9).
# --- Tactile-switch cradles (6x6x5.0 switches, one behind each cap hole) ---
# The switch lies FLAT against the inner wall face, plunger poking into the
# Ø4.6 hole; a printed cradle grips the body, a solid printed backer plate
# behind it takes the press force. Everything lives in the FRONT shell, well
# clear of the seam and the battery. The switch slides in from -y (over a small
# retention bump); wire/leg notches open the +-x walls. See button_cap.py for
# the cap that glues onto the plunger tip.
SW_BODY = 6.0              # switch body footprint (6x6)
SW_BODY_T = 3.6            # body depth; 6x6x5.0 = 3.6 body + 1.4 plunger
SW_PLUNGER_L = 1.4
SW_CLEAR = 0.15            # cradle clearance per side around the body
SW_SEAT_GAP = 0.1          # body front face floats this far off the inner wall
SW_WALL_Z1 = WALL + SW_SEAT_GAP + SW_BODY_T + 0.1    # cradle wall top (5.6)
SW_LEG_NOTCH = 5.6         # leg/wire opening width in the +-x cradle walls
# Keep-out around the screen PCB tab (hangs to y=-29.9, x +-15.25, sits at
# z~4.3..5.9 with header pins behind): cradle/backer material encroaching on it
# is trimmed above this z, leaving full-height walls only where safe.
SW_TAB_KEEPOUT_X = 15.45   # tab half-width + 0.2 clearance
SW_TAB_KEEPOUT_Y = -30.1   # keep-out applies above this y
SW_TAB_KEEPOUT_Z = 4.2     # ...and above this z (tab glass side starts ~4.3)

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
                                                     # (BAT_W = enveloppe nominale, informative)
BAT_POCKET_W = 34.5        # largeur INTERIEURE entre les deux nervures batterie,
                           # centree sur x=0 (revue annotee : la batterie reelle est
                           # plus etroite que l'enveloppe nominale 503040)
TP_W, TP_H = 24.0, 18.0                              # cotes MESUREES de la carte reelle
TP_CXY = (USB_CX - TP_USB_OFF, -50.9)                # front layer, bas-centre, HORIZONTALE :
                                                     # decalee de -5.5 pour que le connecteur
                                                     # tombe pile au centre du badge. Elle
                                                     # s'appuie contre la paroi BASSE (bord
                                                     # inferieur a -59.9, 0.3 du mur),
                                                     # connecteur vers le bas ; bracketee sur
                                                     # les deux flancs + le haut.
SD_W, SD_H, SD_CXY = 17.8, 17.9, (-20.8, -41.5)      # empreinte de l'EX-poche SD : sert encore
                                                     # a positionner sa paroi +y, conservee
                                                     # comme butee basse de l'ecran
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
    """USB-C opening through the BOTTOM (-Y) edge, at local z (thickness) —
    both side edges of the badge stay smooth."""
    return Pos(USB_OPEN_CX, -H / 2, z) * extrude(
        Plane.XZ * RectangleRounded(USB_W, USB_H, 1.0), WALL * 2, both=True
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
    """Three equal Ø8.8 switch-insertion holes on the arc (front face, native
    z=0). WALL-deep only: they must NOT pierce the cradle backer plates."""
    holes = [Pos(bx, by, 0) * extrude(Circle(BTN_HOLE_DIA / 2), WALL + 0.2)
             for bx, by in button_centers()]
    out = holes[0]
    for h in holes[1:]:
        out += h
    return out


def _switch_keepouts():
    """Clearance envelope of each seated switch (body + -y insertion path), cut
    from the shell AFTER the TP/SD pocket walls are added: their +y walls
    otherwise run straight through the side switches. The cradles (added after
    this cut) rebuild clean walls around the openings."""
    hw = SW_BODY / 2 + SW_CLEAR
    # base des coupes exactement au plancher (pas de morsure), deborde en haut
    ko_h = SW_WALL_Z1 - WALL + 0.2
    ko_mid = WALL + ko_h / 2
    out = None
    for bx, by in button_centers():
        # wide enough for the gull-wing legs + wire bends (the cradle walls,
        # re-added after this cut, rebuild everything solid except the notches)
        ko = Pos(bx, by - 1.5, ko_mid) * Box(
            2 * hw + 2 * RIB_T + 1.0, 2 * hw + 3.0, ko_h)
        out = ko if out is None else out + ko
    return out


def _switch_cradles():
    """Printed cradles holding the three 6x6x5 tactile switches against the inner
    wall face (plunger toward the face). The switch inserts from the OUTSIDE,
    straight through the Ø8.8 face hole (6x6 body diagonal = 8.49), so the
    cradle is closed on all 4 sides. Per switch: 4 walls around the body,
    leg/wire notches through the +-x walls, and a SOLID backer plate behind the
    body that takes the press force. Material near the screen PCB tab is trimmed
    by a keep-out cut (full-height walls remain only where safe)."""
    hw = SW_BODY / 2 + SW_CLEAR              # pocket half-width (3.15)
    ow = hw + RIB_T                          # outer half-width
    z0, z1 = WALL, SW_WALL_Z1
    roof_z1 = T_FRONT - 0.1
    out = None
    for bx, by in button_centers():
        walls = Pos(bx, by, (z0 + z1) / 2) * Box(2 * ow, 2 * ow, z1 - z0)
        walls -= Pos(bx, by, (z0 + z1) / 2) * Box(2 * hw, 2 * hw, z1 - z0 + 0.02)
        # leg/wire notches through both x walls
        for sgn in (-1, 1):
            walls -= Pos(bx + sgn * (hw + RIB_T / 2), by, (z0 + z1) / 2) * Box(
                RIB_T + 0.02, SW_LEG_NOTCH, z1 - z0 + 0.02)
        # solid backer plate behind the body (press-force reaction)
        roof = Pos(bx, by, (z1 + roof_z1) / 2) * Box(2 * ow, 2 * ow, roof_z1 - z1)
        cradle = walls + roof
        # fentes passe-pattes dans la plaque : les pattes du switch, repliees
        # vers l'arriere le long du corps, debouchent a l'interieur du boitier
        # -> soudure APRES insertion, bien plus simple. Le centre de la plaque
        # (ou s'appuie le corps) reste plein.
        for sgn in (-1, 1):
            # la fente traverse le bord exterieur de la plaque (sinon il reste
            # une lamelle fantome de 0.1 mm le long du bord)
            cradle -= Pos(bx + sgn * 3.65, by, (z1 + roof_z1) / 2) * Box(
                3.3, 7.0, roof_z1 - z1 + 0.2)
        out = cradle if out is None else out + cradle
    # trim whatever encroaches on the screen PCB tab envelope
    out -= Pos(0, SW_TAB_KEEPOUT_Y + 60, SW_TAB_KEEPOUT_Z + (T_FRONT - SW_TAB_KEEPOUT_Z) / 2 + 0.5) * Box(
        2 * SW_TAB_KEEPOUT_X, 120, T_FRONT - SW_TAB_KEEPOUT_Z + 1.0)
    # ...and on the TP4056 / SD module envelopes (+0.2 clearance): the side
    # cradles' -y corner posts otherwise dip ~0.7 mm into the board tops
    for w, h, (cx, cy) in ((TP_W, TP_H, TP_CXY), (SD_W, SD_H, SD_CXY)):
        out -= Pos(cx, cy, T_FRONT / 2) * Box(w + 0.4, h + 0.4, T_FRONT + 1.0)
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

    # M2 clearance through-holes & 90° head countersinks + lamage du capuchon
    for x, y in _corners():
        solid -= Pos(x, y, 0) * extrude(Circle(M2_CLEAR_DIA / 2), T_FRONT)
        # countersink: cone wide (Ø4.4) at the screen face, narrowing to the
        # clearance hole at CSK_DEPTH — a flush conical seat for the flat head.
        solid -= Pos(x, y, 0) * Cone(
            CSK_DIA / 2, M2_CLEAR_DIA / 2, CSK_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # Lamage d'encastrement du capuchon decoratif + MEMBRANE sacrificielle
        # d'une couche fermant l'ouverture du fraisage au fond de la poche :
        # le plafond du lamage ponte sur un disque plein (impression propre).
        # A percer apres impression (la pointe d'une vis M2 suffit).
        solid -= Pos(x, y, 0) * extrude(Circle(SCREWCAP_SEAT_DIA / 2), SCREWCAP_SEAT_DEPTH)
        solid += Pos(x, y, SCREWCAP_SEAT_DEPTH) * extrude(
            Circle(CSK_DIA / 2 + 0.2), 0.2)

    # Screen locating ring + front-layer module pockets (walls stop short of seam).
    # Pocket walls are CLIPPED to the cavity so the corner-overlap padding can't push
    # a wall past the perimeter and poke out the outer edge face.
    cav = _cavity_solid(T_FRONT)
    solid += _pcb_ring() & cav
    # TP4056 horizontale bas-centre : ouverte vers -y (l'USB-C sort par la paroi
    # basse, qui sert aussi de registre). Revue montage :
    #  - cloison "gauche vue de l'interieur" (natif -x) RAPPROCHEE de 1.5 mm
    #    (la carte reelle est un peu plus etroite que l'enveloppe 24 : ajustage serre)
    #  - le mur du haut est remplace par DEUX FREINS de 5 mm (a 2 mm de chaque
    #    bord de la carte) : le milieu reste ouvert pour souder les fils.
    tp_l = TP_CXY[0] - TP_W / 2
    tp_r = TP_CXY[0] + TP_W / 2
    tp_t = TP_CXY[1] + TP_H / 2
    zmid = (WALL + FRONT_POCKET_TOP) / 2
    zh = FRONT_POCKET_TOP - WALL
    wall_face_l = tp_l + 1.0  # etait tp_l - 0.5 : rapprochee de 1.5
    solid += (Pos(wall_face_l - RIB_T / 2, TP_CXY[1], zmid)
              * Box(RIB_T, TP_H + 2 * RIB_T, zh)) & cav
    solid += (Pos(tp_r + FIT_CLEAR + RIB_T / 2, TP_CXY[1], zmid)
              * Box(RIB_T, TP_H + 2 * RIB_T, zh)) & cav
    # Support sous la carte : un muret dont la hauteur egale EXACTEMENT la
    # distance plancher -> bas de l'ouverture USB (parametrique : 2.2 mm), pour
    # que la carte repose a plat (muret a l'arriere + bord bas de l'ouverture
    # cote connecteur) sans jamais etre de travers. Place sous la bande du bord
    # haut de la carte (zone nue du PCB), juste sous les freins.
    usb_bot_h = (USB_GZ - USB_H / 2) - WALL  # 2.2
    # (descendu de 5 mm vers le port USB pour degager la zone de soudure)
    solid += (Pos(-4.75, tp_t - 5.8, WALL + usb_bot_h / 2)
              * Box(19.0, 1.6, usb_bot_h)) & cav
    # freins de 5 mm a 2 mm des bords, descendus de 0.5 mm : leur face tombe
    # EXACTEMENT au ras du bord haut de la carte (18.0 mm mesures) — contact
    # affleurant, la carte est tenue sans interference. (1 mm l'aurait bloquee.)
    # (frein GAUCHE decale de +2 mm vers la droite — revue soudure ; le droit
    # reste a 2 mm du bord droit)
    for x0 in (tp_l + 2.0 + 2.0, tp_r - 2.0 - 5.0):
        solid += (Pos(x0 + 2.5, tp_t + FIT_CLEAR + RIB_T / 2 - 0.5, zmid)
                  * Box(5.0, RIB_T, zh)) & cav
    # Ex-poche SD : seule la paroi +y est conservee — elle sert de butee basse
    # a l'ecran (module SD abandonne, fente laterale supprimee).
    solid += _walls(SD_W, SD_H, SD_CXY, WALL, FRONT_POCKET_TOP, ["+y"]) & cav
    # Switch cradles + backer plates behind the three cap holes (the old snap-
    # flange clearance notches are gone: the new caps have no flange). First
    # open the switch envelopes through the TP/SD pocket walls, then add the
    # cradles, which rebuild clean walls around the openings.
    solid -= _switch_keepouts()
    solid += _switch_cradles() & cav

    # Edge ports (this shell's portion; local z = global z)
    solid -= _usb_cut(USB_GZ)

    # Three button cap holes on an arc below the screen (caps drop in — button_cap.py).
    solid -= _button_holes()

    if BTN_STYLE == "ring":
        # Lamage de centrage des collerettes rapportees (puits des capuchons)
        for bx, by in button_centers():
            solid -= Pos(bx, by, 0) * extrude(Circle(BTN_RING_SEAT_DIA / 2), BTN_RING_SEAT_DEPTH)
    else:
        # Variante flush : lamage direct dans la paroi, tete quasi affleurante.
        # + MEMBRANE SACRIFICIELLE d'une couche (0.2) fermant le trou au fond du
        # lamage : le plafond de la poche ponte alors sur un disque plein (lignes
        # droites, propre) au lieu d'un anneau au-dessus du vide (spaghetti).
        # A PERCER au tournevis/cutter apres impression, avant d'inserer les switches.
        for bx, by in button_centers():
            solid -= Pos(bx, by, 0) * extrude(Circle(BTN_FLUSH_CB_DIA / 2), BTN_FLUSH_CB_DEPTH)
            solid += Pos(bx, by, BTN_FLUSH_CB_DEPTH) * extrude(
                Circle(BTN_HOLE_DIA / 2 + 0.2), 0.2)

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
    # Revue annotee (-1 MM) : ecartement des murs ESP resserre de 1 mm au total
    # (clear 0.5 -> 0 par cote) pour caler la carte sans jeu lateral.
    solid += _walls(ESP_W, ESP_H, ESP_CXY, WALL, BACK_POCKET_TOP, ["+x", "-x"], clear=0.0) & cav
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
    # Revue annotee : les deux nervures restent SYMETRIQUES (centrees sur x=0),
    # ecartees pour laisser exactement BAT_POCKET_W (34.5) de largeur interieure.
    rib_x = BAT_POCKET_W / 2 + RIB_T / 2
    rib_top = BAT_CXY[1] + BAT_H / 2 + FIT_CLEAR + RIB_T          # +y end (matches _walls)
    rib_bot = -(H / 2 - SCREW_INSET) + BOSS_OD / 2 + 4.0          # ~4 mm above the bosses
    for sx in (-1, 1):
        rib = Pos(sx * rib_x, (rib_top + rib_bot) / 2, (WALL + BACK_POCKET_TOP) / 2) * Box(
            RIB_T, rib_top - rib_bot, BACK_POCKET_TOP - WALL
        )
        solid += rib & cav

    # --- Corrections (revue annotee 2026-07-31) ---
    esp_wx = ESP_W / 2 + RIB_T / 2                        # 14.9 (murs ESP +-x, clear=0)
    esp_top = ESP_CXY[1] + ESP_H / 2 + RIB_T              # 56.1 (extremite haute)
    # Les boites de coupe partent EXACTEMENT du plancher (z=WALL) et ne debordent
    # qu'au-dessus du sommet des murs : aucune morsure dans le plancher.
    cut_h = BACK_POCKET_TOP - WALL + 0.2
    cut_mid = WALL + cut_h / 2
    # (CYAN) passage de fils dans le mur ESP +x : fenetre debouchante de 15 mm
    # de long, commencant a 30 mm de l'extremite haute du mur.
    solid -= Pos(esp_wx, esp_top - 30.0 - 7.5, cut_mid) * Box(RIB_T + 2.0, 15.0, cut_h)
    # (VERT) les deux extremites basses des murs ESP raccourcies de 5 mm
    # (symetriques : fin a y=-5.4 au lieu de -10.4).
    for sx in (-1, 1):
        solid -= Pos(sx * esp_wx, -7.9, cut_mid) * Box(RIB_T + 2.0, 5.0, cut_h)
    # Passages de fils en haut des DEUX murs ESP : fenetres de 15 mm collees a
    # l'extremite haute (les murs s'arretent a CAVITY_TOP=55 contre le bloc
    # sangle). A gauche : les boutons (GPIO 19/20/21, coin haut-gauche du
    # devkit). A droite : l'alimentation TP4056 (OUT+ -> 5V, OUT- -> GND) et le
    # faisceau SPI de l'ecran (GPIO 10-14) — ces broches sont toutes en bout de
    # colonne cote haut-droit.
    for sx in (-1, 1):
        solid -= Pos(sx * esp_wx, CAVITY_TOP - 7.5, cut_mid) * Box(RIB_T + 2.0, 15.0, cut_h)

    # Edge ports. The back shell is flipped about Y when the case closes (x -> -x),
    # so its cuts are MIRRORED in X (about the YZ plane) to line up with the front
    # shell's ports after the flip. Native z = TOTAL_T - global z.
    # (encoche USB supprimee de la coque arriere — revue impression : le
    # connecteur n'affleure que sur la moitie avant, l'encoche arriere ne
    # faisait qu'un trou inutile.)

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
