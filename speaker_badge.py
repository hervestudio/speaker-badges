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
import os

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
# TROIS VARIANTES (comparatif d'impression 2026-08-04/05), via BADGE_VARIANT :
# - "short"  (defaut) : 64 x 124, l'originale — LiPo 503450 1000 mAh.
# - "medium" : 66 x 134 — +10 mm EN HAUT seulement (l'ESP remonte se caler
#   sous le header, l'ecran garde sa distance au bord BAS -> dans le repere
#   centre le contenu absolu descend de 5) ; LiPo 505060 2000 mAh en paysage.
# - "long"   : 66 x 144 — +10 mm en haut ET en bas, ecran/ESP inchanges ;
#   LiPo 505060 en paysage. (BADGE_H_EXTRA=20 reste accepte comme alias.)
VARIANT = os.environ.get("BADGE_VARIANT", "")
if not VARIANT:
    VARIANT = "long" if os.environ.get("BADGE_H_EXTRA") else "short"
assert VARIANT in ("short", "medium", "long"), VARIANT
H_EXTRA = {"short": 0.0, "medium": 10.0, "long": 20.0}[VARIANT]
ABS_SHIFT = -5.0 if VARIANT == "medium" else 0.0  # decalage du contenu absolu
W = 64.0 if VARIANT == "short" else 66.0  # base width (X); floor set by the
                           # Ø59.24 screen PCB + walls (~0.3 mm/side, snug)
H = 124.0 + H_EXTRA        # body height (Y); scaled with the 2.1" screen to keep
                           # the v1 proportions (H/W ≈ 1.94). The ESP + battery
                           # stack (95.7) now has slack in the 115.2 mm cavity.
HEADER_H = 7.0             # solid top strip housing the strap slot + internal bar
BULGE_DIA = 72.0           # body bulges 4 mm proud of the base around the screen —
                           # same frame width beyond the bezel as v1 (~7.7 mm),
                           # scaled with the screen; base still 64 (holds the PCB)
CORNER_R = 4.0             # smoothing radius for outer silhouette
WALL = 1.8                 # thinned from 2.0 in v1 for module clearance; kept
T_FRONT = 8.75             # +1.5 le 2026-08-13 (revue montage : cablage trop
                           # serre) — l'espace gagne est cote plan de joint, la
                           # ou passent les fils. Le DOS reste a 7.25 : plus de
                           # la moitie des coques arriere sont deja imprimees.
T_BACK = 7.25
TOTAL_T = T_FRONT + T_BACK
CAVITY_TOP = H / 2 - HEADER_H   # cavity stops here; header above stays solid

# --- Screen (2.1" round TFT 360x360 module: glass bonded on its own PCB) ---
# Per the "foot position chart": PCB Ø59.24 disc + a ~30.5 mm connector tab at
# the bottom (total PCB height 67.47); LCM glass Ø55.92; active area Ø52.92.
# AA / glass / PCB disc are concentric (side offsets are equal), so everything
# centers on (0, SCREEN_CY); only the tab hangs below the disc.
SCREEN_CUTOUT_DIA = 53.7   # covers the Ø52.92 active area + small margin
SCREEN_CY = 8.0 + ABS_SHIFT  # below lanyard, sized to fit bulge (v1 forehead ratio)

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
USB_GZ = 7.25              # FIXE a l'ancien mi-plan (etait TOTAL_T/2 = 7.25 a
                           # l'epoque symetrique) : le connecteur est lie a la
                           # FACE AVANT, il ne doit pas suivre l'epaississement.
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
SW_TAB_KEEPOUT_Y = SCREEN_CY - 38.1  # keep-out applies above this y (suit
                           # l'ecran : -30.1 en short/long, -35.1 en medium)
SW_TAB_KEEPOUT_Z = 4.2     # ...and above this z (tab glass side starts ~4.3)

# --- Internal retention (printed pockets/ribs; screen on a ledge + foam) ---
RIB_T = 1.6                # pocket / rib wall thickness
FIT_CLEAR = 0.5            # clearance around each module
POCKET_GAP = 0.8           # stop pocket walls short of the seam so the front and
                           # back shells' walls never butt together at the mid-plane
FRONT_POCKET_TOP = 7.25 - POCKET_GAP  # FIGE a la cote d'origine (etait
                           # T_FRONT - POCKET_GAP) : la facade epaissie ne doit
                           # PAS rehausser les parois TP/butees ecran/anneau —
                           # le 1.5 mm gagne reste un degagement pour les fils.
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
ESP_W, ESP_H = 28.2, 64.4
# top registers on header ceiling (0.5 sous CAVITY_TOP) ; en Medium l'ESP
# REMONTE avec le header (+10) pour liberer 50 mm en bas pour la batterie.
# 22.3 = H/2 - 39.7 pour H=124 : la formule reproduit exactement le Short.
ESP_CXY = (0.0, H / 2 - 39.7) if VARIANT == "medium" else (0.0, 22.3)
# Batteries REELLES par variante (l'ancienne enveloppe 503040 etait fausse) :
# - Short : LiPo 503450 (5 x 34 x 50, 1000 mAh) — occupe quasi tout l'espace
#   bas (murs ESP raccourcis de 1.2 pour lui laisser 1 mm de jeu).
# - Long : LiPo 505060 (5 x 50 x 60, 2000 mAh) posee en PAYSAGE (60 en X,
#   50 en Y) : elle ne passe pas entre les futs d'inserts (Ø5 vers ±26), donc
#   elle repose sur une ETAGERE juste au-dessus d'eux. Pas de nervures
#   laterales (1.2 mm de jeu par flanc contre les murs peripheriques) ;
#   languettes vers le HAUT pour rejoindre l'ESP. La 503450 y rentre aussi.
if VARIANT != "short":
    BAT_W, BAT_H = 60.0, 50.0
    # assise 0.3 au-dessus du sommet des bosses des coins bas
    BAT_CXY = (0.0, -(H / 2) + SCREW_INSET + BOSS_OD / 2 + 0.3 + BAT_H / 2)
else:
    BAT_W, BAT_H = 40.0, 50.0
    BAT_CXY = (0.0, -(H / 2 - WALL - BAT_H / 2))     # bottom rests on perimeter wall
BAT_POCKET_W = 34.5 if VARIANT == "short" else 60.5  # largeur INTERIEURE de la poche batterie
                           # (Short : entre les deux nervures symetriques ;
                           # Long : quasi mur-a-mur, sans nervures)
TP_W, TP_H = 24.0, 18.0                              # cotes MESUREES de la carte reelle
TP_CXY = (USB_CX - TP_USB_OFF, -(H / 2 - 11.1))      # front layer, bas-centre, HORIZONTALE :
                                                     # decalee de -5.5 pour que le connecteur
                                                     # tombe pile au centre du badge. Elle
                                                     # s'appuie contre la paroi BASSE (bord
                                                     # inferieur a -59.9, 0.3 du mur),
                                                     # connecteur vers le bas ; bracketee sur
                                                     # les deux flancs + le haut.
SD_W, SD_H, SD_CXY = 17.8, 17.9, (-20.8, -41.5 + ABS_SHIFT)  # empreinte de l'EX-poche SD : sert encore
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
    roof_z1 = 7.15  # FIGE a la cote d'origine (etait T_FRONT - 0.1 : la
    # facade epaissie a 8.75 aurait epaissi les plafonds de 1.5 — les cages
    # restent identiques a la version validee, l'espace gagne reste aux fils)
    out = None
    for bx, by in button_centers():
        walls = Pos(bx, by, (z0 + z1) / 2) * Box(2 * ow, 2 * ow, z1 - z0)
        walls -= Pos(bx, by, (z0 + z1) / 2) * Box(2 * hw, 2 * hw, z1 - z0 + 0.02)
        # leg/wire notches through both x walls
        for sgn in (-1, 1):
            walls -= Pos(bx + sgn * (hw + RIB_T / 2), by, (z0 + z1) / 2) * Box(
                RIB_T + 0.02, SW_LEG_NOTCH, z1 - z0 + 0.02)
        # berceaux LATERAUX : murs +-x supprimes ENTIEREMENT (poteaux d'angle
        # compris) — ils genaient l'insertion du switch (revue 2026-08-12).
        # Le corps reste tenu par les murs +-y, la plaque d'appui et le
        # plongeur centre dans le trou de facade. (Le central garde les siens :
        # son mur +y ampute par la languette ecran les rend necessaires.)
        if (bx, by) != button_centers()[0]:
            for sgn in (-1, 1):
                walls -= Pos(bx + sgn * (hw + RIB_T / 2), by, (z0 + z1) / 2) * Box(
                    RIB_T + 0.04, 2 * ow + 0.04, z1 - z0 + 0.02)
        # solid backer plate behind the body (press-force reaction)
        roof = Pos(bx, by, (z1 + roof_z1) / 2) * Box(2 * ow, 2 * ow, roof_z1 - z1)
        cradle = walls + roof
        # fentes passe-pattes dans la plaque : les pattes du switch, repliees
        # vers l'arriere le long du corps, debouchent a l'interieur du boitier
        # -> soudure APRES insertion, bien plus simple. Le centre de la plaque
        # (ou s'appuie le corps) reste plein.
        for sgn in (-1, 1):
            # fentes RETRECIES (revue casse 2026-08-05) : 2.7 x 5.6 au lieu de
            # 3.3 x 7.0 — les pattes (a ±2.25) passent toujours, mais la plaque
            # reste attachee aux murs par ses coins au lieu de finir en
            # languette en porte-a-faux qui casse a l'appui. La fente traverse
            # toujours le bord exterieur (x 2.6..5.3 > 4.75, pas de lamelle).
            cradle -= Pos(bx + sgn * 3.95, by, (z1 + roof_z1) / 2) * Box(
                2.7, 5.6, roof_z1 - z1 + 0.2)
        if (bx, by) == button_centers()[0]:
            # bouton CENTRAL : mur -y DOUBLE (3.2) — le mur +y, ampute par la
            # languette ecran (z<=4.2), ne porte plus le plafond ; tout l'appui
            # du switch transite par ce mur-ci.
            cradle += Pos(bx, by - ow - RIB_T / 2, (z0 + z1) / 2) * Box(
                2 * ow, RIB_T, z1 - z0)
        # Renforts de plafond (ceinture-bretelles apres la casse du plafond
        # central) — deux variantes :
        #  - CENTRAL : piliers de fente historiques (version imprimee/validee,
        #    on n'y touche pas) : pilier au milieu de chaque fente + patte de
        #    liaison au plafond.
        #  - LATERAUX (simplifies, revue 2026-08-13) : une EQUERRE par cote —
        #    un poteau propre ENTIEREMENT au-dela du trou d'insertion Ø8.8
        #    (x 4.5..6.0 > r 4.4 : assise pleine sur le plancher, plus de
        #    porte-a-faux au bord du trou) + un pont plat au niveau du plafond
        #    (z 5.6..7.15) traversant la fente et NOYE de 0.3 dans la masse du
        #    plafond (x 2.3..6.0). Les pattes du switch sortent a ±2.25, le
        #    pont a ±1.0 ne les gene pas ; la fente reste ouverte dessous.
        if (bx, by) == button_centers()[0]:
            for sgn in (-1, 1):
                cradle += Pos(bx + sgn * 4.575, by, (z0 + roof_z1) / 2) * Box(
                    2.85, 2.0, roof_z1 - z0)
                cradle += Pos(bx + sgn * 2.875, by, (z1 + roof_z1) / 2) * Box(
                    0.55, 2.0, roof_z1 - z1)
        else:
            for sgn in (-1, 1):
                cradle += Pos(bx + sgn * 5.25, by, (z0 + z1 + 0.5) / 2) * Box(
                    1.5, 2.0, z1 + 0.5 - z0)
                cradle += Pos(bx + sgn * 4.15, by, (z1 + roof_z1) / 2) * Box(
                    3.7, 2.0, roof_z1 - z1)
        out = cradle if out is None else out + cradle
    # trim whatever encroaches on the screen PCB tab envelope
    ko_z_mid = SW_TAB_KEEPOUT_Z + (T_FRONT - SW_TAB_KEEPOUT_Z) / 2 + 0.5
    ko_z_h = T_FRONT - SW_TAB_KEEPOUT_Z + 1.0
    out -= Pos(0, SW_TAB_KEEPOUT_Y + 60, ko_z_mid) * Box(
        2 * SW_TAB_KEEPOUT_X, 120, ko_z_h)
    # Berceau CENTRAL : la languette ecran interdit toute matiere haute sur
    # son cote +y. Au lieu de necks residuels trop fins (revues impression
    # 2026-08-05), on coupe TOUT (murs ET plafond) au-dessus de z=4.2 des la
    # ligne des fentes (y rel +2.8) : le plafond devient un U ancre sur trois
    # cotes pleins (mur -y double + murs +-x), le cote +y n'est qu'un muret
    # bas z<=4.2. Aucune paroi restante sous 1.6 mm.
    out -= Pos(0, (SCREEN_CY - 38.7) + 60, ko_z_mid) * Box(
        2 * (SW_BODY / 2 + SW_CLEAR + RIB_T + 0.2), 120, ko_z_h)
    # ...and on the TP4056 envelope (+0.2 clearance): the center cradle's -y
    # wall otherwise dips into the board top. (La decoupe SD a ete SUPPRIMEE
    # avec le module — elle charcutait le berceau gauche pour rien ; revue
    # 2026-08-05 : les deux berceaux lateraux sont de nouveau identiques.)
    out -= Pos(TP_CXY[0], TP_CXY[1], T_FRONT / 2) * Box(
        TP_W + 0.4, TP_H + 0.4, T_FRONT + 1.0)
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
        # countersink A LA FACE, comme a l'origine : le cone s'imprime sur le
        # plateau (siege net et solide). La version "tete renfoncee" imprimait
        # le cone en surplomb au-dessus d'un puits -> siege affaisse, la tete
        # passait au travers (revue impression 2026-08-13). Avec la facade a
        # 8.75, utiliser des vis M2x12 (prise ~3.25 mm dans l'insert).
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
    # parois EPAISSIES a 2.8 (etaient RIB_T=1.6, jugees trop fragiles au
    # montage 2026-08-13) — l'epaississement part vers l'EXTERIEUR, les faces
    # interieures ne bougent pas (la carte garde ses 23.5 mm pile)
    TPW_T = 2.8
    solid += (Pos(wall_face_l - TPW_T / 2, TP_CXY[1], zmid)
              * Box(TPW_T, TP_H + 2 * RIB_T, zh)) & cav
    solid += (Pos(tp_r + FIT_CLEAR + TPW_T / 2, TP_CXY[1], zmid)
              * Box(TPW_T, TP_H + 2 * RIB_T, zh)) & cav
    # Support sous la carte : un muret dont la hauteur egale EXACTEMENT la
    # distance plancher -> bas de l'ouverture USB (parametrique : 2.2 mm), pour
    # que la carte repose a plat (muret a l'arriere + bord bas de l'ouverture
    # cote connecteur) sans jamais etre de travers. Place sous la bande du bord
    # haut de la carte (zone nue du PCB), juste sous les freins.
    usb_bot_h = (USB_GZ - USB_H / 2) - WALL - 0.5  # 2.2 - 0.5 : abaisse de
    # 1.5 le 2026-08-12 (la carte reposait trop haut), puis remonte de 1.0 le
    # 2026-08-13 (revue Romain : +1 de haut) — il reste 0.5 de jeu sous la
    # carte, elle ne peut plus s'affaisser qu'a peine
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
    # a l'ecran (module SD abandonne, fente laterale supprimee). SYMETRISEE
    # (revue 2026-08-05) : la meme butee est ajoutee en miroir cote +x, sinon
    # l'ecran ne s'appuyait en bas que d'un cote.
    solid += _walls(SD_W, SD_H, SD_CXY, WALL, FRONT_POCKET_TOP, ["+y"]) & cav
    solid += _walls(SD_W, SD_H, (-SD_CXY[0], SD_CXY[1]), WALL, FRONT_POCKET_TOP,
                    ["+y"]) & cav
    # Entailles PASSE-FILS aux extremites exterieures des deux butees
    # (demande Romain 2026-08-12, nettoyees 2026-08-13) : l'ecran ne
    # s'appuie que sur sa portion centrale (languette, |x|<15), le bout
    # exterieur ne portait rien. Coupe PROPRE :
    #  - de PILE au flanc des berceaux lateraux (x=24.55, aucun moignon ;
    #    les berceaux sont re-ajoutes APRES et ne peuvent etre entames)
    #    jusqu'au-dela du mur peripherique, mais BORNEE a la cavite (& cav) :
    #    ni le mur ni le plancher ne sont marques, la coupe ne retire que la
    #    butee elle-meme ;
    #  - au ras du plancher (z demarre a WALL), 0.2 de marge au-dessus du
    #    sommet de la butee seulement.
    stop_y = SD_CXY[1] + SD_H / 2 + FIT_CLEAR + RIB_T / 2
    for sx in (-1, 1):
        solid -= (Pos(sx * 29.0, stop_y, WALL + (zh + 0.2) / 2) * Box(
            8.9, RIB_T + 2.0, zh + 0.2)) & cav
    # Switch cradles + backer plates behind the three cap holes (the old snap-
    # flange clearance notches are gone: the new caps have no flange). First
    # open the switch envelopes through the TP/SD pocket walls, then add the
    # cradles, which rebuild clean walls around the openings.
    # Assise pour la languette STRIPBOARD (bus GND + les 2 ponts diviseurs
    # 100k soudes dessus, resistances debout) : decoupe conseillee 5 bandes x
    # 8 trous (12.7 x 20.3, plaque 1.6). Cadre a rebords de 1.2, 2.2 de haut,
    # interieur avec 0.6 de jeu ; deux echancrures passe-fils sur les flancs.
    # Zone libre bas-droit de la facade (a gauche, les murs TP encombrent).
    # Ajoute AVANT le keep-out des switchs : il retaille le cadre au besoin.
    # allonge a 8 trous (revue montage 2026-08-11) : 20.3 + 0.7 de jeu
    STRIP_W, STRIP_H = 13.4, 21.0
    STRIP_CX, STRIP_CY = 16.4, -(H / 2 - 15.5)
    rim = Pos(STRIP_CX, STRIP_CY, WALL + 1.6) * Box(STRIP_W + 2.4, STRIP_H + 2.4, 3.2)
    rim -= Pos(STRIP_CX, STRIP_CY, WALL + 1.6) * Box(STRIP_W, STRIP_H, 3.4)
    for sgn in (-1, 1):  # echancrures pour sortir les fils a plat (traversent
        # toujours le sommet du cadre rehausse)
        rim -= Pos(STRIP_CX + sgn * (STRIP_W / 2 + 0.6), STRIP_CY,
                   WALL + 1.85) * Box(1.5, 5.0, 3.8)
    solid += rim & cav

    solid -= _switch_keepouts()
    solid += _switch_cradles() & cav

    # Edge ports (this shell's portion; local z = global z)
    # Ouverture USB : trou de 9 x 3.75. Le bord BAS reste a sa cote (4.0 :
    # il sert de registre a la carte TP4056), le haut monte a 7.75 — +0.5 mm
    # de jeu en epaisseur pour la prise, un peu dure a passer a 3.25 (revue
    # impression 2026-08-13). Le linteau s'imprime toujours en pont de 9 mm.
    solid -= Pos(USB_OPEN_CX, -H / 2, USB_GZ - USB_H / 4 + 0.25) * extrude(
        Plane.XZ * RectangleRounded(USB_W, USB_H / 2 + 0.5, 1.0), WALL * 2, both=True
    )

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
    # Renforts des futs (revue 2026-08-04) : croix de nervures fines autour de
    # chaque boss — 2 branches se fondent dans le mur peripherique, 2 pointent
    # vers l'interieur. Hauteur partielle (~2/3) : l'insert reste accessible
    # par le plan de joint et les branches ne genent pas les composants.
    GUSSET_T = 1.0
    GUSSET_L = 6.0   # demi-longueur de la croix depuis l'axe du boss
    GUSSET_H = 3.4
    cav_for_gussets = _cavity_solid(T_BACK)
    for x, y in _corners():
        # Boss + blind hole for an M2 heat-set insert, pressed in from the seam.
        solid += Pos(x, y, WALL) * extrude(Circle(BOSS_OD / 2), cavity_depth)
        cross = Pos(x, y, WALL + GUSSET_H / 2) * Box(2 * GUSSET_L, GUSSET_T, GUSSET_H)
        cross += Pos(x, y, WALL + GUSSET_H / 2) * Box(GUSSET_T, 2 * GUSSET_L, GUSSET_H)
        # les branches ne doivent pas entrer dans le volume batterie (en Long,
        # la 505060 paysage descend jusqu'a 0.3 au-dessus des bosses)
        cross -= Pos(BAT_CXY[0], BAT_CXY[1], (WALL + T_BACK) / 2) * Box(
            BAT_POCKET_W + 0.6, BAT_H + 0.6, T_BACK - WALL + 0.2)
        solid += cross & cav_for_gussets
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
    # (2026-08-04 : coupe etendue de 1.2 vers le haut — la batterie 503450 de
    # 50 mm montait a 0.2 mm des bouts de murs en Short ; l'ESP ne perd que
    # 0.7 mm d'appui a ses coins bas)
    solid -= Pos(0, esp_wall_end - 0.9, (WALL + BACK_POCKET_TOP) / 2) * Box(
        2 * (ESP_W / 2 + FIT_CLEAR + RIB_T + 1.0), 4.2, BACK_POCKET_TOP - WALL
    )

    # Battery side ribs (+x / -x). Built explicitly rather than via _walls, and
    # stopped ~4 mm ABOVE the bottom insert bosses so the ribs don't run down
    # alongside the inserts (per the design review) — the bosses stand free for
    # clean heat-set access. The rib backs the upper ~2/3 of the battery's sides;
    # the bottom corners are located by the bosses + the perimeter wall. (Free rib
    # ends just add footprint loops to the floor face — verified NOT through-holes.)
    # Revue annotee : les deux nervures restent SYMETRIQUES (centrees sur x=0),
    # ecartees pour laisser exactement BAT_POCKET_W (34.5) de largeur interieure.
    if VARIANT == "short":
        # Short : nervures laterales de part et d'autre de la 503450
        rib_x = BAT_POCKET_W / 2 + RIB_T / 2
        rib_top = BAT_CXY[1] + BAT_H / 2 + FIT_CLEAR + RIB_T      # +y end (matches _walls)
        rib_bot = -(H / 2 - SCREW_INSET) + BOSS_OD / 2 + 4.0      # ~4 mm above the bosses
        for sx in (-1, 1):
            rib = Pos(sx * rib_x, (rib_top + rib_bot) / 2, (WALL + BACK_POCKET_TOP) / 2) * Box(
                RIB_T, rib_top - rib_bot, BACK_POCKET_TOP - WALL
            )
            solid += rib & cav
    else:
        # Long : la 505060 paysage est quasi mur-a-mur — pas de nervures
        # laterales, mais une ETAGERE transversale sous son bord bas pour
        # qu'elle repose au-dessus des bosses d'inserts (0.3 de jeu).
        bat_bot = BAT_CXY[1] - BAT_H / 2
        shelf = Pos(0, bat_bot - RIB_T / 2, (WALL + BACK_POCKET_TOP) / 2) * Box(
            40.0, RIB_T, BACK_POCKET_TOP - WALL
        )
        solid += shelf & cav

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
    import subprocess
    import sys

    from build123d import export_step
    suffix = "" if VARIANT == "short" else f"_{VARIANT}"
    export_step(gen_step(), f"speaker_badge{suffix}.step")
    print(f"wrote speaker_badge{suffix}.step")
    if VARIANT == "short" and not os.environ.get("BADGE_VARIANT"):
        # regenere aussi les variantes Medium et Long en sous-processus
        for v in ("medium", "long"):
            subprocess.run([sys.executable, __file__],
                           env={**os.environ, "BADGE_VARIANT": v}, check=True)
