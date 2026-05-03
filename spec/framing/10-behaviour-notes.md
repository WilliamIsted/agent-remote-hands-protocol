## 10. Behaviour notes

### 10.1 Concurrency

Verbs from a single connection are serialised — the agent processes them in receive order and responses arrive in the same order. Verbs across different connections may run concurrently.

### 10.2 Idempotency

Most verbs are not idempotent. Callers that require at-most-once semantics SHOULD wrap retry logic with appropriate guards.

`watch.cancel` is idempotent: cancelling an already-cancelled subscription returns `OK 0`.

### 10.3 Element id stability

Element IDs are stable for the connection lifetime unless the underlying UI element is destroyed or invalidated. After invalidation, calls referencing the ID return `ERR target_gone`. The ID is not reused for a different element on the same connection.

### 10.4 Foreground locks

Windows enforces foreground-window locks to prevent applications from stealing focus. When `window.focus` is denied by this mechanism, the agent returns `ERR lock_held` rather than silently succeeding. Callers may retry after granting their own process the foreground privilege via `AllowSetForegroundWindow`.

### 10.5 UIPI behaviour

See §8 for the full discussion of integrity-level interactions. Briefly: synthetic input verbs (`input.*`, `element.invoke`) and UIA-based search verbs (`element.find`, `element.wait`) surface cross-IL barriers explicitly via `ERR uipi_blocked` and `ERR uia_blind` rather than silently succeeding.

### 10.6 Wire-desync recovery

If a client sends a malformed request (mis-stated payload length, header exceeding 65 535 bytes, etc.), the agent SHOULD return `ERR wire_desync` and discard the inbound buffer. The client recovers by sending `connection.reset` and resuming.
