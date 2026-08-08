# Kamaʻāina

**An AI Development Kit (ADK) for local-first AI on consumer hardware.**

Skills-based agentic development — the Claude Code style of packaged, instruction-driven AI tooling — quietly assumes frontier infrastructure: enormous context windows, provider-side optimization, cheap parallel subagents. Open-weight models on consumer and prosumer hardware get none of that, and won't for the foreseeable future. Kamaʻāina's bet is that this is a *design problem*, not a waiting problem: like game development in the 70s–80s, the limits are the design space. This kit collects the principles, patterns, and tools for building agentic skills that fit — small contexts budgeted like scarce RAM, external memory instead of long sessions, deterministic tools wherever a model isn't actually needed.

Built with frontier assistance today; **usable entirely within a local stack** the moment you download it. (A frontier model can use this ADK too — it's just an over-provisioned consumer of the same artifacts.)

## The two artifact classes

Everything here is exactly one of:

| Class | What | Where | Audience |
|---|---|---|---|
| **1** | Human-readable documentation — research, theory, best practices, design rationale | [`docs/`](docs/), [`design/`](design/) | Humans (and frontier models helping them) |
| **2** | Downloadable tools — `SKILL.md` + `manifest.yaml`, runnable at a declared tier with no frontier dependency | [`tools/`](tools/) | Local AI stacks |

## Tiers at a glance

Every tool declares the minimum hardware/model floor it needs. Full definitions in [docs/tiers.md](docs/tiers.md); the standing rule is **design for the lowest tier that can do the job**.

| Tier | Class | Model | Usable context |
|---|---|---|---|
| 1 | Laptop | ~7–9B | 8k–16k |
| 2 | Prosumer | ~14–32B | ~32k |
| 3 | Workstation (DGX Spark-class) | 70B+ / large MoE | ~128k |

## Principles

1. **Local-first** — no frontier calls at use-time, `network: none` by default.
2. **Not-AI when possible** — a calculator beats an LLM at arithmetic; deterministic tools first, model tokens reserved for judgment. Teach to fish.
3. **Transparency** — every tool's manifest declares everything it touches; you can always be your own mechanic.

The full argument: [docs/philosophy.md](docs/philosophy.md).

## Start here

1. [Philosophy](docs/philosophy.md) — why this exists and the three principles.
2. [Tiers](docs/tiers.md) — the hardware floors everything is designed against.
3. [The same skill, built two ways](docs/examples/release-notes-walkthrough.md) — a worked example of a frontier-habit build failing at the tiers, and the Kamaʻāina build that doesn't. The fastest way to feel what this ADK is for.
4. [Context engineering patterns](docs/patterns/context-engineering.md) — the pattern catalog, with real worked examples and anti-examples.
5. [Loea design](design/loea/overview.md) — the skill-creator that enforces all of the above: [manifest schema](design/loea/manifest-schema.md) · [permission model](design/loea/permission-model.md) · [context budgets](design/loea/context-budget.md).
6. [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md).

## About the name

*Kamaʻāina* — "child of the land," a longtime local — names the goal: AI tooling that belongs to the machine it runs on. The project's names honor the author's upbringing in Hawaiʻi and follow proper Hawaiian orthography in prose (ASCII in paths); the full note and glossary are in [docs/naming.md](docs/naming.md).

## Status

Early. Foundation docs and the first tool ([Waihona](tools/waihona/), the context-base) are in; Loea v0 is next. Follow the [roadmap](ROADMAP.md) and issues.

## License

[MIT](LICENSE).
