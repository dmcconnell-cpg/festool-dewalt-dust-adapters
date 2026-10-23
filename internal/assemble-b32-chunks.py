#!/usr/bin/env python3
"""Assemble stl-chunks/*.b32.part* into .stl.zb64 files."""
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "stl-chunks"
groups = {}
for p in sorted(CHUNKS.glob("*.b32.part*")):
    base, _, n = p.name.partition(".b32.part")
    groups.setdefault(base, []).append((int(n), p))

for base, parts in groups.items():
    parts.sort()
    data = base64.b32decode("".join(p.read_text().strip() for _, p in parts))
    if base.startswith("docs__"):
        dest = ROOT / "docs" / base[len("docs__") :]
    elif base.startswith("internal__"):
        dest = ROOT / "internal" / base[len("internal__") :]
    else:
        dest = ROOT / "docs" / base
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"wrote {dest.relative_to(ROOT)} ({len(data)} bytes) from {len(parts)} b32 parts")
