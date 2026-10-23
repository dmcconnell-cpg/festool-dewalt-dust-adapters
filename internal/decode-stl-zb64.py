#!/usr/bin/env python3
"""Decode *.stl.zb64 (zlib+base64 of binary STL) next to this script's outputs.

Usage: python3 internal/decode-stl-zb64.py
Writes binary STLs to docs/ and internal/ from sibling *.stl.zb64 packs.
"""
from pathlib import Path
import base64, zlib, sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    packs = list(ROOT.rglob("*.stl.zb64"))
    if not packs:
        print("no .stl.zb64 packs found", file=sys.stderr)
        return 1
    for pack in sorted(packs):
        out = Path(str(pack)[:-5])  # strip .zb64
        data = zlib.decompress(base64.b64decode(pack.read_text()))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        print(f"wrote {out.relative_to(ROOT)} ({len(data)} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
