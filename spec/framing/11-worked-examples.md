## 11. Worked examples

### 11.1 Minimal session

```
> connection.hello agent-remote-hands 2.1
< OK 0
> system.info
< OK 312
{"name":"win-host-42","protocol":"2.1","os":"windows-modern","integrity":"medium",
 "tiers":["read","create","update","delete","extra_risky"],"current_tier":"read", ...}
> system.health
< OK 0
> connection.close
< OK 0
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
