# Agent Remote Hands — Protocol

[![Specification](https://github.com/WilliamIsted/agent-remote-hands-protocol/actions/workflows/specification.yml/badge.svg?branch=main)](https://github.com/WilliamIsted/agent-remote-hands-protocol/actions/workflows/specification.yml)
[![License](https://img.shields.io/github/license/WilliamIsted/agent-remote-hands-protocol?label=License&color=blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.2%20stable-blue)](spec/verbs/)
[![Conformance: pytest](https://img.shields.io/badge/conformance-pytest-0A9EDC)](tests/conformance/)
[![Last commit](https://img.shields.io/github/last-commit/WilliamIsted/agent-remote-hands-protocol?logo=github)](https://github.com/WilliamIsted/agent-remote-hands-protocol/commits/main)

The wire-protocol spec, conformance suite, and reference Python client for [Agent Remote Hands](https://github.com/WilliamIsted/agent-remote-hands) — a Windows control surface for AI agents.

This repo is the **contract**. Implementations live elsewhere (the modern Windows agent, a planned NT agent, future cross-OS agents); this repo defines what they all speak.

## What's here

The spec is split into **source** (humans edit) and **generated** (machines + humans consume):

| Source | Purpose |
|---|---|
| [`spec/verbs/`](spec/verbs/) | One JSON file per verb. Each file is a strict-tool definition with `x-*` extensions for protocol metadata (CRUDX, families, errors, output schema, tool-fallback chains). |
| [`spec/families.json`](spec/families.json) | OS-family declarations + per-family metadata (token paths, capability hints). |
| [`spec/framing/`](spec/framing/) | Hand-written markdown for the non-verb sections of `dist/PROTOCOL.md` (wire format, lifecycle, error model, etc.). |
| [`spec/operators/`](spec/operators/) | Hand-written markdown for `dist/LLM-OPERATORS.md` (the operator's-eye view for LLMs driving an agent). |
| [`spec/AUTHORING-CHECKLIST.md`](spec/AUTHORING-CHECKLIST.md) | Per-verb completion definition. |
| [`spec/reserved-names.json`](spec/reserved-names.json) | v1 verb names + superseded v2.0 / v2.1.0-rc names that MUST NOT be reintroduced. Enforced by `tests/check_spec.py`. |
| [`Tools/gen.py`](Tools/gen.py) | Renders the generated artefacts below from the source files. Stdlib-only Python. |

| Generated (under `dist/`, gitignored — run `python Tools/gen.py` to produce) | Purpose |
|---|---|
| `dist/PROTOCOL.md` | The canonical rendered spec — wire format, framing, lifecycle, tier model, error model, every verb's signature. Concatenated from `spec/framing/` + generated §4. |
| `dist/verbs-windows-modern.md` | One-line conceptual catalogue of every verb the `windows-modern` agent implements. |
| `dist/verbs-windows-legacy.md` | Same for the `windows-legacy` agent (XP SP3 → Win 10 pre-1809; v141_xp toolchain). Currently MVP — only `connection.hello` opted-in. Added v2.2. |
| `dist/verbs-windows-classic.md` | Same for the `windows-classic` agent (UIA-only verbs filtered out). |
| `dist/verbs.json` | Concatenated strict-tool definitions with `x-*` stripped, all-families superset. Use when the target family isn't known at registration time and you'll capability-gate at runtime. |
| `dist/verbs-windows-modern.json` | Same shape as `dist/verbs.json`, filtered to verbs the `windows-modern` family implements. Drop-in for `client.messages.create(tools=...)` against a known-family agent. |
| `dist/verbs-windows-legacy.json` | Same for `windows-legacy`. |
| `dist/verbs-windows-classic.json` | Same for `windows-classic`. |
| `dist/LLM-OPERATORS.md` | Operator's-eye view for LLMs driving an agent. Concatenated from `spec/operators/`. |
| [`tests/conformance/`](tests/conformance/) | Executable contract — pytest suite that any agent claiming to speak the protocol must pass. Includes [`wire.py`](tests/conformance/wire.py), the canonical Python reference client (stdlib-only — speaks MCP-stdio framing post-hello, with a `WsWireClient` subclass for RFC 6455 binary frames). |

## Reading paths

Different reading tasks, different docs:

- **"I want to understand the wire"** → `dist/PROTOCOL.md` (run `python Tools/gen.py` first).
- **"What verbs exist and what do they do"** → `dist/verbs-<family>.md` for the family you target. One-line per verb; scan in 30 seconds.
- **"I want to register the verbs as Anthropic strict-tool definitions"** → `dist/verbs-<family>.json` if you know the target family at build time; `dist/verbs.json` (the all-families superset) if you'll capability-gate at runtime.
- **"I'm an LLM about to drive an agent"** → `dist/LLM-OPERATORS.md` (run `python Tools/gen.py` first; source under [`spec/operators/`](spec/operators/)). What to read, what to assume, footguns to know about, a worked example.
- **"I need to verify my implementation conforms"** → [`tests/conformance/`](tests/conformance/) + [`wire.py`](tests/conformance/wire.py).
- **"I want to author / amend the spec itself"** → [`spec/`](spec/). Edit `spec/verbs/<verb>.json` for verb changes; `spec/framing/*.md` for framing-section changes; regenerate with `python Tools/gen.py`.

## Status

| Version | Status | Notes |
|---|---|---|
| 2.2 | Stable (this repo's `main`) | Wire-framing modernisation: MCP-stdio (`Content-Length: N\r\n\r\n<JSON>` carrying MCP JSON-RPC 2.0) becomes the default ongoing framing; RFC 6455 WS framing is opt-in via `--framing ws`. The v2.0 / v2.1 ARH header-line text format is retired as an ongoing framing — retained only for the `connection.hello` bootstrap. v2.1 clients receive `ERR protocol_mismatch`; clean break. New `windows-legacy` family declared (XP SP3 → Win 10 builds before 1809; v141_xp toolchain; honours `mcp` framing only). windows-modern floor corrected to Win 10 1809 / build 17763. `system.verbs` returns full strict-tool defs over the wire (backs MCP `tools/list`). `input.mouse.click` gains `triple: true` and `clicks: N` (caller-controlled `clicks_interval_ms`). `screen.capture` `format` enum extended with `jpeg`/`heic` forward-compat values; hard-coded `quality: 80` default removed. `system.info` gains `framings` array. New `framing_unsupported` error code. Per-family `format_supported` arrays in `families.json`. New `tools/list_changed` is **not** emitted on tier transitions — the catalog is complete from first call (resolves the tier-elevation cost concern). See `dist/PROTOCOL.md` §1.5 / §1.6 / §2.2 / §12.5. |
| 2.1 | Superseded by 2.2; never tagged final | CRUDX tier ladder; `clipboard.read`/`write` → `clipboard.get`/`set`; `directory.*` namespace split; `system.*` power verbs re-namespaced; `registry.*` resource-first restructure; `input.*` split into mouse/keyboard sub-namespaces; argument quoting; native `vision.ocr`. Released as `v2.1.0-rc.3` only — final tag was never cut; v2.1 features are included in `v2.2.0`. |
| 2.0 | Released | Pin clients here for the old `observe`/`drive`/`power` tier vocabulary and the `clipboard.read`/`write`/`file.list`/`file.mkdir` verb names. Implemented by `windows-modern@v0.2.x`. |
| 3.0 | In design | Modern-family major — privsep dispatcher + tier-restricted workers. The "JSON-RPC + Content-Length framing" portion of the original v3 design landed in v2.2 ahead of schedule; v3.0 now focuses on the privsep architecture. See the agent repo's `Documents/Overview/Planning/v3-structural-review.md` for the cross-repo design context. |

Protocol versioning is **per-family-branched**, not linear: `windows-classic` (NT, 2000, XP, 2003) plateaus at the 2.x line; `windows-modern` (10, 11, Server 2016+) moves to 3.x. Both are alive at the same time. See `dist/PROTOCOL.md` §12 for the full versioning policy.

## Honest scope

Today's spec is **Windows-flavoured**. Roughly 70% of verbs are Win32-specific in shape (`window.*`, `element.*`, `registry.*`, parts of `system.*`); the framing layer (length-prefixed wire, tier model, capability advertisement, watch subscriptions) is platform-agnostic.

The verb namespace admits new families via `spec/families.json` + per-family `x-families.<family>` slots on each verb file. `dist/verbs-<family>.md` filters per family — verbs marked `implemented: false` for a family are omitted from that family's catalogue.

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

Tests are **capability-gated**: agents that don't advertise a verb get the relevant tests skipped, not failed. The suite covers all 12 namespaces; tier-raising tests need the agent's elevation token (default `%ProgramData%\AgentRemoteHands\token`, override with `--token-path`).

See [`tests/conformance/README.md`](tests/conformance/README.md) for the full invocation reference and what's intentionally not covered (synthetic input that would perturb the host, real reboots, etc.).

## Generating the rendered spec

```bash
python Tools/gen.py
```

Produces `dist/PROTOCOL.md`, `dist/verbs-windows-modern.md`, `dist/verbs-windows-classic.md`, `dist/verbs.json`, `dist/verbs-windows-modern.json`, and `dist/verbs-windows-classic.json`. `dist/` is gitignored — consumers regenerate as needed. CI verifies the generator runs cleanly against the current spec tree.

## Relationship to the agent repo

The agent (Windows binary, MCP bridge, install scripts, release pipeline) lives in [agent-remote-hands](https://github.com/WilliamIsted/agent-remote-hands). That repo references this one as a git submodule at `protocol/`, pinned to a specific Protocol-repo tag. Each agent release ships the rendered `dist/PROTOCOL.md`, `dist/LLM-OPERATORS.md`, and `wire.py` alongside the binary in the release zip — sourced from the submodule, generated at release time.

## Contributing

This repo accepts:

- **Errata** for the current spec — typos, ambiguities, missing edge cases. Edit `spec/verbs/<verb>.json` (verb-level) or `spec/framing/*.md` (framing-level); PRs against `main`.
- **New verb proposals** — open an issue first; design discussion happens in comments, decisions are captured in the issue body before a spec PR lands.
- **Conformance gaps** — if your implementation passes the suite but breaks against a real agent (or vice versa), that's a suite bug. PR a failing test first, fix second.
- **Cross-OS verb namespaces** — see "Honest scope" above. Coordinate via an issue before drafting.

PRs that touch the spec must also update the conformance suite; PRs that touch the conformance suite without a spec change get reviewed for "is this a clarification or a contract change in disguise".

## Where design proposals live

Long-form proposals (RFC-shaped, pre-implementation) live as GitHub issues tagged `enhancement`. If a proposal lands and ships, the contract moves into `spec/verbs/<verb>.json` (or `spec/framing/*.md` for framing changes); the rendered `dist/PROTOCOL.md` follows automatically. Don't drop speculative design docs into this repo unprompted; the spec is the durable artefact.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

Copyright 2026 William Isted and contributors.
