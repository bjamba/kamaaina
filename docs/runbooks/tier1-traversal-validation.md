# Runbook: Tier 1 Traversal Validation

**Who runs this:** you, or an agent session on the machine that serves your models. It makes no difference to the result — the validation is carried by a deterministic driver script that fixes the interaction and the scoring, so the operator only runs commands.

**What it proves:** that a small, locally-run model can execute the Waihona traversal protocol ([`tools/waihona/find.md`](../../tools/waihona/find.md)) for real — read the root index, descend only relevant branches, load at most three leaves, and honestly report a gap when nothing matches. This is the last open acceptance item on issue [#5](https://github.com/bjamba/kamaaina/issues/5), and the claim behind the context-base spec's Tier 1 story.

**What it needs from your stack — exactly two facts:** an OpenAI-compatible chat-completions endpoint URL, and a model name that endpoint serves. Everything machine-specific (how models are served, ports, keys) belongs to your stack-builder repo, not here — see [docs/stack-boundary.md](../stack-boundary.md).

## Procedure

On the machine (or any machine that can reach the endpoint):

```bash
# 1. Get the repo and confirm the harness is sound (offline, no model)
git clone https://github.com/bjamba/kamaaina && cd kamaaina
python3 tools/waihona/scripts/validate_traversal.py --selftest

# 2. Generate the deterministic 24-leaf fixture base
python3 tools/waihona/scripts/cb.py fixture /tmp/cb-fixture

# 3. Run the validation (fill in your endpoint + model; stamp the metadata)
python3 tools/waihona/scripts/validate_traversal.py \
  --base /tmp/cb-fixture \
  --endpoint "$ENDPOINT" --model "$MODEL" \
  --quantization "<quant>" --params "<e.g. 4B>" \
  --operator "<you>" --date "<YYYY-MM-DD>" \
  --out "<date>-<model>.json"
```

The driver runs three queries (single-branch retrieval, cross-branch retrieval, and a deliberate gap), logs every file the model asks for, and scores the log against the protocol's rules and the fixture's known-correct answers. It prints a per-query PASS/FAIL table and writes a `certification-run/v0` JSON record containing the full transcript and file-access log. Exit code 0 = all three passed.

## Recording the result

1. Commit the JSON record to `tools/waihona/validation/records/<date>-<model>.json` via PR (the record includes transcripts — that's the evidence, keep it).
2. In the same PR, update the "Run status" line in the spec's Validation plan section (`design/context-base/context-base.md`).
3. Tick the validation checkbox on issue #5. If this was the last open item, the issue closes.

## If it fails — read this before rerunning

**A failed run is a finding, not a mistake.** Commit the failing record too, and open an issue describing which criterion tripped — that is data about where the protocol's wording or the format's design loses a small model, which is exactly what this ADK exists to learn. Never quietly retry until green: repeated runs are fine for transport errors, but a model that flunks the protocol at temperature 0 will flunk it again, and a "pass" fished out of variance would poison the tier claim.

Calibrate what a result means by where your model sits relative to the tier floor (Tier 1 assumes ~7–9B — [docs/tiers.md](../tiers.md)):

- A **below-floor** model (e.g. a 4B) **passing** is strong evidence the floor is safe.
- A below-floor model **failing** is *not* a Tier 1 failure — note it, and rerun with a floor-sized model before concluding anything.
- A floor-sized model failing is the real red flag: the protocol (or the format's sizing) needs work, and the spec's "Mandatory at Tier 1" claims are on notice.

## Appendix — Example: DGX Spark (bjamba's stack)

> Machine specifics live in your stack repo ([stack boundary](../stack-boundary.md)); this appendix only shows what the two generic facts look like on one real machine.

```bash
ssh spark          # Tailscale SSH; then work inside tmux, per that repo's conventions
tmux new -s kamaaina
git clone https://github.com/bjamba/kamaaina && cd kamaaina

# llama-swap serves an OpenAI-compatible API on loopback :9000;
# model keys are tier names. `fast` = Qwen3.5-4B — below the Tier 1 floor,
# so a pass is strong floor evidence (see calibration above).
python3 tools/waihona/scripts/validate_traversal.py \
  --base /tmp/cb-fixture \
  --endpoint http://127.0.0.1:9000 --model fast \
  --quantization UD-Q4_K_XL --params 4B \
  --operator bjamba --date "$(date +%F)" \
  --out "$(date +%F)-fast.json"

# Optional contrast run with a much larger model (80B-A3B MoE):
#   --model coder --params 80B-A3B --out "$(date +%F)-coder.json"
```

No API key is needed on loopback; if you run through a gateway that wants one, pass `--api-key-file ~/.spark-key`.
