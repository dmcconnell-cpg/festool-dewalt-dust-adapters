#!/usr/bin/env python3
"""Festool CT MIDI II 27mm twistlock ↔ Dewalt DW735 dust-port adapter.

Generates docs/festool-27mm-to-dewalt-dw735-61.5mm-adapter.stl by:
  1. Building Dewalt friction socket + transition (build123d)
  2. Boolean-union with the measured Festool 27mm reference mesh

Requires: build123d, trimesh, manifold3d, numpy
"""
from pathlib import Path
import numpy as np
import trimesh
from build123d import BuildPart, BuildSketch, Circle, Plane, extrude, loft, Mode, export_stl

STORE = Path(__file__).resolve().parents[1]
OUT_STL = STORE / "docs" / "festool-27mm-to-dewalt-dw735-61.5mm-adapter.stl"
REF = STORE / "internal" / "Festool_27mm_HoseConnector.stl"

# Dewalt DW735 — user primary OD 61.50 mm; PortMatch lists ~62 mm (2-7/16")
DEWALT_OD = 61.50
CLEARANCE = 1.30  # 62.80 - 61.50; confirmed shop fit
SOCKET_ID = 62.80  # confirmed fit-test ring
SOCKET_DEPTH = 25.0
WALL = 2.5
SOCKET_OD = SOCKET_ID + 2 * WALL  # 67.80
CHAMFER_DEPTH = 1.5
CHAMFER_ID = SOCKET_ID + 2.0  # 64.80 lead-in

# Festool 27mm (CT MIDI II) twistlock sleeve — measured from REF (NOT D36 hose)
FEST_H, FEST_OD, FEST_ID = 30.0, 40.0, 36.0
TRANS_H, OVERLAP = 22.0, 2.0


def build():
    z_sock1 = SOCKET_DEPTH
    z_trans0, z_trans1 = z_sock1, z_sock1 + TRANS_H
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

    tmp = Path("/tmp/adapter_body.stl")
    export_stl(adapter.part, tmp)

    fest = trimesh.load(str(REF))
    # Native Festool Z=0 joins transition; Z=30 (hose/tool face with lug access) points +Z
    fest.apply_translation([0, 0, z_fest0])
    body = trimesh.load(str(tmp))
    united = trimesh.boolean.union([body, fest], engine="manifold")
    united.merge_vertices()
    united.process(validate=True)

    OUT_STL.parent.mkdir(parents=True, exist_ok=True)
    united.export(str(OUT_STL))
    return united


if __name__ == "__main__":
    m = build()
    print(f"wrote {OUT_STL} wt={m.is_watertight} vol={m.volume:.1f} extents={m.extents}")
