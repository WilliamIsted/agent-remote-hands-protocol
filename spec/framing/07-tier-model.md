## 7. Tier model

The tier vocabulary follows CRUDX — each verb's required tier matches the side-effect class it belongs to.

### 7.1 Tier semantics

| Tier | CRUDX letter | Capability |
|---|---|---|
| `read` | R | Observe state without changing it. Capture the screen, list windows, read files, query elements, watch for events. The default tier on a fresh connection. |
| `create` | C | All `read` capabilities plus operations that bring something new into existence: `directory.create`, `process.start`, `process.shell`. |
| `update` | U | All `create` capabilities plus operations that overwrite or move existing things: synthetic input, file writes, registry writes, focus changes, element invocations, window moves, file rename. |
| `delete` | D | All `update` capabilities plus operations that make existing things cease to be: `file.delete`, `process.kill`, `registry.delete`. |
| `extra_risky` | X | All `delete` capabilities plus operations that affect connection / system / power state: `system.shutdown`, `system.reboot`, `system.logoff`, `system.hibernate`, `system.sleep`, `system.power.cancel`. |

The ladder is strict — holding a higher tier subsumes every lower tier. A connection at `delete` can call any `R`/`C`/`U`/`D`-tier verb (but not `X`-tier).

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
