## Filing issues from operational use

If you encounter a bug or ergonomic gap during real use, file it on GitHub with the labels `agent-feedback,agent-authored`. Issues #62 and #63 are examples of LLM-surfaced findings that landed real fixes. Concrete reproduction steps + the agent's response (`OkResponse(payload=...)` or `ErrResponse(code=..., detail=...)`) are the most useful body content; don't include conversation history or LLM-internal reasoning.

## Where this document lives

The release zip ships this file alongside `remote-hands.exe`, `dist/PROTOCOL.md`, `README.md`, and `wire.py`. If you have the binary, you have the spec. If you're browsing the GitHub repo, the source is split under [`spec/operators/`](../spec/operators/) and the rendered output is at `dist/LLM-OPERATORS.md` — generated at release time by `python Tools/gen.py`. Either way, this document is the entry point — read it first.
