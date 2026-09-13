# stagecraft

A consolidated suite of AI theatre/performance systems — a production framework,
a 6-layer musical-theater generation pipeline, a 3D stage for AI actors, and a
radio-drama streaming platform. Assembled 2026-09-13 from four repositories (see
`docs/PROVENANCE.md`).

## Contents

| Path | What |
|---|---|
| `framework/thespian` | AI-driven theatrical production framework (Python) |
| `pipeline/playwright` | 6-layer theater generation pipeline (Python, stdlib-only) |
| `stage3d/theater-stage` | 3D theater stage for AI actors (Three.js, jest) |
| `apps/dramas-fm` | Radio drama streaming platform (Next.js) |

## Quick start

```bash
# Thespian framework
cd framework/thespian && pip install -r ../../requirements/thespian.txt && pytest tests/

# PlayWright pipeline (stdlib only)
cd pipeline/playwright && python -m pytest  # (no suite in source; import-check only)

# 3D stage
cd stage3d/theater-stage && npm ci && npm test

# Dramas-FM app
cd apps/dramas-fm && npm ci && npm run dev
```

See `docs/ARCHITECTURE.md` for the full layout and `docs/PROVENANCE.md` for
where every file came from.
