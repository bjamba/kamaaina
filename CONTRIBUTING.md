# Contributing to Kamaʻāina

Thanks for wanting to build local-first. One rule sits above everything:

> **Every contribution is exactly one of the two artifact classes.**
> **Class 1** — human-directed documentation (research, best practices, theory) → `docs/` or `design/`.
> **Class 2** — a local-AI-directed tool → `tools/`, and it **must carry a `manifest.yaml`** ([schema](design/loea/manifest-schema.md)).

If a contribution is neither a doc a human would read nor a tool a local stack can run, it doesn't belong here yet — open an issue and let's find its shape first.

## Ground rules

- **Local-first at use-time.** Frontier models may help you *build* a contribution; the shipped artifact must work entirely within a local stack at its declared [tier](docs/tiers.md). `network: none` is the manifest default; a frontier API in the use-time loop is a rejection, not a review comment.
- **Lowest tier that can do the job.** A minimum tier above 1 requires a written justification in the manifest. Design against the [pattern × tier table](docs/patterns/context-engineering.md#pattern--tier-requirements).
- **Not-AI-first.** PRs for Class 2 tools should be able to answer, step by step: *why does this step need a model?* The manifest's `not_ai` block is where the deterministic answers live; an empty one will be questioned.
- **Transparency.** Everything a tool touches — files, network, executables, state — is declared in its manifest. Undeclared behavior is a bug.
- **Naming & orthography.** Proper Hawaiian orthography in prose (Kamaʻāina, Loea), ASCII in paths and identifiers — full rule and glossary in [docs/naming.md](docs/naming.md). New Hawaiian-derived names are part of design review, and cultural corrections are always welcome as issues.

## How to propose

- **A new tool** → open a [tool proposal](.github/ISSUE_TEMPLATE/tool-proposal.md) issue *before* building: minimum tier + justification, permissions you expect to need, and which steps are deterministic. Cheap to redirect an idea; expensive to redirect a finished monolith.
- **A pattern, research note, or doc improvement** → a [pattern write-up](.github/ISSUE_TEMPLATE/pattern-writeup.md) issue, or a PR directly for small fixes.
- **A scoped piece of work** (implementation, research, docs) → a [work item](.github/ISSUE_TEMPLATE/work-item.md) issue. The bar: a stranger should be able to understand the problem space, build it themselves, or debate whether it's the right work at all. Sparse issues get sent back for scope.
- **A correction** (technical, cultural, or factual) → plain issue, any format.

Design work that precedes a tool gets a design doc in `design/` using [design/TEMPLATE.md](design/TEMPLATE.md) — the doc stays as the rationale record after the tool ships. PRs follow the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## PR expectations

1. Class declared in the PR description (1 or 2).
2. Class 2: manifest present and consistent with the instructions (until the validator ships, reviewers check by hand — declared `state_files`, `exec`, and budgets must match what the instruction files actually say).
3. Class 2: worst-case simultaneous instruction load fits the declared `instructions_max_tokens` and the tier guideline.
4. Docs: internal links resolve; tier names/numbers match `docs/tiers.md` rather than restating them.

License: MIT for everything ([LICENSE](LICENSE)). By contributing you agree your contribution is MIT-licensed.
