# Context-Budget Methodology (draft)

How Kū decides whether a skill fits its target tier — and how it keeps skills honest about it. This is memory accounting: the window is RAM, and the budget is counted before anything ships.

## The accounting identity

For any single session of a skill:

```
usable_context = raw_window − harness_overhead − instruction_load − answer_headroom
```

- **raw_window** — what the model/runtime actually provides (measured, not spec-sheet).
- **harness_overhead** — system prompt, tool definitions, harness scaffolding. Measured once per stack during Kū's setup interview.
- **instruction_load** — every instruction token loaded *simultaneously*: entry router + the active routed file + all references that file mandates + relevant manifest/state excerpts. This is the number `context_budget.instructions_max_tokens` declares, computed at worst case across all routes.
- **answer_headroom** — reserved space for the model's own output plus in-flight tool results. Skills that generate files need real headroom; a rule of thumb is at least 25% of the raw window.

What's left is what the actual work — user turns, file contents, working state — must fit inside. If a step's working set exceeds it, the step decomposes further; the budget bends the design, never the reverse.

## The two declared numbers

From the [manifest schema](manifest-schema.md):

- **`instructions_max_tokens`** — the worst-case simultaneous instruction load. Must fit the tier guideline from [tiers.md](../../docs/tiers.md): ~2,000 (Tier 1), ~4,000 (Tier 2), ~8,000 (Tier 3).
- **`session_max_tokens`** — the expected peak of the whole identity above for the skill's heaviest session. Must fit within the tier's usable-context range with margin.

Both are measured claims. Counting tokens is deterministic work: the manifest validator counts each instruction file with a real tokenizer (falling back to the conservative ~4-chars-per-token estimate), sums the worst-case route, and fails validation if the declaration is exceeded. No model in the loop (Principle 2).

## Techniques for staying under budget

In the order Kū applies them (details in the [patterns catalog](../../docs/patterns/context-engineering.md)):

1. **Route harder** — anything not needed by the current step moves behind the router. Help text, rare paths, and reference prose are the usual bloat.
2. **Externalize invariants** — facts that must survive across steps go to state files re-read on demand, not instructions held throughout.
3. **Deterministic substitution** — steps a script can do leave the instruction set entirely; a one-line `exec` beats a paragraph of procedure.
4. **Checkpoint compaction** — long procedures write state-of-play files at milestones so any session can end there and a fresh one resume cold.
5. **Split the skill** — if a coherent operation still can't fit, it becomes two skills chained through persistent state; a seam on disk beats an overflow in context.

## Case study: teach-me blows the budget

The author's `teach-me` skill (frontier-designed) as measured:

| Load | Size |
|---|---|
| SKILL.md, always loaded | 953 lines ≈ 13k tokens |
| Mandatory references during generation (formatting, style-guide, accessibility, design, libraries) | ~950 lines ≈ 13k tokens |
| **Worst-case simultaneous instruction load** | **≈ 26k tokens** |

Against the tiers: Tier 1's *entire raw window* may be 8k–16k — the instructions alone are 2–3× the house. Tier 2 (32k) fits the instructions and almost nothing else. Even Tier 3 (128k) then runs teach-me's single uninterrupted whole-repo generation while holding theme tokens, an exact attribution string, and a cross-file path graph in context to the last file — invariant drift is a *when*, not an *if*, on anything below frontier.

The refactor (Milestone 3) applies the techniques in order: mode-router entry (~300 tokens), per-phase instruction files under 2k, invariants and curriculum state externalized to files, page-at-a-time generation with checkpoint compaction, and a deterministic script for the consistency pass and link checks — which also removes the live-URL-verification step that made the skill unusable offline. Target: `instructions_max_tokens ≤ 2000`, full behavior at Tier 2, honest degraded mode at Tier 1.

## Open questions for v0

- Tokenizer variance across model families — ship a conservative default multiplier, or per-model profiles in the setup interview?
- Should `session_max_tokens` be validated empirically (a dry-run harness) or remain a reviewed estimate in v0? Leaning: estimate in v0, empirical in the benchmark-methodology work (Milestone 1 issue).
