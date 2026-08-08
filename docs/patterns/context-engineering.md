# Context Engineering Patterns

A catalog of the patterns Kamaʻāina tools use to fit real work into small context windows. Each pattern includes a worked example drawn from real skills the author built for frontier stacks — including honest anti-examples of what breaks when those skills meet a local model.

Treat context the way a 1980s game developer treated RAM: a hard budget, accounted for line by line. The tier instruction budgets these patterns serve are defined in [tiers.md](../tiers.md); the accounting method is in [Kū's context-budget doc](../../design/ku/context-budget.md).

---

## 1. Decomposition

**Problem:** A task that takes one long session on a frontier model — many steps, with facts from step 1 still needed at step 40 — cannot survive in an 8k–16k window.

**Pattern:** Split the task into sub-tasks that each fit a single short session. Any fact needed across sub-tasks must be *written down*, not remembered. Each sub-task starts by reading only the state it needs and ends by writing its results and updating a work list.

**Anti-example (teach-me):** The author's `teach-me` skill builds an entire multi-module course website in one uninterrupted generation run. Cross-cutting invariants — theme token names, an exact attribution string, a relative-path graph, per-page footers — must survive in-context from the first generated file to the last. On a frontier model this mostly holds; on a small model the invariants drift and the late files silently disagree with the early ones. That drift is the signature failure of undecomposed work.

**Refactored shape:** Emit the invariants once to a checklist file (`invariants.md`) and a machine-readable manifest of pages to build. Generate one page per session-slice, reading only the invariants file plus that page's spec. Finish with a *deterministic* verification pass (a script — see Pattern 5) that checks every page against the checklist. Nothing needs to be remembered; everything is re-read or re-checked.

---

## 2. External memory & the context-base

**Problem:** Long-lived projects accumulate far more relevant knowledge than any window can hold — and "relevant" changes step to step.

**Pattern:** Maintain a **context-base**: a knowledge base built specifically for context loading. Its properties:

- **Hierarchical** — small index files at each level (`INDEX.md`) that describe what's below in one line per entry, so a model can navigate by reading indexes, not contents.
- **Chunked to budget** — every leaf file is sized to be loadable whole within the tier's instruction budget; if it grows past that, it splits and the index updates.
- **Traversal protocol** — the model reads the root index, descends only the branches the current task names, and loads at most N leaves. The protocol is part of the tool's instructions, so "grab just what you need" is a procedure, not a hope.
- **Write path** — sessions end by filing new knowledge into the right leaf (or flagging it for filing), keeping the base current instead of relying on transcripts.

This is hot-swappable persistent state: the session pulls a leaf in, uses it, and lets it fall out of context when the step is done.

**Reference design:** the pattern is specified concretely as **Waihona** — on-disk format, sizing rules, traversal protocol, and write path in [`design/context-base/context-base.md`](../../design/context-base/context-base.md), with the deterministic scaffold/maintenance tool at [`tools/waihona/`](../../tools/waihona/). (`teach-me`'s `curriculum.json` + `TUTOR_CONTEXT.md` handoff files were the two-file proto-version that seeded it.)

---

## 3. Routing & progressive disclosure

**Problem:** A monolithic instruction file loads everything for every invocation, no matter how little the current step needs.

**Pattern:** The entry-point instruction file is a small **router**: it identifies which operation the user wants and loads exactly one operation file. Help text, rare-path instructions, and reference material live behind the router, never in it.

**Good example (hacky-hours):** The author's `hacky-hours` skill routes ~30 verbs from a dispatch table — each invocation loads only that verb's file. Right idea.

**Anti-example (same skill):** Its flagship verbs then stack 1,500–2,500 lines of instructions (verb file + two format references + 12 role persona prompts) and assume frontier subagent fan-out for parallel personas. Its documented fallback — "roleplay all 12 roles sequentially in one context" — is precisely what a small model cannot do. Routing at the front door doesn't help if the room behind the door is bigger than the house.

**Rule of thumb:** the router plus the *largest single routed file* plus any references that file mandates must fit the tier's instruction budget. If a routed operation is still too big, it decomposes further (Pattern 1) — sequential sessions with externalized state (Pattern 2), not personas held in parallel.

---

## 4. Compaction & offloading

**Problem:** Even a well-scoped session accumulates conversation history and tool output until the window fills mid-task.

**Pattern:** Build compaction into the tool's procedure instead of hoping the harness handles it:

- **Checkpoint summaries** — at defined milestones, the tool writes a compact state-of-play file (decisions made, open items, next step) to disk. The instruction set treats that file, not the transcript, as the source of truth after each checkpoint.
- **Flush what's done** — once a sub-task's results are written out, its intermediate material is dead weight; the procedure moves on without referring back to it, so a context reset (or a fresh session) at any checkpoint boundary loses nothing.
- **Summarize in flight** — bulky inputs (a long file, a log) are reduced to a purpose-built digest *on first read*, and the digest is what future steps use — written to disk if it must outlive the session.

**Litmus test:** could the session be killed at any checkpoint and resumed cold by a fresh session reading only the state files? If not, something important is living solely in context, and it will die there.

---

## 5. Not-AI-first

**Problem:** LLMs get used as a bazooka for anthill problems — slower, less reliable, and more expensive than the purpose-built tool, and on small hardware the waste is fatal to the context budget.

**Pattern:** Before every step in a tool's procedure, ask: **can this be deterministic?** Counting, validation, formatting, renaming, diffing, checking invariants, arithmetic — scripts, schemas, and checklists do these faster and perfectly, and every token they save is available for the steps that genuinely need a model. The manifest's `not_ai` block records each deterministic component, both for transparency and as a design forcing-function.

**Example:** the decomposed teach-me verification pass in Pattern 1 is a script, not a model pass — a model *proofreading* for a missing footer across 40 files is exactly the anthill/bazooka case.

**Corollary (teach-to-fish):** where a tool does use the model, prefer producing a durable artifact the user keeps (a script, a template, a checklist) over an answer that evaporates — each run should, where possible, reduce the need for the next one.

---

## Pattern × tier requirements

| Pattern | Tier 1 — Laptop | Tier 2 — Prosumer | Tier 3 — Workstation |
|---|---|---|---|
| 1. Decomposition | **Mandatory** | **Mandatory** | Recommended |
| 2. External memory / context-base | **Mandatory** | **Mandatory** | Recommended |
| 3. Routing / progressive disclosure | **Mandatory** | **Mandatory** | **Mandatory** |
| 4. Compaction & offloading | **Mandatory** | Recommended | Optional |
| 5. Not-AI-first | **Mandatory** | **Mandatory** | **Mandatory** |

Routing and not-AI-first are mandatory everywhere because they cost nothing and pay at every scale. Tier 3's slack is a convenience, not an invitation — a tool that *relies* on that slack has a Tier 3 minimum and must justify it (see [tiers.md](../tiers.md)).
