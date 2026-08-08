<!-- Kamaʻāina PR template — full expectations in CONTRIBUTING.md.
     Terms used below are defined inline the first time; deeper context:
     artifact classes → docs/philosophy.md · tiers → docs/tiers.md
     manifests → the manifest-schema.md doc under design/ -->

## Deliverable

<!-- FIRST THING a reviewer reads: what this PR ships, and in what form.
     One or two sentences, concrete: "A new doc at docs/x.md that ...",
     "A working tool at tools/y/ with commands a, b, c." The reviewer should
     know exactly what they are getting before reading anything else. -->

## Problem it solves

<!-- The problem in plain language, before any project terminology.
     What was broken, missing, or unknown — and for whom. Link the issue(s). -->

Closes #

## Where this sits

<!-- Roadmap position, so this PR is legible against the bigger picture:
     - Which milestone this advances, and which issue(s) it executes
     - What it builds on and what it unblocks (issues/PRs by number)
     - What related work is deliberately NOT here, and where that work lives
     - If stacked on other PRs: the merge order -->

## Terminology

<!-- Define, in one line each, any repo-specific term the sections above or the
     checklists below rely on (artifact class, tier, manifest, tool names...).
     Delete lines the PR doesn't use; never assume the reader knows the jargon. -->

## Artifact class

Kamaʻāina sorts every contribution into one of two **artifact classes**. Check one and delete the other:

- [ ] **Class 1 — documentation for humans.** Research, best practices, design rationale. Lives in `docs/` or `design/`.
- [ ] **Class 2 — a tool for local AI stacks.** An instruction set (`SKILL.md` + routed files) plus a `manifest.yaml` that a locally-run open-weight model can use directly. Lives in `tools/`. The **manifest** is the tool's self-description — everything it reads, writes, executes, and needs — and it is required.

## Class 2 checklist <!-- delete this section for Class 1 PRs -->

*"Tier" = the minimum hardware/model floor the tool needs (Tier 1 laptop → Tier 3 workstation, defined in [docs/tiers.md](https://github.com/bjamba/kamaaina/blob/main/docs/tiers.md)). "Instruction load" = the token cost of every instruction file a model holds at once.*

- [ ] `manifest.yaml` present and consistent with the instruction files (declared `state_files`, `exec`, permissions all match what the instructions actually do)
- [ ] Worst-case simultaneous instruction load fits the declared `instructions_max_tokens` and the tier guideline in `docs/tiers.md`
- [ ] `tier.minimum > 1` carries a written `justification` (the standing rule: target the lowest tier that can do the job)
- [ ] `not_ai` block lists every deterministic step (work a script does so the model doesn't have to); remaining model-steps genuinely need a model
- [ ] Works with `network: none` at use-time — no frontier/cloud API calls needed to use the tool

## Class 1 checklist <!-- delete this section for Class 2 PRs -->

- [ ] Internal links resolve; tier names/numbers reference `docs/tiers.md` rather than restating them
- [ ] New named artifacts added to the glossary in `docs/naming.md`

## Both

- [ ] Hawaiian orthography in prose (ʻokina/kahakō — e.g. Kamaʻāina), ASCII in paths and identifiers (rule: [docs/naming.md](https://github.com/bjamba/kamaaina/blob/main/docs/naming.md))
- [ ] ROADMAP.md updated if this changes milestone intent

## How it was verified

<!-- Commands run, tiers tested on, docs proofread by whom/what. Be literal. -->
