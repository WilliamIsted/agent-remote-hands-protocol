# Windows-specific verb surface

This directory contains the 33 verbs that depend on Windows-specific APIs. They are implemented by `windows-modern` and `windows-classic` families where the underlying API is available.

## Why these verbs are Windows-only

| Namespace | Verbs | API |
|---|---|---|
| `element.*` (14 verbs) | `element.at`, `element.at_invoke`, `element.collapse`, `element.expand`, `element.find`, `element.find_invoke`, `element.focus`, `element.invoke`, `element.list`, `element.set_text`, `element.text`, `element.toggle`, `element.tree`, `element.wait` | UI Automation (IUIAutomation COM interface, Vista+). No cross-platform equivalent at the protocol level. |
| `input.*` (2 verbs) | `input.post_message`, `input.send_message` | Win32 message queue (PostMessage / SendMessage). OS-specific IPC mechanism. |
| `process.*` (1 verb) | `process.shell` | ShellExecuteEx — opens files and URLs using the registered shell verb handler. |
| `registry.*` (6 verbs) | `registry.key.delete`, `registry.key.read`, `registry.value.create`, `registry.value.delete`, `registry.value.read`, `registry.value.update` | Windows registry. No cross-platform equivalent. |
| `system.power.*` (8 verbs) | `system.power.blockers`, `system.power.cancel`, `system.power.hibernate`, `system.power.lock`, `system.power.logoff`, `system.power.reboot`, `system.power.shutdown`, `system.power.sleep` | ExitWindowsEx, InitiateSystemShutdownExW, SetSuspendState, ShutdownBlockReasonQuery — Windows-only power management API. |
| `watch.*` (2 verbs) | `watch.element`, `watch.registry` | UI Automation event hooks and registry change notifications (RegNotifyChangeKeyValue). |

## Declaring non-support in a non-Windows family

A non-Windows family that does not implement a verb in this directory declares:

```json
"x-families": {
  "your-family": {
    "implemented": false,
    "reason": "Requires UI Automation (Windows-only)."
  }
}
```

The `check_spec.py` validator accepts `implemented: false` entries without requiring an `implementations_in_order` chain.

## Future additions

New Windows-specific verbs go here. The current open proposal is `element.range_value` (issue [#95](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/95)), which exposes the UIA `IRangeValueProvider` pattern for sliders and progress bars.
