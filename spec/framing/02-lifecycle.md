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
> connection.hello <client-name> <protocol-version>
< OK 0
```

The client identifies itself and asserts a protocol major version. The agent rejects mismatched versions with `ERR protocol_mismatch {"agent":"2","client":"<n>"}`.

`<client-name>` is informational and logged by the agent.

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
