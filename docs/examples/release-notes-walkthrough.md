# Worked Example: The Same Skill, Built Two Ways

This walkthrough takes one concrete skill idea and builds it twice: first the way skills are usually built today (on frontier habits), then through Kamaʻāina's process with [Loea](../../design/loea/overview.md), the skill-creator. If you are new to this repository, this is the fastest way to feel the difference the whole ADK exists to make.

Terms used here, defined once: a **skill** is a packaged instruction set an AI model follows to do a job. A **tier** is the minimum hardware/model floor a tool needs — Tier 1 is laptop-class (~7–9B model, 8k–16k usable context), Tier 3 is workstation-class ([full definitions](../tiers.md)). A **manifest** is a tool's mandatory self-description: everything it reads, writes, executes, and stores ([schema](../../design/loea/manifest-schema.md)). A **context-base (Waihona)** is indexed external memory on disk that a model reads piece by piece instead of holding things in its head ([spec](../../design/context-base/context-base.md)).

## The skill idea

**release-notes** — "look at everything merged since the last release tag and write polished release notes in our project's voice."

A realistic, useful, medium-sized skill: it touches real repository data, it has taste requirements (the project's voice), it has structure requirements (sections, links, ordering), and it recurs — you run it every release.

---

## Build one: the normal way

You describe what you want, and you get one `SKILL.md`, written in an afternoon — maybe 400 lines: a tone guide, three examples of good release notes, categorization rules (features vs. fixes vs. breaking changes), edge-case handling, help text. All of it loads on every invocation: roughly **5–6k tokens before any work starts**.

At run time, the model shells out to `git log`, and the raw log plus the interesting diffs — easily **15–40k tokens** on a real repository — lands directly in context. The model then holds everything at once: the instructions, the tone guide, the whole history, and the draft it is writing, while you go back and forth ("group these differently," "punchier"). When it's done, the session ends, and everything the model figured out about your project's voice and conventions evaporates. Next release, you pay to re-teach it from scratch.

On a frontier stack this *works*, which is exactly the trap: a 200k window absorbs the whole mess, so nothing ever forces discipline. Here is the same skill meeting the tiers:

| Tier | What happens |
|---|---|
| **Tier 1** (8k–16k usable) | Dead on arrival. The instruction file alone is a third to two-thirds of the window; the git log doesn't fit at all. |
| **Tier 2** (~32k) | Loads, then degrades. By the third section the voice drifts and the categories get inconsistent — and a crash mid-draft loses everything. |
| **Tier 3** (~128k) | Mostly works, slowly — while burning a workstation's whole window on work that is largely deterministic. |

Notice where the tokens actually go: collecting commits, grouping them by prefix, checking that every entry links a pull request. None of that is judgment. It's the bazooka aimed at the anthill — and on small hardware, the wasted tokens aren't just inefficient, they're the reason nothing fits.

---

## Build two: the Kamaʻāina way

Loea's job is to run the same request through its [six-step journey](../../design/loea/overview.md#the-user-journey), where the constraint envelope is established *before* the skill is designed, not discovered after it fails.

### Step 1 — Setup interview

Loea doesn't ask what skill you want yet. It establishes your envelope first — and it measures rather than asks wherever a script can do the job (a probe script reads your memory and test-drives your model's usable window; asking a human to estimate these is less reliable and violates [not-AI-first](../philosophy.md#principle-2--not-ai-when-possible) in spirit). Say you're on a 16 GB laptop running an 8B model: **~12k usable tokens** after harness overhead.

### Step 2 — Tier determination

That's **Tier 1**. Loea says so explicitly, and states what Tier 1 makes mandatory per the [pattern × tier table](../patterns/context-engineering.md#pattern--tier-requirements): decomposition, external memory, routing, compaction. The envelope now exists before a single line of the skill does.

### Step 3 — Budget-fit design

Now you describe the skill. Loea decomposes it and sorts every step into model-work or script-work:

| Step | Who does it | Why |
|---|---|---|
| Collect commits/PRs since the last tag, group by type, batch into chunks of ~10 | `collect.py` script | Pure mechanics — zero model tokens |
| Summarize one batch in the project's voice | Model | Genuinely needs language judgment |
| Write the highlights paragraph | Model | Genuinely needs synthesis |
| Verify format invariants (every entry links a PR, sections ordered, style rules held) | `verify.py` script | Checking is deterministic |
| Remember the project's voice and conventions between releases | Waihona leaf | External memory, not context |

The structure that falls out:

- A **~200-token router** `SKILL.md` dispatching to `draft.md` and `polish.md`, each under 1.5k tokens ([routing](../patterns/context-engineering.md#3-routing--progressive-disclosure)).
- The project's **voice lives in a context-base leaf** (`context-base/release-notes/voice.md`, ≤1k tokens), read at the start of each drafting session and improved at the end of each release — the skill gets better over time instead of resetting ([external memory](../patterns/context-engineering.md#2-external-memory--the-context-base)).
- The work list (`batches.json`) and the growing draft are **state files with a checkpoint after every batch** ([compaction](../patterns/context-engineering.md#4-compaction--offloading)).

### Step 4 — Transparency pass

Before generating anything, Loea shows you the under-the-hood plan: reads `.git` and the voice leaf; writes `./release-notes/` and its checkpoints; executes two named scripts; `network: none`. You approve knowing everything the skill will ever touch.

### Step 5 — Manifest and permissions

The plan becomes the skill's `manifest.yaml` — Tier 1 minimum, `instructions_max_tokens: 1700`, both scripts declared in the `not_ai` block, every state file listed — and your approval is recorded in a grants file you own ([permission model](../../design/loea/permission-model.md)).

### Step 6 — Scaffold generation

Loea emits the skill. A run now looks like this:

1. `collect.py` gathers and batches the commits — **0 model tokens**.
2. The model drafts batch 1, reading only the voice leaf plus that batch — **~4k peak context** — then writes a checkpoint.
3. Batches 2, 3, … same shape. Kill the session anywhere; a fresh session resumes cold from the state files.
4. `verify.py` checks every invariant mechanically.
5. The model writes the highlights paragraph from the checkpoint summaries, never re-reading the raw history.

---

## The scoreboard

| | Normal build | Kamaʻāina build |
|---|---|---|
| Instruction load per session | ~5–6k tokens, always | ≤ ~1.7k, only what the step needs |
| Peak working context | 20–45k | ~4–5k |
| Runs at Tier 1? | No | Yes — that is its floor |
| Crash mid-run | Start over | Resume from the last checkpoint |
| Voice consistency | Model memory (drifts) | Voice leaf + script verification (checked) |
| Knowledge between releases | None | Voice leaf improves every release |
| Runs on a frontier model? | Yes | Yes — just faster, with budget to spare |

The last row is [Principle 1](../philosophy.md#principle-1--local-first) made concrete. The Kamaʻāina version is not a compromise edition for weak hardware; it is a better-engineered skill on every stack — cheaper, resumable, self-improving. The frontier version only appears to match it because a 200k window hides the waste.

## Where to go from here

- The failure modes shown here, generalized: [Context Engineering Patterns](../patterns/context-engineering.md).
- The process that produced build two: [Loea's design](../../design/loea/overview.md) (implementation tracked in issue #4).
- The storage layer build two leans on: [the Waihona context-base](../../design/context-base/context-base.md).
- A real, larger version of this exercise: the planned refactor of the author's `teach-me` skill (issue #8), whose "normal build" measures ~26k tokens of instruction load.
