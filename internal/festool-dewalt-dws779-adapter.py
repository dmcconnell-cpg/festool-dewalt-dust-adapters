#!/usr/bin/env python3
"""Festool CT MIDI II 27mm twistlock ↔ Dewalt DWS779 miter dust port.

Stub OD 42.33 mm; socket ID 42.23 mm — locked from shop fit-test ring.
"""
from pathlib import Path
import numpy as np
import trimesh
from build123d import BuildPart, BuildSketch, Circle, Plane, extrude, loft, Mode, export_stl

STORE = Path(__file__).resolve().parents[1]
OUT_STL = STORE / "docs" / "festool-27mm-to-dewalt-dws779-42.33mm-adapter.stl"
REF = STORE / "internal" / "Festool_27mm_HoseConnector.stl"

TOOL_OD = 42.33
SOCKET_ID = 42.23  # confirmed fit-test ring
SOCKET_DEPTH = 25.0
WALL = 2.5
SOCKET_OD = SOCKET_ID + 2 * WALL
CHAMFER_DEPTH = 1.5
CHAMFER_ID = SOCKET_ID + 2.0
FEST_H, FEST_OD, FEST_ID = 30.0, 40.0, 36.0
TRANS_H, OVERLAP = 18.0, 2.0

def build():
    z_trans0, z_trans1 = SOCKET_DEPTH, SOCKET_DEPTH + TRANS_H
    z_fest0 = z_trans1 - OVERLAP
    with BuildPart() as adapter:
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
    tmp = Path("/tmp/dws779_body.stl")
    export_stl(adapter.part, tmp)
    body = trimesh.load(str(tmp), force="mesh")
    fest = trimesh.load(str(REF), force="mesh")
    fest.apply_translation([0, 0, z_fest0])
    united = trimesh.boolean.union([body, fest], engine="manifold")
    united.merge_vertices()
    united.process(validate=True)
    OUT_STL.parent.mkdir(parents=True, exist_ok=True)
    united.export(str(OUT_STL))
    return united

if __name__ == "__main__":
    m = build()
    print(f"wrote {OUT_STL} wt={m.is_watertight} extents={m.extents}")
