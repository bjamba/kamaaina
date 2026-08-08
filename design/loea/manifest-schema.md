# Manifest Schema (draft)

Every Class 2 tool ships a `manifest.yaml` beside its `SKILL.md`. The manifest is the tool's honest, complete self-description: what it needs, what it touches, what it does deterministically, and what tier it runs at. A user should be able to read the manifest and know everything the tool can do before running it — and a tool must refuse to do anything its manifest doesn't declare.

This is a v0 draft schema. A deterministic validator (`tools/manifest-validator/`, itself a not-AI artifact) is tracked as a Milestone 2 issue and will be the schema's executable form.

## Schema

```yaml
# Identity
name: string             # ASCII slug; matches the tool's directory name (see docs/naming.md)
title: string            # proper orthography, e.g. "Loea"
version: string          # semver
artifact_class: 2        # manifests exist for Class 2 tools; the field is explicit anyway
summary: string          # one line, human-readable

# Where it runs — see docs/tiers.md
tier:
  minimum: 1 | 2 | 3     # lowest tier at which full behavior is supported
  justification: string  # REQUIRED if minimum > 1: why a lower tier can't do the job
  degraded:              # optional: honest reduced mode below minimum
    tier: 1 | 2 | 3
    notes: string        # what still works, what the user must do manually

# Context accounting — see design/loea/context-budget.md
context_budget:
  instructions_max_tokens: int   # ceiling on instruction text loaded simultaneously
  session_max_tokens: int        # expected peak working context of any single session

# Least-privilege capability declaration — see design/loea/permission-model.md
permissions:
  filesystem:
    read: [path-patterns]        # e.g. ["./", "~/.kamaaina/context-base/"]
    write: [path-patterns]       # e.g. ["./output/", "./state/"]
  network: none | [hosts]        # "none" is the default and the ideal
  exec: [commands]               # exact binaries the tool may invoke, e.g. ["python3 scripts/verify.py"]

# What must exist for the tool to work
dependencies:
  tools: [names]                 # other Kamaʻāina tools, by manifest name
  binaries: [names]              # e.g. ["python3", "git"]
  model:
    min_params: string           # e.g. "7B"
    capabilities: [strings]      # e.g. ["json-mode", "tool-calls"]

# External memory — every file the tool reads/writes as state
state_files:
  - path: string                 # e.g. "state/invariants.md"
    purpose: string
    lifecycle: session | persistent   # discarded when done vs. long-term memory

# Principle 2 accounting — the deterministic components
not_ai:
  - step: string                 # e.g. "verify every page carries footer + attribution"
    implementation: string       # e.g. "scripts/verify.py (stdlib only)"
```

## Field notes

- **`name` / `title`** — the slug/orthography split per the [naming rule](../../docs/naming.md). The slug is the identity in code; the title is the identity in prose.
- **`tier.justification`** — the schema's teeth for "Loea targets the lowest tier that can do the job." A Tier 2+ minimum without a justification is a validation error, not a style complaint.
- **`context_budget`** — declared, not aspirational: `instructions_max_tokens` must cover the worst-case *simultaneous* load (router + largest routed file + its mandatory references), and must fit the declared tier's guideline in [tiers.md](../../docs/tiers.md). The [context-budget doc](context-budget.md) defines how to measure it.
- **`permissions.network: none`** — the default and the expectation. A tool listing hosts must be doing something inherently networked (e.g. fetching a declared dataset), and use-time function must never depend on a frontier API endpoint appearing here.
- **`permissions.exec`** — exact commands, not categories. `["python3 scripts/verify.py"]`, never `["python3"]` alone if the tool only runs one script.
- **`state_files`** — makes the external-memory pattern auditable: if the tool's instructions mention a file not listed here, that's a defect. `persistent` files are the user's data; a tool must document their format well enough that the user (or another tool) can read them.
- **`not_ai`** — doubles as a design review: a manifest whose `not_ai` list is empty invites the question "really — *nothing* here is deterministic?"

## Filled example

A hypothetical tiny tool that maintains a reading-notes context-base:

```yaml
name: noteskeeper
title: Noteskeeper
version: 0.1.0
artifact_class: 2
summary: Files reading notes into an indexed context-base and retrieves budget-sized digests.

tier:
  minimum: 1

context_budget:
  instructions_max_tokens: 1500
  session_max_tokens: 6000

permissions:
  filesystem:
    read: ["~/.kamaaina/context-base/notes/"]
    write: ["~/.kamaaina/context-base/notes/"]
  network: none
  exec: ["python3 scripts/reindex.py"]

dependencies:
  tools: []
  binaries: ["python3"]
  model:
    min_params: "7B"
    capabilities: []

state_files:
  - path: "~/.kamaaina/context-base/notes/INDEX.md"
    purpose: "One-line-per-entry index the model reads to navigate without loading leaves"
    lifecycle: persistent
  - path: "~/.kamaaina/context-base/notes/<topic>/<leaf>.md"
    purpose: "Budget-sized note leaves (split automatically past ~1000 tokens)"
    lifecycle: persistent

not_ai:
  - step: "Rebuild INDEX.md and split oversized leaves"
    implementation: "scripts/reindex.py (stdlib only)"
  - step: "Validate leaf size before filing"
    implementation: "scripts/reindex.py --check"
```
