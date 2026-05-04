## The 10% path: speaking the wire directly

If you're writing a custom client, running on a host without the MCP bridge, or debugging behaviour the bridge layer obscures — read these in order:

1. **[`dist/PROTOCOL.md`](PROTOCOL.md)** — the contract. Framing rules, every verb's argument shape, error codes, the connection state machine, the tier model. This is the source of truth; nothing on the wire works differently from what's documented here.
2. **[`tests/conformance/wire.py`](../tests/conformance/wire.py)** — a canonical Python client that implements the framing correctly. ~220 lines, no dependencies beyond the Python stdlib. Use it as a reference, copy it, or just import it. The framing has corners (length-prefixed payloads, EVENT frames interleaving with command responses) that are easy to get wrong from scratch.
3. **[`tests/conformance/test_*.py`](../tests/conformance/)** — one file per namespace, with worked examples of every conformant verb call. When you're not sure how to invoke `screen.capture --window` or `registry.value.read`, find the test that does it.
