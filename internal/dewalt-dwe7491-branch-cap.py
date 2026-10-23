#!/usr/bin/env python3
"""DWE7491 dual-port branch cap — friction over 1.5\" stub, tether tab with 4.0 mm hole."""
from pathlib import Path
from build123d import (
    BuildPart, BuildSketch, Circle, Plane, Mode, extrude, loft, export_stl,
    Locations, Rectangle,
)

STORE = Path(__file__).resolve().parents[1]
OUT = STORE / "docs" / "dewalt-dwe7491-branch-cap.stl"

CAP_ID = 38.7
CAP_DEPTH = 22.0
CAP_WALL = 2.5
FLANGE_EXTRA = 4.0
TAB_EXTRA = 10.0
TAB_WIDTH = 14.0
HOLE_D = 4.0
TAB_THICK = 3.0

def build():
    outer_r = CAP_ID / 2 + CAP_WALL
    flange_r = outer_r + FLANGE_EXTRA
    with BuildPart() as cap:
        with BuildSketch(Plane.XY):
            Circle(outer_r)
        extrude(amount=CAP_DEPTH + CAP_WALL)
        with BuildSketch(Plane.XY):
            Circle(CAP_ID / 2)
        extrude(amount=CAP_DEPTH, mode=Mode.SUBTRACT)
        with BuildSketch(Plane.XY):
            Circle(CAP_ID / 2 + 0.8)
        with BuildSketch(Plane.XY.offset(1.5)):
            Circle(CAP_ID / 2)
        loft(mode=Mode.SUBTRACT)
        z_flange = CAP_DEPTH + CAP_WALL
        with BuildSketch(Plane.XY.offset(z_flange)):
            Circle(flange_r)
        extrude(amount=TAB_THICK)
        with BuildSketch(Plane.XY.offset(z_flange)):
            with Locations((flange_r + TAB_EXTRA / 2 - 1, 0)):
                Rectangle(TAB_EXTRA + 6, TAB_WIDTH)
        extrude(amount=TAB_THICK)
        hole_x = flange_r + TAB_EXTRA - 3.5
        with BuildSketch(Plane.XY.offset(z_flange - 0.1)):
            with Locations((hole_x, 0)):
                Circle(HOLE_D / 2)
        extrude(amount=TAB_THICK + 0.3, mode=Mode.SUBTRACT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    export_stl(cap.part, OUT)
    return cap.part

if __name__ == "__main__":
    p = build()
    print(f"wrote {OUT} vol={p.volume:.1f}")
