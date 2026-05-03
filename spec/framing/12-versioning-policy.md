## 12. Versioning policy

### 12.1 Major version

The protocol major version (currently `2`) appears in:

- `system.info.protocol`
- mDNS TXT record `protocol=`
- The `connection.hello` second argument

Major version changes when the wire format, framing rules, or core semantics break compatibility. Clients MUST refuse to operate against an agent whose major version differs from the version they were built against.

### 12.2 Minor version

Minor versions add verbs, capability flags, or error codes without breaking existing clients. Clients SHOULD ignore unrecognised fields in `system.info`, unrecognised verbs in `system.capabilities`, and unrecognised error codes (treating them as opaque strings).

### 12.3 Conformance

An agent claims conformance to a protocol version by:

1. Returning that version string from `system.info.protocol`.
2. Implementing every verb advertised in `system.capabilities` per this spec.
3. Passing the conformance suite for that version.

The conformance suite under `tests/conformance/` is the executable contract.

### 12.4 Capability advertisement

Verbs not implemented on a particular target MUST be omitted from `system.capabilities`. Clients MUST NOT issue verbs absent from the capabilities map; agents MAY return `ERR not_supported` if they do.

### 12.5 Release notes

#### 2.1.0 — CRUDX tier vocabulary; `clipboard` rename

Wire-breaking. No alias period.

- **Tier rename.** The three tiers `observe` / `drive` / `power` become five: `read` < `create` < `update` < `delete` < `extra_risky`, ordered as a strict ladder (holding a higher tier subsumes every lower tier). The new vocabulary mirrors the CRUDX letter on each verb (§7).
- **Argument quoting (additive).** §1.2.5 defines a double-quote-grouping grammar so args containing spaces (e.g. `"C:\Program Files\App"`) are now representable on the header line. Backward-compatible: any token without spaces or quotes parses identically under v2.0 and v2.1. Embedded `"` is not representable; use the length-prefixed payload form when raw bytes are needed.
- **Verb rename.** `clipboard.read` → `clipboard.get`, `clipboard.write` → `clipboard.set` (§4.10). Aligns the wire with the source-of-truth spec under [`spec/verbs/`](spec/verbs/).
- **Directory namespace split.** Directory-only verbs leave the `file.*` namespace and become `directory.*`: `file.list` → `directory.list`, `file.mkdir` → `directory.create` (§4.7). Polymorphic verbs that operate on either files or directories (`file.delete`, `file.stat`, `file.exists`, `file.wait`, `file.rename`) stay in `file.*`.
- **Per-verb tier annotations.** §4 now uses CRUDX shorthand letters (R / C / U / D / X) instead of the previous O / D / P. Each verb carries the required tier inferred from its CRUDX classification.
- **No compatibility shim.** Agents on v2.1 reject the v2.0 tier names and verb names with `ERR invalid_args` (tier names) or `ERR not_supported` (verb names). Clients still on the v2.0 vocabulary should pin to a `v2.0.x` release of the spec/agent.
- **Migration.** Existing clients raising to `drive` should now raise to `update`. Existing clients raising to `power` should now raise to `extra_risky`. `clipboard.read`/`write` callers update verb names. `file.list` callers move to `directory.list`; `file.mkdir` callers move to `directory.create`.

#### 2.0.0

First ratified release of the 2.0 spec.

---

## Appendix A: Verb summary

For a scannable per-family verb catalogue, see [`dist/windows-modern/VERBS.md`](../windows-modern/VERBS.md) and [`dist/windows-classic/VERBS.md`](../windows-classic/VERBS.md). Both files are generated from `spec/verbs/*.json` and filtered to the verbs each family actually implements.
