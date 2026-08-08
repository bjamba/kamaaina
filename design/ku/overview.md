# Kū — Design Overview

Kū is Kamaʻāina's skill-creator: a tool that helps a user build agentic skills **from the ground up around the limitations of their actual local setup**, rather than porting frontier habits down and watching them fail. It is the ADK's keystone Class 2 artifact — the tool that makes the other tools.

This directory is the Class 1 design record for Kū v0. When Kū ships, the implementation lives in `tools/ku/`; these documents remain as the rationale.

## Why a *different* skill-creator

Existing skill-creators assume frontier conditions: instructions can be long, sessions can be long, context is abundant, subagents are cheap. A skill authored under those assumptions is a monolith with invisible dependencies — and on a Tier 1 or 2 stack ([tiers](../../docs/tiers.md)) it fails in characteristic ways: instruction load alone eats the window, invariants drift across a long generation, "fallback" paths ask a small model to do exactly what it can't.

Kū's difference is that **the constraint model comes first**. Kū doesn't ask "what should this skill do?" and then hope it fits; it establishes what the user's stack can actually hold, then designs the skill inside that envelope using the [context engineering patterns](../../docs/patterns/context-engineering.md) as its structural vocabulary.

## The user journey

1. **Setup interview.** Kū asks about the user's stack: hardware, model(s), quantization, harness, measured context window. Where possible it prefers *measuring* over asking (Principle 2 — a script can read VRAM and test usable context more reliably than a user can estimate it).
2. **Tier determination.** The answers map to a tier floor. Kū states the tier, what it implies, and which patterns are mandatory at it (the [pattern × tier table](../../docs/patterns/context-engineering.md#pattern--tier-requirements)).
3. **Skill design within budget.** The user describes what they want the skill to do. Kū decomposes it, assigns each step to model-work or deterministic-work (not-AI-first), designs the state files and routing structure, and computes the instruction budget per the [context-budget methodology](context-budget.md).
4. **Transparency pass.** Before generating anything, Kū tells the user *how the skill will work under the hood*: what it reads and writes, what it executes, what stays on disk, what the model actually does at each step.
5. **Manifest generation & permission request.** Kū writes the skill's [`manifest.yaml`](manifest-schema.md) and walks the user through each requested permission per the [permission model](permission-model.md). Nothing undeclared, nothing silent.
6. **Scaffold generation.** Kū emits the skill: router-style `SKILL.md`, per-operation instruction files sized to budget, state-file templates, and any deterministic scripts — plus the manifest.

## The transparency contract

Kū's defining behavioral commitment, applied to itself and to every skill it creates:

- It explains what it is about to do **before** doing it, in terms a user can audit.
- Every capability a generated skill needs appears in its manifest; the skill is designed to refuse actions its manifest doesn't declare.
- The user can always answer "what does this thing touch, and why?" by reading one file.

This is Principle 3 ("be your own mechanic") made operational: the manifest is the exploded parts diagram, and Kū never ships a sealed unit.

## Kū eats its own cooking

Kū is not exempt from anything it enforces. Self-application is a design requirement, not an aspiration, and it goes beyond fitting the instruction budgets:

- **Storage.** Kū's own working state — the setup interview's stack profile, in-progress skill designs, the record of skills it has generated and the manifests it has emitted — lives in the same external-memory structures it prescribes (declared `state_files`, context-base conventions), never in conversation memory. The stack profile in particular is long-term storage: measured once, reused by every future Kū session and every skill it designs.
- **Session discipline.** A skill design is a long dialogue; Kū runs it as its own patterns demand — decomposed steps, checkpoint compaction at each journey stage, and the litmus test honored: kill Kū between any two stages and a fresh session resumes the design cold from state files alone.
- **Optimization.** Every deterministic step in Kū's own procedure (probing the stack, counting tokens, emitting scaffolds from templates, diffing grants) is a script in Kū's `not_ai` block, not model work. Kū's routing is real routing: one journey stage's instructions loaded at a time.
- **The audit.** Kū's own `manifest.yaml` is reviewed against the same bar as any tool it generates — and the validator must pass on it. If following Kū's methodology produces a Kū that can't run at a low tier, that is evidence against the methodology and gets fixed in the methodology, not waived for the tool.

## v0 scope

- **In:** the journey above, for single skills, targeting Tiers 1–3; manifest generation; the grants-file workflow; scaffolds built from the five core patterns.
- **Out (later):** skill evals/benchmarking at tier, multi-skill composition, automated tier measurement suite, Kū improving existing manifests in place.
- **Bootstrap honesty:** v0's design (these documents) is frontier-assisted — Class 1 feeding Class 2, exactly as [the philosophy](../../docs/philosophy.md#principle-1--local-first) prescribes. The shipped Kū must itself run at the lowest tier it can; its own manifest declares what it needs, and Kū at Tier 1 with degraded features is preferred over Kū that requires Tier 3.

## First proving ground

Kū v0 is validated by refactoring the author's **teach-me** skill — a 953-line monolithic frontier skill that violates nearly every pattern in the catalog — into a tier-declared Kamaʻāina tool. If Kū's methodology can carry teach-me's genuinely rich functionality down to a small-context stack, the methodology is real. Tracked as the "Refactor teach-me" issue (Milestone 3).
