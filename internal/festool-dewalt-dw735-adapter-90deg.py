#!/usr/bin/env python3
"""Festool CT MIDI II 27mm twistlock ↔ Dewalt DW735 with 90° elbow.

Generates docs/festool-27mm-to-dewalt-dw735-61.5mm-adapter-90deg.stl

Elbow is a loft of circular sections along the centerline (full tube),
not a clipped torus — an earlier torus+box clip sliced off the outer wall.

Requires: build123d, trimesh, manifold3d, numpy
"""
from pathlib import Path
import math
import numpy as np
import trimesh
from build123d import BuildPart, BuildSketch, Circle, Plane, extrude, loft, export_stl

STORE = Path(__file__).resolve().parents[1]
OUT_STL = STORE / "docs" / "festool-27mm-to-dewalt-dw735-61.5mm-adapter-90deg.stl"
REF = STORE / "internal" / "Festool_27mm_HoseConnector.stl"

SOCKET_ID = 62.80
SOCKET_DEPTH = 25.0
WALL = 2.5
SOCKET_OD = SOCKET_ID + 2 * WALL
CHAMFER_DEPTH = 1.5
CHAMFER_ID = SOCKET_ID + 2.0
FEST_OD, FEST_ID = 40.0, 36.0
OVERLAP = 2.5
MID_ID = 48.0
MID_OD = MID_ID + 2 * WALL
REDUCE_H = 18.0
ELBOW_R = 42.0
EXIT_STRAIGHT = 14.0
FEST_REDUCE_H = 18.0
OL = 2.0

z_red0 = SOCKET_DEPTH
z_red1 = SOCKET_DEPTH + REDUCE_H
x0 = ELBOW_R + EXIT_STRAIGHT
z_arm = z_red1 + ELBOW_R
x_fest0 = x0 + FEST_REDUCE_H - OVERLAP


def to_mesh(shape, path: Path) -> trimesh.Trimesh:
    export_stl(shape, path)
    m = trimesh.load(str(path), force="mesh")
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    if not m.is_watertight:
        raise RuntimeError(f"{path} not watertight")
    return m


def elbow_solid(radius: float, phi0_deg: float = -4, phi1_deg: float = 94, n: int = 28):
    """Full circular disk lofted along the 90° elbow centerline."""
    with BuildPart() as p:
        for i in range(n + 1):
            phi = math.radians(phi0_deg + (phi1_deg - phi0_deg) * i / n)
            cx = ELBOW_R * (1 - math.cos(phi))
            cz = z_red1 + ELBOW_R * math.sin(phi)
            tx, tz = math.sin(phi), math.cos(phi)
            with BuildSketch(Plane(origin=(cx, 0, cz), z_dir=(tx, 0, tz))):
                Circle(radius)
        loft()
    return p.part


def build() -> trimesh.Trimesh:
    outers, inners = [], []

    with BuildPart() as a:
        with BuildSketch(Plane.XY):
            Circle(SOCKET_OD / 2)
        extrude(amount=SOCKET_DEPTH + OL)
    outers.append(to_mesh(a.part, Path("/tmp/90A.stl")))
    with BuildPart() as ai:
        with BuildSketch(Plane.XY):
            Circle(CHAMFER_ID / 2)
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        loft()
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        extrude(amount=SOCKET_DEPTH - CHAMFER_DEPTH + OL + 0.5)
    inners.append(to_mesh(ai.part, Path("/tmp/90Ai.stl")))

    with BuildPart() as b:
        with BuildSketch(Plane.XY.offset(z_red0 - OL)):
            Circle(SOCKET_OD / 2)
        with BuildSketch(Plane.XY.offset(z_red1 + OL)):
            Circle(MID_OD / 2)
        loft()
    outers.append(to_mesh(b.part, Path("/tmp/90B.stl")))
    with BuildPart() as bi:
        with BuildSketch(Plane.XY.offset(z_red0 - OL - 0.2)):
            Circle(SOCKET_ID / 2)
        with BuildSketch(Plane.XY.offset(z_red1 + OL + 0.2)):
            Circle(MID_ID / 2)
        loft()
    inners.append(to_mesh(bi.part, Path("/tmp/90Bi.stl")))

    outers.append(to_mesh(elbow_solid(MID_OD / 2), Path("/tmp/90C.stl")))
    inners.append(to_mesh(elbow_solid(MID_ID / 2), Path("/tmp/90Ci.stl")))

    with BuildPart() as d:
        with BuildSketch(Plane(origin=(ELBOW_R - OL, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(MID_OD / 2)
        extrude(amount=EXIT_STRAIGHT + OL)
    outers.append(to_mesh(d.part, Path("/tmp/90D.stl")))
    with BuildPart() as di:
        with BuildSketch(Plane(origin=(ELBOW_R - OL - 0.2, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(MID_ID / 2)
        extrude(amount=EXIT_STRAIGHT + OL + 0.5)
    inners.append(to_mesh(di.part, Path("/tmp/90Di.stl")))

    with BuildPart() as e:
        with BuildSketch(Plane(origin=(x0 - OL, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(MID_OD / 2)
        with BuildSketch(Plane(origin=(x0 + FEST_REDUCE_H, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(FEST_OD / 2)
        loft()
        with BuildSketch(Plane(origin=(x_fest0, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(FEST_OD / 2)
        extrude(amount=OVERLAP + 1.0)
    outers.append(to_mesh(e.part, Path("/tmp/90E.stl")))
    with BuildPart() as ei:
        with BuildSketch(Plane(origin=(x0 - OL - 0.2, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(MID_ID / 2)
        with BuildSketch(Plane(origin=(x0 + FEST_REDUCE_H + 1.0, 0, z_arm), z_dir=(1, 0, 0))):
            Circle(FEST_ID / 2)
        loft()
    inners.append(to_mesh(ei.part, Path("/tmp/90Ei.stl")))

    outer = trimesh.boolean.union(outers, engine="manifold")
    inner = trimesh.boolean.union(inners, engine="manifold")
    body = trimesh.boolean.difference([outer, inner], engine="manifold")

    fest = trimesh.load(str(REF), force="mesh")
    fest.apply_transform(np.array([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]], float))
    fest.apply_translation([x_fest0, 0, z_arm])

    united = trimesh.boolean.union([body, fest], engine="manifold")
    united.merge_vertices()
    united.process(validate=True)
    OUT_STL.parent.mkdir(parents=True, exist_ok=True)
    united.export(str(OUT_STL))
    return united


if __name__ == "__main__":
    m = build()
    print(f"wrote {OUT_STL} wt={m.is_watertight} vol={m.volume:.1f} extents={m.extents}")
