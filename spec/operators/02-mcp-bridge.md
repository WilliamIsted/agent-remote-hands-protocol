## The 90% path: use the MCP bridge

If you're driving the agent through Claude Code, Claude Desktop, or any MCP-aware client, **you don't need to read `dist/PROTOCOL.md`**. The MCP bridge — which lives in the [agent repo](https://github.com/WilliamIsted/agent-remote-hands), not this Protocol repo — exposes the wire verbs as named tools (`take_screenshot`, `click_element`, `write_file`, etc.) with a tier-elevation flow that keeps destructive operations behind explicit caller intent.

Read first:
- [The MCP bridge in the agent repo](https://github.com/WilliamIsted/agent-remote-hands/tree/main/mcp-server) — bridge architecture, tier-elevation flow, environment variables.

Tier elevation is stateful and follows the v2.1 CRUDX ladder (`read` < `create` < `update` < `delete` < `extra_risky`). Call `request_update_access(reason="…")` before tools like `click_element` or `write_file`; call `request_delete_access(reason="…")` before tools like `delete_file` or `kill_process`; call `request_extra_risky_access(reason="…")` before tools like `cancel_pending_shutdown`. (`request_create_access` exists too, for tools that only need create — backed by C-tier verbs like `directory.create`, `file.create`, `process.start`.) The bridge handles the token dance for you.
