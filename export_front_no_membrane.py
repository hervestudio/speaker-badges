# Exporte la FACADE seule (variante medium) SANS les membranes
# sacrificielles : les lamages des capuchons de vis et des boutons
# debouchent directement (rien a percer apres impression).
# Demande Romain 2026-09-18.
#
#   .venv/bin/python export_front_no_membrane.py
#
# Sortie : front_shell_medium_no_membrane.step
#          print/front_shell_medium_no_membrane.stl (pose d'impression
#          native : face exterieure sur le plateau, cavite vers le haut)
import os

os.environ["BADGE_VARIANT"] = "medium"
os.environ["BADGE_NO_MEMBRANE"] = "1"

from build123d import export_step, export_stl

import speaker_badge as sb

assert sb.VARIANT == "medium" and sb.NO_MEMBRANE

front = sb.front_shell()
front.label = "front_shell_medium_no_membrane"

export_step(front, "front_shell_medium_no_membrane.step")
print("wrote front_shell_medium_no_membrane.step")

os.makedirs("print", exist_ok=True)
# meme finesse de tesselation que print_parts.py (bombe rond + conges lisses)
export_stl(front, "print/front_shell_medium_no_membrane.stl",
           tolerance=0.02, angular_tolerance=0.15)
print("wrote print/front_shell_medium_no_membrane.stl")
