## 5. Error codes

Errors take the form:

```
< ERR <code> [<length>\n<json-detail>]
```

`<code>` is a stable identifier suitable for client-side switching. `<json-detail>`, when present, carries diagnostic context.

### 5.1 Verb-agnostic codes

| Code | Detail fields | Meaning |
|---|---|---|
| `tier_required` | `{required, current}` | Current tier insufficient for this verb |
| `not_supported` | `{verb, reason?}` | Verb / capability not advertised on this agent |
| `invalid_args` | `{message}` | Malformed verb call |
| `invalid_state` | `{required}` | Verb not valid in current connection state (e.g. pre-hello) |
| `wire_desync` | — | Caller payload corrupt; recoverable via `connection.reset` |
| `timeout` | `{deadline}` | `*.wait` or streaming verb expired |
| `busy` | `{max}` | Too many concurrent connections |
| `conflict` | varies | Verb cannot proceed because of in-flight state (e.g. `system.power.shutdown` `--delay-seconds` while one is already pending — detail `{"pending_until_ms":<n>}`) |
| `protocol_mismatch` | `{agent, client}` | Hello specified an incompatible protocol version |
| `auth_required` | — | Reserved for v0.4 SSPI (Protocol 4.0) |
| `auth_invalid` | — | Authentication token rejected. Used today by `connection.tier_raise` when the supplied tier-elevation token is wrong; reserved for v0.4 SSPI in addition. |

### 5.2 Domain-specific codes

| Code | Detail fields | Meaning |
|---|---|---|
| `target_gone` | `{handle, last_known_state?}` | Element / window / process vanished mid-call |
| `uipi_blocked` | `{agent_il, target_il}` | Integrity barrier blocked input |
| `not_found` | — | Search returned nothing, or referenced path / handle does not exist |
| `uia_blind` | — | UIA cannot see across the IL barrier; distinct from `not_found` |
| `lock_held` | `{lock_type, holder?}` | Foreground / clipboard / registry lock denied |
| `readonly` | — | Write to immutable target |
| `not_supported_by_target` | `{pattern?}` | Target element / object lacks the required UIA pattern |
| `insufficient_privilege` | `{missing}` | Token lacks the required Win32 privilege |
| `permission_denied` | `{message?}` | OS-level access denial (filesystem ACL, TCC grant missing, sandbox boundary, etc.). Distinct from `tier_required` (wire-tier gate) and `insufficient_privilege` (Win32 token privilege). |
| `already_exists` | `{message?}` | Target path / handle already exists and the verb refused to overwrite. `directory.create`, `file.download create_only`, `directory.rename` without `--overwrite`. |
| `not_empty` | — | Removing a non-empty directory without `--recursive`. `file.delete`, `directory.remove`. |
| `not_a_directory` | `{message?}` | Path exists but refers to a file when the verb requires a directory (or vice versa). All `directory.*` verbs that resolve an existing path. |
| `cross_device` | `{message?}` | Operation crosses a filesystem boundary and the verb refuses without explicit opt-in. `directory.rename` without `--cross-fs`. |
| `empty` | — | Source has no content to read. `clipboard.get` when the clipboard has no text. |
| `unsupported_format` | `{requested, supported?}` | Verb received a format value the connected agent cannot produce or consume. `screen.capture` when output `format` is outside the family's supported list; `vision.ocr` when an unrecognised codec is sniffed from a `path` input or supplied via `bytes_format`. |
| `image_too_large` | `{max_dimension, observed}` | Image's largest dimension exceeds the OCR engine's `MaxImageDimension`. `vision.ocr` when source pixels would overflow the engine's hard cap. Caller should downscale and retry. |
| `no_handler` | `{message?}` | Shell-execute could not find a registered handler for the requested verb / file association. `process.shell`. |
| `no_implementation_available` | `{tried?}` | The verb's `x-implementations` chain was exhausted on the connected agent (no detect-positive backend). `file.download` when neither curl nor wget nor any platform fallback is present. |
| `policy_blocked` | `{policy?}` | OS / domain group policy refuses the operation. `system.power.shutdown / .reboot / .logoff` when `SeShutdownPrivilege` exists but policy denies. |
| `size_limit_exceeded` | `{limit, observed?}` | Caller-set `max_bytes` exceeded mid-transfer. `file.download`. |
| `transfer_failed` | `{status_code?, message?}` | Transfer aborted by the network or remote server. `file.download` for HTTP errors and connection drops. |
| `user_cancelled` | — | UAC consent prompt or shell verb dialog was dismissed by the user. `process.shell` with `verb: runas`. |

### 5.3 Detail JSON

When present, detail is UTF-8 JSON. Agents SHOULD always include detail for codes that benefit from diagnostic context (`tier_required`, `uipi_blocked`, `target_gone`, `timeout`, `lock_held`). Detail MAY include a `message` field with a human-readable explanation; clients SHOULD treat the code as the authoritative signal and the message as informational.
