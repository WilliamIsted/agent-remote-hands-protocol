# Framing markdown

Hand-written markdown for the non-verb sections of `dist/PROTOCOL.md`. `Tools/gen.py` concatenates these in filename-ordinal order, splicing the generated §4 (verbs) between `03-*.md` and `05-*.md`.

## Section provenance

| Filename | Renders as |
|---|---|
| `00-intro.md` | Front matter — title, version banner, ToC-equivalent intro |
| `01-wire.md` | §1 Wire format |
| `02-lifecycle.md` | §2 Connection lifecycle |
| `03-capability-discovery.md` | §3 Capability discovery |
| _(gap at 04)_ | §4 Verbs by namespace — **generated** from `spec/verbs/*.json` |
| `05-errors.md` | §5 Error codes |
| `06-subscriptions.md` | §6 Subscriptions and EVENT frames |
| `07-tier-model.md` | §7 Tier model |
| `08-elevation.md` | §8 Elevation and integrity levels |
| `09-discovery.md` | §9 Discovery |
| `10-behaviour-notes.md` | §10 Behaviour notes |
| `11-worked-examples.md` | §11 Worked examples |
| `12-versioning-policy.md` | §12 Versioning policy |

The `04-` ordinal is intentionally absent — `Tools/gen.py` knows to splice the generated verb sections at that position.

## Convention

- One file per top-level `## N. Title` section. Filenames use the section number as a two-digit prefix.
- Each file's content starts at the section's `## N. ...` heading and runs to (but excluding) the next section.
- No horizontal-rule separators inside the framing files — `Tools/gen.py` adds the `---` between sections at render time.
