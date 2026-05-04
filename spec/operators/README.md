# Operators markdown

Hand-written markdown for `dist/LLM-OPERATORS.md`. `Tools/gen.py` concatenates these in filename-ordinal order, same model as `spec/framing/`.

## Section provenance

| Filename | Renders as |
|---|---|
| `01-overview.md` | Title + 90/10 framing intro |
| `02-mcp-bridge.md` | The 90% path: use the MCP bridge |
| `03-wire-direct.md` | The 10% path: speaking the wire directly |
| `04-runtime-discovery.md` | What the agent tells you at runtime |
| `05-footguns.md` | Footguns to know about |
| `06-worked-example.md` | A worked example session |
| `07-what-not-to-assume.md` | What not to assume |
| `08-meta.md` | Filing issues + where this document lives |

## Convention

- One file per top-level `## ...` section (the file may also lead with a `# ...` H1 — only `01-overview.md` does this for the document title).
- Filenames use a two-digit ordinal prefix; `Tools/gen.py` concatenates them in sorted-filename order.
- `Tools/gen.py` adds horizontal-rule separators (`---`) between files at render time — don't write them inside.
- Backticked dotted tokens are scanned by `tests/check_spec.py` against the live verb set in `spec/verbs/`. Any `<namespace>.<verb>` token that doesn't resolve fails CI. Use the allowlist in `check_spec.py` for historical references (e.g. v1 names mentioned in migration prose).
