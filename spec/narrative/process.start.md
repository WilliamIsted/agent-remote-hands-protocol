# process.start — long-form rationale

## stdin handling and a future binary-encoding extension

Today, `process.start.stdin` accepts UTF-8 text only. The text is piped to the child's stdin and the pipe is closed after writing. This is sufficient for the dominant case (programs that read text input), but precludes piping arbitrary bytes to children expecting binary input on stdin (e.g. `gzip -d`, `base64 -d`, image processors).

A future extension would add `stdin_encoding: "utf-8" | "binary"` (default `"utf-8"`). Under `binary`, `stdin` is interpreted as base64-encoded bytes and decoded by the agent before piping. This avoids invalidating the strict-tool input shape (the field stays a JSON string) while admitting binary payloads.

Not implemented today; recorded here so the future addition is traceable to the original design intent rather than appearing as a new ad-hoc field.

## process.shell vs process.start

For path-with-spaces, unicode filenames, or the UAC-elevation case (`verb: runas`), prefer `process.shell` — it uses `ShellExecuteEx` which handles those correctly. `process.start` uses `CreateProcessW` directly and is the right choice for the common case where the caller has a precise argv-array.


## Waiting for the first window (wait_for_window_ms)

Most callers that launch a program want to drive its UI next, which needs a window handle. Guessing the title for `watch.window` fails often: Edge's first window title depends on first-run state, and installers add vendor-specific suffixes. `wait_for_window_ms` lets the launch call wait for the new process's own window.

The wait ends on whichever comes first: a matching window, the process exiting, or the timeout. Ending on exit matters for launchers and browsers that hand off to an already-running instance. Running `msedge.exe` while Edge is open starts a short-lived process that passes the URL to the existing one and exits, and the window that appears belongs to the existing process. Without the exit terminator the call would block for the full timeout.

On a timeout or exit the verb still returns `OK` with the pid, because the process did start. The caller may still want to kill or wait on it. `window_timeout: true` tells the two outcomes apart, and `exit_code` is present when the process has already exited.

The window filter matches `window.list`, plus a check that the window has no owner window, so dialogs owned by another window are skipped. An app that shows a splash screen first returns the splash screen.

`process.shell` takes the same argument. When the shell opens the target in an existing handler and no process spawns (`pid: null`), there is nothing to wait for and the argument is ignored.
