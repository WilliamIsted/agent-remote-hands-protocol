## 9. Discovery

Agents MAY advertise themselves on the local network via mDNS / DNS-SD when started with `REMOTE_HANDS_DISCOVERABLE=1` or `--discoverable`.

Service type: `_remote-hands._tcp.local.`

TXT record fields:

| Field | Example | Meaning |
|---|---|---|
| `protocol` | `2` | Wire protocol major version |
| `os` | `windows-modern` | Target identifier |
| `tiers` | `read,create,update,delete,extra_risky` | Comma-separated tier list |
| `auth` | `token` | Comma-separated auth methods |
| `framings` | `mcp,ws` | Comma-separated wire-framing modes the agent will honour in `connection.hello`. Always includes `mcp` on a v2.2+ agent. Added v2.2. |

Discovery is opt-in per deployment. The protocol has no transport authentication, so mDNS advertising on an untrusted network is a footgun.
