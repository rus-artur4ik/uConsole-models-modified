"""Rework the uConsole front panel for a 5.5" 1080x1920 AMOLED (BOE BO055FHM class).

Takes the stock front panel extracted from ClockworkPi's STEP and:
  1. removes the stock screen window and its raised bezel,
  2. cuts a pocket into the back of the plate that holds the AMOLED glass
     (the panel is only 0.68 mm thick, so it sits inside the front panel
     instead of the middle frame like the stock LCD),
  3. cuts a window sized to the AMOLED active area,
  4. adds a new raised bezel around the window.
It also writes a "dummy" body of the display (glass + FPC bend) placed where
the pocket puts it, to check the fit against the rest of the assembly.

By default the glass and its FPC fold are centred in the stock 131 mm panel,
which puts the window 2.25 mm off centre. --aa-cx 0 centres the active area
instead; the FPC end of the glass then sticks out past the stock side edge,
so the panel has to be widened there (--widen fpc|both).

All coordinates are the original assembly coordinates (mm): X across the
panel, Y along it (screen at +Y, keyboard at -Y), Z out of the front face.

Requires the OpenCascade Python bindings:  pip install cadquery-ocp
Usage:  python build_front_panel.py [--fpc-side left] [--aa-offset-fpc 5.6] [...]
        python build_front_panel.py --aa-cx 0 --widen both --suffix _centered
"""
import argparse
import os

from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace,
                                BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform)
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer, BRepFilletAPI_MakeFillet
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCP.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS

try:  # OCP >= 7.8 exposes NCollection lists here
    from OCP.collections import List_TopoDS_Shape as ShapeList
except ImportError:
    from OCP.TopTools import TopTools_ListOfShape as ShapeList

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

# Stock front panel, measured from the official model
Z_BACK = 38.78        # back face of the 1.5 mm plate, rests on the middle frame
Z_FRONT = 40.28       # front face of the plate
BEZEL_TOP = 41.28     # top of the raised bezels (1.0 mm above the plate)
FLAT_X = 64.30        # |X| up to which the front face is flat (the edge chamfer starts at 64.6)
EDGE_X = 65.50        # half width of the stock panel
EDGE_CHAMFER = 0.90   # 45 degree chamfer on the front outer edge
SIDE_STRAIGHT = 75.2  # the side edge is straight up to this Y, then turns into the R6 top corner
OLD_BEZEL = (-59.6, 59.6, -2.4, 68.8)   # XY box around the stock screen bezel incl. its fillets


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--src', default=os.path.join(REPO, 'front_panel', 'uConsole_front_panel.step'))
    p.add_argument('--out', default=HERE)
    # Display. BOE BO055FHM datasheet: glass 70.71 x 128.44 x 0.50, AA 68.31 x 121.44, Pol+Cell 0.679
    p.add_argument('--aa-w', type=float, default=121.44, help='active area, long side')
    p.add_argument('--aa-h', type=float, default=68.31, help='active area, short side')
    p.add_argument('--glass-w', type=float, default=128.44)
    p.add_argument('--glass-h', type=float, default=70.71)
    p.add_argument('--glass-t', type=float, default=0.68, help='polarizer + cell thickness')
    p.add_argument('--aa-offset-fpc', type=float, default=5.8,
                   help='glass edge to AA on the FPC/IC end (read off the vendor drawing, check on the real part)')
    p.add_argument('--fpc-side', choices=('right', 'left'), default='right',
                   help='end where the FPC folds behind the panel (the stock LCD FPC is on the right)')
    p.add_argument('--fpc-bend', type=float, default=0.9,
                   help='how far the folded FPC sticks out past the glass end')
    p.add_argument('--glass-cx', type=float, default=None,
                   help='X centre of the glass; default centres glass + FPC bend in the panel')
    p.add_argument('--aa-cx', type=float, default=None,
                   help='X centre of the active area (0 = window centred); overrides --glass-cx')
    p.add_argument('--aa-cy', type=float, default=33.3, help='Y centre of the active area (stock window centre)')
    # Front panel features
    p.add_argument('--window-margin', type=float, default=0.25, help='window overlap past the AA, per side')
    p.add_argument('--window-r', type=float, default=0.5, help='window corner radius')
    p.add_argument('--pocket-depth', type=float, default=0.75,
                   help='glass pocket depth from the back face (glass + ~0.07 mm adhesive)')
    p.add_argument('--pocket-clearance', type=float, default=0.10, help='gap around the glass, per side')
    p.add_argument('--pocket-r', type=float, default=0.3, help='pocket corner radius (<= 0.3 clears a square glass corner)')
    p.add_argument('--bezel-w', type=float, default=2.0, help='raised bezel width')
    p.add_argument('--bezel-min', type=float, default=1.2,
                   help='bezel sides narrower than this (after clipping to the flat face) are left out')
    p.add_argument('--bezel-r', type=float, default=1.5, help='bezel outer corner radius')
    p.add_argument('--bezel-edge-r', type=float, default=0.4, help='fillet on the bezel top edges')
    # Widening the panel where the glass does not fit inside the stock 131 mm width
    p.add_argument('--widen', choices=('none', 'fpc', 'both'), default='none',
                   help='grow the side edge next to the display: on the FPC side only, or on both sides')
    p.add_argument('--widen-x', type=float, default=68.8,
                   help='new half width there (68.8 = the middle frame side lugs)')
    p.add_argument('--min-wall', type=float, default=0.7, help='smallest side wall left around the pocket')
    p.add_argument('--suffix', default='', help='appended to the output file names')
    a = p.parse_args()
    fpc_end = a.aa_offset_fpc
    other_end = a.glass_w - a.aa_w - a.aa_offset_fpc
    sign = 1 if a.fpc_side == 'right' else -1
    if a.aa_cx is not None:
        a.glass_cx = a.aa_cx + sign * (fpc_end - other_end) / 2
    elif a.glass_cx is None:
        a.glass_cx = -sign * a.fpc_bend / 2
    return a


def box(x0, x1, y0, y1, z0, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def edges(shape):
    e = TopExp_Explorer(shape, TopAbs_EDGE)
    while e.More():
        yield TopoDS.Edge(e.Current())
        e.Next()


def edge_points(edge):
    return (BRep_Tool.Pnt_s(TopExp.FirstVertex_s(edge)),
            BRep_Tool.Pnt_s(TopExp.LastVertex_s(edge)))


def fillet(shape, r, pick):
    """Fillet every edge whose end points satisfy pick(p0, p1)."""
    mk = BRepFilletAPI_MakeFillet(shape)
    n = 0
    for e in edges(shape):
        if pick(*edge_points(e)):
            mk.Add(r, e)
            n += 1
    if not n:
        return shape
    mk.Build()
    if not mk.IsDone():
        raise RuntimeError('fillet failed')
    return mk.Shape()


def vertical(p0, p1):
    return abs(p0.X() - p1.X()) < 1e-6 and abs(p0.Y() - p1.Y()) < 1e-6


def at_z(z):
    return lambda p0, p1: abs(p0.Z() - z) < 1e-6 and abs(p1.Z() - z) < 1e-6


def rounded_box(x0, x1, y0, y1, z0, z1, r):
    b = box(x0, x1, y0, y1, z0, z1)
    return fillet(b, r, vertical) if r > 0 else b


def shape_list(*shapes):
    lst = ShapeList()
    for s in shapes:
        lst.Append(s)
    return lst


def boolean(op, a, b, fuzzy=1e-4):
    alg = op()
    alg.SetArguments(shape_list(a))
    alg.SetTools(shape_list(b))
    alg.SetFuzzyValue(fuzzy)
    alg.Build()
    if not alg.IsDone():
        raise RuntimeError(f'{op.__name__} failed')
    u = ShapeUpgrade_UnifySameDomain(alg.Shape(), True, True, True)
    u.Build()
    return u.Shape()


def volume(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    return p.Mass()


def read_step(path):
    r = STEPControl_Reader()
    if r.ReadFile(path) != IFSelect_RetDone:
        raise RuntimeError(f'cannot read {path}')
    r.TransferRoots()
    return r.OneShape()


def write_step(shape, path):
    Interface_Static.SetCVal_s('write.step.schema', 'AP214')
    Interface_Static.SetCVal_s('write.step.unit', 'MM')
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    w.Write(path)


def write_stl(shape, path, deflection=0.02):
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.2, True).Perform()
    w = StlAPI_Writer()
    w.ASCIIMode = False
    w.Write(shape, path)


def layout(a):
    """Glass, active area, window and pocket rectangles as (x0, x1, y0, y1)."""
    side = (a.glass_h - a.aa_h) / 2                   # long-edge borders
    other_end = a.glass_w - a.aa_w - a.aa_offset_fpc  # border at the end opposite the FPC
    gx0, gx1 = a.glass_cx - a.glass_w / 2, a.glass_cx + a.glass_w / 2
    if a.fpc_side == 'right':
        ax0, ax1 = gx0 + other_end, gx1 - a.aa_offset_fpc
    else:
        ax0, ax1 = gx0 + a.aa_offset_fpc, gx1 - other_end
    ay0, ay1 = a.aa_cy - a.aa_h / 2, a.aa_cy + a.aa_h / 2
    glass = (gx0, gx1, ay0 - side, ay1 + side)
    aa = (ax0, ax1, ay0, ay1)
    m = a.window_margin
    window = (ax0 - m, ax1 + m, ay0 - m, ay1 + m)
    c = a.pocket_clearance
    px0, px1 = gx0 - c, gx1 + c
    if a.fpc_side == 'right':
        px1 += a.fpc_bend
    else:
        px0 -= a.fpc_bend
    pocket = (px0, px1, glass[2] - c, glass[3] + c)
    return glass, aa, window, pocket


def edge(p0, p1, mid=None):
    curve = GC_MakeArcOfCircle(p0, mid, p1).Value() if mid else GC_MakeSegment(p0, p1).Value()
    return BRepBuilderAPI_MakeEdge(curve).Edge()


def side_bulge(a, pocket, side):
    """Extension of the plate past the stock side edge, with the stock 45 degree edge chamfer.

    The outline leaves the stock edge through a concave R1.5 blend, runs out to
    --widen-x with R1.5 corners and comes back the same way, far enough past the
    pocket ends to keep the corner walls thick. Built on the right, mirrored for the left.
    """
    r, R, e, x_in = 1.5, 1.5, 0.5, EDGE_X - 1.5
    if r + R > a.widen_x - EDGE_X:
        raise SystemExit("--widen-x is too small for the blend radii")
    x0, x1 = EDGE_X, a.widen_x
    y0, y1 = pocket[2] - 3.3, pocket[3] + 3.3
    if y1 + r + e > SIDE_STRAIGHT:
        raise SystemExit('the widened part would run into the top corner of the panel')
    z = Z_BACK
    P = lambda x, y: gp_Pnt(x, y, z)
    c = 2 ** -0.5
    pts = [
        (P(x_in, y0 - r - e), P(x0, y0 - r - e), None),
        (P(x0, y0 - r - e), P(x0, y0 - r), None),
        (P(x0, y0 - r), P(x0 + r, y0), P(x0 + r - r * c, y0 - r + r * c)),     # concave blend
        (P(x0 + r, y0), P(x1 - R, y0), None),
        (P(x1 - R, y0), P(x1, y0 + R), P(x1 - R + R * c, y0 + R - R * c)),     # outer corner
        (P(x1, y0 + R), P(x1, y1 - R), None),
        (P(x1, y1 - R), P(x1 - R, y1), P(x1 - R + R * c, y1 - R + R * c)),
        (P(x1 - R, y1), P(x0 + r, y1), None),
        (P(x0 + r, y1), P(x0, y1 + r), P(x0 + r - r * c, y1 + r - r * c)),
        (P(x0, y1 + r), P(x0, y1 + r + e), None),
        (P(x0, y1 + r + e), P(x_in, y1 + r + e), None),
        (P(x_in, y1 + r + e), P(x_in, y0 - r - e), None),
    ]
    wire = BRepBuilderAPI_MakeWire()
    for p0, p1, mid in pts:
        wire.Add(edge(p0, p1, mid))
    face = BRepBuilderAPI_MakeFace(wire.Wire()).Face()
    solid = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, Z_FRONT - Z_BACK)).Shape()
    # Chamfer the new outer top edge (everything on or past the stock edge line).
    ch = BRepFilletAPI_MakeChamfer(solid)
    for ed in edges(solid):
        p0, p1 = edge_points(ed)
        if at_z(Z_FRONT)(p0, p1) and min(p0.X(), p1.X()) > x0 - 1e-6:
            ch.Add(EDGE_CHAMFER, ed)
    ch.Build()
    if not ch.IsDone():
        raise RuntimeError('chamfer on the widened edge failed')
    solid = ch.Shape()
    if side == 'left':
        t = gp_Trsf()
        t.SetMirror(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
        solid = BRepBuilderAPI_Transform(solid, t, True).Shape()
    return solid


def bezel_ring(a, win):
    """Raised bezel around the window, clipped to the flat part of the front face."""
    lo = win[0] - a.bezel_w
    hi = win[1] + a.bezel_w
    bx0, bx1 = max(lo, -FLAT_X), min(hi, FLAT_X)
    by0, by1 = win[2] - a.bezel_w, win[3] + a.bezel_w
    # Sides that would be too thin to hold are dropped: the ring stops flush with the window there.
    hole = list(win)
    dropped = []
    if win[0] - bx0 < a.bezel_min:
        bx0, hole[0] = win[0], win[0] - 1
        dropped.append('left')
    if bx1 - win[1] < a.bezel_min:
        bx1, hole[1] = win[1], win[1] + 1
        dropped.append('right')
    ring = rounded_box(bx0, bx1, by0, by1, Z_FRONT - 0.3, BEZEL_TOP, a.bezel_r)
    ring = boolean(BRepAlgoAPI_Cut, ring, rounded_box(*hole, Z_FRONT - 1, BEZEL_TOP + 1, a.window_r))
    if a.bezel_edge_r > 0:
        ring = fillet(ring, a.bezel_edge_r, at_z(BEZEL_TOP))
    return ring, (bx0, bx1, by0, by1), dropped


def main():
    a = parse_args()
    glass, aa, win, pocket = layout(a)
    print('glass  X %7.2f..%6.2f  Y %6.2f..%6.2f' % glass)
    print('AA     X %7.2f..%6.2f  Y %6.2f..%6.2f' % aa)
    print('window X %7.2f..%6.2f  Y %6.2f..%6.2f  (%.2f x %.2f)' % (*win, win[1] - win[0], win[3] - win[2]))
    print('pocket X %7.2f..%6.2f  Y %6.2f..%6.2f  depth %.2f' % (*pocket, a.pocket_depth))

    fpc = a.fpc_side
    sides = {'none': [], 'fpc': [fpc], 'both': ['left', 'right']}[a.widen]
    half = {sd: (a.widen_x if sd in sides else EDGE_X) for sd in ('left', 'right')}
    walls = {'left': pocket[0] + half['left'], 'right': half['right'] - pocket[1]}
    for sd, w in walls.items():
        print(f'side wall {sd:5s} {w:5.2f} mm at the back face' + ('' if sd not in sides else ' (widened)'))
    thin = [sd for sd, w in walls.items() if w < a.min_wall]
    if thin:
        raise SystemExit(f'pocket leaves less than {a.min_wall} mm on the {"/".join(thin)} side; '
                         'move the glass or use --widen')

    panel = read_step(a.src)
    v0 = volume(panel)

    # 1. Shave the stock bezel off just above the plate; the new bezel re-fills the rest.
    x0, x1, y0, y1 = OLD_BEZEL
    panel = boolean(BRepAlgoAPI_Cut, panel, box(x0, x1, y0, y1, Z_FRONT + 0.2, BEZEL_TOP + 1))

    # 1b. Widen the side edge(s) where the glass needs it.
    for sd in sides:
        panel = boolean(BRepAlgoAPI_Fuse, panel, side_bulge(a, pocket, sd))

    # 2. New raised bezel.
    ring, ring_box, dropped = bezel_ring(a, win)
    print('bezel  X %7.2f..%6.2f  Y %6.2f..%6.2f' % ring_box, '(no %s side)' % '/'.join(dropped) if dropped else '')
    panel = boolean(BRepAlgoAPI_Fuse, panel, ring)

    # 3. Glass pocket in the back of the plate.
    panel = boolean(BRepAlgoAPI_Cut, panel,
                    rounded_box(*pocket, Z_BACK - 1, Z_BACK + a.pocket_depth, a.pocket_r))

    # 4. Window through what is left.
    panel = boolean(BRepAlgoAPI_Cut, panel, rounded_box(*win, Z_BACK - 2, BEZEL_TOP + 2, a.window_r))

    ok = BRepCheck_Analyzer(panel).IsValid()
    print(f'valid={ok}  volume {v0:.1f} -> {volume(panel):.1f} mm3')
    if not ok:
        raise SystemExit('resulting solid is not valid')

    os.makedirs(a.out, exist_ok=True)
    name = 'uConsole_front_panel_amoled55' + a.suffix
    write_step(panel, os.path.join(a.out, name + '.step'))
    write_stl(panel, os.path.join(a.out, name + '.stl'))

    # Display dummy: glass seated in the pocket (on its adhesive) plus the FPC fold at its end.
    top = Z_BACK + a.pocket_depth - 0.07
    dummy = box(glass[0], glass[1], glass[2], glass[3], top - a.glass_t, top)
    fx0, fx1 = (glass[1], glass[1] + a.fpc_bend) if a.fpc_side == 'right' else (glass[0] - a.fpc_bend, glass[0])
    fold = box(fx0, fx1, glass[2] + 3, glass[3] - 3, top - a.glass_t - 1.5, top + 0.05)
    dummy = boolean(BRepAlgoAPI_Fuse, dummy, fold)
    write_step(dummy, os.path.join(a.out, 'amoled55_display_dummy' + a.suffix + '.step'))
    write_stl(dummy, os.path.join(a.out, 'amoled55_display_dummy' + a.suffix + '.stl'), 0.1)
    print('written to', a.out)


if __name__ == '__main__':
    main()
