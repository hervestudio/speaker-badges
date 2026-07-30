"""Cross-section through one corner screw of the assembled badge, to verify the
M2 cap head seats on the lid counterbore shoulder and the shaft engages the
brass insert. A 1.2 mm slab is cut on the screw axis and each part sliced
individually (Compound '&' only slices one body), then recombined.

Read bottom->top in the default 'right' view: cap head (hex socket) recessed in
the lid counterbore -> Ø2.4 shaft through the lid -> knurled insert in the boss.
The head (Ø3.8) is wider than the through-hole (Ø2.4), so it cannot pull through.
"""

from build123d import Box, Compound, Pos

import screw_assembly as sa
import speaker_badge as sb


def gen_step():
    cx = sb.W / 2 - sb.SCREW_INSET
    cy = sb.H / 2 - sb.SCREW_INSET
    slab = Pos(cx, cy, sb.TOTAL_T / 2) * Box(1.2, 12, sb.TOTAL_T + 2)
    out = []
    # Slice the un-posed children: gen_step() re-poses the assembly upright for
    # review, but this slab is positioned in the flat build frame.
    for child in sa._children():
        piece = child & slab
        if piece.volume > 1e-6:
            piece.label = child.label
            out.append(piece)
    return Compound(label="corner_section", children=out)


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "section_view.step")
    print("wrote section_view.step")
