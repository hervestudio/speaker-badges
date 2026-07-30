"""V1 vs V2 side by side — both review assemblies standing next to each other.

V1 (left): 1.73" AMOLED, body 54 x 105.  V2 (right): 2.1" TFT, body 64 x 124.
Reads the exported badge_v1.step / badge_v2.step (badge_v1 is generated from
the `main` branch; regenerate it from a main checkout if v1 changes), so this
script only re-poses and labels — it does not rebuild either version.
"""

from build123d import Compound, Pos, import_step

GAP = 14.0  # clear space between the two bodies (v1 bulge r 30.5, v2 bulge r 36)


def gen_step():
    v1 = Pos(-(30.5 + GAP / 2), 0, 0) * import_step("badge_v1.step")
    v1.label = "badge_V1"
    v2 = Pos(36 + GAP / 2, 0, 0) * import_step("badge_v2.step")
    v2.label = "badge_V2"
    return Compound(label="v1_vs_v2", children=[v1, v2])


if __name__ == "__main__":
    from build123d import export_step
    export_step(gen_step(), "compare_v1_v2.step")
    print("wrote compare_v1_v2.step")
