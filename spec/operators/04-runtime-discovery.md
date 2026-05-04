## What the agent tells you at runtime

Two verbs are designed to be your starting point on a fresh connection:

- **`system.info`** — agent identity, OS, hostname, integrity level, monitor count, available image formats, capability summary, **and the connection's currently-active tier (`current_tier`)** so you can introspect your own tier without tracking it client-side. Call it once after `connection.hello`.
- **`system.capabilities`** — the verb→required-tier map, exhaustively. If a verb isn't in the response, this build doesn't implement it. Tiers are CRUDX letters mapped to ladder rungs (R→`read`, C→`create`, U→`update`, D→`delete`, X→`extra_risky`); a verb tagged `tier: extra_risky` needs `connection.tier_raise extra_risky <token>` before calling it.

These two together let you discover what the agent supports and what tier you currently hold without consulting the spec or tracking state client-side. They're not a substitute for reading `dist/PROTOCOL.md` (the *shape* of arguments isn't advertised), but they're enough to gate-check anything you'd want to call.
