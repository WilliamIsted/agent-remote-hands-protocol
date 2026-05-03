# Source-of-truth verb definitions

One JSON file per verb under [`verbs/`](verbs/), each a valid Anthropic strict-tool definition with `x-*` extensions for protocol metadata (CRUDX, families, errors, output schema, fallback chains). [`families.json`](families.json) declares the supported OS families.

These files are the canonical source: an MCP bridge or Anthropic-API caller can register them directly via `tools = [json.load(open(f)) for f in verb_files]` and get schema-validated tool inputs end-to-end.

The `x-*` extensions are stripped at the API boundary — see the design doc for the recommended `strip_x_extensions` helper.

## Provenance

Authored as part of the Option 13 source-of-truth design. The full design rationale, shape, authoring patterns, and trade-offs live alongside the original mock-up:

`Documents/Overview/Planning/source-of-truth-options/option-13-structured-outputs/README.md`

(in the user's local Overview workspace; not part of this repo).

## Coverage

20 verbs across 9 namespaces. Two OS families: `windows-modern` (Win 10 1803+) and `windows-classic` (NT 4 – 8.1). CRUDX letters R / C / U / D / X all appear at least once. Production has more wire verbs than appear here today; spec coverage extends opportunistically. Other-OS families (macOS, Linux) are not in the production spec — when an agent for one of those targets ships, its family entry lands here at the same time.
