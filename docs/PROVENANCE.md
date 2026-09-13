# PROVENANCE — stagecraft

Clean-copy consolidation of the theatre/performance cluster, executed 2026-09-13.
Each entry maps a subtree in this repo to its source repository and the exact
commit it was copied from. Source repos were archived (not deleted) after
verification; their full histories remain available there.

## Base

| Path | Source | Commit |
|---|---|---|
| `framework/thespian/` | `CrazyDubya/thespian` (renamed to `stagecraft`) | `bf6489422e23422e05a6da1610ea9e156a80f512` (main) |

Full tree copied (framework package, CLI, tests, docs, examples).

## Merged sources

| Path | Source | Commit | Notes |
|---|---|---|---|
| `pipeline/playwright/` | `CrazyDubya/PlayWright` | `1dd5af93ab3990a794ec4a6c8ebcceea15415af7` (main) | `engines/` code only: 6-layer pipeline (`layer1_seeds` → `layer6_transformation`) + `orchestrator/` (21 .py files, stdlib-only); the ~590 process-doc markdowns stay in the archived source; `CREATIVE_METHODOLOGY.md` and `QUICK_START.md` curated into `docs/` |
| `stage3d/theater-stage/` | `CrazyDubya/theater-stage` → `projects/scratch/` | `b5770511fe950a3491475220444fcba17278a1f6` (main) | Three.js 3D stage app kept as JS subproject with its own package.json |
| `apps/dramas-fm/` | `CrazyDubya/dramas-fm` | `e1f56dd672a19dacbbb76c40e73e39f6c973d7f0` (dev) | Next.js 15 radio-drama platform kept intact with its own package.json and CI; `.env.local.example` contains a real Cloudflare **account ID** (identifier, not a secret) — token field is a placeholder |

## Requirements mapping

| File | Source |
|---|---|
| `requirements/thespian.txt` | `thespian/requirements.txt` |
| `requirements/playwright.txt` | (none declared — `pipeline/playwright` is stdlib-only) |

## Visibility

Public — all absorbed sources were public.

## Verification

- Secret scan of the merged tree: clean (no API keys, tokens, or `sk-*` literals).
- Test baselines recorded pre-merge and re-run post-merge; results in the
  consolidation report. Failures match baselines exactly.
