## 12. Versioning policy

### 12.1 Major version

The protocol major version (currently `2`) appears in:

- `system.info.agent_protocol`
- mDNS TXT record `protocol=`
- The `connection.hello` `client_version` positional argument (and the agent echoes its negotiated version back in the response body's `agent_protocol` field)

Major version changes when the wire format, framing rules, or core semantics break compatibility. Clients MUST refuse to operate against an agent whose major version differs from the version they were built against.

### 12.2 Minor version

Minor versions add verbs, capability flags, or error codes without breaking existing clients. Clients SHOULD ignore unrecognised fields in `system.info`, unrecognised verbs in `system.capabilities`, and unrecognised error codes (treating them as opaque strings).

### 12.3 Conformance

An agent claims conformance to a protocol version by:

1. Returning that version string from `system.info.agent_protocol`.
2. Implementing every verb advertised in `system.capabilities` per this spec.
3. Passing the conformance suite for that version.

The conformance suite under `tests/conformance/` is the executable contract.

### 12.4 Capability advertisement

Verbs not implemented on a particular target MUST be omitted from `system.capabilities`. Clients MUST NOT issue verbs absent from the capabilities map; agents MAY return `ERR not_supported` if they do.

### 12.5 Release notes

#### 2.1.0 — CRUDX tier vocabulary; namespace consolidation; v1.0.0 milestone closure

Wire-breaking. No alias period. Cumulative summary across rc.1 → rc.2 → rc.3.

- **Tier rename.** The three tiers `observe` / `drive` / `power` become five: `read` < `create` < `update` < `delete` < `extra_risky`, ordered as a strict ladder (holding a higher tier subsumes every lower tier). The new vocabulary mirrors the CRUDX letter on each verb (§7).
- **Argument quoting (additive).** §1.2.5 defines a double-quote-grouping grammar so args containing spaces (e.g. `"C:\Program Files\App"`) are now representable on the header line. Backward-compatible: any token without spaces or quotes parses identically under v2.0 and v2.1. Embedded `"` is not representable; use the length-prefixed payload form when raw bytes are needed.
- **`clipboard` rename.** `clipboard.read` → `clipboard.get`, `clipboard.write` → `clipboard.set` (§4.10).
- **Directory namespace split (rc.2).** Directory-only verbs leave the `file.*` namespace and become `directory.*`: `file.list` → `directory.list`, `file.mkdir` → `directory.create`, plus new directory primitives (`directory.stat`, `directory.exists`, `directory.rename`, `directory.delete`). Polymorphic verbs that operate on either files or directories stay in `file.*`. `directory.remove` → `directory.delete` later in the same cut.
- **`file.*` create/update split (rc.2).** `file.write` is narrowed to U-only (existing file required); a new `file.create` verb takes the C-tier role. The pre-rc.2 `create_only: true` flag is gone — choose the verb whose semantic matches the intent.
- **`system.power.*` re-namespace (rc.2).** All power-control verbs move into a sub-namespace: `system.shutdown` → `system.power.shutdown`, `system.reboot` → `system.power.reboot`, `system.logoff` → `system.power.logoff`, `system.hibernate` → `system.power.hibernate`, `system.sleep` → `system.power.sleep`, `system.lock` → `system.power.lock`, `system.shutdown_blockers` → `system.power.blockers`, plus the new `system.power.cancel` (U-tier; cancels a pending in-process delayed shutdown).
- **`registry.*` resource-first restructure (rc.2).** Three monolithic verbs (`registry.read` / `registry.write` / `registry.delete`) are replaced by six resource-first verbs: `registry.value.{read, create, update, delete}` for individual values, `registry.key.{read, delete}` for whole keys. The pre-rc.2 `registry.wait` synchronous wait is consolidated into `watch.registry --until-change`.
- **`input.*` mouse/keyboard split (rc.3).** The flat `input.*` namespace splits into three: top-level `input.*` (`input.position`, `input.send_message`, `input.post_message`); `input.mouse.*` (`click`, `move`, `scroll`, `press`, `release`, `drag`); `input.keyboard.*` (`key`, `type`, `key_down`, `key_up`). The renames are mechanical — `input.click` → `input.mouse.click`, `input.key` → `input.keyboard.key`, etc.
- **v1.0.0 milestone closure (rc.3).** Six new verbs land closing the last v1-parity gaps: `input.position` (cursor query), `input.mouse.press` / `release` (indefinite hold), `input.mouse.drag` (atomic press-move-release), `input.keyboard.key_down` / `key_up` (indefinite key hold).
- **Per-verb tier annotations.** §4 now uses CRUDX shorthand letters (R / C / U / D / X) instead of the previous O / D / P. Each verb carries the required tier inferred from its CRUDX classification.
- **No compatibility shim.** Agents on v2.1 reject the v2.0 tier names and verb names with `ERR invalid_args` (tier names) or `ERR not_supported` (verb names). Clients still on the v2.0 vocabulary should pin to a `v2.0.x` release of the spec/agent. The full list of superseded names is enumerated in [`spec/reserved-names.json`](../reserved-names.json) and enforced by `tests/check_spec.py`.
- **Migration.** Tier raises: `drive` → `update`, `power` → `extra_risky`. Verb migrations: `clipboard.read`/`write` → `clipboard.get`/`set`; `file.list` → `directory.list`; `file.mkdir` → `directory.create`; `directory.remove` → `directory.delete`; `system.shutdown` etc. → `system.power.shutdown` etc.; `registry.read` (whole-key) → `registry.key.read`; `registry.read --value` → `registry.value.read`; `registry.write` → `registry.value.create` or `registry.value.update`; `registry.delete --value` → `registry.value.delete`; `registry.delete` (whole-key) → `registry.key.delete`; `registry.wait` → `watch.registry --until-change`; `input.click` → `input.mouse.click`; `input.move` → `input.mouse.move`; `input.scroll` → `input.mouse.scroll`; `input.key` → `input.keyboard.key`; `input.type` → `input.keyboard.type`. Existing `file.write` callers that were creating new files move to `file.create`.

**Native OCR (added during the v2.1.0 rc cycle):**

- **New verb:** `vision.ocr` extracts text and per-line bounding boxes from a region / window / monitor / image file / supplied buffer. Five-way mutually-exclusive input model (`region` / `window` / `monitor` / `path` / `bytes`). Native on `windows-modern` via `Windows.Media.Ocr.OcrEngine`; `implemented: false` on `windows-classic` until a tesseract integration lands. Token-cheap alternative to `screen.capture` for text-heavy UIs (60-250x context reduction).
- **New `vision.*` namespace.** Future caller-side-plugin verbs (`vision.describe`, `vision.find`) will live in the same namespace once the plugin runtime ships; plugins cannot shadow native verb names so `vision.ocr` itself stays native-only.
- **`system.info.capabilities` gains three OCR-related sub-keys** on `windows-modern`: `ocr_languages` (installed BCP-47 tags from `OcrEngine.AvailableRecognizerLanguages`), `ocr_max_dimension` (engine's `MaxImageDimension`), `ocr_input_formats` (supported decoder codecs for `path` / `bytes` inputs). All absent on `windows-classic`.
- **New error code:** `image_too_large` for OCR sources exceeding the engine's `MaxImageDimension`. Detail: `{max_dimension, observed: {w, h}}`. Caller downscales and retries. `unsupported_format` is also reused by `vision.ocr` for unrecognised path-codec sniffs and unsupported `bytes_format` values.
- **Additive only.** Clients that don't know about `vision.ocr` are unaffected; no breaking change vs the rest of v2.1.

#### 2.0.0

First ratified release of the 2.0 spec.

---

## Appendix A: Verb summary

For a scannable per-family verb catalogue, see [`dist/verbs-windows-modern.md`](../verbs-windows-modern.md) and [`dist/verbs-windows-classic.md`](../verbs-windows-classic.md). Both files are generated from `spec/verbs/*.json` and filtered to the verbs each family actually implements.
