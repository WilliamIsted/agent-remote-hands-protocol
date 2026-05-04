## A worked example session

Minimal Python session against an agent on `127.0.0.1:8765`:

```python
import json
from wire import WireClient, OkResponse

with WireClient("127.0.0.1", 8765) as c:
    c.hello("my-llm-rig", "2.1")

    info = c.info()                         # system.info — includes current_tier
    caps = c.capabilities()                 # system.capabilities

    # Take a screenshot at the default `read` tier (no token needed).
    r = c.request("screen.capture", "--format", "png")
    assert isinstance(r, OkResponse)
    with open("shot.png", "wb") as f:
        f.write(r.payload)

    # Elevate to update tier for input synthesis. Token from
    # %ProgramData%/AgentRemoteHands/token.
    with open(r"C:\ProgramData\AgentRemoteHands\token") as f:
        token = f.read().strip()
    c.request("connection.tier_raise", "update", token)

    # Now you can drive input.
    c.request("input.mouse.click", "100", "100")

    c.request("connection.close")
```

The same flow via the MCP bridge would be a sequence of MCP tool calls — different surface, same semantics — but the wire-level version above is the most reductive form.
