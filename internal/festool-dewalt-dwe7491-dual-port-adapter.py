#!/usr/bin/env python3
"""DWE7491 dual-port: rear 65.41 socket + Festool 27mm + 1.5\" branch stub + tether ear.

Proportions match the earlier tall layout: full-depth friction socket, long cone,
side branch mid-cone with a stepped root collar (not clipped into the socket).
"""
from pathlib import Path
import numpy as np
import trimesh
from build123d import (
    BuildPart,
    BuildSketch,
    Circle,
    Plane,
    Mode,
    Locations,
    Rectangle,
    extrude,
    loft,
    export_stl,
)

STORE = Path(__file__).resolve().parents[1]
OUT_STL = STORE / "docs" / "festool-27mm-to-dewalt-dwe7491-dual-port-adapter.stl"
REF = STORE / "internal" / "Festool_27mm_HoseConnector.stl"

SOCKET_ID = 65.41
SOCKET_DEPTH = 25.0  # full friction-fit length on the saw stub
WALL = 2.5
SOCKET_OD = SOCKET_ID + 2 * WALL
CHAMFER_DEPTH = 1.5
CHAMFER_ID = SOCKET_ID + 2.0
FEST_OD, FEST_ID = 40.0, 36.0
# Tall enough that the full branch collar sits BELOW the Festool sleeve so the
# hose cuff can slide on and twist-lock (needs ~30 mm clear above the branch).
TRANS_H = 54.0
OVERLAP = 2.0

STUB_OD0 = 37.8
STUB_OD1 = 38.4
STUB_ID = 32.0
STUB_R = STUB_OD1 / 2
BRANCH_LEN = 54.0
# Stepped collar at the root (matches earlier robust junction look)
COLLAR_LEN = 16.0
COLLAR_OD = STUB_OD0 + 8.0  # ~45.8
COLLAR_R = COLLAR_OD / 2
# Center branch in the cone band; keep collar top below Festool by ≥3 mm.
_Z_FEST0 = SOCKET_DEPTH + TRANS_H - OVERLAP
_BAND = _Z_FEST0 - SOCKET_DEPTH
BRANCH_Z = SOCKET_DEPTH + _BAND / 2.0  # ≈ 51
assert BRANCH_Z - STUB_R >= SOCKET_DEPTH, "branch eats friction socket"
assert BRANCH_Z + COLLAR_R <= _Z_FEST0 - 3.0, "branch blocks Festool hose cuff"
# Local cone OD at BRANCH_Z is ~50 mm+; start inside that skin.
BRANCH_START = 12.0

# Tether lug on +Y at stub mid-height (into the wall, hole clear of OD)
HOLE_D = 4.0
EAR_HOLE_X = BRANCH_START + COLLAR_LEN + 10.0
EAR_HOLE_Y = STUB_R + 7.0
EAR_X0, EAR_X1 = EAR_HOLE_X - 7.0, EAR_HOLE_X + 7.0
EAR_Y0 = STUB_R - 3.0
EAR_Y1 = EAR_HOLE_Y + 6.0
EAR_Z_BOT = BRANCH_Z - 3.5
EAR_Z_TOP = BRANCH_Z + 3.5
EAR_THICK = EAR_Z_TOP - EAR_Z_BOT


def to_mesh(shape, path: Path) -> trimesh.Trimesh:
    export_stl(shape, path)
    m = trimesh.load(str(path), force="mesh")
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    m.merge_vertices()
    m.process(validate=True)
    if not m.is_watertight:
        raise RuntimeError(f"{path} not watertight vol={getattr(m, 'volume', '?')}")
    return m


def build_main():
    z_trans0 = SOCKET_DEPTH
    z_trans1 = SOCKET_DEPTH + TRANS_H
    with BuildPart() as main:
        with BuildSketch(Plane.XY):
            Circle(SOCKET_OD / 2)
        extrude(amount=SOCKET_DEPTH)
        with BuildSketch(Plane.XY.offset(z_trans0)):
            Circle(SOCKET_OD / 2)
        with BuildSketch(Plane.XY.offset(z_trans1)):
            Circle(FEST_OD / 2)
        loft()
        with BuildSketch(Plane.XY.offset(z_trans1 - OVERLAP)):
            Circle(FEST_OD / 2)
        extrude(amount=OVERLAP + 1.0)
        with BuildSketch(Plane.XY):
            Circle(CHAMFER_ID / 2)
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        loft(mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        extrude(amount=SOCKET_DEPTH - CHAMFER_DEPTH + 0.01, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(z_trans0 - 0.01)):
            Circle(SOCKET_ID / 2)
        with BuildSketch(Plane.XY.offset(z_trans1 + 1.0)):
            Circle(FEST_ID / 2)
        loft(mode=Mode.SUBTRACT)
    return main.part, z_trans1 - OVERLAP


def build_branch_with_ear():
    """Collar + tapered stub + tether ear, rooted into the cone."""
    ear_cx = (EAR_X0 + EAR_X1) / 2
    ear_cy = (EAR_Y0 + EAR_Y1) / 2
    collar_end = BRANCH_START + COLLAR_LEN
    with BuildPart() as branch:
        # Root collar (larger OD) then taper to hose stub
        with BuildSketch(Plane(origin=(BRANCH_START, 0, BRANCH_Z), z_dir=(1, 0, 0))):
            Circle(COLLAR_OD / 2)
        extrude(amount=COLLAR_LEN)
        with BuildSketch(Plane(origin=(collar_end - 0.5, 0, BRANCH_Z), z_dir=(1, 0, 0))):
            Circle(STUB_OD0 / 2)
        with BuildSketch(Plane(origin=(BRANCH_LEN, 0, BRANCH_Z), z_dir=(1, 0, 0))):
            Circle(STUB_OD1 / 2)
        loft()
        # Tether tab on +Y (outside Festool r≈20)
        with BuildSketch(Plane.XY.offset(EAR_Z_BOT)):
            with Locations((ear_cx, ear_cy)):
                Rectangle(EAR_X1 - EAR_X0, EAR_Y1 - EAR_Y0)
        extrude(amount=EAR_THICK)
        with BuildSketch(Plane.XY.offset(EAR_Z_BOT - 0.2)):
            with Locations((EAR_HOLE_X, EAR_HOLE_Y)):
                Circle(HOLE_D / 2)
        extrude(amount=EAR_THICK + 0.5, mode=Mode.SUBTRACT)
        # Continuous bore into main body
        with BuildSketch(Plane(origin=(BRANCH_START - 0.2, 0, BRANCH_Z), z_dir=(1, 0, 0))):
            Circle(STUB_ID / 2)
        extrude(amount=BRANCH_LEN - BRANCH_START + 0.5, mode=Mode.SUBTRACT)
    return branch.part


def verify_hole(m: trimesh.Trimesh) -> bool:
    origin = np.array([[EAR_HOLE_X, EAR_HOLE_Y, EAR_Z_BOT - 5.0]])
    loc, _, _ = m.ray.intersects_location(origin, np.array([[0.0, 0.0, 1.0]]))
    zs = sorted(float(z) for z in loc[:, 2]) if len(loc) else []
    print(f"hole ray hits={len(zs)} zs={[round(z, 2) for z in zs]}")
    return len(zs) == 0


def verify_attached(m: trimesh.Trimesh) -> bool:
    try:
        components = m.split(only_watertight=False)
    except Exception:
        components = [m]
    n = len(components) if isinstance(components, list) else 1
    print(f"connected_components={n} wt={m.is_watertight}")
    o = np.array([[EAR_HOLE_X, EAR_HOLE_Y + 3.0, EAR_Z_BOT - 5.0]])
    loc, _, _ = m.ray.intersects_location(o, np.array([[0.0, 0.0, 1.0]]))
    zs = sorted(float(z) for z in loc[:, 2]) if len(loc) else []
    print(f"ear plate ray hits={len(zs)} zs={[round(z, 2) for z in zs]}")
    plate_ok = len(zs) >= 2 and zs[0] <= EAR_Z_BOT + 0.2 and zs[-1] >= EAR_Z_TOP - 0.2
    return n == 1 and plate_ok


def verify_branch_junction(m: trimesh.Trimesh) -> bool:
    y = 0.5 * (STUB_ID / 2 + STUB_OD0 / 2)
    z = BRANCH_Z
    o = np.array([[-40.0, y, z]])
    loc, _, _ = m.ray.intersects_location(o, np.array([[1.0, 0.0, 0.0]]))
    xs = sorted(float(x) for x in loc[:, 0]) if len(loc) else []
    print(f"junction ray y={y:.1f} z={z:.1f} hits={len(xs)} xs={[round(x, 2) for x in xs]}")
    intervals = list(zip(xs[0::2], xs[1::2]))
    print(f"junction solid intervals={[(round(a, 2), round(b, 2)) for a, b in intervals]}")
    for a, b in intervals:
        if a <= 15.0 and b >= 30.0:
            return True
    return False


def verify_socket_clear(m: trimesh.Trimesh) -> bool:
    """Stub must not eat the friction socket — bottom of branch above SOCKET_DEPTH."""
    stub_bottom = BRANCH_Z - STUB_R
    ok = stub_bottom >= SOCKET_DEPTH - 0.05
    print(f"socket_depth={SOCKET_DEPTH} stub_bottom={stub_bottom:.2f} clear={ok}")
    z = SOCKET_DEPTH * 0.5
    o = np.array([[0.0, -40.0, z]])
    loc, _, _ = m.ray.intersects_location(o, np.array([[0.0, 1.0, 0.0]]))
    ys = sorted(float(y) for y in loc[:, 1]) if len(loc) else []
    print(f"socket mid-height y-hits={[round(y, 2) for y in ys]}")
    return ok and len(ys) >= 4


def verify_festool_clearance(m: trimesh.Trimesh, z_fest0: float) -> bool:
    """No branch/collar geometry inside the Festool cuff envelope.

    Hose cuff slides over the 40 mm sleeve (z_fest0 .. z_fest0+30). Keep a
    cylindrical keep-out ~r=32 mm through that band (and 2 mm below).
    """
    z_lo, z_hi = z_fest0 - 2.0, z_fest0 + 30.0
    r_keep = 32.0
    v = m.vertices
    sel = (v[:, 2] >= z_lo) & (v[:, 2] <= z_hi)
    if not sel.any():
        print("festool band: no verts")
        return False
    r = np.sqrt(v[sel, 0] ** 2 + v[sel, 1] ** 2)
    # Sleeve itself is r<=20; anything 20.5..r_keep is an intrusion.
    intr = (r > 20.5) & (r < r_keep)
    n = int(intr.sum())
    collar_top = BRANCH_Z + COLLAR_R
    print(
        f"festool z={z_fest0:.1f}..{z_fest0+30:.1f} collar_top={collar_top:.1f} "
        f"gap={z_fest0 - collar_top:.1f} intrusive_verts(r<{r_keep})={n}"
    )
    return (z_fest0 - collar_top) >= 2.5 and n == 0


def build():
    main_p, z_fest0 = build_main()
    branch_p = build_branch_with_ear()
    main_m = to_mesh(main_p, Path("/tmp/dual_main.stl"))
    branch_m = to_mesh(branch_p, Path("/tmp/dual_branch_ear.stl"))
    print(
        f"parts wt main={main_m.is_watertight} branch+ear={branch_m.is_watertight} "
        f"branch_vol={branch_m.volume:.1f} z_fest0={z_fest0} BRANCH_Z={BRANCH_Z}"
    )

    body = trimesh.boolean.union([main_m, branch_m], engine="manifold")
    body.merge_vertices()
    body.process(validate=True)
    print(f"body wt={body.is_watertight} vol={body.volume:.1f}")
    if not body.is_watertight:
        raise RuntimeError("body union not watertight")

    fest = trimesh.load(str(REF), force="mesh")
    fest.apply_translation([0, 0, z_fest0])
    united = trimesh.boolean.union([body, fest], engine="manifold")
    united.merge_vertices()
    united.process(validate=True)
    print(f"final wt={united.is_watertight} vol={united.volume:.1f}")
    if not united.is_watertight:
        raise RuntimeError("final mesh not watertight after festool union")

    OUT_STL.parent.mkdir(parents=True, exist_ok=True)
    united.export(str(OUT_STL))
    return united


if __name__ == "__main__":
    z_fest0 = SOCKET_DEPTH + TRANS_H - OVERLAP
    print(
        f"SOCKET_DEPTH={SOCKET_DEPTH} TRANS_H={TRANS_H} BRANCH_Z={BRANCH_Z:.1f} "
        f"stub_bottom={BRANCH_Z - STUB_R:.1f} collar_top={BRANCH_Z + COLLAR_R:.1f} "
        f"z_fest0={z_fest0} COLLAR_OD={COLLAR_OD}"
    )
    m = build()
    ok_hole = verify_hole(m)
    ok_att = verify_attached(m)
    ok_junc = verify_branch_junction(m)
    ok_sock = verify_socket_clear(m)
    ok_fest = verify_festool_clearance(m, z_fest0)
    print(
        f"wrote {OUT_STL} wt={m.is_watertight} extents={m.extents} "
        f"bounds={m.bounds.tolist()} hole_clear={ok_hole} attached={ok_att} "
        f"branch_joined={ok_junc} socket_clear={ok_sock} festool_clear={ok_fest}"
    )
    if not ok_hole:
        raise SystemExit("tether hole not clear along +Z at ear center")
    if not ok_att:
        raise SystemExit("tether ear not attached to stub")
    if not ok_junc:
        raise SystemExit("branch not joined to main body (gap at junction)")
    if not ok_sock:
        raise SystemExit("branch intrudes into friction socket")
    if not ok_fest:
        raise SystemExit("branch/collar blocks Festool hose twistlock cuff")
