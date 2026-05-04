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

- Native OCR via `vision.ocr` (Windows.Media.Ocr.OcrEngine on
  windows-modern; `implemented: false` on windows-classic). Five-way
  mutually-exclusive input selector covering live capture
  (`region`/`window`/`monitor`) and static image sources (`path`/`bytes`).
  Per-line bounding boxes with optional per-word granularity; `language`
  hint defaulting to the OS user-profile language; `coordinate_space`
  enum disambiguates screen vs image bbox coordinate systems.
- `system.info.capabilities` gains three OCR-related sub-keys on
  windows-modern: `ocr_languages`, `ocr_max_dimension`,
  `ocr_input_formats`. All absent on windows-classic.
- New error code: `image_too_large` (OCR sources exceeding the engine's
  `MaxImageDimension`); `unsupported_format` reused for codec-mismatch
  on `vision.ocr` path/bytes inputs.
- New `vision.*` namespace; future caller-side-plugin verbs
  (`vision.describe`, `vision.find`) will live alongside once the
  plugin runtime ships.

## v2.1.0-rc.2 — 2026-05-04

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

## v2.0.0

- First ratified release of the Protocol 2.0 spec.
- Three-tier model: `observe` < `drive` < `power` (superseded in v2.1 by
  the CRUDX ladder).
- Verb namespaces: connection, system, screen, window, input, element,
  file, process, registry, clipboard, watch.

For older history, see git log.
