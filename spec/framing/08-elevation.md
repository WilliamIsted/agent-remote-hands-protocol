## 8. Elevation and integrity levels

Windows runs each process at one of four mandatory integrity levels — `low`, `medium`, `high`, `system`. User Interface Privilege Isolation (UIPI) silently blocks synthetic input from a lower-IL process to a higher-IL window. This is the agent's most common silent-failure mode and is worth understanding before deploying.

The OS-level integrity model is **separate** from the wire-protocol tier model in §7: tiers gate wire verbs (read / create / update / delete / extra_risky) and live entirely in the agent process; integrity levels gate cross-process effects and are enforced by the kernel. A connection at the `extra_risky` tier whose agent runs at `medium` IL still cannot drive a `high`-IL installer wizard.

### 8.1 The Medium-IL agent / High-IL installer trap

When started by a Task Scheduler logon-task with default settings, the agent runs at **Medium IL** in the logged-on user's session. Common installers — Mozilla NSIS, MSI installs, Steam, anything carrying a `requestedExecutionLevel="requireAdministrator"` manifest — auto-elevate to **High IL**.

UIPI then drops every synthesised input that crosses the IL boundary upward. From the wire, every diagnostic looks fine: `element.find` returns `OK <id>`, `element.invoke` returns `OK`, `input.keyboard.key` returns `OK` — but the wizard never advances. v1 agents had no observability into this; v2 agents surface it explicitly (see §8.3).

### 8.2 Surfacing the agent's IL

`system.info` (§3.1) returns two fields:

| Field | Values | Meaning |
|---|---|---|
| `integrity` | `low` / `medium` / `high` / `system`, or `null` on platforms without IL | The agent's own IL |
| `uiaccess` | boolean | Whether the agent's binary is signed with `uiAccess="true"` — exempts it from UIPI for synthetic input |

A caller that sees `integrity=medium` and `uiaccess=false` knows up front that cross-IL automation against any high-IL installer will fail.

### 8.3 Runtime UIPI failure surfaces

| Error | Detail | Returned by | Meaning |
|---|---|---|---|
| `uipi_blocked` | `{agent_il, target_il}` | `input.*`, `element.invoke`, `element.find_invoke`, `element.at_invoke` | Synthetic input rejected because the target window's IL exceeds the agent's |
| `uia_blind` | `{agent_il, target_il}` | `element.find`, `element.find_invoke`, `element.wait` | UIA tree walk completed without a match, *and* a higher-IL foreground window is present — distinguishes "element doesn't exist" from "I can't see across the barrier" |

Both are deterministic: callers can branch on the code rather than retrying blindly.

### 8.4 Workarounds for cross-IL automation

1. **Spawn a second, elevated agent.** Run a second `remote-hands.exe --port 8766` under an elevated token. The Medium-IL agent handles ordinary automation; the elevated one drives installer wizards. Callers pick the agent that matches the target window's IL.
2. **Sign the agent with `uiAccess="true"`.** Embedding `<requestedExecutionLevel uiAccess="true" level="asInvoker"/>` in the manifest, signing with a trusted code-signing certificate, and installing the binary under `Program Files` exempts the agent from UIPI without making it elevated. This is the path accessibility tools use; once `system.info.uiaccess=true`, cross-IL input verbs work as if the agent were High-IL.
3. **`--install` with the registering user already in `BUILTIN\Administrators`.** The installed Task Scheduler task uses `HighestAvailable`; if the user is an admin, the task runs elevated on their next logon, making the agent itself High-IL.

(1) is simplest; (2) is most ergonomic for production deployments; (3) is the fastest path on dev boxes where the user is already a local admin.

### 8.5 Related sections

- `system.info` field shapes — §3.1
- Error codes `uipi_blocked` and `uia_blind` — §5.2
- Wire-protocol tier model — §7
