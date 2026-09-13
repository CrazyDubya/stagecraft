# stagecraft — architecture

A consolidated suite of AI theatre/performance systems. Public repo.

## Layout

```
stagecraft/
  framework/
    thespian/        # Thespian: AI-driven theatrical production framework (Python).
                     # thespian/agents/theatrical, thespian/llm, thespian/processors,
                     # thespian/config, cli.py, tests/ (unit + integration)
  pipeline/
    playwright/      # PlayWright's 6-layer musical-theater generation pipeline
                     # (Python, stdlib-only): layer1_seeds → layer2_foundation →
                     # layer3_translation → layer4_manifestation → layer5_critique →
                     # layer6_transformation + orchestrator/
  stage3d/
    theater-stage/   # 3D theater stage for AI actors (Three.js): blocking markers,
                     # curtains, elevating platforms, lighting presets, save/load,
                     # tests/ (jest)
  apps/
    dramas-fm/       # Radio drama streaming platform (Next.js 15, Cloudflare D1
                     # over Archive.org metadata). Finished product, kept intact.
  docs/              # PROVENANCE.md, ARCHITECTURE.md, curated PlayWright docs
  requirements/      # Per-component Python deps
```

## Conceptual seams (future work, not this merge)

- `pipeline/playwright`'s 6-layer generation pipeline produces material that
  `framework/thespian`'s production agents can stage.
- `stage3d/theater-stage` is the visualization layer where either framework's
  output can be performed.
- `apps/dramas-fm` is the distribution channel for audio drama output.

No actual integration was attempted in this consolidation — the seams are
documented, not wired.

## Dependency discipline

- `requirements/thespian.txt` and `requirements/playwright.txt` (stdlib-only)
  stay separate; never a unified env.
- `stage3d/theater-stage` and `apps/dramas-fm` are independent JS projects
  with their own package.json files.
