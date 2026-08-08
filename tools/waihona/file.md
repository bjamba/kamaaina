# Save knowledge / file the inbox

## Saving during a task (cheap path — default)

Do not edit the tree mid-task. Append one block per fact to `<base-root>/_inbox.md`:

```
---
proposed-branch: <existing branch slug, or "new: <slug>">
proposed-summary: <one line, <=140 chars — what a reader would find>
---
<the fact, freeform markdown>
```

Then continue the task. Filing happens later.

## Filing (dedicated pass — at session end, or when asked)

1. Run `python3 scripts/cb.py check <base-root>` first; fix nothing yet, just know the state.
2. For each inbox block, one at a time:
   - Fits an existing leaf → append/merge into that leaf; update its `summary:` if the topic widened and `updated:` to today.
   - Genuinely new topic → create a leaf in the proposed branch with frontmatter (`summary:`, `updated:`), body ≤ 1000 tokens.
   - Hard to place → leave it in the inbox with a note; never mis-file to empty the box.
   - Marked GAP → decide with the user whether it becomes a research task or an empty-slot leaf.
3. Resolve any conflict notes: newer fact wins; rewrite the losing leaf (say "supersedes" in the body) or delete it.
4. Remove filed blocks from `_inbox.md`.
5. Run `python3 scripts/cb.py reindex <base-root>` then `check <base-root>`. If check flags an oversized leaf, split it: sibling leaves or a new sub-branch, each piece with its own one-topic `summary:` — then reindex and check again.
