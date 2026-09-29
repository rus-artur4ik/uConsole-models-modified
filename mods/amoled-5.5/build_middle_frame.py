"""Rework the uConsole middle frame to go with build_front_panel.py.

Takes the stock middle frame extracted from ClockworkPi's STEP and:
  1. widens the top band of the side wall(s) to --widen-x, flush with the
     widened front panel (only when --widen is used): it carries the end of
     the glass that sticks out past the stock side and covers the FPC fold,
  2. cuts a relief on the FPC side: a slot for the FPC fold at the glass end
     and a passage through the rim of the stock LCD pocket, so the FPC can
     run under the glass into the stock pocket and FPC channel.

It takes the same display and layout options as build_front_panel.py, so
build both parts with the same arguments.

Usage:  python build_middle_frame.py                                   # offset window
        python build_middle_frame.py --aa-cx 0 --widen both --suffix _centered
"""
import os

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

from build_front_panel import (REPO, Z_BACK, EDGE_X, boolean, box, bulge_face, chamfer_outer,
                               finish_args, layout, make_parser, mirror_x, read_step, volume,
                               widened_sides, write_step, write_stl)

# Stock middle frame, measured from the official model
Z_TOP = Z_BACK        # top face, the front panel rests on it
TOP_CHAMFER = 0.2     # small chamfer on the outer top edge (the groove where frame and panel meet)
LUG_TOP = 36.77       # top of the side lugs (part s3) at the upper corners, just outside the side wall
RIM_INNER_X = 62.3    # inner edge of the rim on the right of the stock LCD pocket (pocket floor 36.78)


def parse_args():
    p = make_parser(__doc__)
    p.add_argument('--frame-src', default=os.path.join(REPO, 'middle_frame', 'uConsole_middle_frame.step'))
    p.add_argument('--band-bottom', type=float, default=36.9,
                   help='lowest Z of the widened band; must stay above the side lugs (36.77) and ports (34.2)')
    p.add_argument('--band-chamfer', type=float, default=0.5, help='chamfer on the underside edge of the band')
    p.add_argument('--relief-clearance', type=float, default=0.15,
                   help='gap around the FPC fold envelope in the relief')
    return finish_args(p.parse_args())


def side_band(a, pocket, side):
    """Top band of the side wall pushed out to --widen-x, same outline as the widened front panel."""
    face = bulge_face(a, pocket, a.band_bottom)
    band = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, Z_TOP - a.band_bottom)).Shape()
    band = chamfer_outer(band, TOP_CHAMFER, Z_TOP)
    if a.band_chamfer > 0:
        band = chamfer_outer(band, a.band_chamfer, a.band_bottom)
    return mirror_x(band) if side == 'left' else band


def main():
    a = parse_args()
    if a.band_bottom <= LUG_TOP:
        raise SystemExit(f'--band-bottom must be above the side lugs at Z {LUG_TOP}')
    glass, aa, win, pocket = layout(a)
    sides = widened_sides(a)

    # FPC relief: from inside the stock pocket rim out to the end of the front panel pocket,
    # over the length of the fold, deep enough for the folded FPC under the glass.
    c = a.relief_clearance
    rel_z = Z_TOP - a.fold_depth - c
    rel_y = (glass[2] + 3 - c, glass[3] - 3 + c)
    if a.fpc_side == 'right':
        rel_x = (RIM_INNER_X, pocket[1])
    else:
        rel_x = (pocket[0], -RIM_INNER_X)
    outer = max(abs(rel_x[0]), abs(rel_x[1]))
    side_x = a.widen_x if a.fpc_side in sides else EDGE_X
    print('glass  X %7.2f..%6.2f  Y %6.2f..%6.2f' % glass)
    print('relief X %7.2f..%6.2f  Y %6.2f..%6.2f  Z %.2f..top' % (*rel_x, *rel_y, rel_z))
    print(f'side wall left beside the relief: {side_x - outer:.2f} mm')
    if a.fpc_side in sides:
        print(f'floor under the relief in the widened band: {rel_z - a.band_bottom:.2f} mm')
    if side_x - outer < 0.5:
        raise SystemExit('relief leaves less than 0.5 mm of side wall')

    frame = read_step(a.frame_src)
    v0 = volume(frame)
    for sd in sides:
        frame = boolean(BRepAlgoAPI_Fuse, frame, side_band(a, pocket, sd))
        print(f'widened {sd} band to X {a.widen_x} over Z {a.band_bottom}..{Z_TOP}')
    frame = boolean(BRepAlgoAPI_Cut, frame, box(rel_x[0], rel_x[1], rel_y[0], rel_y[1], rel_z, Z_TOP + 1))

    ok = BRepCheck_Analyzer(frame).IsValid()
    print(f'valid={ok}  volume {v0:.1f} -> {volume(frame):.1f} mm3')
    if not ok:
        raise SystemExit('resulting solid is not valid')
    name = 'uConsole_middle_frame_amoled55' + a.suffix
    write_step(frame, os.path.join(a.out, name + '.step'))
    write_stl(frame, os.path.join(a.out, name + '.stl'), 0.03)
    print('written to', a.out)


if __name__ == '__main__':
    main()
