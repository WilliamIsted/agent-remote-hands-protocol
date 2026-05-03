## 6. Subscriptions and EVENT frames

Long-running observation operations register subscriptions on the connection. Each `watch.*` verb returns immediately with `OK <len>\n{"subscription_id":"sub:N"}`. The subscription is active until the client issues `watch.cancel` or the connection closes.

Subscriptions are **connection-scoped observation handles, not durable agent state**. CRUDX-classification: every `watch.*` verb (creators and `watch.cancel`) carries `R`. The state being observed is what's tier-gated — a screen-content watch needs `read`-tier visibility, a registry watch needs read access to the key — but the act of creating or cancelling a watch is treated as observation. See `07-tier-model.md` for the exemption rationale.

### 6.1 EVENT framing

Events arrive interleaved with regular request/response pairs:

```
< EVENT <subscription_id> <length>\n
<bytes>
```

Subscription ID format: `sub:` followed by a connection-scoped sequential integer.

EVENT frames are atomic: they appear between request boundaries, never mid-response. A client reading the wire MUST be prepared to receive EVENT frames at any point after the first `OK` returned from a `watch.*` verb.

### 6.2 EVENT payload shape

The verb spec is canonical for each watch.* event payload. Payload format depends on the watch type and (for `watch.region`) the `encoding` input parameter:

| Watch verb | EVENT payload |
|---|---|
| `watch.region` (encoding=binary, default) | Raw image bytes (PNG / WebP / BMP per the `format` argument). Length-prefixed in the EVENT frame; no JSON envelope. |
| `watch.region` (encoding=base64) | UTF-8 JSON: `{"image":"<base64>","format":"<png\|webp\|bmp>","timestamp_unix_ms":N}` |
| `watch.process` | UTF-8 JSON: `{"exit_code":N}` |
| `watch.window` | UTF-8 JSON: `{"kind":"created\|destroyed","handle":"win:...","title":"...","pid":N}` |
| `watch.element` | UTF-8 JSON: `{"reason":"destroyed\|reparented\|structure_changed"}` |
| `watch.file` | UTF-8 JSON: `{"kind":"created\|modified\|deleted\|renamed","path":"...","old_path":"..."}` (`old_path` only present when `kind: "renamed"`) |
| `watch.registry` | UTF-8 JSON: `{"path":"..."}` |

**Convention:** the `kind` field is omitted from EVENT payloads whose only possible kind is a single fixed value (e.g. `watch.process`, `watch.registry`). Where a verb produces multiple event kinds, `kind` is required and enumerated.

### 6.3 Auto-cancellation

Some subscriptions end on their own:

- `watch.process` auto-cancels after emitting the exit event.
- `watch.element` auto-cancels after emitting an invalidation event.
- `watch.region` with `until_change: true` auto-cancels after emitting one frame.

For auto-cancelled subscriptions, the client MAY issue `watch.cancel` defensively; the agent returns `OK 0` whether or not the subscription is still active.

### 6.4 Ordering

Within a single subscription, EVENT frames are emitted in the order events occurred. Across subscriptions, frame ordering is unspecified.
