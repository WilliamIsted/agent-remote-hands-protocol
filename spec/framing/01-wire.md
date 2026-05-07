## 1. Wire format

### 1.1 Transport

- TCP, default port `8765` (configurable per agent).
- One agent listens on one port; per-thread connection model.
- No transport encryption today. Treat the wire as cleartext on the LAN.

### 1.2 Bootstrap framing (`connection.hello` only)

The framing in this section applies **only** to the `connection.hello` request and its `OK N\n<JSON>` response. Some wire format is required before the framing mode can be negotiated; the v2.0 / v2.1 ARH header-line format fills that bootstrap role and nothing else. Once the hello `OK N` body has been fully consumed, the connection switches to the negotiated framing — `mcp` (§1.6) or `ws` (§1.5) — and every subsequent byte on the socket follows the new format. The bootstrap framing is never used for any other verb.

> **Note for v2.0 / v2.1 readers:** in earlier protocol versions this same framing was the ongoing wire format for every request and response. v2.2+ retires it from that role. Implementers porting an older agent should keep their existing parser for `connection.hello` only and route every other verb through the negotiated framing.

Every bootstrap message — the `connection.hello` request or its `OK` / `ERR` response — is a single header line followed by an optional length-prefixed payload.

**Header line:**

```
<directive> <args...>\n
```

The header is ASCII, terminated by `\n`. A leading `\r` immediately before `\n` is tolerated and ignored. Tokens within the header are separated by single spaces; tokens that contain spaces themselves are double-quoted (see §1.2.5). The header MUST NOT exceed 65 535 bytes.

**Payload:**

If the directive's grammar specifies a `<length>` argument (always the final argument when present), exactly `<length>` bytes follow the header line. `<length>` is decimal ASCII. A length of `0` means no payload. Payload bytes are opaque to the framing layer — interpretation depends on the verb.

**Examples (bootstrap exchange only):**

| Form | Meaning |
|---|---|
| `connection.hello conformance 2.2\n` | Bootstrap request with no payload |
| `connection.hello conformance 2.2 --framing ws\n` | Bootstrap request, `ws` framing requested |
| `OK 312\n{...312 bytes of JSON...}` | Hello success — body carries the negotiated framing and other handshake fields |
| `ERR protocol_mismatch 28\n{"agent":"2.2","client":"2.1"}` | Hello failure — peer is not v2.2-capable |
| `ERR framing_unsupported 0\n` | Hello failure — agent does not support the requested framing |

**Response framing is uniform.** The hello `OK` and `ERR` responses carry a length prefix — `0` for empty bodies, otherwise the byte count of the payload that follows. From v2.2 onwards `connection.hello`'s OK body is mandatory (it carries the negotiated `framing` field; see `spec/verbs/common/connection.hello.json`). All subsequent verb invocations use the negotiated framing — see §1.5 (`ws`) and §1.6 (`mcp`).

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

### 1.4 Directives (bootstrap)

The bootstrap framing recognises three directives. They appear only in the `connection.hello` exchange.

| Directive | Direction | Purpose |
|---|---|---|
| `connection.hello` | Client → agent | Bootstrap request |
| `OK` | Agent → client | Successful response to the bootstrap request |
| `ERR` | Agent → client | Failed response to the bootstrap request |

After the hello OK body is consumed, request / response / event delivery is governed by the negotiated framing (§1.5 or §1.6). `EVENT` is no longer a wire-level directive in v2.2+; events are delivered as MCP notifications inside the negotiated framing — see §1.6.5.

### 1.5 WS framing mode (`ws`)

A v2.2 client requests the `ws` framing by passing `--framing ws` in the bootstrap `connection.hello` line (§2.2). When the agent's hello `OK` body has been fully consumed (and the body's `framing` field reads `"ws"`), the connection switches to RFC 6455 framing for every subsequent byte. There is **no HTTP upgrade**: the WebSocket handshake's HTTP layer is skipped and the connection moves directly into RFC 6455's data phase, because the framing negotiation has already happened in `connection.hello`.

**Wire shape:**

- Each ARH message — request, response, or notification — is exactly one RFC 6455 frame.
- Frames are FIN=1 binary frames (opcode `0x02`). Continuation frames are not used.
- Client-to-server frames MUST be masked (4-byte random masking key per frame, XOR-applied to the payload). Server-to-client frames MUST NOT be masked. This matches RFC 6455 §5.2 / §5.3.
- The frame payload is one complete MCP JSON-RPC 2.0 object, UTF-8 encoded — the same body shape as §1.6 (MCP-stdio), with the WS frame boundary replacing the `Content-Length` header. The MCP session lifecycle, tool catalogue, tier enforcement, subscription/event mapping, and binary handling described in §1.6.1–1.6.7 apply identically over `ws`.
- The agent SHOULD respond to WS ping frames (opcode `0x09`) with a matching pong (opcode `0x0A`). Close frames (opcode `0x08`) are honoured per RFC 6455 §5.5.1.

**Availability:** `windows-modern` only. `windows-classic` returns `ERR framing_unsupported` to `--framing ws`.

### 1.6 MCP framing mode (`mcp`)

The default framing for v2.2 connections. When the bootstrap `connection.hello` negotiates a protocol version `>= "2.2"` and the client passes no `--framing` argument (or explicitly passes `--framing mcp`), the connection switches to MCP-stdio framing for every subsequent byte once the hello `OK` body is consumed.

**Wire shape:**

```
Content-Length: <N>\r\n
\r\n
<N bytes of UTF-8 JSON>
```

This is the same framing Claude Code uses for stdio MCP servers (LSP-style header). Each frame carries one MCP JSON-RPC 2.0 object: a request, a result, an error, or a notification. There is no separate length-prefixed binary payload alongside the JSON — every byte transferred over the framing belongs to one of those four shapes.

**Availability:** `windows-modern` only. `windows-classic` returns `ERR framing_unsupported` to `--framing mcp`.

#### 1.6.1 MCP session lifecycle

Once the framing has switched, the client MUST initiate an MCP session before invoking any verbs. The standard MCP three-step handshake applies:

1. Client sends `initialize` request (`{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"<client>","version":"<v>"}}}`).
2. Agent responds with its capabilities. The agent advertises `tools` and `notifications`; `serverInfo.name` is `"AgentRemoteHands"` and `serverInfo.version` echoes the negotiated ARH protocol version (e.g. `"2.2"`).
3. Client sends the `notifications/initialized` notification.

The connection is then ready for `tools/call` and `tools/list` traffic.

#### 1.6.2 Tool catalogue

ARH verbs are exposed as MCP tools. The MCP tool name is the canonical dotted-namespace verb name — `system.info`, `file.write`, `input.mouse.click` — never a flattened or renamed form. The `inputSchema` for each tool is the verb's `input_schema` from `spec/verbs/common/<verb>.json` or `spec/verbs/windows/<verb>.json`. Discovery is via MCP `tools/list`, which the agent backs internally with `system.verbs`.

**Catalog model (resolves overview issue #12).** `tools/list` always returns **all** verbs the agent implements, regardless of the connection's current tier. Each tool definition carries the relevant `x-*` extension fields from the spec — notably `x-crudx` (the CRUDX tier letter `R` / `C` / `U` / `D` / `X`) and `x-tier` (the human-readable tier name `read` / `create` / `update` / `delete` / `extra_risky`). Clients use these fields to know in advance which tools require tier elevation; **no re-fetch of the tool catalogue is needed after `connection.tier_raise` or `connection.tier_drop`**.

#### 1.6.3 Tool invocation

Verbs are invoked via MCP `tools/call`. The `params.name` field carries the verb name; `params.arguments` is a JSON object whose keys correspond to the verb's `input_schema` properties.

**Successful invocation:**

```json
{"jsonrpc":"2.0","id":42,"result":{
  "content":[{"type":"text","text":"<JSON body of the verb's response>"}],
  "isError":false
}}
```

The `text` field contains the verb's OK-body JSON serialised as a string; clients parse it as JSON to recover the structured response.

**Failed invocation:**

```json
{"jsonrpc":"2.0","id":42,"result":{
  "content":[{"type":"text","text":"<JSON detail of the error>"}],
  "isError":true,
  "arh_error_code":"<code>"
}}
```

`arh_error_code` is an ARH extension field carrying the verb's error code (`tier_required`, `not_found`, `target_gone`, etc. — see §5). The `text` field carries the error's detail JSON. MCP protocol-level errors (the `error` member of a JSON-RPC response) are reserved for MCP protocol failures (malformed `tools/call`, unknown method, etc.); verb-level failures always travel as `isError: true` results.

#### 1.6.4 Tier model

A new connection starts at `read` tier. Tier elevation and downgrade are exposed as ordinary MCP tools — `connection.tier_raise` and `connection.tier_drop` — invoked via `tools/call`. Tier enforcement happens at `tools/call` time: invoking a verb whose `x-tier` exceeds the connection's current tier returns `isError: true`, `arh_error_code: "tier_required"`. The tool catalogue is unchanged by tier transitions; the agent does **not** emit `notifications/tools/list_changed` on `tier_raise` / `tier_drop`, because clients already know the tier requirements from the catalog model (§1.6.2).

#### 1.6.5 Subscriptions and events

`watch.*` verbs return `{"subscription_id":"sub:<n>"}` as the `tools/call` text body. Events for the subscription are delivered as MCP notifications:

```json
{"jsonrpc":"2.0","method":"notifications/arh/event","params":{
  "subscription_id":"sub:7",
  "data":{ ... event body per the watch verb's schema ... }
}}
```

Subscriptions are cancelled via `watch.cancel` `tools/call`. Notifications continue to arrive until either the cancel returns OK or the connection closes.

#### 1.6.6 Binary data

Binary data crosses the wire as base64 strings inside JSON, per MCP convention. Two patterns apply:

- **File / clipboard verbs** (`file.read`, `file.write`, `clipboard.set`, `clipboard.get`): the verb's `input_schema` / output schema declares a `content` field plus an `encoding` discriminator (`"text"` or `"binary"`). When `encoding: "binary"`, `content` is a base64-encoded string.
- **Image input** (`vision.ocr` with `bytes` input, `screen.capture` output): MCP image content items — `{"type":"image","data":"<base64>","mimeType":"image/png"}`. `screen.capture` returns its frame as an image content item rather than a text content item; clients reconstruct the raw bytes by base64-decoding `data`.

The Shape B binary side-channel (JSON header declares `blob_size`, raw bytes follow) is deferred — the current MCP mode uses base64 throughout. See `Overview/Planning/v3-structural-review.md` PR1 for the deferred design.

#### 1.6.7 Verbs excluded from MCP

A handful of verbs are not surfaced as MCP tools because their semantics are owned by the framing layer or by the bootstrap:

- `connection.hello` — runs in the bootstrap framing (§1.2) before MCP exists; never appears in `tools/list`.
- `connection.close` — handled by MCP session shutdown; clients close the connection by closing the transport.
- `connection.reset` — has no analogue in MCP (there is no header / payload split to desync); not exposed.
- `system.verbs` — backs `tools/list` internally; not surfaced as a separate tool.
