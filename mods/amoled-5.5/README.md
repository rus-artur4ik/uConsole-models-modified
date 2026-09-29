# Front panel and middle frame for a 5.5" 1080×1920 AMOLED

Rework of the stock uConsole front panel and middle frame for the 5.5" FHD AMOLED touch display sold on AliExpress with an HDMI / USB-C driver board
(Wisecoco TOP055FHDT00CTP01, "AM-OLED 5.5 Inch 1920x1080 OLED Screen … Multi-Touch … Raspberry Pi Display 60Hz Driver Board").

> Untested prototype: built from the vendor datasheet, not yet checked against a real display.

There are two versions:

| | Offset window | Centred window |
|---|---|---|
| Files | `*_amoled55.*` | `*_amoled55_centered.*` |
| Window | 2.75 mm left of centre | centred |
| Case outline | stock, 131 mm | widened to 137.6 mm next to the screen (front panel and middle frame) |
| Thinnest wall | ≈0.4 mm in the front panel (CNC or SLA / MJF only) | 0.53 mm (frame floor under the FPC fold) |
| Middle frame | relief for the FPC in the right rim | widened top band on both sides, FPC slot and passage on the right |

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

### Why folding the FPC does not avoid the widening

The model already folds the FPC behind the glass (the orange strip on the glass end in the viewer). It is bonded to the front of the glass ledge, so it has to wrap round the glass end and cannot leave straight from the back. The fold only adds its bend (0.9 mm assumed) past the glass.

The real limit is the glass: with the image centred, the FPC end of the glass itself is at X 66.52, 1 mm past the stock side at 65.5. In the stock width the best case is:

| FPC fold past the glass | Wall | Window offset |
|---|---|---|
| 0.9 mm (default) | 0.73 mm | 2.75 mm |
| 0.5 mm | 0.73 mm | 2.35 mm |
| 0.3 mm | 0.73 mm | 2.15 mm |
| 0 (impossible) | 0.73 mm | 1.85 mm |

A tighter fold saves a few tenths of a millimetre; a centred window needs a panel whose active area is centred on its glass, or a wider case.

## Common to both versions

- The stock window and raised bezel are removed. The new window is the active area plus 0.25 mm per side (121.94 × 68.81 mm, Y −1.11…67.70), with a new raised bezel around it.
- The glass sits in a 0.75 mm pocket in the back of the front panel (glass + 0.10 mm clearance per side, plus 0.9 mm at the right end for the FPC fold). Its back face ends up level with the back of the front panel, so it rests on the middle frame's rims.
- The FPC is on the right, like the stock LCD. The middle frame gets a relief (Y 0.8…65.8, down to Z 37.43, i.e. 1.35 mm below the glass) from the fold into the stock LCD pocket, and from there into the stock FPC channel (X 43…62, Y 8.6…57.8, 3 mm deep).
- The middle of the glass spans the empty 2 mm stock LCD pocket. Put a 2 mm foam or plate under it so touches do not flex the AMOLED.
- Keyboard, buttons, screw holes, back cover and side lugs are untouched; the parts keep the original assembly coordinates.

## Offset window (`*_amoled55`)

The glass plus its FPC fold is centred in the stock 131 mm width, which puts the window **2.75 mm left of centre** (X −63.72…58.22).

- Front panel: the pocket (X ±64.77) leaves **≈0.4 mm** where its top edge meets the panel's outer chamfer, along both long sides. Make it by CNC (aluminium) or SLA / MJF printing; FDM will not hold that wall. There is no room for the raised bezel on the left of the window.
- Middle frame: only the FPC relief, X 62.3…64.77 in the right rim, leaving a 0.73 mm outer wall (0.53 mm at its top chamfer).

## Centred window (`*_amoled55_centered`)

With the active area centred (window X ±60.97) the glass spans X −61.92…66.52 and the FPC fold reaches 67.42, past the stock side at 65.5. So both parts are widened next to the screen:

- **Front panel:** both side edges grow from 65.5 to **68.8** (the width of the middle frame's side lugs) over Y −7.5…74.1, with R1.5 blends and the stock 0.9 mm edge chamfer. The pocket (X −62.02…67.52) has 1.28 mm side walls; the raised bezel fits on all four sides.
- **Middle frame:** the top band of both side walls grows to 68.8 with the same outline, from Z 36.9 up to the top face (38.78), with the stock 0.2 mm top chamfer and a 0.5 mm chamfer underneath. It carries the end of the glass and covers the FPC fold. The band stops 0.13 mm above the side lugs (part `s3`, top at Z 36.77) at the upper corners.
- **FPC relief** on the right: X 62.3…67.52, from the rim of the stock LCD pocket through the widened band. It leaves a 1.28 mm outer wall and a **0.53 mm floor** in the band.
- Only the right side is needed for the display; the left one is there for symmetry (`--widen fpc` drops it on both parts).

Checked against every part of the official assembly with `amoled55_display_dummy_centered.step`: the display, the new front panel and the new middle frame do not collide with each other or with any stock part.

Watch the **side ports**: the right wall has openings at Y 5…53, Z 26.8…34.2. The widened band starts about 2.7 mm above their top edge and sticks out 3.3 mm, so slim plugs are fine but a bulky USB-A plug may touch it.

How much widening is needed depends on the border at the FPC end: half width ≈ 60.72 + border + 1.75 mm (fold, clearance and a 0.75 mm wall). 5.8 mm gives 68.27; 4.5 mm gives 66.97. Measure it on the real part.

## Before you make it

1. Check the marking on the display FPC. If it is not a BO055FHM-class panel, measure the glass and the active area and rebuild with the right numbers.
2. Measure the distance from the glass end to the first lit pixel on the FPC side (`--aa-offset-fpc`, 5.8 mm by default). A 0.3 mm error here shows up as a black strip or a cropped edge in the window.
3. Fold the FPC and measure how far it sticks out past the glass end (`--fpc-bend`, 0.9 mm by default) and how much room it and its parts need under the glass (`--fold-depth`, 1.2 mm by default).

Not covered here: where the driver board goes, and how the HDMI and USB (touch) cables reach it.

## Files

| File | |
|---|---|
| `uConsole_front_panel_amoled55.step` / `.stl` | front panel, offset window |
| `uConsole_middle_frame_amoled55.step` / `.stl` | middle frame, offset window |
| `uConsole_front_panel_amoled55_centered.step` / `.stl` | front panel, centred window, widened next to the screen |
| `uConsole_middle_frame_amoled55_centered.step` / `.stl` | middle frame, centred window, widened next to the screen |
| `amoled55_display_dummy*.step` / `.stl` | display glass and FPC fold envelope for each version, for fit checks |
| `build_front_panel.py` | builds the front panels (and dummies) from `front_panel/uConsole_front_panel.step` |
| `build_middle_frame.py` | builds the middle frames from `middle_frame/uConsole_middle_frame.step` |

## Rebuilding

Build both parts with the same arguments so they match:

```sh
pip install cadquery-ocp
python build_front_panel.py && python build_middle_frame.py            # offset window
python build_front_panel.py --aa-cx 0 --widen both --suffix _centered  # centred window
python build_middle_frame.py --aa-cx 0 --widen both --suffix _centered
python build_front_panel.py --aa-offset-fpc 5.6 --fpc-bend 0.5        # with measured values
```

Main options: `--aa-cx`, `--widen none|fpc|both`, `--widen-x`, `--fpc-side left|right`, `--aa-offset-fpc`, `--fpc-bend`, `--fold-depth`,
`--glass-w/--glass-h/--glass-t`, `--aa-w/--aa-h`, `--window-margin`, `--pocket-depth`, `--pocket-clearance`, `--bezel-w`;
middle frame only: `--band-bottom`, `--band-chamfer`, `--relief-clearance`.
