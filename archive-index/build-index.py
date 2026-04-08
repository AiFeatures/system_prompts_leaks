#!/usr/bin/env python3
"""
build-index.py — generate a searchable archive index over leaked system
prompts organized by vendor. Minimum delighter slice for the P1 backlog item
"searchable prompt archive index" (category: UX/UI).

Walks the repository root for known vendor directories and emits:

  archive-index/index.json   machine-readable
  archive-index/index.md     human-friendly browse

No runtime dependencies beyond the standard library.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

VENDORS = ["Anthropic", "Google", "Misc", "OpenAI", "Perplexity", "xAI"]
EXTS = {".md", ".txt", ".json"}


def walk_vendor(root: Path, vendor: str) -> list[dict]:
    vendor_dir = root / vendor
    if not vendor_dir.is_dir():
        return []
    entries: list[dict] = []
    for dirpath, _, filenames in os.walk(vendor_dir):
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in EXTS:
                continue
            rel = p.relative_to(root)
            stat = p.stat()
            entries.append(
                {
                    "vendor": vendor,
                    "path": str(rel).replace(os.sep, "/"),
                    "name": p.stem,
                    "size_bytes": stat.st_size,
                    "modified": datetime.utcfromtimestamp(stat.st_mtime)
                    .isoformat()
                    + "Z",
                    "model_hint": infer_model_hint(p.stem),
                    "theme_hint": infer_theme_hint(p.stem),
                }
            )
    return entries


def infer_model_hint(stem: str) -> str | None:
    s = stem.lower()
    for key in ("opus", "sonnet", "haiku", "gpt-4", "gpt-5", "gemini", "grok", "claude"):
        if key in s:
            return key
    return None


def infer_theme_hint(stem: str) -> str | None:
    s = stem.lower()
    for key in ("safety", "tool", "memory", "agent", "refusal", "persona", "system"):
        if key in s:
            return key
    return None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    all_entries: list[dict] = []
    for v in VENDORS:
        all_entries.extend(walk_vendor(root, v))
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "count": len(all_entries),
                "vendors": VENDORS,
                "entries": all_entries,
            },
            indent=2,
        )
    )
    md = ["# System Prompt Archive Index", ""]
    md.append(f"{len(all_entries)} files indexed across {len(VENDORS)} vendors.")
    md.append("")
    md.append("| Vendor | Path | Model hint | Theme hint |")
    md.append("|---|---|---|---|")
    for e in sorted(all_entries, key=lambda x: (x["vendor"], x["path"])):
        md.append(
            f"| {e['vendor']} | `{e['path']}` | {e['model_hint'] or '-'} | {e['theme_hint'] or '-'} |"
        )
    (out_dir / "index.md").write_text("\n".join(md) + "\n")
    print(f"Indexed {len(all_entries)} files -> archive-index/index.{{json,md}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
