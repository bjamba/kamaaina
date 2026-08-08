# Design Doc Template

<!-- Copy this file to design/<area>/<topic>.md. Design docs are Class 1 artifacts:
     the memorialized thinking behind a Class 2 tool or a load-bearing decision.
     They stay as the rationale record after the thing ships — write for the reader
     two years from now who asks "why is it like this?" -->

# <Title — proper orthography>

**Status:** draft | reviewed | implemented (→ link to `tools/<name>/`) | superseded (→ link)
**Issue:** #
**Author(s):**

## Problem

<!-- The problem in Kamaʻāina's terms: what breaks on resource-limited stacks,
     which principle or pattern is at stake (cite docs/philosophy.md,
     docs/patterns/context-engineering.md), and why now. -->

## Constraints

<!-- The envelope the design must fit: target tier(s) and their budgets
     (docs/tiers.md), permission expectations, offline requirements,
     what must stay deterministic (not-AI-first). -->

## Design

<!-- The proposed shape. For tools: the user journey, the routing structure,
     state files and their lifecycles, the draft manifest. Diagrams and worked
     examples beat abstraction. -->

## Alternatives considered

<!-- The roads not taken and the actual reason — "rejected because X blows the
     Tier 1 instruction budget" is a design fact worth keeping. -->

## Tier & budget analysis

<!-- The accounting per design/ku/context-budget.md: worst-case instruction load,
     expected session peak, which tier this lands at and the justification if >1,
     the degraded mode below it. -->

## Open questions

<!-- What's genuinely unresolved, and what would resolve it (a measurement,
     a prototype, a decision from the maintainer). -->
