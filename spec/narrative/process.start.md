# process.start — long-form rationale

## stdin handling and a future binary-encoding extension

Today, `process.start.stdin` accepts UTF-8 text only. The text is piped to the child's stdin and the pipe is closed after writing. This is sufficient for the dominant case (programs that read text input), but precludes piping arbitrary bytes to children expecting binary input on stdin (e.g. `gzip -d`, `base64 -d`, image processors).

A future extension would add `stdin_encoding: "utf-8" | "binary"` (default `"utf-8"`). Under `binary`, `stdin` is interpreted as base64-encoded bytes and decoded by the agent before piping. This avoids invalidating the strict-tool input shape (the field stays a JSON string) while admitting binary payloads.

Not implemented today; recorded here so the future addition is traceable to the original design intent rather than appearing as a new ad-hoc field.

## process.shell vs process.start

For path-with-spaces, unicode filenames, or the UAC-elevation case (`verb: runas`), prefer `process.shell` — it uses `ShellExecuteEx` which handles those correctly. `process.start` uses `CreateProcessW` directly and is the right choice for the common case where the caller has a precise argv-array.
