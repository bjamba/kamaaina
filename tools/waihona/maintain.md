# Maintain a context-base

All of this is script work — run the command, report the output, act only where a step says so.

| Task | Command |
|---|---|
| Create a new base | `python3 scripts/cb.py init <base-root>` |
| Health check (sizes, caps, drift, stale inbox) | `python3 scripts/cb.py check <base-root>` |
| Rebuild all INDEX.md files | `python3 scripts/cb.py reindex <base-root>` |
| Generate the Tier 1 validation fixture | `python3 scripts/cb.py fixture <base-root>` |

Notes:

- `check` exits non-zero on violations. Two kinds need a model or a human afterward: **oversized leaf/index** → semantic split per `file.md` step 5; **stale inbox** → run a filing pass per `file.md`. Everything else (drift, formatting) is fixed by `reindex`.
- After `init`, write the root `INDEX.md` purpose line (`> ...`) with the user — it is the only hand-authored part of an index and reindex preserves it.
- Stricter bases (Tier 1 floor machines) may pass overrides, e.g. `check <root> --max-leaf-tokens 600`. Record chosen overrides in the root purpose line so future sessions know.
