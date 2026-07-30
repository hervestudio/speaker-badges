# Speaker Badge Enclosure

A 3D-printable, two-piece enclosure for an electronic event **speaker badge**,
modeled parametrically in Python with [build123d](https://github.com/gumyr/build123d).

Portrait shell, **54 × 105 × 14.5 mm**, with a round body bulge (Ø61) framing the
screen. A webbing strap threads through a slot on the top face and loops around a
drop-in wrap bar. USB-C exits the right edge, the micro SD slot the left edge, and
three buttons sit on the front face on an arc following the screen's lower curve
(through-holes + separately printed drop-in caps).

## Bill of materials
- AMOLED 1.73" round touch display (Ø48.4 glass) + CO5300 adapter board
- ESP32-S3 N16R8 devkit (28.2 × 64.4 × 4.8 mm)
- LiPo 503040 (40 × 30 × 5 mm, 600 mAh)
- TP4056 + 5 V boost, USB-C charge board
- micro SD module + 3 tactile buttons (side pair ≤6×6 mm; center ≤4×4 mm)
- **Closure:** 4× M2 countersunk screws into 4× M2 brass heat-set inserts
- **Strap bar:** printed `wrap_bar` *or* a Ø3 mm steel rod cut to ~29.4 mm

## Files
| File | Purpose |
|------|---------|
| `speaker_badge.py` | the enclosure — front + back shells |
| `m2_screw.py`, `insert.py` | M2 countersunk screw + heat-set insert models |
| `wrap_bar.py` | drop-in strap wrap bar |
| `button_cap.py` | drop-in button caps (snap-fit sides, glued center) |
| `screw_assembly.py` | assembled enclosure (shells + screws + inserts + bar) |
| `exploded_view.py` | exploded view of all parts |
| `section_view.py` | cross-section through a corner screw |
| `interference.py`, `footprint_check.py` | verification scripts |

`*.step` are the generated CAD outputs (regenerable from the scripts).

## Regenerate
```sh
python3 -m venv .venv
.venv/bin/pip install build123d
.venv/bin/python speaker_badge.py   # writes speaker_badge.step
```
Each script writes its own `.step` when run directly.
