# Changelog

Per-release notes for the Agent Remote Hands wire protocol. The detailed
release notes for each spec version live in `dist/PROTOCOL.md` §12.5 (run
`python Tools/gen.py` to render) — this file is a brief index pointing at
them.

Versioning is per-family-branched (see `dist/PROTOCOL.md` §12 and
[`CLAUDE.md`](CLAUDE.md)). The leading "v" tag form (`v2.1.0`, `v2.0.0`, …)
matches the spec version embedded in the document frontmatter and reported
by `system.info.agent_protocol`.

## Unreleased

- v2.1 working tree: CRUDX tier ladder (`read` < `create` < `update` <
  `delete` < `extra_risky`) replacing v2.0's three-tier model;
  `clipboard.read`/`write` renamed to `clipboard.get`/`set`; new
  `directory.*` namespace split out of `file.*` with full CRUDX-complete
  primitives; `system.*` power verbs re-namespaced to `system.power.*`;
  `registry.*` restructured into resource-first
  `registry.value.{read,create,update,delete}` + `registry.key.{read,delete}`;
  `input.*` split into `input.mouse.*` + `input.keyboard.*` sub-namespaces
  (rc.3); header-line argument quoting (`"path with spaces"`);
  source-of-truth `spec/` tree with `dist/`-rendered artefacts.
  Not yet tagged — pending build verification of the agent.

## v2.0.0

- First ratified release of the Protocol 2.0 spec.
- Three-tier model: `observe` < `drive` < `power` (superseded in v2.1 by
  the CRUDX ladder).
- Verb namespaces: connection, system, screen, window, input, element,
  file, process, registry, clipboard, watch.

For older history, see git log.
