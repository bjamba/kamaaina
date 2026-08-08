# Waihona — context-base scaffold & maintenance

Waihona manages a **context-base**: indexed external memory on disk that a small model traverses to load only what a task needs. Format spec: `design/context-base/context-base.md` in the Kamaʻāina repo.

Everything deterministic is `scripts/cb.py`; never count tokens or rebuild an index yourself.

## Routing

Identify the user's intent and read **exactly one** of these files, then follow it:

| Intent | Read |
|---|---|
| Retrieve knowledge from a base for the current task | `find.md` |
| Save new knowledge, or file what's in the inbox | `file.md` |
| Create a base, check its health, rebuild indexes, make the test fixture | `maintain.md` |

Base locations: durable cross-project knowledge → `~/.kamaaina/context-base/`; project-local → `./context-base/`. If the user doesn't say which, ask once.
