#!/usr/bin/env python3
"""Drive and score the Tier 1 traversal validation for a context-base.

The context-base spec (design/context-base/context-base.md) claims that a
small, locally-run model can follow the traversal protocol in find.md:
read the root index, descend only relevant branches, load at most three
leaves, and honestly report a gap when nothing matches. This script is
the lab equipment that tests the claim against a real model.

It works by playing the filesystem's role in a scripted conversation.
The model under test receives the protocol text plus a query, and can
only interact through a strict grammar: `READ: <path>` to request a file
(this script serves the content back), then `ANSWER: ...` or `GAP: ...`
to finish. Every request is logged, and the log — not anyone's opinion —
is scored against the protocol's rules and the query's known-correct
answers. The fixture base is deterministic (`cb.py fixture`), so the
right leaves for each query are known in advance. No model judges
another model; scoring is pure bookkeeping.

Whoever runs this — a human over SSH, or an agent session on the
machine — is just an operator. The interaction contract and the scoring
are fixed, so the result is reproducible and cannot be steered.

This is a development/certification-time harness: unlike waihona's
use-time operations it contacts an inference endpoint (any
OpenAI-compatible /v1/chat/completions, e.g. llama.cpp, llama-swap,
ollama). It never needs the wider internet.

Typical run:

    python3 cb.py fixture /tmp/cb-fixture
    python3 validate_traversal.py --base /tmp/cb-fixture \
        --endpoint http://127.0.0.1:9000 --model fast \
        --quantization Q4_K_XL --operator bjamba --date 2026-08-09 \
        --out 2026-08-09-fast.json

Run `--selftest` (no network, no model) to verify the loop, parser, and
scorer against scripted transcripts before trusting a real run.

Exit code 0 means every query passed; 1 means at least one did not.
"""
import argparse
import json
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

TERMINAL_RE = re.compile(r"^(READ|ANSWER|GAP):\s*(.*)$")
MAX_CORRECTIONS = 2

CONTRACT = """
--- Interaction contract for this validation run ---
You have no filesystem access. To read a file, reply with exactly one line:
READ: <path relative to the context-base root>
I will return its contents. One READ per reply, no other text.

When you are done, reply with exactly one line, either:
ANSWER: <your answer, naming the leaf files you used>
or, if no index description matched the task:
GAP: <proposed-branch> | <one-line proposed summary> | <what was missing>
(The GAP line stands in for the _inbox.md append — you cannot write files here.)
"""

CORRECTION = ("Your reply did not contain a valid line. Reply with exactly one "
              "line: 'READ: <path>', 'ANSWER: <answer>', or 'GAP: <branch> | "
              "<summary> | <missing>'.")


class HttpEndpoint:
    """Talks to an OpenAI-compatible chat-completions API over HTTP.

    Accepts a base URL with or without a trailing /v1. Sends temperature 0
    (and a seed if given) so runs are as repeatable as the server allows.
    Retries once on transport errors only — never on model output, because
    "the model answered badly" is a result, not an error.
    """

    def __init__(self, endpoint, model, api_key=None, seed=None):
        base = endpoint.rstrip("/")
        if not base.endswith("/v1"):
            base += "/v1"
        self.url = base + "/chat/completions"
        self.model = model
        self.api_key = api_key
        self.seed = seed

    def call(self, messages):
        payload = {"model": self.model, "messages": messages,
                   "temperature": 0, "stream": False}
        if self.seed is not None:
            payload["seed"] = self.seed
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(self.url, json.dumps(payload).encode(),
                                     headers)
        last_err = None
        for _ in range(2):
            try:
                with urllib.request.urlopen(req, timeout=600) as resp:
                    data = json.load(resp)
                return data["choices"][0]["message"]["content"]
            except (OSError, KeyError, json.JSONDecodeError) as e:
                last_err = e
        raise RuntimeError(f"endpoint failed twice: {last_err}")


class FakeEndpoint:
    """Replays a scripted list of replies, for --selftest.

    Implements the same call() interface as HttpEndpoint, so the real
    conversation loop, parser, and scorer run unmodified against known
    transcripts. Runs out of script → returns an empty reply, which the
    loop treats like any other malformed model output.
    """

    def __init__(self, replies):
        self.replies = list(replies)

    def call(self, _messages):
        return self.replies.pop(0) if self.replies else ""


def parse_reply(text):
    """Extract the model's action from a reply, tolerating noise.

    Small models often leak reasoning text around the required line, so
    we take the LAST line matching the grammar and record whether there
    was extra noise. Returns (action, argument, had_noise) or
    (None, None, had_noise) when no valid line exists.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    match = None
    for ln in lines:
        m = TERMINAL_RE.match(ln)
        if m:
            match = m
    if match is None:
        return None, None, bool(lines)
    had_noise = len(lines) > 1
    return match.group(1), match.group(2).strip(), had_noise


def normalize(path_str):
    """Reduce a model-supplied path to a clean base-relative form.

    Strips leading './' and quotes/backticks models sometimes add. A path
    that tries to escape the base with '..' comes back as None and is
    served as missing — the base is the whole world here.
    """
    p = path_str.strip().strip("`'\"").lstrip("./")
    if not p or ".." in Path(p).parts:
        return None
    return p


def listed_links(index_text, index_dir):
    """Return the base-relative paths an index file's entries point to.

    Index entries look like `- [name](relative/path)`. Links are relative
    to the index's own directory, so they are joined onto it. This is how
    the scorer knows whether a READ target was legitimately discovered
    (listed in an index the model had already seen) or guessed.
    """
    links = set()
    for m in re.finditer(r"^- \[[^\]]*\]\(([^)]+)\)", index_text, re.M):
        target = (Path(index_dir) / m.group(1)).as_posix()
        links.add(target.lstrip("./"))
    return links


def run_query(endpoint, base, query, protocol_text, max_turns):
    """Run one query's conversation and return its raw event log.

    The loop serves files and records events; it never blocks a
    violating read — the point is to measure compliance, not to prevent
    non-compliance. Returns a dict with the transcript, the file-access
    log, the terminal action, and bookkeeping the scorer needs.
    """
    messages = [
        {"role": "system", "content": protocol_text + CONTRACT},
        {"role": "user",
         "content": f"Task: {query['query']}\n"
                    "The context-base root is `.` — begin."},
    ]
    access_log, transcript = [], []
    served_links = set()          # paths listed in indexes served so far
    served_indexes = set()        # index paths already served
    terminal = {"action": None, "argument": None, "reason": None}
    corrections = 0

    for turn in range(1, max_turns + 1):
        reply = endpoint.call(messages)
        messages.append({"role": "assistant", "content": reply})
        action, argument, noise = parse_reply(reply)
        transcript.append({"turn": turn, "reply": reply, "noise": noise})

        if action is None:
            corrections += 1
            if corrections > MAX_CORRECTIONS:
                terminal["reason"] = "no_valid_completion"
                break
            messages.append({"role": "user", "content": CORRECTION})
            continue

        if action in ("ANSWER", "GAP"):
            terminal.update(action=action, argument=argument)
            break

        # action == READ: serve the file and log everything about it.
        rel = normalize(argument)
        target = (Path(base) / rel) if rel else None
        exists = bool(target) and target.is_file()
        is_index = bool(rel) and Path(rel).name == "INDEX.md"
        event = {
            "turn": turn, "path": rel or argument, "exists": exists,
            "is_index": is_index,
            "is_leaf": exists and not is_index and Path(rel).name != "_inbox.md",
            "is_inbox": bool(rel) and Path(rel).name == "_inbox.md",
            "listed": rel in served_links or rel == "INDEX.md",
        }
        access_log.append(event)
        if exists:
            content = target.read_text(encoding="utf-8")
            if is_index:
                served_indexes.add(rel)
                served_links |= listed_links(content, Path(rel).parent)
            messages.append({"role": "user",
                             "content": f"FILE: {rel}\n---\n{content}"})
        else:
            messages.append({"role": "user",
                             "content": f"ERROR: no such file: {argument}"})
    else:
        terminal["reason"] = "max_turns_exceeded"

    return {"access_log": access_log, "transcript": transcript,
            "terminal": terminal, "served_indexes": sorted(served_indexes)}


def score_query(query, run):
    """Score one query's event log against the protocol and expectations.

    Every criterion is a boolean computed from the log — bookkeeping, not
    judgment. `pass` requires all of them. Extra in-budget leaves on a
    retrieval query are recorded but don't fail (the protocol permits up
    to three leaves).
    """
    log = run["access_log"]
    leaves = [e["path"] for e in log if e["is_leaf"]]
    branches = {Path(e["path"]).parts[0] for e in log
                if e["exists"] and Path(e["path"]).parts[0:1]
                and len(Path(e["path"]).parts) > 1}
    indexed_dirs = {str(Path(p).parent) for p in run["served_indexes"]}

    criteria = {
        "completed": run["terminal"]["action"] is not None,
        "first_read_root": bool(log) and log[0]["path"] == "INDEX.md",
        "all_reads_listed": all(e["listed"] for e in log),
        "no_missing_files": all(e["exists"] for e in log),
        "branches_within_limit": len(branches) <= 2,
        "leaves_within_limit": len(leaves) <= query.get("max_leaves", 3),
        "leaf_after_its_index": all(
            str(Path(p).parent) in indexed_dirs for p in leaves),
        "inbox_never_read": not any(e["is_inbox"] for e in log),
    }
    if query["expect"] == "gap":
        criteria["gap_honored"] = (run["terminal"]["action"] == "GAP"
                                   and not leaves)
    else:
        criteria["required_leaves_read"] = (
            set(query["required_leaves"]) <= set(leaves)
            and run["terminal"]["action"] == "ANSWER")

    return {
        "id": query["id"], "kind": query["kind"], "pass": all(criteria.values()),
        "criteria": criteria,
        "leaves_read": leaves,
        "branches_entered": sorted(branches),
        "precision_extra": sorted(set(leaves) - set(query.get("required_leaves", []))),
        "terminal": run["terminal"],
        "file_access_log": log,
        "transcript": run["transcript"],
    }


def run_validation(endpoint, base, queries, protocol_text, max_turns, meta):
    """Run all queries sequentially and assemble the certification record."""
    results = [score_query(q, run_query(endpoint, base, q, protocol_text,
                                        max_turns))
               for q in queries]
    return {
        "record": "certification-run/v0",
        "tool": "waihona", "operation": "find", "tier_claimed": 1,
        "run": meta,
        "fixture": {"generator": "scripts/cb.py fixture",
                    "shape": "3 branches x 2 sub-branches x 4 leaves",
                    "leaves": 24},
        "inbox_write_path": ("not exercised — driver is read-only; the write "
                             "path (file.md) is a skill-level concern, "
                             "validated separately"),
        "queries": results,
        "result": "pass" if all(r["pass"] for r in results) else "fail",
    }


def print_report(record):
    """Print the human-readable summary the operator actually reads."""
    print(f"\n=== Traversal validation: {record['result'].upper()} "
          f"(model: {record['run'].get('model', '?')}) ===")
    for r in record["queries"]:
        print(f"\nQuery {r['id']} ({r['kind']}): "
              f"{'PASS' if r['pass'] else 'FAIL'}")
        for name, ok in r["criteria"].items():
            print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        print(f"  leaves read: {r['leaves_read'] or '(none)'}")
        if r["precision_extra"]:
            print(f"  extra in-budget leaves: {r['precision_extra']}")


# --- selftest -------------------------------------------------------------

def selftest(repo_waihona_dir):
    """Prove the loop, parser, and scorer work — no network, no model.

    Generates the real fixture into a temp directory, checks the queries
    file still matches it (fixture-drift guard), then replays scripted
    transcripts through the genuine machinery: one perfect run that must
    pass, and a set of failure vignettes that must each trip exactly the
    criterion they are designed to trip.
    """
    import subprocess
    queries = json.loads(
        (repo_waihona_dir / "validation" / "queries.json").read_text())
    protocol = (repo_waihona_dir / "find.md").read_text()
    failures = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "fixture"
        subprocess.run([sys.executable,
                        str(repo_waihona_dir / "scripts" / "cb.py"),
                        "fixture", str(base)], check=True,
                       capture_output=True)

        print("fixture-drift guard:")
        for q in queries:
            for leaf in q.get("required_leaves", []):
                check(f"fixture has {leaf}", (base / leaf).is_file())

        qa, qb, qc = queries

        def run_scripted(query, replies):
            return score_query(query,
                               run_query(FakeEndpoint(replies), base, query,
                                         protocol, max_turns=12))

        print("perfect run:")
        r = run_scripted(qa, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "READ: models/quantization/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md",
            "ANSWER: Q4 trades some quality for latency; see q4-vs-q5.md"])
        check("A passes", r["pass"])
        r = run_scripted(qb, [
            "READ: INDEX.md", "READ: hardware/INDEX.md",
            "READ: hardware/laptops/INDEX.md",
            "READ: hardware/laptops/m-series-16gb.md",
            "READ: models/INDEX.md", "READ: models/quantization/INDEX.md",
            "READ: models/quantization/long-context-falloff.md",
            "ANSWER: envelope per m-series-16gb.md; falloff per "
            "long-context-falloff.md"])
        check("B passes", r["pass"])
        r = run_scripted(qc, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "GAP: new: audio | local speech-to-text notes | nothing in the "
            "base covers STT"])
        check("C passes (gap honored)", r["pass"])

        print("failure vignettes:")
        r = run_scripted(qa, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md", "ANSWER: skipped index"])
        check("leaf before its index trips", not r["pass"]
              and not r["criteria"]["leaf_after_its_index"])
        r = run_scripted(qa, [
            "READ: INDEX.md", "READ: models/quantization/secret.md",
            "ANSWER: guessed"])
        check("unlisted path guess trips", not r["pass"]
              and not r["criteria"]["all_reads_listed"])
        r = run_scripted(qa, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "READ: models/quantization/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md",
            "READ: models/quantization/kv-cache.md",
            "READ: models/quantization/json-mode.md",
            "READ: models/quantization/long-context-falloff.md",
            "ANSWER: read everything"])
        check("fourth leaf trips", not r["pass"]
              and not r["criteria"]["leaves_within_limit"])
        r = run_scripted(qa, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "READ: hardware/INDEX.md", "READ: patterns/INDEX.md",
            "READ: models/quantization/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md", "ANSWER: toured"])
        check("third branch trips", not r["pass"]
              and not r["criteria"]["branches_within_limit"])
        r = run_scripted(qc, [
            "READ: INDEX.md", "ANSWER: made something up"])
        check("ANSWER on gap query trips", not r["pass"]
              and not r["criteria"]["gap_honored"])
        r = run_scripted(qc, [
            "READ: INDEX.md", "READ: models/INDEX.md",
            "READ: models/quantization/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md",
            "GAP: new: audio | stt | nothing found"])
        check("leaf read on gap query trips", not r["pass"]
              and not r["criteria"]["gap_honored"])
        r = run_scripted(qa, ["hm", "still thinking", "no idea"])
        check("malformed replies exhaust corrections", not r["pass"]
              and not r["criteria"]["completed"]
              and r["terminal"]["reason"] == "no_valid_completion")
        r = run_scripted(qa, ["READ: INDEX.md"] * 13)
        check("turn cap trips", not r["pass"]
              and r["terminal"]["reason"] == "max_turns_exceeded")
        r = run_scripted(qa, [
            "Let me think about this.\nThe index seems right.\nREAD: INDEX.md",
            "READ: models/INDEX.md", "READ: models/quantization/INDEX.md",
            "READ: models/quantization/q4-vs-q5.md",
            "Based on the leaf:\nANSWER: Q4 vs Q5 per q4-vs-q5.md"])
        check("noise with valid last line passes", r["pass"])

    print(f"\nselftest: {'PASS' if not failures else 'FAIL'} "
          f"({len(failures)} failure(s))")
    return 0 if not failures else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true",
                    help="verify loop/parser/scorer with no network or model")
    ap.add_argument("--base", type=Path, help="context-base root (fixture)")
    ap.add_argument("--endpoint", help="OpenAI-compatible base URL")
    ap.add_argument("--model", help="model name/key at the endpoint")
    ap.add_argument("--queries", type=Path,
                    help="queries file (default: ../validation/queries.json)")
    ap.add_argument("--out", type=Path, default=Path("record.json"),
                    help="where to write the JSON certification record")
    ap.add_argument("--date", default="unstated",
                    help="run date, stamped by the operator (YYYY-MM-DD)")
    ap.add_argument("--operator", default="unstated")
    ap.add_argument("--quantization", default="unstated")
    ap.add_argument("--params", default="unstated",
                    help="model parameter count, e.g. 4B")
    ap.add_argument("--api-key-file", type=Path,
                    help="file holding a bearer token, if the endpoint needs one")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--max-turns", type=int, default=12)
    args = ap.parse_args()

    waihona_dir = Path(__file__).resolve().parent.parent
    if args.selftest:
        return selftest(waihona_dir)

    if not (args.base and args.endpoint and args.model):
        ap.error("--base, --endpoint, and --model are required "
                 "(or use --selftest)")
    queries = json.loads((args.queries or
                          waihona_dir / "validation" / "queries.json"
                          ).read_text())
    protocol = (waihona_dir / "find.md").read_text()
    api_key = (args.api_key_file.read_text().strip()
               if args.api_key_file else None)
    endpoint = HttpEndpoint(args.endpoint, args.model, api_key, args.seed)
    meta = {"date": args.date, "operator": args.operator,
            "endpoint_type": "openai-chat-completions", "model": args.model,
            "quantization": args.quantization, "params": args.params,
            "temperature": 0, "seed": args.seed,
            "driver": "validate_traversal.py/v0"}
    record = run_validation(endpoint, args.base, queries, protocol,
                            args.max_turns, meta)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print_report(record)
    print(f"\nrecord written to {args.out}")
    return 0 if record["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
