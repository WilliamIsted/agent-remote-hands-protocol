## 3. Capability discovery

### 3.1 `system.info`

The negotiation contract. Returns a JSON object describing the agent's identity, advertised capabilities, current connection state, and supported namespaces.

```
> system.info
< OK <length>\n
{
  "name": "<agent-name>",
  "version": "<agent-build-version>",
  "protocol": "2.0",
  "os": "<os-tag>",
  "arch": "x64",
  "hostname": "<host>",
  "user": "<run-as-account>",
  "integrity": "medium",
  "uiaccess": false,
  "monitors": 2,
  "privileges": ["SeShutdownPrivilege"],
  "tiers": ["read", "create", "update", "delete", "extra_risky"],
  "current_tier": "read",
  "auth": ["token"],
  "max_connections": 4,
  "namespaces": [
    "system", "screen", "window", "input", "element",
    "file", "directory", "process", "registry", "clipboard", "watch", "connection"
  ],
  "capabilities": {
    "capture": "wgc",
    "ui_automation": "uia",
    "image_formats": ["png", "webp", "bmp"],
    "discovery": "mdns"
  }
}
```

Field semantics:

| Field | Type | Notes |
|---|---|---|
| `name` | string | Agent product name (e.g. `agent-remote-hands`) |
| `version` | string | Agent build version (e.g. `2.0.0+abc123`) |
| `protocol` | string | Wire protocol version. MUST be `"2.0"` for this spec. |
| `os` | string | Target identifier: `windows-modern`, `windows-nt`, etc. |
| `arch` | string | `x86`, `x64`, `arm64` |
| `hostname` | string | Target machine hostname |
| `user` | string | Run-as account name |
| `integrity` | string \| null | `"low"`, `"medium"`, `"high"`, `"system"`, or `null` if integrity levels don't exist on this OS |
| `uiaccess` | boolean | `true` if the agent process has the UIAccess flag set (lets it drive higher-IL UI) |
| `monitors` | int | Number of physical monitors attached. The 0-based index used by `window.list.monitor_index` and `screen.capture --monitor` matches `EnumDisplayMonitors` enumeration order (typically primary first). |
| `privileges` | array of strings | Win32 privilege names enabled in the agent's token |
| `tiers` | array of strings | Tiers this agent supports. Always at least `["read"]`. |
| `current_tier` | string | Tier of the current connection |
| `auth` | array of strings | Supported elevation methods. `"token"` today; `"sspi"` in the v0.4 milestone (Protocol 4.0). |
| `max_connections` | integer | Concurrent connection cap |
| `namespaces` | array of strings | Verb namespaces this agent advertises |
| `capabilities` | object | Sub-capabilities (capture engine, UIA flavour, image formats, etc.) |

Clients SHOULD check `protocol`, `namespaces`, and `capabilities` before issuing verbs that depend on optional features.

### 3.2 `system.capabilities`

```
> system.capabilities
< OK <length>\n
{
  "system.info": {"tier": "read"},
  "system.health": {"tier": "read"},
  "system.reboot": {"tier": "extra_risky"},
  "screen.capture": {"tier": "read"},
  ...
}
```

Map of verb name to required tier (and any verb-specific flags). A verb absent from this map is not implemented by this agent — clients MUST NOT issue it.
