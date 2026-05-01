# Archived: Protocol 1.0.0-alpha (originally "Version 1")

**Status:** Withdrawn pre-release. Never formally ratified. Superseded by Protocol 2.0 before stabilising.

**Do not implement against this version.** It is preserved here for historical reference only.

## What this is

The first wire-protocol design for [Agent Remote Hands](https://github.com/WilliamIsted/agent-remote-hands), as it stood at the project's initial commit (`agent-remote-hands@0ab328b`, "Initial commit: Agent Remote Hands (windows-modern + windows-nt + MCP)"). The spec self-declared as `Version: 1`; this archive renames the tag to `v1.0.0-alpha` to signal SemVer-honestly that it never reached a stable release.

## Why it was withdrawn

Protocol 1 was a working design draft, not a ratified spec. It was redesigned in place — not extended — into Protocol 2.0, with breaking changes across:

- **Verb naming** — uppercase tokens (`PING`, `CAPS`, `INFO`, `RUN`, `LIST`) became namespaced lowercase (`system.health`, `system.capabilities`, `system.info`, `process.start`, `file.list`).
- **Encoding** — ANSI / Latin-1 wire became UTF-8.
- **Tabular responses** — tab-separated rows packed into a single payload became structured JSON.
- **Subscriptions** — multi-`OK` long-poll terminated by `END\n` became out-of-band `EVENT` frames with explicit subscription IDs.
- **Tier model** — V2 introduced the observe / drive / power tier hierarchy with file-token authentication; V1 had a single `REMOTE_HANDS_POWER=1` env-var gate.
- **Error model** — V1's `ERR <message>` became V2's `ERR <code> [<json-detail>]` with stable string codes.

V2's [`PROTOCOL.md`](https://github.com/WilliamIsted/agent-remote-hands-protocol/blob/main/PROTOCOL.md) is the living spec. Implementations should target V2.0 or later.

## What's preserved in this tag

| File | Purpose |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | The V1 spec, ~275 lines. Body text retains historical "protocol version 1" / `protocol=1` language. The version header at the top is renamed to `1.0.0-alpha` with a note on the rename. |
| [`tests/conformance/`](tests/conformance/) | The V1-era conformance suite. Different shape from V2 — uses `client.py` (not `wire.py`), capability-gated tests against the V1 verb set (`PING`, `CAPS`, `INFO`, `SHOT`, `RUN`, `LIST`, `WINLIST`, etc.). |
| [`LICENSE`](LICENSE) | Apache 2.0 (added at archive time — V1 originally shipped without an explicit license file; the archive applies the project's chosen license retrospectively). |
| `ARCHIVED.md` | This file. |

## What's not here

- No `LLM-OPERATORS.md` — that document is V2-era; it didn't exist for V1.
- No `VERBS.md` — also V2-era.
- No agent implementations — they live in the [agent repo](https://github.com/WilliamIsted/agent-remote-hands) at the corresponding archived tag (`v0.1.0`, with V1 binaries attached as a pre-release).

## Reading this archive

```bash
# View the V1 spec at this tag
git show v1.0.0-alpha:PROTOCOL.md

# Check out the entire V1 archive
git checkout v1.0.0-alpha
```

Tags in this repo are write-once. If you find a typo or ambiguity in this archived spec, the convention is to record it in the next-version migration notes rather than retroactively editing this tag.

## Related

- **Protocol 2.0** (current) — `git checkout v2.0.0` or browse `main`.
- **Agent v0.1.0** — pre-release in the agent repo containing V1 windows-modern + windows-nt binaries.
- **Cross-version design context** — see the project's Overview workspace for the rationale behind V1's withdrawal and V2's redesign.
