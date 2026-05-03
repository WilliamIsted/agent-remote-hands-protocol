#!/usr/bin/env python3
"""One-shot fix for mojibaked / over-escaped non-ASCII in element.*.json files.

The earlier rename script read files in cp1252 (Windows default), then wrote
back as JSON with `ensure_ascii=True` (the default) escaping every non-ASCII
char as `\\uXXXX`. The cp1252 misread mojibaked UTF-8 em-dashes into
`\\u00e2\\u20ac\\u201d` etc.

This script:
  1. Loads each JSON file (json.load resolves the \\uXXXX escapes).
  2. Recursively walks all string values and undoes the cp1252 mojibake by
     re-encoding the string as cp1252 and decoding as UTF-8 — which restores
     the original UTF-8 character.
  3. Writes back with ensure_ascii=False so native UTF-8 chars are preserved.

Idempotent on already-correct text (cp1252→utf-8 round-trip on plain ASCII
or already-correct UTF-8 either passes through or fails cleanly; we
fall back to original on failure).
"""
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
files = sorted((repo_root / "spec" / "verbs").glob("element.*.json"))

def demojibake(s):
    """If s looks mojibaked (contains chars in the cp1252 high range that
    cp1252-encode + utf-8-decode cleanly), restore the original UTF-8.
    Otherwise return s unchanged."""
    if not isinstance(s, str):
        return s
    # Mojibake characters all live in the 0x80-0xFF cp1252 range plus a few
    # specials. Quick test: any char outside ASCII?
    if all(ord(c) < 128 for c in s):
        return s
    try:
        recovered = s.encode('cp1252').decode('utf-8')
        return recovered
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def walk(node):
    if isinstance(node, dict):
        return {k: walk(v) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(x) for x in node]
    if isinstance(node, str):
        return demojibake(node)
    return node

for p in files:
    with p.open('r', encoding='utf-8') as fh:
        d = json.load(fh)
    d2 = walk(d)
    with p.open('w', encoding='utf-8') as fh:
        json.dump(d2, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print(f"processed: {p.relative_to(repo_root)}")
print("done")
