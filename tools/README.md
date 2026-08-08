# tools/

This directory holds Kamaʻāina's **Class 2 artifacts** — local-AI-directed tools, immediately usable by a local model stack at their declared [tier](../docs/tiers.md). Nothing here may require a frontier model at use-time.

**Empty on purpose.** The first inhabitants arrive with Milestone 2: the manifest validator and Kū v0 (design in [`design/ku/`](../design/ku/)).

## Required structure

```
tools/<name>/
├── manifest.yaml      # required — see design/ku/manifest-schema.md
├── SKILL.md           # entry-point instructions (router-style; see the patterns catalog)
├── <operation>.md     # routed instruction files, each sized to the tier's budget
├── scripts/           # deterministic components declared in the manifest's not_ai block
└── state/             # templates/format docs for the tool's declared state_files
```

A tool without a manifest is not a Kamaʻāina tool. Directory name = manifest `name` (ASCII slug per the [naming rule](../docs/naming.md)).
