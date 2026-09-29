# Front panel for a 5.5" 1080×1920 AMOLED

Rework of the stock uConsole front panel for the 5.5" FHD AMOLED touch display sold on AliExpress with an HDMI / USB-C driver board
(Wisecoco TOP055FHDT00CTP01, "AM-OLED 5.5 Inch 1920x1080 OLED Screen … Multi-Touch … Raspberry Pi Display 60Hz Driver Board").

> Untested prototype: built from the vendor datasheet, not yet checked against a real display.

There are two versions:

| | Offset window | Centred window |
|---|---|---|
| Files | `uConsole_front_panel_amoled55.*` | `uConsole_front_panel_amoled55_centered.*` |
| Window | 2.25 mm left of centre | centred |
| Panel outline | stock, 131 mm | widened to 137.6 mm next to the screen |
| Thinnest wall | ≈0.4 mm (CNC or SLA / MJF only) | 0.75 mm |
| Middle frame | one relief cut for the FPC fold | widening on the FPC side, plus a passage for the FPC |

## Display

The Wisecoco listing gives 128.44 × 70.71 mm and 121.44 × 68.31 mm, the same numbers as the BOE **BO055FHM** panel datasheet, so the model is built around it:

| | |
|---|---|
| Glass outline | 128.44 × 70.71 × 0.50 mm |
| Active area | 121.44 × 68.31 mm (5.486") |
| Total thickness (polarizer + cell) | 0.679 mm |
| Touch | on-cell, GT1151 |
| AA offset from glass edge | ≈5.8 mm at the FPC end, ≈1.2 mm on the other three sides (read off the BOE drawing; the Wisecoco picture is not to scale) |

The active area is not centred on the glass: the FPC end has a 5.8 mm border, the other end 1.2 mm. That is what forces the choice between the two versions.

## Common to both versions

- The stock window and raised bezel are removed. The new window is the active area plus 0.25 mm per side (121.94 × 68.81 mm, Y −1.11…67.70), with a new raised bezel around it.
- The glass sits in a 0.75 mm pocket in the back of the front panel (glass + 0.10 mm clearance per side, plus 0.9 mm at the right end for the FPC fold). Its back face ends up level with the back of the front panel, so it rests on the middle frame's rims. The stock LCD pocket behind it (2 mm) is left for foam backing and for routing the FPC.
- The FPC is on the right, like the stock LCD, next to the stock FPC channel in the middle frame.
- Keyboard, buttons and screw holes are untouched; the parts keep the original assembly coordinates.

## Offset window (`uConsole_front_panel_amoled55`)

The glass plus its FPC fold is centred in the stock 131 mm panel, which puts the window **2.25 mm left of centre** (X −63.72…58.22).

- The pocket (X ±64.77) leaves **≈0.4 mm** where its top edge meets the panel's outer chamfer, along both long sides. Make this part by CNC (aluminium) or SLA / MJF printing; FDM will not hold that wall.
- There is no room for the raised bezel on the left side of the window.
- **Middle frame:** the FPC fold runs into its right rim (X 63.8…64.7, Y 1…65.6, Z 37.3…38.8, about 89 mm³), which needs a relief cut.

## Centred window (`uConsole_front_panel_amoled55_centered`)

With the active area centred (window X ±60.97) the glass spans X −61.92…66.52 and the FPC fold reaches 67.42, past the stock side edge at 65.5. So the panel is widened:

- Both side edges grow from 65.5 to **68.8** (the width of the middle frame's side lugs) over Y −7.5…74.1, with R1.5 blends and the stock 0.9 mm edge chamfer. Only the right side is needed for the display; the left one is there for symmetry (`--widen fpc` drops it).
- The pocket (X −62.02…67.52) now has 1.28 mm side walls; the thinnest material is the 0.75 mm plate over the glass border.
- The raised bezel fits on all four sides.

### Middle frame changes this version needs

Checked against every part of the official assembly with `amoled55_display_dummy_centered.step`. Nothing collides, but the end of the glass and the FPC fold hang outside the frame's side wall (X 65.5…67.4, Z 37.3…39.5, about 177 mm³). On the FPC (right) side the frame needs:

1. **Widening of the top band of the side wall** from X 65.5 to 68.8, over Y −7.5…74.1, flush with the widened front panel and with the same outline. It supports the end of the glass (X 65.5…66.5, which would otherwise overhang) and closes over the FPC fold. Keep it above Z ≈ 36.9 near the top corner (Y 58…70): the side lugs (part `s3`) reach Z 36.77 there. Going deeper elsewhere (down to Z 24.3) gives a thicker floor and a cleaner side, but has to stay clear of the side ports.
2. **A slot for the FPC fold** inside that widening: X ≈ 66.4…67.6, Y ≈ 0.9…65.7, from Z ≈ 37.2 up to the top face (depth depends on the real FPC thickness).
3. **A passage back into the case:** cut the right rim of the stock LCD pocket (X 62.8…65.5, down to Z ≈ 37.0) over the FPC width, so the FPC can run under the glass into the stock pocket and on into the stock FPC channel (X 43…62, Y 8.6…57.8, 3 mm deep).
4. **Left side (optional):** the same widening, only if you keep the symmetric `--widen both` front panel.

Also check:

- **Side ports:** the right wall has openings at Y 5…53, Z 26.8…34.2. The widened band starts about 2.7 mm above their top edge and sticks out 3.3 mm, so slim plugs are fine but a bulky USB-A plug may touch it.
- **Glass support:** the middle of the glass spans the empty 2 mm stock LCD pocket. Put a 2 mm foam or plate under it so touches do not flex the AMOLED.
- Back cover, keyboard, side lugs and screws do not change.

How much widening is needed depends on the border at the FPC end: half width ≈ 60.72 + border + 1.75 mm (fold, clearance and a 0.75 mm wall). 5.8 mm gives 68.27; 4.5 mm gives 66.97. It fits the stock 65.5 only if that border is under about 3 mm, which the BOE drawing rules out. Measure it on the real part.

## Before you make it

1. Check the marking on the display FPC. If it is not a BO055FHM-class panel, measure the glass and the active area and rebuild with the right numbers.
2. Measure the distance from the glass end to the first lit pixel on the FPC side (`--aa-offset-fpc`, 5.8 mm by default). A 0.3 mm error here shows up as a black strip or a cropped edge in the window.
3. Fold the FPC and measure how far it sticks out past the glass end (`--fpc-bend`, 0.9 mm by default).

Not covered here: where the driver board goes, and how the HDMI and USB (touch) cables reach it.

## Files

| File | |
|---|---|
| `uConsole_front_panel_amoled55.step` / `.stl` | offset-window front panel |
| `uConsole_front_panel_amoled55_centered.step` / `.stl` | centred-window front panel, widened next to the screen |
| `amoled55_display_dummy*.step` / `.stl` | display glass and FPC fold envelope for each version, for fit checks |
| `build_front_panel.py` | the script that builds them from `front_panel/uConsole_front_panel.step` |

## Rebuilding

```sh
pip install cadquery-ocp
python build_front_panel.py                                        # offset window
python build_front_panel.py --aa-cx 0 --widen both --suffix _centered   # centred window
python build_front_panel.py --aa-offset-fpc 5.6 --fpc-bend 0.7    # with measured values
```

Main options: `--aa-cx`, `--widen none|fpc|both`, `--widen-x`, `--fpc-side left|right`, `--aa-offset-fpc`, `--fpc-bend`,
`--glass-w/--glass-h/--glass-t`, `--aa-w/--aa-h`, `--window-margin`, `--pocket-depth`, `--pocket-clearance`, `--bezel-w`.
