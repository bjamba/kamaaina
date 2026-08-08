# Philosophy

Kamaʻāina exists because of a mismatch: the most exciting patterns in AI-assisted development — skills, agents, long-running collaborative sessions — were designed on frontier infrastructure, and they quietly assume it. Enormous context windows, provider-side caching and optimization, cheap parallel subagents. Take those away and the patterns don't degrade gracefully; they collapse.

Local stacks — open-weight models on consumer and prosumer hardware — will not get those resources in the foreseeable future. So the answer is not to wait for "more computer." The answer is the one game developers and systems programmers lived by in the 70s and 80s: **treat the limits as the design space.** Know exactly how much memory you have, budget every byte, build tools that are clever about the machine instead of demanding a bigger one. That discipline produced some of the best engineering of that era. This ADK tries to cultivate the same discipline for local AI.

## Principle 1 — Local-first

An artifact in this ADK, once downloaded for use, must be **entirely usable within a local model stack** at its declared [tier](tiers.md). No frontier API calls in the loop, no phoning home, `network: none` as the manifest default.

The development story is explicitly two-sided, and it's important not to confuse the sides:

- **Development-time**: frontier models may help *build* the ADK — drafting design docs, distilling instructions, stress-testing patterns. That's the bootstrap, and this repo's Class 1 documentation is largely a product of it.
- **Use-time**: none of that assistance may be *required* to use what ships. If a tool needs a frontier model to work, it doesn't belong in `tools/`.

The relationship also runs the other way: a frontier model is just another consumer of this ADK — an over-provisioned one. Frontier stacks can and should use these same artifacts to develop local-focused resources. Designing for the floor doesn't exclude the ceiling; it's the ceiling-only designs that exclude the floor.

## Principle 2 — Not-AI when possible

AI is currently marketed as a general-purpose problem solver, and the result is people using an LLM where a calculator would do: slower, less reliable, vastly more energy-hungry, and — worse — building a dependency instead of a capability. That's eating fish, not learning to fish.

Every artifact in this ADK is expected to ask, step by step: *can a deterministic tool do this?* A script, a grep, a schema validator, a template, a checklist. If yes, the deterministic tool wins, and the manifest's `not_ai` block records the choice. The LLM is reserved for the parts that genuinely need judgment, language, or synthesis — and on a resource-limited stack, every token you don't spend on work a script could do is a token available for work only the model can do. On small hardware, Principle 2 isn't just ideology; it's how anything fits at all.

The long-run ambition is **AI-trending-to-zero** for any given workflow: use the model to bootstrap a purpose-built tool, then let the tool carry the load. (Prior art: the author's [`without-ai`](https://github.com/bjamba/bjamba-skills) skill, which plans exactly this kind of infrastructure.)

## Principle 3 — Transparency ("be your own mechanic")

The mentality this ADK cultivates: everyone striving to be their own mechanic, their own artisan. That is only possible if the tools are honest about what they do.

Concretely:

- Every Class 2 tool carries a **manifest** declaring its tier requirements, permissions, dependencies, state files, and deterministic components — [the full schema](../design/ku/manifest-schema.md).
- Tools **request permissions and explain themselves** before acting; grants are recorded in a human-readable file the user owns — [the permission model](../design/ku/permission-model.md).
- Nothing happens "under the hood" that the manifest doesn't disclose. A user should be able to read a tool's manifest and know everything it can touch before running it.

## The two artifact classes

Everything in this repository is exactly one of:

1. **Class 1 — human/frontier-directed.** Human-readable documentation: research, theory, best practices, discussion, R&D. Lives in `docs/` and `design/`. This is where thinking is memorialized.
2. **Class 2 — local-AI-directed.** Downloadable tools (a `SKILL.md`-style instruction set plus a `manifest.yaml`) immediately usable by a local stack at their declared tier. Lives in `tools/`.

Class 1 feeds Class 2: designs are worked out in prose with whatever help is available, then distilled into artifacts small and disciplined enough to run at the target tier. An artifact that is neither — a doc no human would read, or a tool no local stack can run — doesn't belong here.

## The core technical problem: context as scarce memory

The recurring engineering problem behind all of this is that a local model's context window is small, and the frontier habits — long back-and-forth sessions, monolithic instruction files, "just keep it all in your head" — blow the budget immediately. The ADK's answer is a set of patterns treated the way old-school developers treated RAM:

- **Decompose** work so no single session carries long context.
- **Externalize memory** — write to and read from persistent state instead of holding it.
- **Route** — load only the instructions the current step needs.
- **Compact and hot-swap** — summarize in flight, flush what's done, swap in stored context when needed.
- **Traverse a context-base** — a knowledge base built for context: hierarchical, indexed, designed so a model can grab just what it needs.

These are cataloged with worked examples in [Context Engineering Patterns](patterns/context-engineering.md), and enforced by [Kū's context-budget methodology](../design/ku/context-budget.md).
