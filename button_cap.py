"""Drop-in button caps — print separately. ONE uniform variant (x3).

The 6x6x5 tactile switch inserts through the Ø8.8 face hole into its printed
cradle (see speaker_badge.py) and seats plunger-forward, tip ~0.5 mm behind the
face. The cap is a Ø13.5 head (1.5x the v2 Ø9) with a short nub that GLUES onto
the plunger tip — a Ø3.9 recess in the nub's back face locates the plunger and
pockets the glue. The cap therefore rides the plunger: head floats ~0.35 mm
proud of the face at rest, full switch travel on press. The glue bond is the
retention for the cap AND the switch (head -> face stops the chain falling out
through the Ø8.8 hole).

Print orientation: depuis le dome (2026-08-13), tete EN HAUT (dome vers le
ciel, nub sur le plateau) avec supports auto sous la couronne — la face
arriere (cachee contre la facade) recoit les supports, le dome garde les
couches fines du dessus. print_parts.py exporte deja dans ce sens.
"""

import math

from build123d import (Align, Circle, Compound, Cylinder, Pos, Rotation,
                       SlotCenterToCenter, Sphere, extrude)

import speaker_badge as sb

HEAD_DIA = sb.BTN_CAP_HEAD          # 13.5 proud head
HEAD_H = 1.6
NUB_DIA = 5.0                       # manchon : coulisse librement dans le trou Ø8.8
NUB_H = 0.85                        # (style "ring" historique)
RECESS_DIA = 3.45                   # CLIPSE le plongeur Ø3.5 (leger serrage nominal
                                    # -0.05 ; revue impression : 3.6 trop lache)
RECESS_DEPTH = 0.45                 # (style "ring")

MIN = (Align.CENTER, Align.CENTER, Align.MIN)

DOME_H = 0.7                        # fleche du dome (revue Romain 2026-08-13 :
                                    # boutons plus bombes). Rayon de courbure
                                    # resultant ~32.9 pour une corde de 13.5.


ICON_DEPTH = 0.4                    # profondeur MINIMALE de gravure (remplie
                                    # au feutre acrylique type Posca puis
                                    # essuyee). Fond PLAT (revue 2026-08-14 :
                                    # le fond parallele au dome rendait une
                                    # gravure fantomatique et mal maillee).


def _smiley():
    """Design Figma 4147-1405 : grand contour circulaire Ø11.2 (stroke 0.85)
    + deux yeux ronds Ø1.9 au-dessus du centre, ensemble decale vers la
    droite (vu badge porte). Les x du modele sont MIROIR de la vue portee
    (la face imprimee est retournee sur le badge) : yeux modele a -3.0/+1.4
    -> l'observateur les voit a +3.0/-1.4, regard a droite comme la ref."""
    ring = Circle(5.6) - Circle(4.75)
    eyes = Pos(-3.0, 1.4) * Circle(0.95) + Pos(1.4, 1.4) * Circle(0.95)
    return ring + eyes


def _chevron():
    """Design Figma 4147-1410/1413 : chevron ∨ a bouts et pointe ARRONDIS,
    IDENTIQUE pour les deux boutons lateraux — deux slots (stadiums)
    inclines joints a l'apex bas."""
    arms = None
    for sx in (-1, 1):
        x0, y0, x1, y1 = 0.0, -1.15, sx * 2.55, 1.15
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        sep = math.hypot(x1 - x0, y1 - y0)
        arm = (Pos((x0 + x1) / 2, (y0 + y1) / 2)
               * Rotation(0, 0, ang) * SlotCenterToCenter(sep, 1.4))
        arms = arm if arms is None else arms + arm
    return arms


def _icon_cut(profile, dome=True):
    """Volume de gravure a FOND PLAT : colonne du profil coupee sous un plan
    unique. Avec dome : plan place ICON_DEPTH sous la surface du dome AU
    RAYON LE PLUS EXTERIEUR de l'icone (profondeur >= ICON_DEPTH partout,
    un peu plus au centre). Sans dome (variante plate) : plan a ICON_DEPTH
    sous la face plane. Fond net, aretes verticales franches."""
    if dome:
        r = HEAD_DIA / 2
        R = (r * r + DOME_H * DOME_H) / (2 * DOME_H)
        bb = profile.bounding_box()
        r_max = max(math.hypot(x, y)
                    for x in (bb.min.X, bb.max.X) for y in (bb.min.Y, bb.max.Y))
        r_max = min(r_max, r - 0.05)
        surf = -DOME_H + (R - math.sqrt(R * R - r_max * r_max))
    else:
        surf = 0.0
    return Pos(0, 0, surf + ICON_DEPTH) * extrude(profile, -2.0)


def _dome():
    """Calotte spherique sur la face visible (z<0 du modele) : apex a
    -DOME_H, tangente au bord Ø13.5 de la tete a z=0."""
    r = HEAD_DIA / 2
    R = (r * r + DOME_H * DOME_H) / (2 * DOME_H)
    crown = Pos(0, 0, -DOME_H) * Cylinder(r, DOME_H, align=MIN)
    return crown & Pos(0, 0, R - DOME_H) * Sphere(R)


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


INLAY_DEPTH = 0.4                   # incrustation = DEUX couches de 0.2 :
                                    # la face garde 0.4 d'epaisseur de couleur
                                    # (opaque, le fonce ne transparait pas) et
                                    # la meme piece sert aux DEUX recettes,
                                    # 1 ou 2 changements de filament.


def make_cap(center=False, style=None, icon=None, dome=True, inlay=False):
    """Cap for the three buttons. `style`: None = suit sb.BTN_STYLE (defaut
    du projet), sinon "ring" ou "flush". `icon`: None = smiley pour le
    central, chevron ∨ pour les lateraux (designs Figma 4147-1405/1410/1413,
    les DEUX lateraux sont identiques) ; "none" = face lisse — grave en
    creux de ICON_DEPTH dans le dome, a remplir au feutre acrylique.
    `dome=False` : variante PLATE (revue Romain 2026-08-14) — tete sans
    calotte, s'imprime face contre plateau SANS SUPPORTS (la gravure cote
    plateau sort nette), pour la serie de 40.
    `inlay=True` (plat uniquement) : icone INCRUSTEE EN NEGATIF — gravee
    de DEUX couches (0.4) dans la face, imprimee face contre plateau,
    couches de 0.2. Deux recettes au choix :
      - 1 SEUL changement (economie de pause, revue Romain 2026-08-14) :
        couches 1-2 = couleur capuchon, changement debut couche 3, NOIR
        JUSQU'AU BOUT (icone + corps + nub). Tranche et dos noirs, face
        couleur, icone noire.
      - 2 changements (capuchon entierement couleur) : couches 1-2 couleur,
        noir couches 3-4, retour couleur debut couche 5."""
    style = style or sb.BTN_STYLE
    icon = icon or ("smiley" if center else "chevron")
    if icon in ("up", "down"):
        icon = "chevron"
    head_h = FLUSH_HEAD_H if style == "flush" else HEAD_H
    nub_h = FLUSH_NUB_H if style == "flush" else NUB_H
    head = Cylinder(HEAD_DIA / 2, head_h, align=MIN)
    nub = Pos(0, 0, head_h) * Cylinder(NUB_DIA / 2, nub_h, align=MIN)
    if inlay and dome:
        raise ValueError("inlay=True exige dome=False (face plate)")
    cap = (_dome() + head + nub) if dome else (head + nub)
    recess_d = FLUSH_RECESS_D if style == "flush" else RECESS_DEPTH
    cap -= Pos(0, 0, head_h + nub_h - recess_d) * Cylinder(
        RECESS_DIA / 2, recess_d + 0.02, align=MIN)
    profile = _smiley() if icon == "smiley" else (
        _chevron() if icon == "chevron" else None)
    if profile is not None:
        if inlay:
            # gravure d'UNE couche : la couleur de la couche 2 (apres le
            # changement de filament) remplit ces vides et affleure
            cap -= Pos(0, 0, INLAY_DEPTH) * extrude(profile, -0.5)
        else:
            cap -= _icon_cut(profile, dome)
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
