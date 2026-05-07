## 2. Connection lifecycle

### 2.1 State machine

```
TCP connect  ─►  pre-hello  ─►  connected  ─►  closed
                      │              │
                      │              ├─ tier transitions: read ↔ create ↔ update ↔ delete ↔ extra_risky
                      │              │
                      └──────────────┴────────►  closed (any time, on socket drop)
```

A new connection starts in **pre-hello** state. Only `connection.hello` and `connection.close` are accepted. Any other verb returns `ERR invalid_state` with detail `{"required":"hello"}`.

After a successful `connection.hello`, the connection is **connected** at tier `read`. All verbs are accepted, subject to tier requirements.

The connection terminates on `connection.close` (graceful), socket drop, or agent shutdown.

### 2.2 Hello

```
> connection.hello <client-name> <protocol-version> [--framing <name>]
< OK <length>\n
{"protocol":"arh","agent":"AgentRemoteHands","agent_protocol":"2.2",
 "os_name":"Windows 11 Pro","os_version":"22H2","session_id":"...",
 "framing":"mcp"}
```

The client identifies itself, asserts a protocol version, and optionally selects a wire-framing mode. The agent rejects mismatched versions with `ERR protocol_mismatch {"agent":"2.2","client":"<n>"}`. v2.2+ agents do **not** advertise v2.1 as supported — v2.1 clients connecting to a v2.2+ agent receive `ERR protocol_mismatch` and must upgrade.

`<client-name>` is informational and logged by the agent.

**Response body is mandatory from v2.2 onward.** Earlier versions returned `OK 0`; v2.2 closes that gap. The body carries the negotiated protocol version, agent identifying fields, a fresh `session_id`, and the active `framing` (see `spec/verbs/common/connection.hello.json` for the full schema). Clients use the `framing` field to confirm which framing the agent has selected before switching their parser.

**Framing negotiation (`--framing <name>`).**

| Argument | Behaviour |
|---|---|
| omitted | Default is `mcp` when negotiated version `>= "2.2"`. v2.1 clients receive `ERR protocol_mismatch` (no v2.1 compat in v2.2+ agents). |
| `--framing mcp` | MCP-stdio framing (§1.6) — `Content-Length: N\r\n\r\n<JSON>`, MCP JSON-RPC 2.0 body. Available `windows-modern` only. |
| `--framing ws` | RFC 6455 binary frames carrying MCP JSON-RPC 2.0 body (§1.5). Available `windows-modern` only. No HTTP upgrade — the framing change happens entirely in `connection.hello`. |
| any other value | `ERR framing_unsupported`. |

The agent returns `ERR framing_unsupported` whenever it cannot honour the requested framing — either because the value is unknown, or because the family lacks support (`windows-classic` for `mcp` / `ws`). On `framing_unsupported` the connection remains in pre-hello state; the client may retry with a different `--framing` argument or omit the flag.

**Framing switch timing.** The framing switch takes effect **after** the hello `OK` body has been fully consumed by the client. There is no partial-read ambiguity: the bootstrap framing (§1.2) covers the entire request and its response; from the byte immediately following the hello body, the negotiated framing applies. The MCP session handshake described in §1.6.1 then runs on the new framing.

### 2.3 Tier negotiation

Five tiers, ordered as a strict ladder: `read` < `create` < `update` < `delete` < `extra_risky`. Every connection starts at `read`. Holding a higher tier subsumes every lower tier — a connection at `delete` can call any `read`/`create`/`update`/`delete`-tier verb (but not `extra_risky`).

```
> connection.tier_raise <tier> <token>
< OK <length>\n
{"new_tier":"<tier>"}
```

`<token>` is the contents of the agent's token file (see §2.6). The agent verifies the token matches and the requested tier is reachable, then records the new tier on this connection.

`<tier>` MUST be a tier name advertised in `system.info.tiers`. Requests for unknown tiers — including the v2.0 names `observe`/`drive`/`power` — return `ERR invalid_args`.

```
> connection.tier_drop <tier>
< OK <length>\n
{"new_tier":"<tier>"}
```

Voluntary downgrade. No token required. The target tier MUST be lower than or equal to the current tier; raising via `tier_drop` is `ERR invalid_args`.

### 2.4 Reset

```
> connection.reset
< OK 0
```

Discards any in-flight payload buffer and resets the framing parser. Used to recover from caller-side wire-format errors (a request with the wrong length, an unterminated header, etc.) without dropping the connection.

`connection.reset` does NOT change the tier or cancel subscriptions.

### 2.5 Close

```
> connection.close
< OK 0
(socket closes)
```

Graceful disconnect. The agent drains any pending `EVENT` frames for active subscriptions before sending `OK 0`, then closes the socket.

### 2.6 Token file

Tier elevation requires a token. The agent generates a fresh random token (256 bits, hex-encoded) on each start and writes it to a per-family path. A caller proves authorisation by reading the file (which requires filesystem access to the agent host) and quoting its contents in `connection.tier_raise`.

On agent restart, the token rotates. Existing connections retain their elevated tier; new elevations require the new token.

<!-- gen.py: token-file-table -->


### 2.7 Connection limits

The agent advertises `max_connections` in `system.info`. The `(N+1)`th concurrent connection receives:

```
< ERR busy 16\n
{"max":<N>}
```

before the socket is closed by the agent. Clients that need to interleave commands during a subscription open a side connection within the limit.

### 2.8 Held input state cleanup

`input.mouse.press` and `input.keyboard.key_down` leave a button or key held indefinitely. The OS keyboard / mouse state is system-wide — there's no kernel-level association between a synthesised down event and the connection that issued it. To prevent stuck input on connection loss, the agent maintains a per-connection **held-input set**:

- `input.mouse.press {button}` adds `button` to this connection's set and issues `MOUSEEVENTF_*DOWN`.
- `input.keyboard.key_down {vk}` adds `vk` to this connection's set and issues `KEYEVENTF_KEYDOWN`.
- `input.mouse.release {button}` and `input.keyboard.key_up {vk}` issue the corresponding `*UP` event and remove the entry from any connection's set (cross-connection release is permitted as a fail-safe — see those verbs' descriptions).
- On graceful `connection.close` or socket drop, the agent issues `MOUSEEVENTF_*UP` for every button in the closing connection's mouse set and `KEYEVENTF_KEYUP` for every key in its keyboard set, then drops the set.

The cleanup is idempotent: if the user-app or another connection already released the button/key, the up-event is a no-op at the OS level. The contract is "the agent never leaves input state held after a connection drops"; cross-connection visibility into held state is a fail-safe layer, not a guarantee that another connection's hold is observable.

`input.mouse.click {duration_ms}` and `input.keyboard.key {duration_ms}` do NOT enter the held-input set — they're synchronous (the up event always fires before the verb returns), and the agent's request thread is wedged for the duration. If the connection drops mid-`duration_ms`, the agent's per-thread deadline still fires the up event before the request thread exits.
