# Changelog

Per-release notes for the Agent Remote Hands wire protocol. The detailed
release notes for each spec version live in `dist/PROTOCOL.md` §12.5 (run
`python Tools/gen.py` to render) — this file is a brief index pointing at
them.

Versioning is per-family-branched (see `dist/PROTOCOL.md` §12 and
[`CLAUDE.md`](CLAUDE.md)). The leading "v" tag form (`v2.1.0`, `v2.0.0`, …)
matches the spec version embedded in the document frontmatter and reported
by `system.info.agent_protocol`.

## v2.2.0-rc.1 — 2026-05-07

**Wire-breaking from v2.0 / v2.1.** v2.1 clients connecting to a v2.2+ agent
receive `ERR protocol_mismatch` and must upgrade. Pre-1.0; clean break by
design.

### Wire framing modernisation (Overview repo issues #1, #3, #8, #9)

- The v2.0 / v2.1 ARH header-line text format is **retired as the ongoing
  framing**. It survives only as the bootstrap framing for the
  `connection.hello` request and its OK / ERR response — the
  chicken-and-egg "you need some wire format to negotiate the wire
  format" handshake. After the hello OK body is consumed, the connection
  switches to the negotiated framing.
- New `mcp` framing mode (default for v2.2+ connections):
  MCP-stdio framing — `Content-Length: N\r\n\r\n<JSON>` with each frame
  carrying one MCP JSON-RPC 2.0 object. Same shape as Claude Code's stdio
  MCP servers. ARH verbs are exposed as MCP tools (`tools/list`,
  `tools/call`); subscriptions arrive as `notifications/arh/event`. Tier
  enforcement at `tools/call` time; the catalog is complete from first
  `tools/list` call so no re-fetch is needed after `connection.tier_raise`.
  Available on `windows-modern` and `windows-legacy`.
- New `ws` framing mode (opt-in via `--framing ws`): RFC 6455 binary frames
  (FIN=1, opcode 0x02, client-masked) carrying the same MCP JSON-RPC 2.0
  body. No HTTP upgrade — the framing change is in-protocol. Available on
  `windows-modern` only.
- New error code: `framing_unsupported` — agent cannot honour the
  requested `--framing` value.
- New `system.info.framings` array — agents advertise which framing modes
  they honour.
- `connection.hello` response body is now mandatory (was empty in v2.0 /
  v2.1) and carries a `framing` field so clients can confirm the
  negotiated mode before switching their parser.

### Family declarations (Overview repo issue #4 P1–P6)

- New `windows-legacy` family declared. Covers Windows XP SP3 through
  Windows 10 builds before 1809 (Vista, 7, 8, 8.1, Server 2003 SP2,
  2008/R2, 2012/R2). Built with VS2017 v141_xp toolset. Honours `mcp`
  framing only; rejects `ws`. Pre-v2.2 the same agent code identified
  itself as `windows-classic` on the wire — that misidentification is now
  corrected. `windows-classic` shrinks back to its accurate range:
  NT 4.0 SP6a, Windows 95 OSR2 → ME, Windows 2000.
- `windows-modern` floor corrected: Windows 10 build 17763 (1809), not
  1803. WGC was introduced in 1803 but stabilised at 1809; the modern
  floor sits at the stabilisation point.
- New per-family `format_supported` array in `families.json`. modern:
  `[png, webp, bmp]`; legacy: `[bmp]` + runtime extras `[png, webp]` (WIC
  available on Vista+ in-box, XP SP3 needs the redist); classic: `[bmp]`
  + runtime extras `[png]` (GDI+ runtime).
- `system.info.family` enum extended to include `windows-legacy`.

### Verb additions / extensions

- `system.verbs` (issue #97): full strict-tool definitions over the wire,
  filtered to verbs the agent actually implements. Lets clients build
  their tool catalogue from the live agent rather than bundling spec
  files alongside themselves; closes the bundled-bridge-vs-agent drift
  footgun. Backs MCP `tools/list` in MCP framing mode.
- `input.mouse.click` gains `triple: true` (three press/release pairs
  batched within `GetDoubleClickTime` so the OS triple-click handler
  fires — line / paragraph selection in text fields) and `clicks: N`
  (range 2-10, open-ended count with caller-controlled
  `clicks_interval_ms` defaulting to `double_click_time_ms + 50` so the
  OS treats each click as independent). Mutex set extended to
  `{double, triple, clicks, duration_ms}`. Resolves Overview repo
  issue #11 item 2.
- `screen.capture` `format` enum extended to
  `[png, webp, bmp, jpeg, heic]`. `jpeg` and `heic` are forward-compat
  reservations for future macOS / Linux families; current Windows
  families return `unsupported_format`. Hard-coded `quality: 80` default
  removed — each family's encoder uses its own appropriate default
  (libwebp ~75, WIC quality varies). Resolves Protocol issue #83 P3 / P4.
- `input.keyboard.*`, `input.send_message`, `input.post_message`:
  documentation cross-references to the user32-vs-RawInput / DirectInput
  capability boundary in `spec/operators/05-footguns.md`. Synthesised
  keystrokes deliver via the user32 layer only; DirectInput / RawInput
  targets won't observe them. Documentation only — no wire-shape change.
  Closes Protocol issue #96.

### Spec corpus organisation (issue #98)

- `spec/verbs/` split into `common/` (55 cross-OS verbs) and `windows/`
  (33 Windows-specific verbs that depend on UI Automation, the Win32
  registry, Win32 power APIs, or the Win32 message queue). Foundation for
  future cross-OS family additions.
- New `portability_tier` field in `families.json` (`"windows"` for the
  three Windows families; `"common"` reserved for future macOS / Linux).

### Vision (rolled in from never-tagged v2.1.0 final)

- Native OCR via `vision.ocr` (Windows.Media.Ocr.OcrEngine on
  windows-modern; `implemented: false` on windows-classic). Five-way
  mutually-exclusive input selector: `region` / `window` / `monitor`
  (live capture) and `path` / `bytes` (static image sources). Per-line
  bounding boxes with optional per-word granularity; `language` hint
  defaults to OS user-profile language; `coordinate_space` enum
  disambiguates screen vs image bbox coordinate systems.
- `system.info.capabilities` gains three OCR-related sub-keys on
  windows-modern: `ocr_languages`, `ocr_max_dimension`,
  `ocr_input_formats`. All absent on windows-classic.
- New error code: `image_too_large` (OCR sources exceeding the engine's
  `MaxImageDimension`); `unsupported_format` reused for codec-mismatch
  on `vision.ocr` path/bytes inputs.
- New `vision.*` namespace.

## v2.1.0 — never tagged (rolled into v2.2.0)

`v2.1.0-rc.3` was the latest ratified release on the v2.1 branch; the
final `v2.1.0` tag was never cut because the framing-modernisation work
landing in v2.2 was scoped while v2.1 was still in -rc cycles. v2.2.0
ships the v2.1 features (vision.ocr et al., per the section above)
alongside the framing-modernisation changes.

## v2.1.0-rc.2 — 2026-05-04

- v2.1 working tree: CRUDX tier ladder (`read` < `create` < `update` <
  `delete` < `extra_risky`) replacing v2.0's three-tier model;
  `clipboard.read`/`write` renamed to `clipboard.get`/`set`; new
  `directory.*` namespace split out of `file.*` with full CRUDX-complete
  primitives; `system.*` power verbs re-namespaced to `system.power.*`;
  `registry.*` restructured into resource-first
  `registry.value.{read,create,update,delete}` + `registry.key.{read,delete}`;
  `input.*` split into `input.mouse.*` + `input.keyboard.*` sub-namespaces
  (rc.3); header-line argument quoting (`"path with spaces"`);
  source-of-truth `spec/` tree with `dist/`-rendered artefacts.

## v2.0.0

- First ratified release of the Protocol 2.0 spec.
- Three-tier model: `observe` < `drive` < `power` (superseded in v2.1 by
  the CRUDX ladder).
- Verb namespaces: connection, system, screen, window, input, element,
  file, process, registry, clipboard, watch.

For older history, see git log.
