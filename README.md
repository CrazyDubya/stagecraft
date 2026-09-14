# stagecraft

A consolidated suite of AI theatre/performance systems — a production framework,
a 6-layer musical-theater generation pipeline, a 3D stage for AI actors, a
radio-drama streaming platform, a multi-agent theater criticism system, and an
LLM-powered courtroom simulator.
Assembled 2026-09-13 from four repositories, extended 2026-09-13 with a fifth
and 2026-09-14 with a sixth (see `docs/PROVENANCE.md`).

## Contents

| Path | What |
|---|---|
| `framework/thespian` | AI-driven theatrical production framework (Python) |
| `pipeline/playwright` | 6-layer theater generation pipeline (Python, stdlib-only) |
| `stage3d/theater-stage` | 3D theater stage for AI actors (Three.js, jest) |
| `apps/dramas-fm` | Radio drama streaming platform (Next.js) |
| `theater-critics/` | Multi-agent theater criticism system — AI critic ensemble (Ollama) analyzing musical theater across 18 evaluation dimensions, with `playwright_export.py` feeding the pipeline (Python) |
| `courthouse/` | LLM Courtroom Simulator — multi-agent 3D courtroom drama: each participant (judge, attorneys, witnesses, jury) is an autonomous AI agent with personality, memory, and objectives, playing out full trial proceedings; the user can take any role (Three.js/React frontend, Express backend with Ollama/OpenAI) |

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

# Theater critics (needs Ollama models + pip install -r requirements.txt)
cd theater-critics && python -m pytest

# Courtroom simulator (frontend + backend; backend tests need no live services)
cd courthouse && npm ci && npm run test:run
cd courthouse/backend && npm ci && npm test
```

See `docs/ARCHITECTURE.md` for the full layout and `docs/PROVENANCE.md` for
where every file came from.
