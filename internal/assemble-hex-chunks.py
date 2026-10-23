#!/usr/bin/env python3
"""Assemble stl-chunks/*.hex.part* into .stl.zb64 files, then optionally decode."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "stl-chunks"
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)
(INTERNAL := ROOT / "internal").mkdir(exist_ok=True)

pat = re.compile(r"^(?P<base>.+)\.hex\.part(?P<n>\d+)$")
groups = {}
for p in sorted(CHUNKS.glob("*.hex.part*")):
    m = pat.match(p.name)
    if not m:
        continue
    groups.setdefault(m.group("base"), []).append((int(m.group("n")), p))

for base, parts in groups.items():
    parts.sort()
    hx = "".join(p.read_text().strip() for _, p in parts)
    data = bytes.fromhex(hx)
    # base is like docs__foo.stl.zb64 or internal__foo.stl.zb64
    if base.startswith("docs__"):
        dest = OUT / base[len("docs__") :]
    elif base.startswith("internal__"):
        dest = INTERNAL / base[len("internal__") :]
    else:
        dest = OUT / base
    dest.write_bytes(data)
    print(f"wrote {dest.relative_to(ROOT)} ({len(data)} bytes) from {len(parts)} hex parts")
