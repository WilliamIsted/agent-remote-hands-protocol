## 4. Cross-platform baseline

The verb surface is split into two directories that reflect portability intent:

| Directory | Count | Requirement |
|---|---|---|
| `spec/verbs/common/` | 55 verbs | Any conforming agent on any OS MUST implement all verbs in this directory |
| `spec/verbs/windows/` | 33 verbs | Windows agents additionally implement these; non-Windows agents declare `implemented: false` |

### 4.1 Common surface (55 verbs)

These verbs carry no Windows-specific API dependency. Any OS with a process model, filesystem, screen, and input system can implement all of them.

| Namespace | Verbs |
|---|---|
| `clipboard.*` | `clipboard.get`, `clipboard.set` |
| `connection.*` | `connection.close`, `connection.hello`, `connection.reset`, `connection.tier_drop`, `connection.tier_raise` |
| `directory.*` | `directory.create`, `directory.delete`, `directory.exists`, `directory.list`, `directory.rename`, `directory.stat` |
| `file.*` | `file.create`, `file.delete`, `file.download`, `file.exists`, `file.read`, `file.rename`, `file.stat`, `file.wait`, `file.write`, `file.write_at` |
| `input.*` | `input.position` |
| `input.keyboard.*` | `input.keyboard.key`, `input.keyboard.key_down`, `input.keyboard.key_up`, `input.keyboard.type` |
| `input.mouse.*` | `input.mouse.click`, `input.mouse.drag`, `input.mouse.move`, `input.mouse.press`, `input.mouse.release`, `input.mouse.scroll` |
| `process.*` | `process.kill`, `process.list`, `process.start`, `process.wait` |
| `screen.*` | `screen.capture` |
| `system.*` | `system.capabilities`, `system.health`, `system.info`, `system.verbs` |
| `vision.*` | `vision.ocr` |
| `watch.*` | `watch.cancel`, `watch.file`, `watch.process`, `watch.region`, `watch.window` |
| `window.*` | `window.close`, `window.find`, `window.focus`, `window.list`, `window.move`, `window.state` |

Keyboard and mouse input verbs carry a portability boundary note: synthetic events reach the OS message layer only. RawInput and DirectInput targets (games, certain graphics applications) do not receive synthesised events regardless of OS. This limitation applies uniformly across all implementations and is documented in `spec/verbs/common/README.md`.

### 4.2 Windows-specific surface (33 verbs)

These verbs depend on Windows-specific APIs and are not expected to be implemented by non-Windows families. A non-Windows family declares non-support via `"implemented": false` in the verb's `x-families` block.

| Namespace | Verbs | API dependency |
|---|---|---|
| `element.*` | `element.at`, `element.at_invoke`, `element.collapse`, `element.expand`, `element.find`, `element.find_invoke`, `element.focus`, `element.invoke`, `element.list`, `element.set_text`, `element.text`, `element.toggle`, `element.tree`, `element.wait` | UI Automation (Vista+) |
| `input.*` | `input.post_message`, `input.send_message` | Win32 message queue |
| `process.*` | `process.shell` | ShellExecuteEx |
| `registry.*` | `registry.key.delete`, `registry.key.read`, `registry.value.create`, `registry.value.delete`, `registry.value.read`, `registry.value.update` | Windows registry |
| `system.power.*` | `system.power.blockers`, `system.power.cancel`, `system.power.hibernate`, `system.power.lock`, `system.power.logoff`, `system.power.reboot`, `system.power.shutdown`, `system.power.sleep` | ExitWindowsEx, SetSuspendState, ShutdownBlockReasonQuery |
| `watch.*` | `watch.element`, `watch.registry` | UI Automation, Windows registry |

### 4.3 `portability_tier` in `families.json`

Each family declaration carries a `portability_tier` field:

- `"windows"` — the family implements `spec/verbs/windows/` in addition to `spec/verbs/common/`.
- `"common"` — the family implements only `spec/verbs/common/`. This is the value future macOS or Linux families will use.

### 4.4 For implementers

See [`spec/verbs/common/README.md`](../verbs/common/README.md) for a step-by-step guide to implementing the common surface on a new OS, including per-verb portability notes and instructions for registering a new family in `spec/families.json`.
