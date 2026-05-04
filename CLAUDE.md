# CLAUDE.md

Operational guidance for Claude Code working in this repo. The user-facing overview lives in [`README.md`](README.md). This file complements it rather than duplicating it.

## What this repo is

The canonical wire-protocol spec, conformance suite, and reference Python client for [Agent Remote Hands](https://github.com/WilliamIsted/agent-remote-hands). **Specs and contracts only — no implementation code.** The Windows agent, MCP bridge, install scripts, and release pipeline live in the agent repo; this repo is what they all conform to.

## Source-of-truth layout

The spec is **source-authored as JSON + markdown** under `spec/` and **rendered to `dist/`** by `Tools/gen.py`:

| Source (humans edit) | What it carries |
|---|---|
| `spec/verbs/<verb>.json` | Per-verb strict-tool definition with `x-*` extensions (CRUDX, families, errors, output schema, implementations chain). |
| `spec/families.json` | OS-family declarations with per-family metadata (token paths, capability hints). |
| `spec/framing/*.md` | Hand-written markdown for `dist/PROTOCOL.md` non-verb sections (wire format, lifecycle, errors, tier model, etc.). |
| `spec/operators/*.md` | Hand-written markdown for `dist/LLM-OPERATORS.md` (the operator's-eye view for LLMs driving an agent). |
| `spec/AUTHORING-CHECKLIST.md` | Per-verb completion definition. Read before authoring or amending a verb. |
| `spec/reserved-names.json` | v1 verb names + superseded v2.0 / v2.1.0-rc names that MUST NOT be reintroduced. Enforced by `tests/check_spec.py`. |

| Generated (run `python Tools/gen.py`) | What it carries |
|---|---|
| `dist/PROTOCOL.md` | Canonical rendered spec. Concatenated `spec/framing/*.md` + generated §4 from `spec/verbs/*.json`. |
| `dist/verbs-<family>.md` | One-line per-verb catalogue, filtered to verbs that family implements. |
| `dist/verbs.json` | Concatenated strict-tool defs with `x-*` stripped, ready for `client.messages.create(tools=...)`. |
| `dist/LLM-OPERATORS.md` | Operator's-eye view for LLMs driving an agent. Concatenated `spec/operators/*.md`. |

`dist/` is gitignored — consumers regenerate as needed. CI verifies the generator runs cleanly.

## Division of labour with the agent repo

| Concern | Lives in |
|---|---|
| Wire-protocol spec | this repo (`spec/` + `dist/`) |
| Conformance suite, reference client | this repo (`tests/conformance/`) |
| Cross-implementation operator guidance | this repo (`spec/operators/` → `dist/LLM-OPERATORS.md`) |
| Windows agent implementation | [agent repo](https://github.com/WilliamIsted/agent-remote-hands) |
| MCP bridge | agent repo |
| Install scripts, release pipeline, Scoop manifest | agent repo |
| Per-agent supported-protocols matrix | agent repo (each agent's `SUPPORTED.md`) |

When a wire-protocol change lands, it's typically a coordinated pair: a spec PR here, a corresponding implementation PR in the agent repo. The agent's submodule pin advances to the new Protocol-repo tag once both merge.

## Versioning

Protocol versioning is **per-family-branched**, not linear (see `dist/PROTOCOL.md` §12). Tags on `main`:

- `v2.0.0` — first ratified release of the 2.0 spec.
- `v2.0.1`, `v2.0.2`, … — errata patches.
- `v2.1.0` — current stable (CRUDX tier vocabulary; `clipboard.read`/`write` rename; `directory.*` namespace split).
- `v3.0.0-rc.*`, `v3.0.0` — modern-family major (privsep + JSON-RPC).

Maintenance branches appear only when v3 work would otherwise destabilise v2 maintenance — at that point, `main` carries v3 and `protocol-2.x` (branched off the last v2 tag) carries v2 maintenance commits. Don't pre-create branches.

## Common tasks

### Reading the spec at a specific version

```bash
git checkout v2.1.0
python Tools/gen.py
cat dist/PROTOCOL.md
```

Or browse the source files directly: `cat spec/verbs/screen.capture.json` etc.

For pre-deletion versions:

```bash
git show v2.0.0:PROTOCOL.md          # rendered to stdout (older tags still have root PROTOCOL.md)
```

Tags are write-once by git's nature. Treat archived versions accordingly: errata go into the migration notes for the next version, not into the archived tag.

### Running the conformance suite against an agent

```bash
python tests/conformance/run.py <host> 8765
```

See [`tests/conformance/README.md`](tests/conformance/README.md) for tier-elevation token paths and what's intentionally not covered.

### Generating the rendered spec

```bash
python Tools/gen.py
```

Produces `dist/PROTOCOL.md`, `dist/verbs-<family>.md` per family, and `dist/verbs.json`. `dist/` is gitignored.

### Adding a new verb to the spec

1. Open an issue tagged `enhancement` first. Design discussion happens in comments.
2. Create `spec/verbs/<verb>.json` per [`spec/AUTHORING-CHECKLIST.md`](spec/AUTHORING-CHECKLIST.md). Three stages: skeleton, `windows-modern` family fill, `windows-classic` family fill (or `implemented: false` if unsupported).
3. Add a conformance test in `tests/conformance/test_<namespace>.py`. Gate it with `needs_verb(capabilities, "<verb>")` so older agents skip rather than fail.
4. Run `python tests/check_spec.py` to validate the new file.
5. Run `python Tools/gen.py` and eyeball the `dist/PROTOCOL.md` and `dist/verbs-<family>.md` output.
6. Run the conformance suite locally against the agent that implements it.

PRs missing any of (1)–(4) are incomplete.

### Coordinating a wire-protocol change with the agent repo

1. Spec PR here (steps above). Merge once review settles.
2. Tag the new Protocol release here (`v2.0.1` for errata, `v2.1.0` for additive minors, `v3.0.0` for major).
3. In the agent repo, update the submodule pin: `cd protocol && git fetch && git checkout v2.1.0 && cd .. && git add protocol && git commit -m "Bump protocol to v2.1.0"`.

The agent repo's CI fetches submodules and runs `python Tools/gen.py`; the pin update IS the integration.

## Conventions

- Commit messages: short, bullet-pointed, present-tense. Mirror existing log style.
- Branch off `main`; PRs target `main`.
- Markdown for hand-written docs; JSON for verb specs and family declarations.
- Spec changes always touch `spec/verbs/<verb>.json` + a conformance test. PRs missing either are incomplete.
- Mock-up files in `spec/verbs/` are the contract — do NOT strip fields back to match older PROTOCOL.md content (PROTOCOL.md was deleted; the source files in `spec/` are now authoritative).

## Things not to do

- **Don't edit archived tags.** Pre-deletion tags (`v2.0.0`, `v2.1.0`) still have root `PROTOCOL.md`/`VERBS.md`. Errata go into migration notes for the next version, not retroactively into the tagged spec.
- **Don't pre-split into per-OS verb subdirectories.** Today's `spec/verbs/` is flat. The split into `verbs/<os>/` happens when a second-OS implementation appears, not pre-emptively. See `Documents/Overview/Planning/v3-structural-review.md` (in the Overview repo) for the design rationale.
- **Don't add implementation code.** This repo is specs only. The Python reference client (`wire.py`) and PowerShell ground-truth fixtures (`tests/conformance/fixtures/`) are in support of the conformance suite, not implementations.
- **Don't skip conformance tests when changing verb signatures.** The suite is the contract. A spec change without a matching test is a contract change without verification.
- **Don't commit `dist/`.** It's gitignored; the generator produces it on demand. Committing the generated files defeats the source-of-truth design.

## Where design proposals live

Long-form proposals (RFC-shaped, pre-implementation) live as GitHub issues tagged `enhancement`. Cross-cutting design that spans agent + protocol lives in the Overview repo's `Documents/Overview/Planning/` directory (in the user's local Overview workspace).

If a proposal lands and ships, the contract moves into `spec/verbs/<verb>.json` (or `spec/framing/*.md` for framing-level changes); the rendered `dist/` follows automatically. Issue and Overview-side notes stay as record of what was considered and why.

## Out of scope

- Language-binding generators (the source is JSON; bindings are downstream consumers' work).
- Implementation tutorials (the agent repo's README is the implementation entry point).
- Operational runbooks for deployments (agent repo's `docs/`).
