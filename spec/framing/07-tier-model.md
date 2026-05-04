## 7. Tier model

The tier vocabulary follows CRUDX — each verb's required tier matches the side-effect class it belongs to.

### 7.1 Tier semantics

| Tier | CRUDX letter | Capability |
|---|---|---|
| `read` | R | Observe state without changing it. Capture the screen, list windows, read files, query elements, watch for events. The default tier on a fresh connection. |
| `create` | C | All `read` capabilities plus operations that bring something new into existence: `directory.create`, `process.start`, `process.shell`. |
| `update` | U | All `create` capabilities plus operations that overwrite or move existing things: synthetic input, file writes, registry writes, focus changes, element invocations, window moves, file rename. |
| `delete` | D | All `update` capabilities plus operations that make existing things cease to be: `file.delete`, `process.kill`, `registry.delete`. |
| `extra_risky` | X | All `delete` capabilities plus operations that affect system / power state: `system.power.shutdown`, `system.power.reboot`, `system.power.logoff`, `system.power.hibernate`, `system.power.sleep`, `system.power.lock`. |

The ladder is strict — holding a higher tier subsumes every lower tier. A connection at `delete` can call any `R`/`C`/`U`/`D`-tier verb (but not `X`-tier).

### Exemptions from CRUDX

Two classes of verb are **CRUDX-exempt** — they carry an `R` letter despite mutating state, because the state they mutate is not user-visible:

- **`connection.*` (5 verbs)** — `connection.hello`, `connection.close`, `connection.reset`, `connection.tier_raise`, `connection.tier_drop`. These operate on protocol-layer state (session lifecycle, framing parser, per-connection tier). The CRUDX model is for user-visible-state side-effects; protocol-layer mutations are tier-orthogonal. `tier_raise` is gated by token, not tier; `close`/`reset` always available; `hello` is the handshake.
- **`watch.*` subscription creators (`watch.region`, `watch.process`, `watch.window`, `watch.element`, `watch.file`, `watch.registry`)** plus **`watch.cancel`** — subscriptions are connection-scoped observation handles, not durable agent state. Creating a watch is `R` (you're observing); cancelling is `R` (you're observing the lack of further events). The underlying observed state is what gets gated — e.g. `watch.region` requires `read` for screen content. See `06-subscriptions.md` for the subscription lifecycle model.

`system.power.cancel` was previously listed as X-tier; it is now classified as `U` because cancellation mutates pending-action state but does not introduce new risk.

### 7.2 Tier enforcement

The agent MUST enforce tier requirements at the verb-dispatch layer. A verb whose required tier exceeds the connection's current tier returns:

```
< ERR tier_required <length>\n
{"required":"<tier>","current":"<tier>"}
```

`<tier>` values are exclusively the v2.1 names — `read`, `create`, `update`, `delete`, `extra_risky`. The v2.0 names (`observe`, `drive`, `power`) are not accepted by v2.1 agents.

### 7.3 Privilege management

The agent MAY enable Win32 privileges (e.g. `SeShutdownPrivilege`) only when needed for the current tier. A `read`-tier connection SHOULD see those privileges disabled in the agent's effective token.

This is OS-enforced confinement layered on top of protocol-level tier checks. Protocol 2.x agents are single-process; full process isolation is the v0.3 privsep dispatcher milestone (Protocol 3.0).
