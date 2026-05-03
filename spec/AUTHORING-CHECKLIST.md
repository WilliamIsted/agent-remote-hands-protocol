# Verb authoring checklist

Per-verb completion definition. A verb is "done" — and its row in [`AUTHORING-PROGRESS.md`](AUTHORING-PROGRESS.md) flips to ✅ — only when every required item in this checklist has been filled in `spec/verbs/<verb>.json`.

The checklist is organised by the three sequential authoring stages used in the interactive loop:

- **Stage A** — verb skeleton (wire-shape, family-agnostic).
- **Stage B** — `windows-modern` family fill.
- **Stage C** — `windows-classic` family fill.

Each stage is locked with the user before the next begins.

## Stage A — Verb skeleton

Required:

- `name` — namespaced, dotted, lowercase (e.g. `screen.capture`, `element.find_invoke`).
- `strict: true` — unless the verb genuinely needs a JSON Schema feature outside the strict-tool subset (recursive `$ref: "#"`, complex regex, etc.). If `strict: false`, document why in `spec/narrative/<verb>.md` and reference it via `x-rationale-path`.
- `description` — 1–2 sentences. Action-focused. Tuned for an LLM reading at tool-selection time; longer prose belongs under `x-families.<f>.description` or in narrative.
- `input_schema` — `type: object`, `additionalProperties: false`. Every property typed; enums populated where a closed set applies. Use `$ref` to in-file `$defs` for repeated types like `Bounds`.
- `x-crudx` — single letter `C` / `R` / `U` / `D` / `X`. Match the existing usage convention (see dist/PROTOCOL.md §3 / §7 for the tier model these letters feed).
- `x-since` — wire-protocol version this verb first landed on `main` (e.g. `"2.0"`, `"2.1"`).
- `x-namespace` — the namespace prefix as a string (e.g. `"screen"`).
- `x-output-schema` — JSON-schema description of the response payload. Even when the response is a simple string, declare it.
- `x-errors` — array of `ERR <code>` codes the verb may return. Cross-check against dist/PROTOCOL.md §5.
- `x-implementations` — global registry of every backend the verb could plausibly use across families (tools, native APIs, fallbacks). Required on every verb. For single-backend verbs the array has one entry; uniformity is the point. Each entry: `{ "name", "detect": { ... }, "available_on": [ ... ], "description" }`.

Conditional (Stage A):

- `x-mutually-exclusive` — array of property names that can't co-occur. Required when applicable (e.g. `["region", "window", "monitor"]` on `screen.capture`).
- `$defs` — for in-file type reuse (`Bounds`, `WindowHandle`, etc.). Required when the same shape appears in multiple properties.
- `x-rationale-path` — pointer to `spec/narrative/<verb>.md`. Required when the verb has long-form rationale, migration notes, worked examples, performance notes, or edge-case prose worth preserving outside the schema. Optional otherwise. When present, the narrative file must exist.

## Stage B — `windows-modern` family fill

Required (under `x-families.windows-modern`):

- `description` — 1–4 sentences of behavioural detail. Which API, which version cliff, which permission gate. Reads like the per-family subsection of the rendered PROTOCOL.md.
- `implementations_in_order` — ordered array of backend names from preferred to last-ditch. Each name must appear in Stage A's `x-implementations`. Filtered to entries whose `available_on` includes `windows-modern`.

Conditional (Stage B):

- `install_hint` — required when any entry in the chain depends on user-installable tooling. Single curated prose string; spec author picks the most-useful recommendation.
- `fallback_behavior` — optional; default `"error_no_implementation"`. Set explicitly when the desired exhausted-chain behaviour is something else (`"error_unsupported"`, `"degrade_silent"`, etc.).
- Field-availability overlays:
  - `format_supported` — per-family subset of an enum value.
  - `fields_ignored` — fields the family silently no-ops.
  - `fields_rejected` — fields the family returns `ERR unsupported_field` for.
  - Any other family-specific behavioural metadata referenced by Option 13 subsection E.

If the verb fundamentally cannot work on `windows-modern` (rare — typically an artifact of the `windows-classic` fill instead): use `{ "implemented": false, "reason": "..." }` and skip the rest.

## Stage C — `windows-classic` family fill

Same shape as Stage B, but for `x-families.windows-classic`.

Required when implemented:

- `description` — same 1–4 sentence behavioural prose, classic-stack edition.
- `implementations_in_order` — ordered array; classic-stack backends only (GDI BitBlt instead of WGC, mouse_event/keybd_event instead of SendInput, no UI Automation, narrower API surface).

Conditional:

- `install_hint`, `fallback_behavior`, field-availability overlays — same rules as Stage B.

For verbs that fundamentally cannot work on the classic stack (UIA-dependent verbs, WGC-only verbs, modern-only OS APIs): use `{ "implemented": false, "reason": "..." }` instead of a populated description / chain. The `reason` must be a one-line citation of the missing capability ("requires UI Automation; classic stack predates UIA"; "WGC only; classic GDI cannot capture composited DWM surfaces"; etc.). Empty `reason` strings are a checklist failure.

## Wrap-up (after Stage C is locked)

Mechanical, no design decisions:

1. Write `spec/verbs/<verb>.json` to disk in one shot.
2. (If Stage A flagged narrative needed) Write `spec/narrative/<verb>.md`.
3. Run `python tests/check_spec.py` — verify the new file passes the existing CI validator.
4. Run `python Tools/gen.py` — regenerates `dist/PROTOCOL.md`, `dist/<family>/VERBS.md` per family, and `dist/verbs.json`. Eyeball the rendered §4 section for the verb in `dist/PROTOCOL.md`.
5. If a conformance test exists for this verb, run `python -m pytest tests/conformance/test_<namespace>.py -k <verb>` against a running agent. Skipped tests are fine; failures are not.
6. Flip the verb's row in [`AUTHORING-PROGRESS.md`](AUTHORING-PROGRESS.md) from 🟨 to ✅.

## Notes on `x-implementations` uniformity

`x-implementations` is required on every verb, not just verbs with multiple competing backends. For verbs whose backend story is "there is one Windows API for this and no fallback exists" (e.g. `system.lock` is `LockWorkStation` and that's it), the array still has one entry. The uniformity matters because:

- Renderers, validators, and consuming MCP bridges can rely on the field always being present.
- The "default tool" is always discoverable in the same place — never hidden inside per-family description prose.
- Adding a fallback later (someone discovers a workaround for a Windows version cliff) is an array-append, not a schema migration.
