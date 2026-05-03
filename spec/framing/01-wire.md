## 1. Wire format

### 1.1 Transport

- TCP, default port `8765` (configurable per agent).
- One agent listens on one port; per-thread connection model.
- No transport encryption today. Treat the wire as cleartext on the LAN.

### 1.2 Framing

Every message — request, response, or event — is a single header line followed by an optional length-prefixed payload.

**Header line:**

```
<directive> <args...>\n
```

The header is ASCII, terminated by `\n`. A leading `\r` immediately before `\n` is tolerated and ignored. Tokens within the header are separated by single spaces; tokens that contain spaces themselves are double-quoted (see §1.2.5). The header MUST NOT exceed 65 535 bytes.

**Payload:**

If the directive's grammar specifies a `<length>` argument (always the final argument when present), exactly `<length>` bytes follow the header line. `<length>` is decimal ASCII. A length of `0` means no payload. Payload bytes are opaque to the framing layer — interpretation depends on the verb.

**Examples:**

| Form | Meaning |
|---|---|
| `system.info\n` | Verb with no args, no payload |
| `OK 0\n` | Success, no payload |
| `OK 312\n{...312 bytes of JSON...}` | Success with 312-byte payload |
| `ERR tier_required 47\n{...47 bytes of JSON...}` | Error with structured detail |
| `EVENT sub:7 142\n{...142 bytes...}` | Async event for subscription `sub:7` |
| `file.write /path/foo.txt 1024\n{...1024 bytes...}` | Verb with payload |

**Response framing is uniform.** Every `OK` and `ERR` response carries a length prefix — `0` for empty bodies, otherwise the byte count of the payload that follows. There is no separate "inline-text" shape: verbs that conceptually return scalars wrap them in JSON (e.g. `process.start` → `{"pid":N}`, not `OK N`). The verb tables in §4 list the JSON shape per OK response in the Notes column. Subscriptions emit `EVENT` frames asynchronously between request/response pairs — see §6.

### 1.2.5 Argument quoting

Tokens are space-separated. A token MAY be enclosed in ASCII double-quote characters (`"`); when it is, all bytes between the opening and closing quote — including spaces, backslashes, and any other byte except `"` itself — are taken literally as the token's value.

Grammar:

- An unquoted token is read until the next space or end-of-line. Backslashes inside an unquoted token are literal (this matters for Windows paths like `C:\Windows\System32`).
- A quoted token starts with `"` and is read up to the next `"`. The opening and closing `"` are stripped from the value. There is no escape mechanism inside quotes — embedded `"` is not representable on the header line. Verbs that need raw byte content with embedded `"` use the length-prefixed payload, not header args.
- An unmatched opening `"` (no closing `"` before end-of-line) is a parse error. The agent returns `ERR invalid_args {"message":"unmatched quote in header"}`.
- Empty args are representable as `""`.

Examples:

| Header bytes | Tokens |
|---|---|
| `directory.create C:\Temp\demo` | verb=`directory.create`, args=[`C:\Temp\demo`] |
| `directory.create "C:\Program Files\demo dir"` | verb=`directory.create`, args=[`C:\Program Files\demo dir`] |
| `directory.rename "src dir" "dst dir"` | verb=`directory.rename`, args=[`src dir`, `dst dir`] |
| `directory.rename "src" --overwrite "dst"` | verb=`directory.rename`, args=[`src`, `--overwrite`, `dst`] |
| `clipboard.set 5` (then 5 bytes of payload) | verb=`clipboard.set`, args=[`5`]; payload is opaque |

Backward compatibility: any token without `"` and without spaces parses identically under the old (v2.0) grammar and the new grammar. Quoting is additive — a v2.1 client that doesn't use spaces in any arg sends bytes byte-for-byte identical to a v2.0 client. The new shape only appears when a caller chooses to quote.

Senders SHOULD quote any arg that contains a space or is empty, and MUST NOT send args containing `"` (no escape mechanism). Receivers MUST accept both quoted and unquoted forms for any arg position.

### 1.3 Encoding

- Header bytes are UTF-8.
- Payload bytes are opaque (binary). When a payload is text, it is UTF-8 unless the verb specifies otherwise.
- File paths in verb arguments are UTF-8 and translated to wide-character APIs on Windows targets.

### 1.4 Directives

Three directives appear in responses; one in requests.

| Directive | Direction | Purpose |
|---|---|---|
| `<verb>` | Client → agent | Request |
| `OK` | Agent → client | Successful response to a request |
| `ERR` | Agent → client | Failed response to a request |
| `EVENT` | Agent → client | Asynchronous notification for an active subscription |

`EVENT` frames may interleave between request/response pairs on the same connection — see §6.
