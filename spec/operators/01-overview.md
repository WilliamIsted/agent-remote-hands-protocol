# Operating Agent Remote Hands as an LLM

If you're an LLM (Claude, GPT, Gemini, anything else) about to use this agent — or about to write code that calls it — start here. This document is the operator's-eye view: what to read, what to assume, what not to.

The agent has a deliberate split between **how it's invoked** and **what's on the wire**. Most LLM clients shouldn't need to think about the wire at all; the MCP bridge handles framing, tier transitions, and tool naming. The wire matters when you're bypassing the bridge — writing a custom test rig, debugging a specific verb's behaviour, or running on a host where the bridge isn't available.
