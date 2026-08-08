# Roadmap

Prose mirror of the GitHub milestones and issues, so the repo is legible without the tracker. The tracker is authoritative for status; this file is authoritative for intent.

## Milestone 1 — Foundation docs

The thinking, memorialized. The scaffold you're reading (philosophy, tiers, patterns, Kū design) ships with this milestone; what remains is grounding it in measurement:

- **Finalize tier definitions with real measurements.** The Tier 1/2/3 numbers in [docs/tiers.md](docs/tiers.md) are educated defaults. Validate model-size/context/memory floors against actual local runs (including calibrating Tier 3 against the DGX Spark) and update the doc.
- **Tier benchmark methodology.** A small, repeatable task suite that certifies "this tool runs at Tier N" — so tier declarations become testable claims, not vibes.
- **License posture check-in.** MIT everywhere for now; revisit whether `docs/` wants CC BY 4.0 if attribution norms start to matter.

## Milestone 2 — Kū v0

The keystone tool, built to its own rules ([design](design/ku/overview.md)):

- **Kū v0 implementation.** The full journey: setup interview → tier determination → budget-fit skill design → transparency pass → manifest + scaffold generation.
- **Manifest validator.** Deterministic linter for `manifest.yaml` (schema check, token counting, grant/manifest drift) — the first inhabitant of `tools/`, and a not-AI artifact by design.
- **Permission grants file.** `~/.kamaaina/grants.yaml` read/write, presentation generation, and escalation-on-diff per the [permission model](design/ku/permission-model.md).
- **Context-base reference design.** The indexed, budget-chunked external-memory format and its traversal protocol ([pattern 2](docs/patterns/context-engineering.md)) — a Class 1 spec plus a Class 2 scaffold tool.
- **Benchmarking & testing suite.** A CLI (offline, stdlib-only) plus a GitHub Action running the same checks — manifest validation, budget measurement, repo lints, and verification of checked-in tier-certification records — so every artifact developed for Kamaʻāina is held to the standards mechanically. CI verifies records; contributors run the models.

## Milestone 3 — First refactors

Kū proves itself on real frontier-era skills:

- **Refactor teach-me.** The 953-line monolith becomes a tier-declared tool: routed phases, externalized invariants, page-at-a-time generation, deterministic verification, offline-safe. The [context-budget case study](design/ku/context-budget.md#case-study-teach-me-blows-the-budget) is the spec of the problem.
- **Port one hacky-hours verb.** Replace subagent fan-out with routing + external memory; establish the pattern for multi-persona work on single-context stacks.
- **Compaction reference implementation.** A working demonstration of checkpoint compaction and state hot-swap on an actual Tier 1 model.

## Beyond

Unscheduled but on the horizon: harness adapters that translate manifests into runtime sandboxing; skill evals at tier; multi-skill composition through shared context-bases; a distribution story ("download and it just works at your tier").
