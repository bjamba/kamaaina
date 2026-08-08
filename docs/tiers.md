# Hardware & Model Tiers

Every Class 2 artifact (a tool a local AI stack runs) must declare the minimum tier it needs in its manifest. This file is the single source of truth for what the tiers mean. Numbers here are educated defaults pending real measurement — see the "Finalize tier definitions" and "Tier benchmark methodology" issues.

## The design rule

> **Kū targets the lowest tier that can do the job.**

A skill that works at Tier 1 works everywhere. Declaring a higher minimum tier is a cost that must be justified in the manifest — "it was easier to write" is not a justification; "the task inherently requires holding 40k tokens of source in view" might be.

## Tier definitions

| | Tier 1 — Laptop | Tier 2 — Prosumer | Tier 3 — Workstation |
|---|---|---|---|
| Model class | ~7–9B dense | ~14–32B dense or small MoE | 70B+ dense or large MoE |
| Usable context | 8k–16k | ~32k | ~128k |
| Memory | 8–16 GB system RAM | 24–64 GB RAM / 16–24 GB VRAM | ~128 GB unified (e.g. DGX Spark) |
| Design assumption | One focused sub-task per session; aggressive external memory; no subagents | Modest multi-file reasoning; routing between instruction files is viable | Near-frontier ergonomics — but still not frontier |
| Instruction budget (guideline) | ≤ ~2,000 tokens loaded at once | ≤ ~4,000 tokens | ≤ ~8,000 tokens |

The instruction-budget guideline is elaborated in [Kū's context-budget methodology](../design/ku/context-budget.md).

## "Usable context" is not the context window

The number that matters is what remains after fixed overhead:

```
usable context = raw window
               − system prompt / harness overhead
               − loaded skill instructions
               − reserved headroom for the answer being generated
```

A model advertising a 32k window, running under a harness with a 4k system prompt and a skill that loads 8k tokens of instructions, has less than 20k for the actual work — before the conversation even starts. Skills designed for these tiers must budget against *usable* context, and the manifest's `context_budget` block is where that budget is declared.

Quantization, KV-cache pressure, and long-context quality degradation all mean the practical numbers are usually worse than the spec sheet. When in doubt, design for the pessimistic case.

## What tiers are not

- **Not a quality ranking of people or setups.** Tier 1 is the most important tier — it is where accessibility lives, and the cost of AI-capable hardware is going up, not down.
- **Not frontier-inclusive.** Frontier subscription models sit above Tier 3 and outside this scale. A Kamaʻāina artifact may *also* run well on frontier stacks (many will), but it must never *require* one.
- **Not fixed forever.** Tier boundaries will be recalibrated as open-weight models and consumer hardware evolve; the manifest schema references tiers by number so recalibration doesn't break manifests.

## Declaring tiers in a manifest

```yaml
tier:
  minimum: 2
  degraded:
    tier: 1
    notes: "Works at Tier 1 without the cross-file consistency pass; run `verify` manually afterward."
```

`minimum` is the tier at which the tool's full behavior is supported. The optional `degraded` block documents an honest reduced mode at a lower tier — what still works, what the user must do by hand. See the [manifest schema](../design/ku/manifest-schema.md).
