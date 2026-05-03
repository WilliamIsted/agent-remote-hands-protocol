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
| `conflict` | varies | Verb cannot proceed because of in-flight state (e.g. `system.power` `--delay` while one is already pending — detail `{"pending_until_ms":<n>}`) |
| `protocol_mismatch` | `{agent, client}` | Hello specified an incompatible protocol version |
| `auth_required` | — | Reserved for v0.4 SSPI (Protocol 4.0) |
| `auth_invalid` | — | Reserved for v0.4 SSPI (Protocol 4.0) |

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

### 5.3 Detail JSON

When present, detail is UTF-8 JSON. Agents SHOULD always include detail for codes that benefit from diagnostic context (`tier_required`, `uipi_blocked`, `target_gone`, `timeout`, `lock_held`). Detail MAY include a `message` field with a human-readable explanation; clients SHOULD treat the code as the authoritative signal and the message as informational.
