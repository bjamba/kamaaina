# Permission Model (draft)

The transparency principle made mechanical: a tool **declares** everything it can do in its [manifest](manifest-schema.md), the user **approves** those declarations knowingly, the approval is **recorded** in a file the user owns and can read, and the tool **refuses** anything undeclared.

## The flow

```
manifest declares  →  Loea/installer presents  →  user approves  →  grant recorded  →  tool acts only within grant
```

1. **Declare.** The manifest's `permissions` block enumerates filesystem read/write patterns, network hosts (default `none`), and exact exec commands.
2. **Present.** At install (or first run), each permission is shown with the manifest's stated purpose — not "allow filesystem access?" but "writes course pages under `./output/` — the skill's product." Loea generates this presentation from the manifest; a permission it can't explain is a permission the design shouldn't request.
3. **Approve.** The user grants per-tool, once. Declining a permission either blocks the tool or, where the manifest defines a `degraded` mode that doesn't need it, drops to that mode.
4. **Record.** Grants land in `~/.kamaaina/grants.yaml` — human-readable, hand-editable, the user's property:

```yaml
# ~/.kamaaina/grants.yaml
grants:
  - tool: noteskeeper
    version: 0.1.0
    granted_at: 2026-08-08
    permissions:
      filesystem:
        read: ["~/.kamaaina/context-base/notes/"]
        write: ["~/.kamaaina/context-base/notes/"]
      network: none
      exec: ["python3 scripts/reindex.py"]
```

5. **Honor.** The tool's generated instructions are written so that any action outside the granted set is a stop-and-ask, not an improvisation. (See "Enforcement honesty" below.)

## Escalation

A new version of a tool wanting **new or broader** permissions re-prompts: the grant is keyed to the permission set, not just the tool name. The presentation shows the *diff* ("v0.2.0 additionally requests: write `./exports/`"), never re-asks for what's already granted, and records the new grant alongside the old (`granted_at` preserved per entry). Narrowed permissions update silently — shrinking is always fine.

## Auditability

- `grants.yaml` is the single answer to "what have I allowed on this machine?" — one file, plain YAML, sorted by tool.
- Because manifests are also plain files, `grant vs. manifest` drift is deterministically checkable — the manifest validator (Milestone 2) compares them, offline, no model involved (Principle 2).
- Revocation is deleting or editing an entry. Tools re-present on next run as if never granted.

## Enforcement honesty

An instruction-following LLM is not a security boundary, and this model doesn't pretend otherwise. Layers, honestly labeled:

1. **Design-time (strong):** Loea simply doesn't generate skills whose procedures exceed their manifests — undeclared behavior is a generation bug, and the declared-vs-instructed diff is deterministically lintable.
2. **Run-time instruction (soft):** generated skills carry standing instructions to check the grant before side-effecting actions and to stop-and-ask when out of bounds. Real but not tamper-proof.
3. **Harness (strongest, out of scope):** where the user's runtime has its own sandboxing/allowlists, the manifest's `permissions` block is written to be mechanically translatable into harness configuration. v0 emits the manifest; harness adapters are future work.

The point of the model is not to defeat a malicious tool — don't install those — but to make an honest tool's behavior *fully legible* and its drift *detectable*. That's what "be your own mechanic" requires.
