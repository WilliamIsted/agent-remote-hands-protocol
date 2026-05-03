# Shared structural shapes

Source-of-truth definitions for shapes that appear inline in multiple `spec/verbs/*.json` files (e.g. `Bounds`, `Point`). The strict-tool subset disallows cross-file `$ref`, so verb files cannot reference these directly — instead, each consuming verb declares the shape inline under `$defs`, and `tests/check_spec.py` validates that the inline copy matches the canonical version here.

## Files

| File | Validation mode | Used by |
|---|---|---|
| `Bounds.json` | **exact** — inline copies must match the canonical schema verbatim including descriptions | `screen.capture` (input region); `system.info`, `window.list`, `window.find`, `window.move`, `element.find`, `element.list`, `element.tree`, `element.wait`, `element.at` (output bounds) |
| `Point.json` | **structure-only** — inline copies must match `type`/`required`/`properties` keys/`additionalProperties`. Description text is per-verb (each verb's `actual_position` carries a slightly different semantic). | `input.click`, `input.move`, `input.scroll` (output `actual_position`) |

## Adding a new shared shape

1. Identify a structural shape that appears in 3+ verb files.
2. Add the canonical definition to `spec/types/<Name>.json` using the format below.
3. Update `tests/check_spec.py` to register the new shape and its validation mode.
4. Update each consuming verb's `$defs` to match the canonical (run `python tests/check_spec.py` to confirm).

## File format

```json
{
  "_doc": "One-line description of the shape and where it's used.",
  "schema": { ... canonical JSON Schema ... },
  "_validation": "exact" | "structure-only"
}
```

`_validation` defaults to `"exact"` if omitted. `"structure-only"` allows per-verb description overrides.

## Why not just `$ref` cross-file?

The strict-tool subset (used for Anthropic API tool definitions) does not support cross-file `$ref`. Each verb file must be self-contained and directly consumable as a tool definition. Inline `$defs` with cross-file validation is the trade-off: source-of-truth lives here, but verb files remain standalone-valid.
