#!/usr/bin/env python3
"""Maintenance commands for a Kamaʻāina context-base (waihona).

A context-base is a directory of small markdown "leaf" files, each holding
one topic's worth of facts, organized under branch directories. Every
directory carries an INDEX.md listing what lives below it, one line per
entry, so an AI model can find the right leaf by reading indexes instead
of loading the whole tree. The full format is specified in
design/context-base/context-base.md.

The model-facing side of that workflow (how to traverse, how to file new
facts) lives in the instruction files next to this script. Everything
mechanical belongs here instead: building indexes, enforcing size limits,
and spotting drift between an index and the files it describes. The point
is that no model ever counts tokens or maintains an index by hand — that
work is deterministic, so a script does it.

Four commands, all offline, standard library only:

    init     create an empty context-base (root INDEX.md and _inbox.md)
    reindex  rebuild every INDEX.md from what is actually on disk
    check    report violations of the format's rules (exit 1 if any)
    fixture  build the deterministic demo base used for validation runs

Run as: python3 cb.py <command> <base-root> [--max-leaf-tokens N ...]
"""
import argparse
import datetime
import math
import sys
from pathlib import Path

SPECIAL = {"INDEX.md", "_inbox.md"}
DEFAULTS = dict(max_leaf_tokens=1000, max_index_tokens=1500,
                max_index_entries=50, max_entry_chars=160,
                max_summary_chars=140, max_depth=3, max_inbox_blocks=10)
PLACEHOLDER = "> (purpose not yet written)"


def est_tokens(text: str) -> int:
    """Estimate how many tokens a piece of text costs a model to read.

    Uses the ~4 characters-per-token rule of thumb from the project's
    context-budget methodology (design/loea/context-budget.md). It is the
    fallback when no real tokenizer is available, which on a
    zero-dependency script is always.
    """
    return math.ceil(len(text) / 4)


def parse_frontmatter(path: Path):
    """Split a leaf file into its metadata and its content.

    A leaf starts with a frontmatter block — simple "key: value" lines
    between two "---" lines — carrying its one-line summary and its
    last-updated date. Returns (metadata dict, body text); a file with no
    frontmatter block comes back with an empty dict and the full text,
    which `check` will then flag as a rule violation rather than an error.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 4:]


def purpose_line(index_path: Path) -> str:
    """Return a directory's one-line purpose from its INDEX.md.

    The purpose line (the single "> ..." line near the top of an index)
    is the only hand-authored part of an index — everything else is
    regenerated. This helper exists so `reindex` can carry the human's
    line forward, and so a parent index can describe its branches using
    their own purpose lines. Returns a placeholder if none is written yet.
    """
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("> "):
                return line
    return PLACEHOLDER


def leaves_and_branches(d: Path):
    """List a directory's leaf files and branch subdirectories.

    Leaves are any markdown files except the special INDEX.md and
    _inbox.md; branches are visible subdirectories. Both come back sorted
    so that every command produces the same output for the same tree.
    """
    leaves = sorted(p for p in d.iterdir()
                    if p.is_file() and p.suffix == ".md" and p.name not in SPECIAL)
    branches = sorted(p for p in d.iterdir()
                      if p.is_dir() and not p.name.startswith("."))
    return leaves, branches


def build_index(d: Path, root: Path) -> str:
    """Compose the INDEX.md content for one directory.

    The result is a title, the preserved purpose line, then one line per
    branch and per leaf. Every entry's description is pulled from the
    child itself — a branch's purpose line, a leaf's summary — which is
    what makes indexes trustworthy: they can always be rebuilt from what
    is actually on disk, and `check` treats any difference as drift.
    """
    title = "Context-base" if d == root else d.name
    lines = [f"# {title}", purpose_line(d / "INDEX.md"), ""]
    leaves, branches = leaves_and_branches(d)
    if branches:
        lines.append("## Branches")
        for b in branches:
            lines.append(f"- [{b.name}/]({b.name}/INDEX.md) — "
                         f"{purpose_line(b / 'INDEX.md')[2:]}")
        lines.append("")
    if leaves:
        lines.append("## Leaves")
        for leaf in leaves:
            meta, _ = parse_frontmatter(leaf)
            summary = meta.get("summary", "(no summary)")
            lines.append(f"- [{leaf.stem}]({leaf.name}) — {summary}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def walk_dirs(root: Path):
    """Yield the base root and every branch directory under it.

    Hidden directories are skipped, and the order is stable so commands
    visit (and report on) directories the same way every run.
    """
    yield root
    for p in sorted(root.rglob("*")):
        if p.is_dir() and not p.name.startswith("."):
            yield p


def cmd_init(root: Path, _cfg) -> int:
    """Create a new, empty context-base at the given root.

    Writes a root INDEX.md with a placeholder purpose line and an empty
    _inbox.md. Refuses to run where an INDEX.md already exists, so it can
    never overwrite a base someone is using.
    """
    root.mkdir(parents=True, exist_ok=True)
    idx = root / "INDEX.md"
    if idx.exists():
        print(f"already a context-base: {root}")
        return 1
    idx.write_text(f"# Context-base\n{PLACEHOLDER}\n", encoding="utf-8")
    (root / "_inbox.md").write_text(
        "# Inbox\nStaging only — never read as knowledge. Filed by the filing pass.\n",
        encoding="utf-8")
    print(f"initialized context-base at {root}")
    print("next: write the root INDEX.md purpose line ('> ...')")
    return 0


def cmd_reindex(root: Path, _cfg) -> int:
    """Rebuild every INDEX.md in the base from what is actually on disk.

    Safe to run at any time: hand-written purpose lines are preserved,
    and everything else is regenerated from leaf frontmatter. This is the
    mechanical fix for any "drifted" finding that `check` reports.
    """
    # Bottom-up so parent indexes see fresh child purpose lines.
    for d in reversed(list(walk_dirs(root))):
        (d / "INDEX.md").write_text(build_index(d, root), encoding="utf-8")
    print(f"reindexed {root}")
    return 0


def cmd_check(root: Path, cfg) -> int:
    """Report everything in the base that breaks the format's rules.

    Findings come in two severities. Problems (exit code 1) are rule
    violations: oversized leaves or indexes, indexes that have drifted
    from the files they describe, missing summaries, excessive depth.
    Warnings don't fail the check but deserve attention, like an inbox
    piling up unfiled facts. Each message says what to do next — some
    fixes are mechanical (run `reindex`), while others need judgment
    (splitting an oversized leaf into coherent smaller topics), which is
    exactly the line this tool draws between script work and model work.
    """
    problems, warnings = [], []
    if not (root / "INDEX.md").exists():
        print(f"not a context-base (no INDEX.md): {root}")
        return 1
    for d in walk_dirs(root):
        depth = len(d.relative_to(root).parts)
        if depth > cfg.max_depth:
            problems.append(f"{d}: depth {depth} exceeds max {cfg.max_depth}")
        idx = d / "INDEX.md"
        leaves, branches = leaves_and_branches(d)
        if idx.exists():
            text = idx.read_text(encoding="utf-8")
            if est_tokens(text) > cfg.max_index_tokens:
                problems.append(f"{idx}: index ~{est_tokens(text)} tokens "
                                f"(max {cfg.max_index_tokens}) — split the branch")
            entries = [ln for ln in text.splitlines() if ln.startswith("- [")]
            if len(entries) > cfg.max_index_entries:
                problems.append(f"{idx}: {len(entries)} entries "
                                f"(max {cfg.max_index_entries}) — split the branch")
            for ln in entries:
                if len(ln) > cfg.max_entry_chars:
                    problems.append(f"{idx}: entry over {cfg.max_entry_chars} chars: "
                                    f"{ln[:60]}…")
            if text != build_index(d, root):
                problems.append(f"{idx}: drifted from leaves/branches — run reindex")
        elif d != root:
            problems.append(f"{d}: missing INDEX.md — run reindex")
        for leaf in leaves:
            meta, body = parse_frontmatter(leaf)
            if "summary" not in meta:
                problems.append(f"{leaf}: missing 'summary' frontmatter")
            elif len(meta["summary"]) > cfg.max_summary_chars:
                problems.append(f"{leaf}: summary over {cfg.max_summary_chars} chars")
            if "updated" not in meta:
                warnings.append(f"{leaf}: missing 'updated' frontmatter")
            if est_tokens(body) > cfg.max_leaf_tokens:
                problems.append(f"{leaf}: body ~{est_tokens(body)} tokens "
                                f"(max {cfg.max_leaf_tokens}) — needs semantic split")
    inbox = root / "_inbox.md"
    if inbox.exists():
        blocks = inbox.read_text(encoding="utf-8").count("proposed-branch:")
        if blocks > cfg.max_inbox_blocks:
            warnings.append(f"{inbox}: {blocks} unfiled blocks "
                            f"(warn at {cfg.max_inbox_blocks}) — run a filing pass")
    for w in warnings:
        print(f"WARN  {w}")
    for p in problems:
        print(f"FAIL  {p}")
    print(f"check: {len(problems)} problem(s), {len(warnings)} warning(s)")
    return 1 if problems else 0


def cmd_fixture(root: Path, _cfg) -> int:
    """Build the demo base used to validate traversal on small models.

    Produces a fixed three-branch tree (each branch: two sub-branches of
    four leaves) with deterministic content, per the spec's Validation
    plan. Deterministic on purpose: every run yields an identical base,
    so validation transcripts are comparable across models and machines.
    Refuses to write into a non-empty directory.
    """
    if root.exists() and any(root.iterdir()):
        print(f"refusing: {root} is not empty")
        return 1
    today = datetime.date.today().isoformat()

    def leaf_text(summary, slug):
        body = (f"Fixture leaf `{slug}`. {summary}.\n\n"
                + "\n".join(f"- fact {i}: deterministic filler about {slug}"
                            for i in range(1, 9)) + "\n")
        return f"---\nsummary: {summary}\nupdated: {today}\n---\n{body}"

    spec = {
        "models": ("open-weight model behavior observed on local runs", {
            "quantization": ("effects of quantization choices", [
                ("q4-vs-q5", "Q4 vs Q5 quality/latency tradeoffs observed locally"),
                ("kv-cache", "KV-cache growth per 1k context at common quants"),
                ("long-context-falloff", "where instruction-following degrades vs window size"),
                ("json-mode", "which local models hold JSON schemas reliably")]),
            "families": ("notes per model family", [
                ("llama-class", "llama-family sizes, strengths, licensing notes"),
                ("qwen-class", "qwen-family sizes and multilingual behavior"),
                ("mistral-class", "mistral/mixtral behavior and MoE memory notes"),
                ("phi-class", "small phi-family models for Tier 1 floors")])}),
        "hardware": ("measured limits of local machines", {
            "dgx-spark": ("DGX Spark measurements", [
                ("memory-envelope", "unified memory headroom at various model sizes"),
                ("throughput", "tokens/sec observed by model size and quant"),
                ("thermals", "sustained-load behavior and throttling points"),
                ("concurrency", "what runs alongside inference without starving it")]),
            "laptops": ("consumer-laptop floor measurements", [
                ("m-series-16gb", "16 GB Apple-silicon usable model/context envelope"),
                ("x86-igpu", "x86 iGPU laptops: cpu-only inference reality check"),
                ("egpu", "external GPU setups worth their friction"),
                ("thermal-floor", "laptop sustained inference before throttling")])}),
        "patterns": ("context-engineering practice notes", {
            "routing": ("progressive disclosure in practice", [
                ("router-size", "how small an entry router can get before ambiguity"),
                ("route-maps", "declaring worst-case routes for budget measurement"),
                ("help-text", "keeping help text out of the hot path"),
                ("mode-detection", "cwd-marker vs explicit-verb mode detection")]),
            "compaction": ("checkpoint and digest practice", [
                ("cadence", "checkpoint cadence vs overhead measurements"),
                ("digest-fidelity", "what in-flight digests lose, by task type"),
                ("state-of-play", "state-of-play file shapes that resume cleanly"),
                ("kill-tests", "running kill-and-resume matrices honestly")])})}

    for branch, (bpurpose, subs) in spec.items():
        for sub, (spurpose, leaves) in subs.items():
            d = root / branch / sub
            d.mkdir(parents=True)
            (d / "INDEX.md").write_text(f"# {sub}\n> {spurpose}\n", encoding="utf-8")
            for slug, summary in leaves:
                (d / f"{slug}.md").write_text(leaf_text(summary, slug), encoding="utf-8")
        (root / branch / "INDEX.md").write_text(f"# {branch}\n> {bpurpose}\n",
                                                encoding="utf-8")
    (root / "INDEX.md").write_text(
        "# Context-base\n> fixture base for Tier 1 traversal validation\n",
        encoding="utf-8")
    (root / "_inbox.md").write_text(
        "# Inbox\nStaging only — never read as knowledge. Filed by the filing pass.\n",
        encoding="utf-8")
    cmd_reindex(root, _cfg)
    n = sum(len(ls) for _, subs in spec.values() for _, ls in subs.values())
    print(f"fixture: {len(spec)} branches, {n} leaves at {root}")
    return 0


def main() -> int:
    """Parse the command line and dispatch to the command functions.

    Every sizing rule from the spec has a default here and a matching
    override flag — for example `--max-leaf-tokens 600` for a base that
    must serve a stricter Tier 1 machine.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["init", "reindex", "check", "fixture"])
    ap.add_argument("root", type=Path)
    for k, v in DEFAULTS.items():
        ap.add_argument(f"--{k.replace('_', '-')}", dest=k, type=int, default=v)
    cfg = ap.parse_args()
    root = cfg.root.expanduser()
    return {"init": cmd_init, "reindex": cmd_reindex,
            "check": cmd_check, "fixture": cmd_fixture}[cfg.command](root, cfg)


if __name__ == "__main__":
    sys.exit(main())
