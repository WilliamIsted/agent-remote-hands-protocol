# Changelog

Per-release notes for the Agent Remote Hands wire protocol. The detailed
release notes for each spec version live in `dist/PROTOCOL.md` §12.5 (run
`python Tools/gen.py` to render) — this file is a brief index pointing at
them.

Versioning is per-family-branched (see `dist/PROTOCOL.md` §12 and
[`CLAUDE.md`](CLAUDE.md)). The leading "v" tag form (`v2.1.0`, `v2.0.0`, …)
matches the spec version embedded in the document frontmatter and reported
by `system.info.protocol`.

## Unreleased

- v2.1 working tree: CRUDX tier ladder, clipboard rename, directory
  namespace split, directory primitives, source-of-truth `spec/` tree.
  Not yet tagged — pending build verification of the agent.

## v2.0.0

- First ratified release of the Protocol 2.0 spec.
- Three-tier model: `observe` < `drive` < `power`.
- Verb namespaces: connection, system, screen, window, input, element,
  file, process, registry, clipboard, watch.

For older history, see git log.
