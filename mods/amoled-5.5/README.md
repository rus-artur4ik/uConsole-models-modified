# Front panel for a 5.5" 1080×1920 AMOLED

Rework of the stock uConsole front panel for the 5.5" FHD AMOLED touch display sold on AliExpress with an HDMI / USB-C driver board
("AM-OLED 5.5 Inch 1920x1080 OLED Screen … Multi-Touch … Raspberry Pi Display 60Hz Driver Board").

> Untested prototype: built from the vendor datasheet, not yet checked against a real display.

## Display

The listings for this module quote the same numbers as the BOE **BO055FHM** panel datasheet, so the model is built around it:

| | |
|---|---|
| Glass outline | 128.44 × 70.71 × 0.50 mm |
| Active area | 121.44 × 68.31 mm (5.486") |
| Total thickness (polarizer + cell) | 0.679 mm |
| Touch | on-cell, GT1151 |
| AA offset from glass edge | ≈5.8 mm at the FPC end, ≈1.2 mm on the other three sides (read off the vendor drawing) |

## What changed

| | Stock | This version |
|---|---|---|
| Window | 111.2 × 63.0 mm, centred | 121.94 × 68.81 mm (AA + 0.25 mm per side), X −63.72…58.22, Y −1.11…67.70 |
| Display mount | LCD sits in a 2 mm pocket of the middle frame | glass sits in a 0.75 mm pocket in the back of the front panel |
| Pocket | – | 129.54 × 70.91 mm, X ±64.77, Y −2.15…68.75 (0.10 mm clearance, plus 0.9 mm on the right for the FPC fold) |
| Raised bezel | around the window | redrawn around the new window on the top, right and bottom; there is no room for it on the left |

Everything else (keyboard, buttons, screw holes) is untouched and the part keeps the original assembly coordinates.

The glass is 128.44 mm long and the case is 131 mm wide, so the layout is dictated by the case:

- The glass plus its FPC fold is centred in the panel, which puts the window **2.25 mm left of centre**.
- The pocket walls are **≈0.4 mm thick** where the pocket's top edge meets the panel's outer chamfer, along both long sides. Make this part by CNC (aluminium) or SLA / MJF printing; FDM will not hold that wall.
- With the glass in the pocket its back face is level with the back of the front panel, so it rests on the middle frame's rims. The stock LCD pocket behind it (2 mm) is left free for foam backing and for routing the FPC.

## Before you make it

1. Check the marking on the display FPC. If it is not a BO055FHM, measure the glass and the active area and rebuild with the right numbers.
2. Measure the distance from the glass end to the first lit pixel on the FPC side (`--aa-offset-fpc`, 5.8 mm by default). A 0.3 mm error here shows up as a black strip or a cropped edge in the window.
3. Fold the FPC and measure how far it sticks out past the glass end (`--fpc-bend`, 0.9 mm by default).

## Not covered here

- **Middle frame:** the FPC fold runs into the middle frame's right rim (X 63.8…64.7, Y 1…65.6, Z 37.3…38.8, about 89 mm³). That rim needs a relief cut before the display fits. The glass itself does not collide with anything; checked against every part of the official assembly with `amoled55_display_dummy.step`.
- Where the driver board goes, and how the HDMI and USB (touch) cables reach it.

## Files

| File | |
|---|---|
| `uConsole_front_panel_amoled55.step` / `.stl` | the reworked front panel |
| `amoled55_display_dummy.step` / `.stl` | display glass and FPC fold envelope, for fit checks |
| `build_front_panel.py` | the script that builds both from `front_panel/uConsole_front_panel.step` |

## Rebuilding

```sh
pip install cadquery-ocp
python build_front_panel.py --help
python build_front_panel.py --aa-offset-fpc 5.6 --fpc-bend 0.7
```

Main options: `--fpc-side left|right`, `--aa-offset-fpc`, `--fpc-bend`, `--glass-w/--glass-h/--glass-t`, `--aa-w/--aa-h`,
`--window-margin`, `--pocket-depth`, `--pocket-clearance`, `--bezel-w`.
