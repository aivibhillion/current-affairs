#!/usr/bin/env python3
"""build-index.py - VibhillionAI Current Affairs
Lists every folder like 2026-Telugu/October/ and writes content-index.json
({"folder/path": [{"name":..., "type":"file|dir"}]}) so the viewer never hits the
GitHub API rate limit. Run automatically by the Pages workflow on each push."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SKIP = {".git", ".github", "node_modules"}
idx = {}
def walk(d):
    rel = d.relative_to(ROOT).as_posix()
    rel = "" if rel == "." else rel
    items = []
    for p in sorted(d.iterdir(), key=lambda x: x.name):
        if p.name in SKIP or p.name.startswith("."):
            continue
        if p.is_dir():
            items.append({"name": p.name, "type": "dir"}); walk(p)
        else:
            items.append({"name": p.name, "type": "file"})
    idx[rel] = items
walk(ROOT)
(ROOT / "content-index.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
print("indexed", len(idx), "folders")
