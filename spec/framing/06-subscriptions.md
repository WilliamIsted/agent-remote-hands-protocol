## 6. Subscriptions and EVENT frames

Long-running observation operations register subscriptions on the connection. Each `watch.*` verb returns immediately with `OK <len>\n{"subscription_id":"sub:N"}`. The subscription is active until the client issues `watch.cancel` or the connection closes.

### 6.1 EVENT framing

Events arrive interleaved with regular request/response pairs:

```
< EVENT <subscription_id> <length>\n
<bytes>
```

Subscription ID format: `sub:` followed by a connection-scoped sequential integer.

EVENT frames are atomic: they appear between request boundaries, never mid-response. A client reading the wire MUST be prepared to receive EVENT frames at any point after the first `OK` returned from a `watch.*` verb.

### 6.2 EVENT payload shape

Payload format depends on the watch type:

| Watch verb | EVENT payload |
|---|---|
| `watch.region` | Image bytes (PNG / WebP / BMP per the `--format` argument or the agent's default) |
| `watch.process` | UTF-8 JSON: `{"kind":"process_exit","pid":N,"exit_code":N}` |
| `watch.window` | UTF-8 JSON: `{"kind":"window_appeared\|window_gone","hwnd":"win:...","title":"..."}` |
| `watch.element` | UTF-8 JSON: `{"kind":"element_invalidated","elt":"elt:N"}` |
| `watch.file` | UTF-8 JSON: `{"kind":"created\|modified\|deleted","path":"..."}` |
| `watch.registry` | UTF-8 JSON: `{"kind":"changed","path":"..."}` |

### 6.3 Auto-cancellation

Some subscriptions end on their own:

- `watch.process` auto-cancels after emitting the `process_exit` event.
- `watch.element` auto-cancels after emitting the `element_invalidated` event.
- `watch.region --until-change` auto-cancels after emitting one frame.

For auto-cancelled subscriptions, the client MAY issue `watch.cancel` defensively; the agent returns `OK 0` whether or not the subscription is still active.

### 6.4 Ordering

Within a single subscription, EVENT frames are emitted in the order events occurred. Across subscriptions, frame ordering is unspecified.
