# Wire protocol

**Version:** 2.2
**Status:** Stable.

The Agent Remote Hands wire protocol is a request/response protocol over plain TCP. Clients send verbs; agents respond with success or error replies and out-of-band notifications for active subscriptions.

This document is the canonical contract. Any agent claiming to speak protocol version 2.2 MUST conform to the framing, error model, and verb semantics defined here. The conformance suite under `tests/conformance/` is the executable contract.

> **Architecture note (issue #8).** §1 (Wire format) defines the **transport / framing layer** — how bytes on the TCP socket are delimited and decoded into messages. §§2–12 define the **application layer** — connection lifecycle, verbs, tiers, errors, events, and so on — and are deliberately transport-agnostic: the same verb semantics apply over any framing mode the agent supports. Adding a new framing mode is a §1 change; adding a new verb or error code is a §§2–12 change.

> **Wire-breaking change in 2.2.** The ongoing wire format moves to MCP JSON-RPC 2.0. Two framing modes are negotiated in `connection.hello`: `mcp` (MCP-stdio framing — `Content-Length: N\r\n\r\n<JSON>`, default for v2.2 connections) and `ws` (RFC 6455 binary frames carrying the same MCP JSON-RPC 2.0 body). The legacy ARH header-line format from v2.0 / v2.1 is **retired as an ongoing framing**; it is retained for exactly one purpose — the `connection.hello` bootstrap handshake (chicken-and-egg: some wire format is needed to negotiate the wire format). After the hello OK body is consumed, all subsequent messages on a v2.2+ connection use MCP-stdio or WS+MCP framing. v2.1 clients connecting to a v2.2+ agent receive `ERR protocol_mismatch` and must upgrade. See §1.2 (bootstrap), §1.5 (`ws`), §1.6 (`mcp`), and §2.2 (negotiation).

> **Wire-breaking change in 2.1.** The tier vocabulary moves from `observe`/`drive`/`power` to a five-rung CRUDX ladder (`read` < `create` < `update` < `delete` < `extra_risky`). Two verbs are renamed: `clipboard.read` → `clipboard.get`, `clipboard.write` → `clipboard.set`. **Clean cut, no aliases.** Pin to `v2.0.x` if you need the old vocabulary. See §12.5.
