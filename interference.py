"""Diagnostic: do the two shells actually interfere when the case closes?

Builds front + back in the assembled position (same transform as
assembled_view.py), intersects them, and reports the overlap volume and
where it sits. Also reports the Z-span of each shell's pocket walls so we
can see the gap (or overlap) across the mid-plane seam.
"""

import speaker_badge as sb
from build123d import Pos, Rotation


def zspan(solid, label):
    bb = solid.bounding_box()
    print(f"  {label:18s} z: {bb.min.Z:7.3f} .. {bb.max.Z:7.3f}")


def main():
    front = sb.front_shell()
    back_assembled = Pos(0, 0, sb.TOTAL_T) * Rotation(0, 180, 0) * sb.back_shell()

    print(f"TOTAL_T={sb.TOTAL_T}  seam at z={sb.T_FRONT}")
    print(f"FRONT_POCKET_TOP={sb.FRONT_POCKET_TOP}  BACK_POCKET_TOP={sb.BACK_POCKET_TOP}  POCKET_GAP={sb.POCKET_GAP}")
    print("Shell Z extents (assembled):")
    zspan(front, "front shell")
    zspan(back_assembled, "back shell")

    overlap = front & back_assembled
    vol = overlap.volume
    print(f"\nIntersection volume = {vol:.4f} mm^3")
    if vol > 1e-6:
        bb = overlap.bounding_box()
        print("  OVERLAP bounding box:")
        print(f"    x: {bb.min.X:7.3f} .. {bb.max.X:7.3f}")
        print(f"    y: {bb.min.Y:7.3f} .. {bb.max.Y:7.3f}")
        print(f"    z: {bb.min.Z:7.3f} .. {bb.max.Z:7.3f}")
    else:
        print("  -> shells do NOT interfere.")

    # Components (simplified placeholder bodies, seated) vs the closed shells:
    # catches internal features poking into a module's real volume — this is
    # what exposed the tall glass ring and the ESP-wall stubs.
    import screw_assembly as sa
    shells = front + back_assembled
    print("\nComponent clearances (placeholder body vs shells):")
    bad = 0
    for part in sa._components():
        inter = shells & part
        pvol = inter.volume if inter else 0.0
        flag = "OK" if pvol < 1e-6 else "OVERLAP!"
        if pvol >= 1e-6:
            bad += 1
        print(f"  {part.label:15s} {pvol:10.4f} mm^3  {flag}")
    print("  -> all components seat cleanly." if not bad
          else f"  -> {bad} component(s) interfere with the shells.")


if __name__ == "__main__":
    main()
