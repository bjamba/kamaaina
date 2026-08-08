<!-- Kamaʻāina PR template — see CONTRIBUTING.md for the full expectations. -->

## What & why

<!-- What this PR changes and the problem it solves. Link the issue(s) it addresses. -->

Closes #

## Artifact class

<!-- Every contribution is exactly one (see docs/philosophy.md). Delete the other line. -->

- [ ] **Class 1** — human-directed documentation (`docs/`, `design/`)
- [ ] **Class 2** — local-AI-directed tool (`tools/`) — manifest required

## Class 2 checklist <!-- delete this section for Class 1 PRs -->

- [ ] `manifest.yaml` present and consistent with the instruction files (declared `state_files`, `exec`, permissions all match what the instructions actually do)
- [ ] Worst-case simultaneous instruction load fits the declared `instructions_max_tokens` and the tier guideline in `docs/tiers.md`
- [ ] `tier.minimum > 1` carries a written `justification`
- [ ] `not_ai` block reflects every deterministic step; remaining model-steps genuinely need a model
- [ ] Works with `network: none` at use-time (no frontier calls in the loop)

## Class 1 checklist <!-- delete this section for Class 2 PRs -->

- [ ] Internal links resolve; tier names/numbers reference `docs/tiers.md` rather than restating them
- [ ] New named artifacts added to the glossary in `docs/naming.md`

## Both

- [ ] Hawaiian orthography in prose (ʻokina/kahakō), ASCII in paths and identifiers
- [ ] ROADMAP.md updated if this changes milestone intent

## How it was verified

<!-- Commands run, tiers tested on, docs proofread by whom/what. Be literal. -->
