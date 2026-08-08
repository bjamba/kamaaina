# Where Kamaʻāina Ends and Your Stack Begins

Kamaʻāina deliberately does not tell you how to build or run a local model stack. Plenty of projects do that well — the author's own machine was built from a separate infrastructure repo — and baking any one machine's choices into this ADK would break its promise to every other machine.

The division of labor:

| | Owned by | Examples |
|---|---|---|
| **Kamaʻāina (this repo)** | Portable methodology and artifacts | Tier definitions, context-engineering patterns, skill scaffolds, manifests, validation fixtures and drivers, certification records |
| **Your stack-builder** | One machine's reality | Which inference engine, which models and quants, ports and endpoints, API keys, serving decisions, monitoring |

**The bridge between the two is deliberately thin and standard: an OpenAI-compatible endpoint URL and a model name.** Every Kamaʻāina artifact that must touch a live model (validation drivers, future certification tooling) assumes exactly those two facts and nothing else. If your stack serves an OpenAI-compatible API — llama.cpp's server, llama-swap, ollama, vLLM, a LiteLLM gateway — Kamaʻāina's tooling works with it unmodified, and machine specifics appear only in clearly-marked example appendices.

Two consequences worth stating:

- **A stack repo is about getting running; Kamaʻāina is about growing once you are.** One is the toolshed going up; the other is the craft practiced inside it. They evolve independently — a rebuilt stack shouldn't invalidate a single Kamaʻāina artifact, and a new Kamaʻāina release shouldn't require touching your stack.
- **Certification records name the stack, but don't depend on it.** A `certification-run` record captures model, quantization, and endpoint type as *provenance* — so results are interpretable — never as *requirements* for reproducing them on different hardware.
