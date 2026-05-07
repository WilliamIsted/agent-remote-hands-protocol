## 11. Worked examples

### 11.1 Minimal session

The `connection.hello` exchange uses the bootstrap framing (§1.2). After the hello OK body is consumed the connection switches to MCP-stdio (the v2.2 default) and every subsequent message is one MCP JSON-RPC 2.0 object framed by `Content-Length: N\r\n\r\n`.

```
> connection.hello agent-remote-hands 2.2
< OK 188
{"protocol":"arh","agent":"AgentRemoteHands","agent_protocol":"2.2",
 "os_name":"Windows 11 Pro","os_version":"22H2",
 "session_id":"s-91f0...","framing":"mcp"}

(framing switches to MCP-stdio)

> Content-Length: 156\r\n\r\n{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo","version":"1"}}}
< Content-Length: 178\r\n\r\n{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26","capabilities":{"tools":{},"notifications":{}},"serverInfo":{"name":"AgentRemoteHands","version":"2.2"}}}
> Content-Length: 54\r\n\r\n{"jsonrpc":"2.0","method":"notifications/initialized"}

> Content-Length: 76\r\n\r\n{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"system.info","arguments":{}}}
< Content-Length: 348\r\n\r\n{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{\"family\":\"windows-modern\",\"agent\":\"AgentRemoteHands\",\"agent_protocol\":\"2.2\",\"hostname\":\"win-host-42\",\"current_tier\":\"read\",\"framings\":[\"mcp\",\"ws\"], ...}"}],"isError":false}}

> Content-Length: 78\r\n\r\n{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"system.health","arguments":{}}}
< Content-Length: 102\r\n\r\n{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{}"}],"isError":false}}

(client closes the transport)
```

### 11.2 Tier elevation and input

```
> input.mouse.click 100 200
< ERR tier_required 38
{"required":"update","current":"read"}

> file.read C:\ProgramData\AgentRemoteHands\token
< OK 64
a3f1c8...e9b2

> connection.tier_raise update a3f1c8...e9b2
< OK 23
{"new_tier":"update"}

> input.mouse.click 100 200
< OK 0
```

### 11.3 UIPI surfacing

```
> input.keyboard.type 11
hello world

< ERR uipi_blocked 47
{"agent_il":"medium","target_il":"high","message":"foreground window owned by elevated process"}
```

### 11.4 Subscription with interleaved verbs

```
> watch.window --title-prefix "Mozilla Firefox"
< OK 25
{"subscription_id":"sub:7"}

> screen.capture
< OK 184321
<png bytes>

< EVENT sub:7 142
{"kind":"window_appeared","hwnd":"win:0x1A2B","title":"Mozilla Firefox - Mozilla Firefox","pid":4321}

> window.focus win:0x1A2B
< OK 22
{"prior_hwnd":"win:0x0844"}

> watch.cancel sub:7
< OK 0
```

### 11.5 Reboot

```
> connection.tier_raise extra_risky <token>
< OK 28
{"new_tier":"extra_risky"}

> system.reboot --delay 5 --reason planned
< OK 64
{"phase":"requested","grace_ms":5000,"deadline_unix":1748438201}

(connection drops within ~6 seconds)
```

### 11.6 Wire desync recovery

```
> file.write /path/foo.txt 1024
<sends only 800 bytes, then sends another verb header>
< ERR wire_desync 0
> connection.reset
< OK 0
> file.write /path/foo.txt 1024
<sends 1024 bytes correctly>
< OK 0
```

### 11.7 Directory namespace round-trip

A short scratch-directory lifecycle exercising the v2.1 `directory.*` namespace and the clipboard rename. Assumes the connection has already raised to `delete` tier (which subsumes `update` + `create` + `read`).

```
> directory.create C:\Temp\demo-2c8b
< OK 0

> file.write C:\Temp\demo-2c8b\note.txt 5
hello
< OK 0

> clipboard.set 11
demo content
< OK 0

> clipboard.get
< OK 12
demo content

> directory.list C:\Temp\demo-2c8b
< OK 96
{"entries":[{"name":"note.txt","type":"file","size":5,"mtime_unix":1748520000}]}

> directory.stat C:\Temp\demo-2c8b
< OK 56
{"type":"dir","entry_count":1,"mtime_unix":1748520000}

> directory.remove C:\Temp\demo-2c8b
< ERR not_empty 53
{"message":"directory not empty; pass --recursive"}

> directory.remove C:\Temp\demo-2c8b --recursive
< OK 33
{"removed":true,"entries_removed":1}

> directory.exists C:\Temp\demo-2c8b
< OK 17
{"exists":false}
```

### 11.8 WS framing negotiation

A v2.2 client requests RFC 6455 binary framing in the bootstrap hello. The agent confirms `"framing":"ws"` in the hello body; from the byte after the body the connection is RFC 6455 binary frames carrying MCP JSON-RPC 2.0 — same body shape as §11.9, just wrapped in WS frames.

```
> connection.hello agent-remote-hands 2.2 --framing ws
< OK 187
{"protocol":"arh","agent":"AgentRemoteHands","agent_protocol":"2.2",
 "os_name":"Windows 11 Pro","os_version":"22H2",
 "session_id":"s-04e2...","framing":"ws"}

(framing switches to RFC 6455 binary frames; client-to-server masked, server-to-client unmasked)

> [WS binary frame] {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo","version":"1"}}}
< [WS binary frame] {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26","capabilities":{"tools":{},"notifications":{}},"serverInfo":{"name":"AgentRemoteHands","version":"2.2"}}}
> [WS binary frame] {"jsonrpc":"2.0","method":"notifications/initialized"}

> [WS binary frame] {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"system.info","arguments":{}}}
< [WS binary frame] {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{...system.info JSON...}"}],"isError":false}}

(client sends a WS close frame, agent responds with its own close, sockets terminate)
```

### 11.9 MCP framing session

A standard v2.2 connection — no `--framing` argument, so the negotiated framing is `mcp`. After hello the connection runs the MCP handshake, lists tools, calls verbs, raises tier, runs a watch subscription, and cancels.

```
> connection.hello agent-remote-hands 2.2
< OK 188
{"protocol":"arh","agent":"AgentRemoteHands","agent_protocol":"2.2",
 "os_name":"Windows 11 Pro","os_version":"22H2",
 "session_id":"s-12c9...","framing":"mcp"}

(framing switches to MCP-stdio)

> Content-Length: 156\r\n\r\n{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"demo","version":"1"}}}
< Content-Length: 178\r\n\r\n{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-03-26","capabilities":{"tools":{},"notifications":{}},"serverInfo":{"name":"AgentRemoteHands","version":"2.2"}}}
> Content-Length: 54\r\n\r\n{"jsonrpc":"2.0","method":"notifications/initialized"}

# Discover the tool catalogue (always full, regardless of current tier).
> Content-Length: 56\r\n\r\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","id":2,"result":{"tools":[
    {"name":"system.info","description":"...","inputSchema":{...},"x-crudx":"R","x-tier":"read"},
    {"name":"input.mouse.click","description":"...","inputSchema":{...},"x-crudx":"U","x-tier":"update"},
    {"name":"watch.window","description":"...","inputSchema":{...},"x-crudx":"R","x-tier":"read"},
    ...
  ]}}

# Call system.info.
> Content-Length: 76\r\n\r\n{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"system.info","arguments":{}}}
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{...system.info JSON...}"}],"isError":false}}

# Raise tier to update so we can drive input later.
> Content-Length: 132\r\n\r\n{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"connection.tier_raise","arguments":{"tier":"update","token":"a3f1c8...e9b2"}}}
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"{\"new_tier\":\"update\"}"}],"isError":false}}

# Open a window subscription.
> Content-Length: 122\r\n\r\n{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"watch.window","arguments":{"title_prefix":"Mozilla Firefox"}}}
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","id":5,"result":{"content":[{"type":"text","text":"{\"subscription_id\":\"sub:7\"}"}],"isError":false}}

# Async event arrives between request/response pairs as an MCP notification.
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","method":"notifications/arh/event","params":{"subscription_id":"sub:7","data":{"kind":"window_appeared","hwnd":"win:0x1A2B","title":"Mozilla Firefox - Mozilla Firefox","pid":4321}}}

# Cancel the subscription.
> Content-Length: 102\r\n\r\n{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"watch.cancel","arguments":{"subscription_id":"sub:7"}}}
< Content-Length: ...\r\n\r\n{"jsonrpc":"2.0","id":6,"result":{"content":[{"type":"text","text":"{}"}],"isError":false}}

(client closes the transport)
```
