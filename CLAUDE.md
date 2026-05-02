# CLAUDE.md

Operational guidance for Claude Code working in this repo. The user-facing overview lives in [`README.md`](README.md); the spec itself lives in [`PROTOCOL.md`](PROTOCOL.md). This file complements both rather than duplicating them.

## What this repo is

The canonical wire-protocol spec, conformance suite, and reference Python client for [Agent Remote Hands](https://github.com/WilliamIsted/agent-remote-hands). **Specs and contracts only — no implementation code.** The Windows agent, MCP bridge, install scripts, and release pipeline live in the agent repo; this repo is what they all conform to.

Three peer documents at the root, one per reading task:

- [`PROTOCOL.md`](PROTOCOL.md) — the contract. Wire format, framing, lifecycle, tier model, error model, every verb's signature.
- [`VERBS.md`](VERBS.md) — one-line catalogue per verb. Scannable in 30 seconds.
- [`LLM-OPERATORS.md`](LLM-OPERATORS.md) — operator's-eye view for LLMs driving the agent.

[`tests/conformance/`](tests/conformance/) is the executable contract.

## Division of labour with the agent repo

| Concern | Lives in |
|---|---|
| Wire-protocol spec | this repo (`PROTOCOL.md`) |
| Conformance suite, reference client | this repo (`tests/conformance/`) |
| Cross-implementation operator guidance | this repo (`LLM-OPERATORS.md`) |
| Windows agent implementation | [agent repo](https://github.com/WilliamIsted/agent-remote-hands) |
| MCP bridge | agent repo |
| Install scripts, release pipeline, Scoop manifest | agent repo |
| Per-agent supported-protocols matrix | agent repo (each agent's `SUPPORTED.md`) |

When a wire-protocol change lands, it's typically a coordinated pair: a spec PR here, a corresponding implementation PR in the agent repo. The agent's submodule pin advances to the new Protocol-repo tag once both merge.

## Versioning

Protocol versioning is **per-family-branched**, not linear (see `PROTOCOL.md` §12). Tags on `main`:

- `v2.0.0` — first ratified release of the 2.0 spec.
- `v2.0.1`, `v2.0.2`, … — errata patches.
- `v2.1.0` — NT-family minor (adds NT-specific verbs; wire-compatible with 2.0).
- `v3.0.0-rc.*`, `v3.0.0` — modern-family major (privsep + JSON-RPC).

Maintenance branches appear only when v3 work would otherwise destabilise v2 maintenance — at that point, `main` carries v3 and `protocol-2.x` (branched off the last v2 tag) carries v2 maintenance commits. Don't pre-create branches.

## Common tasks

### Reading the spec at a specific version

```bash
git show v2.0.0:PROTOCOL.md          # rendered to stdout
git checkout v2.0.0 -- PROTOCOL.md   # writes to working tree (don't commit)
```

Tags are write-once by git's nature. Treat archived versions accordingly: errata go into the migration notes for the next version, not into the archived tag.

### Running the conformance suite against an agent

```bash
python tests/conformance/run.py <host> 8765
```

See [`tests/conformance/README.md`](tests/conformance/README.md) for tier-elevation token paths and what's intentionally not covered.

### Adding a new verb to the spec

1. Open an issue tagged `enhancement` first. Design discussion happens in comments.
2. Update [`PROTOCOL.md`](PROTOCOL.md) — verb name, args, success/error shape, tier requirement, namespace.
3. Update [`VERBS.md`](VERBS.md) — one line in the relevant namespace section.
4. Add a conformance test in `tests/conformance/test_<namespace>.py`. Gate it with `needs_verb(capabilities, "<verb>")` so older agents skip rather than fail.
5. Run the suite locally against the agent that implements it.

PRs missing any of (1)–(4) are incomplete.

### Coordinating a wire-protocol change with the agent repo

1. Spec PR here (steps above). Merge once review settles.
2. Tag the new Protocol release here (`v2.0.1` for errata, `v2.1.0` for additive minors, `v3.0.0` for major).
3. In the agent repo, update the submodule pin: `cd protocol && git fetch && git checkout v2.0.1 && cd .. && git add protocol && git commit -m "Bump protocol to v2.0.1"`.

The agent repo's CI fetches submodules; the pin update IS the integration.

## Conventions

- Commit messages: short, bullet-pointed, present-tense. Mirror existing log style.
- Branch off `main`; PRs target `main`.
- Markdown for all docs; prefer `.md` over `.rst` / inline HTML.
- Spec changes always touch `PROTOCOL.md` + `VERBS.md` + a conformance test. PRs missing any are incomplete.

## Things not to do

- **Don't edit archived tags.** `git show v2.0.0:PROTOCOL.md` is what implementers saw at v2.0.0's final state. Errata go into migration notes for the next version, not retroactively into the tagged spec.
- **Don't pre-split into per-OS verb subdirectories.** Today's `PROTOCOL.md` is single-file Windows-flavoured. The split into `verbs/<os>/` happens when a second-OS implementation appears, not pre-emptively. See `Documents/Overview/Planning/v3-structural-review.md` (in the Overview repo) for the design rationale.
- **Don't add implementation code.** This repo is specs only. The Python reference client (`wire.py`) and PowerShell ground-truth fixtures (`tests/conformance/fixtures/`) are in support of the conformance suite, not implementations.
- **Don't skip conformance tests when changing verb signatures.** The suite is the contract. A spec change without a matching test is a contract change without verification.

## Where design proposals live

Long-form proposals (RFC-shaped, pre-implementation) live as GitHub issues tagged `enhancement`. Cross-cutting design that spans agent + protocol lives in the Overview repo's `Documents/Overview/Planning/` directory (in the user's local Overview workspace).

If a proposal lands and ships, the contract moves into `PROTOCOL.md`. Issue and Overview-side notes stay as record of what was considered and why.

## Out of scope

- Language-binding generators (the spec is markdown; bindings are downstream consumers' work).
- Implementation tutorials (the agent repo's README is the implementation entry point).
- Operational runbooks for deployments (agent repo's `docs/`).
