# Archive index (experimental)

Minimum delighter slice for *searchable prompt archive index* (category:
UX/UI).

```
python3 archive-index/build-index.py
```

Walks `Anthropic/`, `Google/`, `Misc/`, `OpenAI/`, `Perplexity/`, `xAI/` and
emits:

- `archive-index/index.json` — per-entry metadata (vendor, path, size, mtime, model hint, theme hint)
- `archive-index/index.md` — human-friendly browse table

Heuristic hints are intentionally crude for this slice — richer classifiers
and a static browse site are the next pass.
