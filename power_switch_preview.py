# Preview de l'interrupteur d'alimentation R13-603 dans la coque dos
# (variante MEDIUM de la serie). Genere la coque + une maquette du switch
# en place (platine, corps, levier, oeillets) pour verifier visuellement le
# lamage, la fente et les degagements. Revue Romain 2026-09-16.
#
#   BADGE_VARIANT=medium .venv/bin/python power_switch_preview.py
import os

os.environ.setdefault("BADGE_VARIANT", "medium")

from build123d import (Box, Circle, Compound, Pos, RectangleRounded, export_step,
                       extrude)

import speaker_badge as sb

assert sb.VARIANT == "medium"

px, py = sb.PSW_CXY
seat_z = sb.WALL - sb.PSW_SEAT_DEPTH   # fond du lamage (1.3)
FLANGE_T = 0.5                          # tole de la platine

# platine 19.5 x 8, bouts arrondis, posee au fond du lamage
flange = Pos(px, py, seat_z) * extrude(
    RectangleRounded(8.0, 19.5, 3.9), FLANGE_T)
# corps 3.4 x ~11.6 x 5.8 sous la platine, vers la cavite (longueur estimee :
# la datasheet ne cote pas le corps ; les trous Ø2.6 a 14.3 le bordent)
body = Pos(px, py, seat_z + FLANGE_T + 5.8 / 2) * Box(3.4, 11.6, 5.8)
# levier 3 x 3, 3.4 au-dessus de la platine, decale sur une position
lever = Pos(px, py + 1.5, seat_z - 3.4 + FLANGE_T) * extrude(
    RectangleRounded(3.0, 3.0, 0.4), 3.4)
# 3 oeillets 3.2 sous le corps (pattes a souder, pliables)
lugs = Compound(children=[
    Pos(px, py + dy, seat_z + FLANGE_T + 5.8 + 1.6) * Box(0.5, 2.0, 3.2)
    for dy in (-4.0, 0.0, 4.0)])

switch = Compound(label="switch_R13_603",
                  children=[flange, body, lever, lugs])

back = sb.back_shell()
back.label = "back_shell_medium"

out = Compound(label="power_switch_preview", children=[back, switch])
export_step(out, "power_switch_preview.step")
print("wrote power_switch_preview.step")
