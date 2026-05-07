# Common verb surface — implementer guide

This directory contains the 54 verbs that form the cross-platform baseline for the Agent Remote Hands Protocol. Any conforming agent on any OS must implement all 54.

## What "common" means

A verb lives here when it has no Windows-specific API dependency — it is implementable on any OS that provides:

- A process model (spawn, kill, wait)
- A filesystem (read, write, stat, watch)
- A screen (capture pixels)
- An input system at the OS message layer (keyboard, mouse)
- A clipboard
- A TCP/WebSocket listener for the wire transport

Verbs that require Windows APIs — UI Automation, the Win32 registry, Win32 power management, or `PostMessage`/`SendMessage` — live in `spec/verbs/windows/` instead.

## Capability boundaries

### Keyboard and mouse input

`input.keyboard.*` and `input.mouse.*` synthesise events at the OS message layer. This means:

- **Reaches:** ordinary GUI applications, web browsers, terminal emulators, most desktop UI.
- **Does not reach:** applications that read raw device input (RawInput on Windows, `/dev/input` on Linux, IOKit HID on macOS) or DirectInput/XInput (games). This is a structural limitation of message-layer synthesis, not an implementation defect. Document it in your family's per-verb description.

### Screen capture

`screen.capture` is implementable on any OS with a screen compositor or framebuffer. The capture engine differs per OS:

| OS | Preferred engine | Fallback |
|---|---|---|
| Windows 10 1803+ | Windows.Graphics.Capture (WGC) | GDI BitBlt |
| Windows 8.1 and earlier | GDI BitBlt | — |
| macOS | ScreenCaptureKit / CGWindowListCreateImage | — |
| Linux (X11) | XGetImage / XShmGetImage | — |
| Linux (Wayland) | wlr-screencopy / xdg-desktop-portal | — |

Declare your engine chain in `x-families.<your-family>.implementations_in_order`.

### `vision.ocr`

`vision.ocr` is listed as common because most modern OSes ship a built-in OCR engine:

| OS | Engine |
|---|---|
| Windows 10 1803+ | Windows.Media.Ocr.OcrEngine |
| macOS 13+ | Vision.VNRecognizeTextRequest |
| Linux | No built-in; tesseract or cloud API required |

If your platform has no built-in OCR engine, declare `"implemented": false` with a `"reason"` in `x-families.<your-family>`. A plugin can supply OCR under a different verb name without shadowing `vision.ocr`.

### `file.download`

`file.download` delegates to a system transfer tool. Common choices:

| OS | Tool chain |
|---|---|
| Windows modern | curl → wget → PowerShell BITS |
| Windows classic | PowerShell BITS → bitsadmin |
| macOS / Linux | curl → wget |

Declare your tool chain in `x-families.<your-family>.implementations_in_order`.

### `process.start` and `process.list`

`process.start` spawns a child process using the OS's native spawn API (`CreateProcessW` on Windows, `posix_spawn` or `fork+exec` on POSIX). `process.list` enumerates processes using the OS's native enumeration API (`EnumProcesses` / `NtQuerySystemInformation` on Windows, `/proc` or `ps` on Linux, `proc_listpids` on macOS).

### `watch.file`, `watch.process`, `watch.window`, `watch.region`

These verbs use OS-native event APIs:

| Verb | Windows | macOS | Linux |
|---|---|---|---|
| `watch.file` | ReadDirectoryChangesW | FSEvents / kqueue | inotify |
| `watch.process` | WaitForSingleObject + process handle | kqueue EVFILT_PROC | netlink proc events |
| `watch.window` | WinEventHook | CGEvent tap / Accessibility notifications | AT-SPI2 / XCB events |
| `watch.region` | WGC / GDI poll | ScreenCaptureKit / CGImage poll | X11 damage extension / poll |

Declare the API used in `x-families.<your-family>.implementations_in_order`.

### `clipboard.get` and `clipboard.set`

Clipboard access uses the OS clipboard API (`OpenClipboard`/`GetClipboardData` on Windows, `NSPasteboard` on macOS, `wl-clipboard` or `xclip` on Linux). Format support varies; document per-family supported formats in `x-families.<your-family>.description`.

### `directory.create`

The `mode` field (POSIX permission bits) is silently ignored on Windows (NTFS uses ACLs). Encode this via the per-family `fields_ignored: ["mode"]` overlay in `x-families.<your-family>`.

## How to add a new OS family

1. **Add a family entry to `spec/families.json`:**

   ```json
   "macos-modern": {
     "description": "macOS 13 (Ventura) and newer. ScreenCaptureKit capture, Vision OCR, Accessibility API for window management.",
     "portability_tier": "common",
     "capabilities": ["screen_capture", "send_input", "ocr", "accessibility_api"],
     "token_file_path": "/Library/Application Support/AgentRemoteHands/token",
     "token_file_acl": "root (full control) + agent run-as account (read). Token rotates on every agent start.",
     "protocol_versions_spoken": ["2.1", "2.2"]
   }
   ```

   Use `"portability_tier": "common"` for non-Windows families.

2. **Add `x-families.<your-family>` blocks to each verb file** in `spec/verbs/common/`. For verbs fully supported on your OS, provide at minimum a `description` and `implementations_in_order`. For verbs not yet supported, use `{"implemented": false, "reason": "<why>"}`.

3. **Skip `spec/verbs/windows/` verbs** unless your OS happens to have an equivalent API. If you do implement a Windows-surface verb, add `x-families.<your-family>` to that verb file too.

4. **Add conformance coverage** for each new verb in `tests/conformance/test_<namespace>.py`. Gate with `needs_verb(capabilities, "<verb>")`.

5. **Validate:** `python tests/check_spec.py` must pass with 0 failures before opening a PR.
