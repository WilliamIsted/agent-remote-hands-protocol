# Wire protocol

**Version:** 2.1
**Status:** Stable.

The Agent Remote Hands wire protocol is a line-oriented, length-prefixed, request/response protocol over plain TCP. Clients send verbs; agents respond with `OK`, `ERR`, or out-of-band `EVENT` frames for active subscriptions.

This document is the canonical contract. Any agent claiming to speak protocol version 2.1 MUST conform to the framing, error model, and verb semantics defined here. The conformance suite under `tests/conformance/` is the executable contract.

> **Wire-breaking change in 2.1.** The tier vocabulary moves from `observe`/`drive`/`power` to a five-rung CRUDX ladder (`read` < `create` < `update` < `delete` < `extra_risky`). Two verbs are renamed: `clipboard.read` → `clipboard.get`, `clipboard.write` → `clipboard.set`. **Clean cut, no aliases.** Pin to `v2.0.x` if you need the old vocabulary. See §12.5.
