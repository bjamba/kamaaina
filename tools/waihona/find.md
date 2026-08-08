# Retrieve from a context-base

To retrieve from the context-base at `<base-root>`:

1. Read `<base-root>/INDEX.md`. Nothing else yet.
2. Choose **at most 2 branches** whose descriptions match the current task. Read only their `INDEX.md` files.
3. Choose **at most 3 leaves total** across those branches, by description. Read them. These leaves are now your working knowledge.
4. **Stop.** Do not browse further. Do not read leaves "just in case."
5. If no description matched the task, do not guess: tell the user what was missing, and append a gap note to `<base-root>/_inbox.md`:

   ```
   ---
   proposed-branch: <branch or "new: <slug>">
   proposed-summary: <one line, <=140 chars>
   ---
   GAP: <what the task needed and could not find>
   ```

6. If two leaves conflict, prefer the newer `updated:` date, and append a conflict note to `_inbox.md` in the same block format.

Never read `_inbox.md` as knowledge — it is unfiled staging.
