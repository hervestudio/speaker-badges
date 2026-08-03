"""Capuchon decoratif de vis — imprime x4, colle par-dessus les tetes M2 apres
montage (facon mockup : un disque chanfreine + un petit carre en relief, l'effet
"vis carree" du design d'origine, sans les faiblesses d'une vraie vis imprimee).

Le dessous a un degagement Ø5 x 0.7 pour la tete M2 (plate, ~flush) et le disque
se pose dans le lamage Ø10.2 x 0.3 de la face avant (centrage + joint de colle
invisible). Impression a plat, carre vers le haut, sans support.
Astuce deux-tons : changement de filament a la hauteur du carre (1.6 mm)."""

from build123d import Align, Axis, Box, Compound, Cylinder, Pos, chamfer

import speaker_badge as sb

CAP_DIA = sb.SCREWCAP_DIA           # 8.0
CAP_H = 1.8                         # epaissi (revue impression : fond transparent)
SQ = 3.2                            # cote du carre decoratif GRAVE (creuse)
SQ_DEPTH = 0.5
HEAD_CLEAR_DIA = 5.0                # degagement de la tete de vis M2 (elle affleure,
HEAD_CLEAR_DEPTH = 0.4              # 0.4 de marge suffit) -> plancher 1.8-0.5-0.4 = 0.9
RIM_CHAMFER = 0.5

MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def make_cap():
    disk = Cylinder(CAP_DIA / 2, CAP_H, align=MIN)
    disk = chamfer(disk.edges().group_by(Axis.Z)[-1], RIM_CHAMFER)
    # carre creuse dans le dessus (facon empreinte de vis carree du mockup)
    cap = disk - Pos(0, 0, CAP_H - SQ_DEPTH) * Box(SQ, SQ, SQ_DEPTH + 0.02, align=MIN)
    cap -= Cylinder(HEAD_CLEAR_DIA / 2, HEAD_CLEAR_DEPTH, align=MIN)
    cap.label = "screw_cap"
    return cap


def gen_step():
    return make_cap()


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "screw_cap.step")
    print("wrote screw_cap.step")
