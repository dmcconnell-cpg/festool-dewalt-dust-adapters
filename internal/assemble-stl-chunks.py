#!/usr/bin/env python3
"""Assemble docs/*.stl and internal/*.stl from stl-chunks/*.partNNN shards."""
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "stl-chunks"

def main():
    groups = defaultdict(list)
    if not CHUNK_DIR.is_dir():
        print("no stl-chunks dir")
        return
    for p in sorted(CHUNK_DIR.iterdir()):
        if ".part" not in p.name:
            continue
        base, _, part = p.name.rpartition(".part")
        # base used __ for /
        rel = base.replace("__", "/")
        groups[rel].append((part, p.read_text()))
    for rel, parts in sorted(groups.items()):
        parts.sort(key=lambda x: x[0])
        content = "".join(c for _, c in parts)
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)
        print(f"wrote {rel} ({len(content)} bytes from {len(parts)} parts)")

if __name__ == "__main__":
    main()
