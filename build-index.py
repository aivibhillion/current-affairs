#!/usr/bin/env python3
"""build-index.py - VibhillionAI Current Affairs
Lists every folder like 2026-Telugu/October/ and writes content-index.json
({"folder/path": [{"name":..., "type":"file|dir"}]}) so the viewer never hits the
GitHub API rate limit. Run automatically by the Pages workflow on each push."""
import json, re
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

def clean(h):
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", h).strip()

# _meta : for each .html file -> its <title> and the tab/section names inside
meta = {}
for f in ROOT.rglob("*.html"):
    rel = f.relative_to(ROOT).as_posix()
    if rel.startswith((".git", ".github")) or rel == "index.html":
        continue
    try:
        t = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    title = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
    secs = []
    nav = re.search(r'<div class="nav">(.*?)</div>', t, re.S)
    if nav:
        secs = [clean(x) for x in re.findall(r"<a[^>]*>(.*?)</a>", nav.group(1), re.S)]
    else:
        d = re.search(r'<script type="application/json" id="data">(.*?)</script>', t, re.S)
        if d:
            try:
                secs = [clean(x["name"]) for x in json.loads(d.group(1)).get("secs", [])]
            except Exception:
                pass
    meta[rel] = {"title": clean(title.group(1)) if title else "", "sections": [x for x in secs if x]}
idx["_meta"] = meta
(ROOT / "content-index.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
print("indexed", len(idx), "folders")
