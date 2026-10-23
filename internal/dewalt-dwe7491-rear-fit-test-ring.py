#!/usr/bin/env python3
"""DWE7491 rear main (was 63.91; +1.5 mm) — fit ring ID 65.41 mm, H 6.35 mm."""
from pathlib import Path
from build123d import BuildPart, BuildSketch, Circle, Plane, extrude, loft, Mode, export_stl

STORE = Path(__file__).resolve().parents[1]
OUT = STORE / "docs" / "dewalt-dwe7491-rear-63.51mm-fit-test-ring.stl"
SOCKET_ID = 65.41
WALL = 2.5
SOCKET_OD = SOCKET_ID + 2 * WALL
CHAMFER_DEPTH = 1.2
CHAMFER_ID = SOCKET_ID + 1.6
HEIGHT = 6.35
TOOL_OD = 63.51

def build():
    with BuildPart() as ring:
        with BuildSketch(Plane.XY):
            Circle(SOCKET_OD / 2)
        extrude(amount=HEIGHT)
        with BuildSketch(Plane.XY):
            Circle(CHAMFER_ID / 2)
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        loft(mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY.offset(CHAMFER_DEPTH)):
            Circle(SOCKET_ID / 2)
        extrude(amount=HEIGHT - CHAMFER_DEPTH + 0.01, mode=Mode.SUBTRACT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    export_stl(ring.part, OUT)
    return ring.part

if __name__ == "__main__":
    p = build()
    print(f"wrote {OUT} vol={p.volume:.1f}")
