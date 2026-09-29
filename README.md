# uConsole-models
Github source for ClockworkPi's official STP and OBJ files for the uConsole, republished here under GPL3 to bypass the checkout/signup step for the download on their website.

### Official source:
https://www.clockworkpi.com/product-page/uconsole-3d-models-in-obj-format-free

![uconsole](https://github.com/user-attachments/assets/4b83cf33-6092-474d-aaeb-d8807baeee94)

### Extracted parts

| Part | Files | Size |
|------|-------|------|
| Front panel (screen window, D-pad/button and keyboard cutouts) | [STL](front_panel/uConsole_front_panel.stl) · [STEP](front_panel/uConsole_front_panel.step) | 131 × 174.5 × 3.5 mm |
| Middle frame | [STL](middle_frame/uConsole_middle_frame.stl) · [STEP](middle_frame/uConsole_middle_frame.step) | 137.6 × 174.5 × 14.5 mm |

### Mods

| Mod | Files |
|-----|-------|
| 5.5" 1080×1920 AMOLED (BOE BO055FHM), window offset 2.75 mm, stock outline | [README](mods/amoled-5.5/README.md) · front panel [STL](mods/amoled-5.5/uConsole_front_panel_amoled55.stl) / [STEP](mods/amoled-5.5/uConsole_front_panel_amoled55.step) · middle frame [STL](mods/amoled-5.5/uConsole_middle_frame_amoled55.stl) / [STEP](mods/amoled-5.5/uConsole_middle_frame_amoled55.step) |
| Same display, window centred, case widened to 137.6 mm next to the screen | [README](mods/amoled-5.5/README.md#centred-window-_amoled55_centered) · front panel [STL](mods/amoled-5.5/uConsole_front_panel_amoled55_centered.stl) / [STEP](mods/amoled-5.5/uConsole_front_panel_amoled55_centered.step) · middle frame [STL](mods/amoled-5.5/uConsole_middle_frame_amoled55_centered.stl) / [STEP](mods/amoled-5.5/uConsole_middle_frame_amoled55_centered.step) |

The front panel (solid `brep_6`) and middle frame (`brep_7`) were extracted from the original STP with OpenCascade, keeping the original assembly coordinates. Opening the STL on GitHub shows an interactive 3D preview.
