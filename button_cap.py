"""Drop-in button caps — print separately. ONE uniform variant (x3).

The 6x6x5 tactile switch inserts through the Ø8.8 face hole into its printed
cradle (see speaker_badge.py) and seats plunger-forward, tip ~0.5 mm behind the
face. The cap is a Ø13.5 head (1.5x the v2 Ø9) with a short nub that GLUES onto
the plunger tip — a Ø3.9 recess in the nub's back face locates the plunger and
pockets the glue. The cap therefore rides the plunger: head floats ~0.35 mm
proud of the face at rest, full switch travel on press. The glue bond is the
retention for the cap AND the switch (head -> face stops the chain falling out
through the Ø8.8 hole).

Print orientation: head-DOWN on the bed (the head's flat top is the only fully
flat face). The recess prints as a shallow blind hole facing up.
"""

from build123d import Align, Compound, Cylinder, Pos

import speaker_badge as sb

HEAD_DIA = sb.BTN_CAP_HEAD          # 13.5 proud head
HEAD_H = 1.6
NUB_DIA = 5.0                       # manchon : coulisse librement dans le trou Ø8.8
NUB_H = 0.85                        # (style "ring" historique)
RECESS_DIA = 3.45                   # CLIPSE le plongeur Ø3.5 (leger serrage nominal
                                    # -0.05 ; revue impression : 3.6 trop lache)
RECESS_DEPTH = 0.45                 # (style "ring")

MIN = (Align.CENTER, Align.CENTER, Align.MIN)


RING_OD = 16.5                      # collerette du puits anti-arrachement
RING_ID = 14.0                      # puits : tete Ø13.5 + 0.25 de jeu par cote
RING_H = 2.3                        # 0.3 dans le lamage du boitier + 2.0 en saillie ;
                                    # le capuchon (sommet a 1.95 de la facade)
                                    # affleure 0.05 sous le bord du puits


def make_ring():
    """Collerette rapportee : anneau imprime a plat, colle dans le lamage
    Ø16.7 x 0.3 de la facade autour de chaque bouton."""
    ring = Cylinder(RING_OD / 2, RING_H, align=MIN)
    ring -= Cylinder(RING_ID / 2, RING_H + 0.02, align=MIN)
    ring.label = "button_ring"
    return ring


# Variante "flush" (option 2) : tete amincie, nub raccourci — le sommet ne
# depasse la facade que de ~0.55 mm, sans collerette (lamage Ø14 x 1.0).
FLUSH_HEAD_H = 1.2
FLUSH_NUB_H = 0.7                   # manchon raccourci (revue impression : a 1.0 il
FLUSH_RECESS_D = 0.85               # butait sur le corps AVANT le declic). Enserre
                                    # 0.85 mm de plongeur et s'arrete a 0.55 au-dessus
                                    # du corps : course de 0.25 + 0.3 de marge.


def make_cap(center=False, style=None):
    """Uniform cap for all three buttons (the `center` flag is kept for the
    callers' sake — both variants are identical). `style`: None = suit
    sb.BTN_STYLE (defaut du projet), sinon "ring" ou "flush"."""
    style = style or sb.BTN_STYLE
    head_h = FLUSH_HEAD_H if style == "flush" else HEAD_H
    nub_h = FLUSH_NUB_H if style == "flush" else NUB_H
    head = Cylinder(HEAD_DIA / 2, head_h, align=MIN)
    nub = Pos(0, 0, head_h) * Cylinder(NUB_DIA / 2, nub_h, align=MIN)
    cap = head + nub
    recess_d = FLUSH_RECESS_D if style == "flush" else RECESS_DEPTH
    cap -= Pos(0, 0, head_h + nub_h - recess_d) * Cylinder(
        RECESS_DIA / 2, recess_d + 0.02, align=MIN)
    cap.label = "button_cap_center" if center else "button_cap"
    return cap


def cap_seat_z(style=None):
    """Position (z coque, face avant = 0) de la face externe du capuchon au
    repos : le plongeur (pointe a z=0.5) porte le fond du logement du nub."""
    style = style or sb.BTN_STYLE
    head_h = FLUSH_HEAD_H if style == "flush" else HEAD_H
    nub_h = FLUSH_NUB_H if style == "flush" else NUB_H
    recess_d = FLUSH_RECESS_D if style == "flush" else RECESS_DEPTH
    return 0.5 - (head_h + nub_h - recess_d)


def gen_step():
    """Two caps side by side + une collerette (les trois boutons utilisent le
    meme capuchon et le meme anneau)."""
    a = make_cap(center=False)
    b = Pos(HEAD_DIA + 3, 0, 0) * make_cap(center=True)
    r = Pos(-(HEAD_DIA + 6), 0, 0) * make_ring()
    return Compound(label="button_caps", children=[a, b, r])


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "button_cap.step")
    print("wrote button_cap.step")
