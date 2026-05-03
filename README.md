# Agent Remote Hands — Protocol

[![Specification](https://github.com/WilliamIsted/agent-remote-hands-protocol/actions/workflows/specification.yml/badge.svg?branch=main)](https://github.com/WilliamIsted/agent-remote-hands-protocol/actions/workflows/specification.yml)
[![License](https://img.shields.io/github/license/WilliamIsted/agent-remote-hands-protocol?label=License&color=blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1%20stable-blue)](PROTOCOL.md)
[![Conformance: pytest](https://img.shields.io/badge/conformance-pytest-0A9EDC)](tests/conformance/)
[![Last commit](https://img.shields.io/github/last-commit/WilliamIsted/agent-remote-hands-protocol?logo=github)](https://github.com/WilliamIsted/agent-remote-hands-protocol/commits/main)

The wire-protocol spec, conformance suite, and reference Python client for [Agent Remote Hands](https://github.com/WilliamIsted/agent-remote-hands) — a Windows control surface for AI agents.

This repo is the **contract**. Implementations live elsewhere (the modern Windows agent, a planned NT agent, future cross-OS agents); this repo defines what they all speak.

## What's here

| File | Purpose |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | The canonical spec — wire format, framing, lifecycle, tier model, error model, every verb's signature. |
| [`VERBS.md`](VERBS.md) | One-line conceptual catalogue of every verb, organised by namespace. Read this first when scanning "what verbs exist and what do they do". |
| [`LLM-OPERATORS.md`](LLM-OPERATORS.md) | Operator's-eye view for LLMs driving an agent through this protocol. What to read, what to assume, common footguns, a worked-example session. |
| [`tests/conformance/`](tests/conformance/) | Executable contract — pytest suite that any agent claiming to speak the protocol must pass. Includes [`wire.py`](tests/conformance/wire.py), the canonical Python reference client (~170 lines, stdlib-only). |

## Reading paths

Different reading tasks, different docs:

- **"I want to understand the wire"** → [`PROTOCOL.md`](PROTOCOL.md). Framing rules, every verb's argument shape, error codes, the connection state machine, the tier model.
- **"What verbs exist and what do they do"** → [`VERBS.md`](VERBS.md). One-line per verb; scan it in 30 seconds.
- **"I'm an LLM about to drive an agent"** → [`LLM-OPERATORS.md`](LLM-OPERATORS.md). What to read, what to assume, footguns to know about, a worked example.
- **"I need to verify my implementation conforms"** → [`tests/conformance/`](tests/conformance/) + [`wire.py`](tests/conformance/wire.py).

## Status

| Version | Status | Notes |
|---|---|---|
| 2.1 | Stable (this repo's `main`) | CRUDX tier ladder (`read` < `create` < `update` < `delete` < `extra_risky`); `clipboard.read`/`write` renamed to `clipboard.get`/`set`; new `directory.*` namespace split out of `file.*` with full CRUDX-complete primitives; header-line argument quoting (`"path with spaces"`). Wire-breaking change vs 2.0 — clean cut, no aliases. Implemented by `windows-modern@v0.3.x`. See [`PROTOCOL.md` §12.5](PROTOCOL.md) for the full release notes and migration ladder. |
| 2.0 | Released | Pin clients here for the old `observe`/`drive`/`power` tier vocabulary and the `clipboard.read`/`write`/`file.list`/`file.mkdir` verb names. Implemented by `windows-modern@v0.2.x`. |
| 3.0 | In design | Modern-family major — privsep dispatcher + tier-restricted workers; JSON-RPC 2.0 wire format with binary side-channel. See the agent repo's `Documents/Overview/Planning/v3-structural-review.md` for the cross-repo design context. |

Protocol versioning is **per-family-branched**, not linear: `windows-classic` (NT, 2000, XP, 2003) plateaus at the 2.x line; `windows-modern` (10, 11, Server 2016+) moves to 3.x. Both are alive at the same time. See [`PROTOCOL.md` §12](PROTOCOL.md) for the full versioning policy.

## Honest scope

Today's spec is **Windows-flavoured**. Roughly 70% of verbs are Win32-specific in shape (`window.*`, `element.*`, `registry.*`, parts of `system.*`); the framing layer (length-prefixed wire, tier model, capability advertisement, watch subscriptions) is platform-agnostic.

The verb namespace is designed to admit `verbs/<os>/` per-OS subdirectories when other-OS implementations materialise — that split happens when a second-OS agent appears, not pre-emptively. Until then, [`VERBS.md`](VERBS.md) tags Windows-specific verbs and namespaces inline.

**External implementers are welcome.** Apache 2.0 covers it. If you're building a macOS, Linux, or BSD agent against this protocol, please open an issue — the framing is generalisable, and we'd prefer to extend the namespace deliberately rather than have parallel forks.

## Running the conformance suite

Against a local agent on the default port:

```bash
pip install pytest
python tests/conformance/run.py 127.0.0.1
```

Against a remote agent:

```bash
python tests/conformance/run.py 192.168.1.42 8765
```

Or invoke pytest directly:

```bash
pytest tests/conformance --host 192.168.1.42 --port 8765 -v
```

Tests are **capability-gated**: agents that don't advertise a verb get the relevant tests skipped, not failed. The suite covers all 11 namespaces; tier-raising tests need the agent's elevation token (default `%ProgramData%\AgentRemoteHands\token`, override with `--token-path`).

See [`tests/conformance/README.md`](tests/conformance/README.md) for the full invocation reference and what's intentionally not covered (synthetic input that would perturb the host, real reboots, etc.).

## Relationship to the agent repo

The agent (Windows binary, MCP bridge, install scripts, release pipeline) lives in [agent-remote-hands](https://github.com/WilliamIsted/agent-remote-hands). That repo references this one as a git submodule at `protocol/`, pinned to a specific Protocol-repo tag. Each agent release ships PROTOCOL.md, LLM-OPERATORS.md, and wire.py alongside the binary in the release zip — sourced from the submodule, byte-identical to what you see here.

## Contributing

This repo accepts:

- **Errata** for the current spec — typos, ambiguities, missing edge cases. PRs against `main`.
- **New verb proposals** — open an issue first; design discussion happens in comments, decisions are captured in the issue body before a spec PR lands.
- **Conformance gaps** — if your implementation passes the suite but breaks against a real agent (or vice versa), that's a suite bug. PR a failing test first, fix second.
- **Cross-OS verb namespaces** — see "Honest scope" above. Coordinate via an issue before drafting.

PRs that touch the spec must also update the conformance suite; PRs that touch the conformance suite without a spec change get reviewed for "is this a clarification or a contract change in disguise".

## Where design proposals live

Long-form proposals (RFC-shaped, pre-implementation) live as GitHub issues tagged `enhancement`. If a proposal lands and ships, the spec moves into [`PROTOCOL.md`](PROTOCOL.md). Don't drop speculative design docs into this repo unprompted; the spec is the durable artefact.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

Copyright 2026 William Isted and contributors.
