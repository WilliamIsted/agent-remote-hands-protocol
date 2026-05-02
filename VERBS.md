# Verb catalogue

A scannable conceptual index of every verb the protocol defines. One line per verb, organised by namespace. Read this when you need to know *what verbs exist and what they do*; read [`PROTOCOL.md`](PROTOCOL.md) when you need full signatures, error codes, or framing details; read [`LLM-OPERATORS.md`](LLM-OPERATORS.md) when you're an LLM driving an agent.

Tier shorthand: **O** = observe, **D** = drive, **P** = power, **—** = lifecycle (any tier).

Format per line:

```
`verb.name` (tier): One-line purpose. Flags: --flag (purpose), --flag (purpose).
```

Verbs without optional flags omit the `Flags:` clause. Mandatory positional arguments are described in the purpose, not as flags.

Today's verb namespace is Windows-flavoured; some namespaces are intrinsically Windows-shaped (HWND, UIA, registry) and tagged inline as *(Windows-specific)*. Other-OS implementations of agnostic-concept namespaces (`screen`, `input`, `file`, `process`, `clipboard`, `watch`, parts of `system`) are admitted by the protocol — see [`PROTOCOL.md`](PROTOCOL.md) §1 for the platform-extensibility note.

---

## `system.*`

Identity, health, and lifecycle.

- `system.info` (O): Returns agent identity, OS, hostname, integrity level, monitor inventory, image-format support, and capability summary.
- `system.capabilities` (O): Returns the verb→required-tier map exhaustively for the current build.
- `system.health` (O): Liveness check; returns `OK` if the agent is responsive.
- `system.shutdown_blockers` (O): Lists windows that have called `ShutdownBlockReasonCreate`. *(Windows-specific.)*
- `system.lock` (O): Locks the workstation (`LockWorkStation`); `not_supported` on platforms without lock support.
- `system.reboot` (P): Initiates an OS reboot. Flags: --delay (defer N seconds in-process before issuing), --force (override blockers), --reason (Win32 shutdown reason code).
- `system.shutdown` (P): Initiates an OS shutdown. Flags: --delay, --force, --reason (as `system.reboot`).
- `system.logoff` (P): Logs the current user off. Flags: --force.
- `system.hibernate` (P): Hibernates the machine.
- `system.sleep` (P): Suspends the machine to sleep.
- `system.power.cancel` (P): Aborts an in-process delayed shutdown scheduled via `--delay`. Capability-gated.

## `screen.*`

Pixel capture.

- `screen.capture` (O): Captures the desktop, a region, a single window, or a single monitor. Flags: --region (x,y,w,h sub-rectangle), --window (capture a specific HWND), --monitor (Nth physical monitor, 0-based), --format (png / webp / webp:Q / bmp). `--region` / `--window` / `--monitor` are mutually exclusive; if none, captures the entire virtual screen.

## `window.*` *(Windows-specific — uses HWND identifiers)*

Top-level window enumeration and control.

- `window.list` (O): Enumerates top-level windows with bounds, title, owning PID, and monitor index. Flags: --filter (title-pattern restriction), --all (include invisible windows).
- `window.find` (O): Returns the first top-level window whose title matches the given pattern.
- `window.focus` (D): Brings the given HWND to the foreground; surfaces foreground-lock denial as `ERR lock_held`.
- `window.close` (D): Sends `WM_CLOSE` to the given HWND; the window may decline.
- `window.move` (D): Moves and resizes the given HWND to the supplied bounds.
- `window.state` (O): Reports whether the window is minimised / maximised / normal / hidden.

## `input.*`

Synthetic mouse and keyboard input. Cross-IL targets surface as `ERR uipi_blocked`. Keyboard verbs do *not* reach RawInput / DirectInput targets (see [`PROTOCOL.md`](PROTOCOL.md) §4.4).

- `input.click` (D): Synthesises a mouse click at the given screen coordinates. Flags: --button (left / right / middle; default left).
- `input.move` (D): Moves the cursor to the given coordinates without clicking.
- `input.scroll` (D): Sends mouse-wheel notches at the given coordinates (positive = up).
- `input.key` (D): Presses a virtual key by name (`enter`, `F4`, `a`, …). Flags: --modifiers (comma-separated, e.g. `ctrl,shift`).
- `input.type` (D): Types a UTF-8 string from a length-prefixed payload; handles Unicode and quote-escape hazards.
- `input.send_message` (D): Synchronous `SendMessage` escape hatch with HWND, msg, wparam, lparam. *(Windows-specific.)*
- `input.post_message` (D): Non-blocking `PostMessage` peer of `input.send_message`; use when the target's message pump is unresponsive. *(Windows-specific.)*

## `element.*` *(Windows-specific — UIA-based; uses `elt:` identifiers, connection-scoped)*

UI Automation introspection and control.

- `element.list` (O): Enumerates interactable / named elements visible on screen. Flags: --region (restrict enumeration to a sub-rectangle).
- `element.tree` (O): Recursive TreeWalker descent from the given element id, returning depth-tagged children.
- `element.at` (O): Hit-tests at screen coordinates and returns the element under the cursor.
- `element.find` (O): Finds the first element matching `<role> <name-pattern>`; distinguishes `not_found` from `uia_blind` (cross-IL barrier).
- `element.wait` (O): Polling form of `element.find` with a deadline; capability-gated.
- `element.find_invoke` (D): Compound `element.find` + `element.invoke` in one round-trip.
- `element.at_invoke` (D): Compound `element.at` + `element.invoke` in one round-trip.
- `element.invoke` (D): Invokes the InvokePattern on the given element id.
- `element.toggle` (D): Toggles a TogglePattern element; returns the new state (on / off / indeterminate).
- `element.expand` (D): Expands an ExpandCollapsePattern element; returns the new state.
- `element.collapse` (D): Collapses an ExpandCollapsePattern element; returns the new state.
- `element.focus` (D): Sets keyboard focus on the given element id.
- `element.text` (O): Reads text from the given element via TextPattern (preferred) or ValuePattern (fallback).
- `element.set_text` (D): Writes text to the given element from a length-prefixed payload; surfaces `readonly` / `not_supported_by_target` distinctly.

## `file.*`

Filesystem operations. UTF-8 paths.

- `file.read` (O): Reads an entire file and returns its bytes as the response payload.
- `file.write` (D): Writes a length-prefixed payload as the entire file contents, truncating any existing file.
- `file.write_at` (D): Random-access write at a given byte offset; the chunked-upload primitive used by the MCP bridge for large files. Flags: --truncate (only meaningful at offset 0; clears the file first).
- `file.list` (O): Lists directory entries with type, size, and mtime.
- `file.stat` (O): Single-entry equivalent of `file.list` for a specific path.
- `file.delete` (P): Deletes a file or empty directory.
- `file.exists` (O): Reports whether a path exists and, if so, its type.
- `file.wait` (O): Resolves when a path matching the glob appears, or returns `ERR timeout`.
- `file.mkdir` (D): Creates a single directory level; the parent must already exist.
- `file.rename` (D): Moves or renames a file or directory.

## `process.*`

Process management.

- `process.list` (O): Enumerates running processes with pid, image path, and ppid. Flags: --filter (image-name pattern).
- `process.start` (D): Spawns a process via `CreateProcess`, returning its pid. Flags: --stdin (length-prefixed bytes piped to the child's stdin).
- `process.shell` (D): Spawns via `ShellExecuteEx`; handles paths with spaces / unicode without shell-escape hazards. Flags: --args (parameter string passed verbatim), --verb (non-default ShellExecute verb, e.g. `runas`, `print`, `edit`). *(Windows-specific.)*
- `process.kill` (P): Terminates the given pid (`TerminateProcess`).
- `process.wait` (O): Waits for the given pid to exit, with a deadline; returns the exit code or `ERR timeout`.

## `registry.*` *(Windows-specific — uses `HKLM\…` / `HKCU\…` paths)*

Windows registry operations.

- `registry.read` (O): Reads a registry key or single value. Flags: --value (read one named value instead of the whole key).
- `registry.write` (D): Writes a typed registry value (REG_SZ, REG_DWORD, etc.) at the given key+name.
- `registry.delete` (P): Deletes a value or the whole key. Flags: --value (delete one named value instead of the whole key).
- `registry.wait` (O): Waits for a key to change (`RegNotifyChangeKeyValue`), with a deadline; returns `ERR timeout` on expiry.

## `clipboard.*`

Clipboard text I/O.

- `clipboard.read` (O): Reads the clipboard's text contents as UTF-8; empty payload if no text.
- `clipboard.write` (D): Replaces the clipboard's text contents with a length-prefixed UTF-8 payload.

## `watch.*`

Subscription-based observation. Each verb returns a `subscription_id`; events arrive as out-of-band `EVENT` frames until cancelled or auto-cancelled (see [`PROTOCOL.md`](PROTOCOL.md) §6).

- `watch.region` (O): Streams image frames of a screen region. Flags: --interval (poll period in ms), --until-change (auto-cancel after the first changed frame).
- `watch.process` (O): Emits one event when the given pid exits, then auto-cancels.
- `watch.window` (O): Emits events on window appearance / disappearance. Flags: --title-prefix (only fire for windows whose title starts with the pattern).
- `watch.element` (O): Emits one event when the given element id is invalidated, then auto-cancels.
- `watch.file` (O): Emits events on file create / modify / delete matching a glob (`ReadDirectoryChangesW`-based).
- `watch.registry` (O): Emits events on registry-key changes (`RegNotifyChangeKeyValue`-based). *(Windows-specific.)*
- `watch.cancel` (O): Ends a subscription by id; idempotent on already-cancelled ids.

## `connection.*`

Lifecycle and tier negotiation. See [`PROTOCOL.md`](PROTOCOL.md) §2 for the state-machine details.

- `connection.hello` (—): First verb after connect; takes client name and protocol version; gates further verbs.
- `connection.tier_raise` (—): Raises the connection to a higher tier (drive / power); requires a token read from the agent's token file.
- `connection.tier_drop` (—): Voluntarily drops the connection to a lower tier; requires no token.
- `connection.reset` (—): Flushes wire-format state; the recovery primitive after `ERR wire_desync`.
- `connection.close` (—): Drains pending EVENT frames and closes the connection cleanly.
