# Verb authoring progress

Parity manifest for the per-verb authoring pass. Every v2 verb in the spec has a row; every row's status flips ⬜ → 🟨 → ✅ as authoring progresses. The migration to `dist/`-rendered docs (deletion of root [`PROTOCOL.md`](../PROTOCOL.md) / [`VERBS.md`](../VERBS.md)) is gated on every row reaching ✅.

Per-verb completion definition: [`AUTHORING-CHECKLIST.md`](AUTHORING-CHECKLIST.md). Three sequential stages per verb (Stage A — skeleton, Stage B — `windows-modern`, Stage C — `windows-classic`).

Source-of-truth for citations:

- **PROTOCOL.md** = `PROTOCOL.md` at HEAD; cited as `§4.X:NNN` (subsection : verb-row line number).
- **VERBS.md** = `VERBS.md` at HEAD; cited as `:NNN` (line number).
- **spec/verbs** = `spec/verbs/<verb>.json` at HEAD. ✅ if a (mock-up) file exists today; per the locked decision in the plan, every row is re-authored from scratch regardless.
- **v1 archive** = the v1 verb name in `git show af6c413:PROTOCOL.md`. The v1 archive lives only in git history (commit `af6c413`); not present in the working tree.
- **Conformance** = `tests/conformance/test_<namespace>.py` if the verb is exercised. Symbol-level grep confirms each ✅.

Status legend: ⬜ not started · 🟨 in progress · ✅ done.

---

## `connection.*` (5 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 1 | `connection.hello` | ✅ | §4.12:457 | :149 | ✅ (mock) | ❌ | `test_connection.py` |
| 2 | `connection.tier_raise` | ✅ | §4.12:458 | :150 | ❌ | ❌ | `test_connection.py` |
| 3 | `connection.tier_drop` | ✅ | §4.12:459 | :151 | ❌ | ❌ | (inferred — no explicit test) |
| 4 | `connection.reset` | ✅ | §4.12:460 | :152 | ❌ | ❌ | ❌ |
| 5 | `connection.close` | ✅ | §4.12:461 | :153 | ❌ | `QUIT` / `EXIT` / `BYE` (consolidated) | `test_connection.py` |

## `system.*` (11 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 6 | `system.info` | ✅ | §4.1:284 | :23 | ✅ (mock) | `INFO` | `test_system.py` |
| 7 | `system.capabilities` | ✅ | §4.1:285 | :24 | ❌ | `CAPS` | `test_system.py` |
| 8 | `system.health` | ✅ | §4.1:286 | :25 | ❌ | `PING` | `test_system.py` |
| 9 | `system.shutdown_blockers` | ✅ | §4.1:287 | :26 | ❌ | ❌ | `test_system.py` |
| 10 | `system.lock` | ✅ | §4.1:288 | :27 | ❌ | `LOCK` | ❌ |
| 11 | `system.reboot` | ✅ | §4.1:289 | :28 | ❌ | `REBOOT` | `test_system.py` |
| 12 | `system.shutdown` | ✅ | §4.1:290 | :29 | ✅ (mock) | `SHUTDOWN` | `test_system.py` |
| 13 | `system.logoff` | ✅ | §4.1:291 | :30 | ❌ | `LOGOFF` | ❌ |
| 14 | `system.hibernate` | ✅ | §4.1:292 | :31 | ❌ | ❌ | ❌ |
| 15 | `system.sleep` | ✅ | §4.1:293 | :32 | ❌ | ❌ | ❌ |
| 16 | `system.power.cancel` | ✅ | §4.1:294 | :33 | ❌ | ❌ | `test_system.py` |

## `screen.*` (1 verb)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 17 | `screen.capture` | ✅ | §4.2:313 | :39 | ✅ (mock) | `SHOT` / `SHOTRECT` / `SHOTWIN` (consolidated) | `test_screen.py` |

## `window.*` (6 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 18 | `window.list` | ✅ | §4.3:325 | :45 | ✅ (mock) | `WINLIST` | `test_window.py` |
| 19 | `window.find` | ✅ | §4.3:326 | :46 | ❌ | `WINFIND` | ❌ |
| 20 | `window.focus` | ✅ | §4.3:327 | :47 | ❌ | `WINFOCUS` | `test_window.py` |
| 21 | `window.close` | ✅ | §4.3:328 | :48 | ❌ | `WINCLOSE` | ❌ |
| 22 | `window.move` | ✅ | §4.3:329 | :49 | ✅ (mock) | `WINMOVE` / `WINSIZE` (consolidated) | ❌ |
| 23 | `window.state` | ✅ | §4.3:330 | :50 | ❌ | `WINMIN` / `WINMAX` / `WINRESTORE` (consolidated → query) | `test_window.py` |

## `input.*` (7 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 24 | `input.click` | ✅ | §4.4:338 | :56 | ✅ (mock) | `CLICK` | `test_input.py` |
| 25 | `input.move` | ✅ | §4.4:339 | :57 | ❌ | `MOVE` | `test_input.py` |
| 26 | `input.scroll` | ✅ | §4.4:340 | :58 | ❌ | `WHEEL` | ❌ |
| 27 | `input.key` | ✅ | §4.4:341 | :59 | ❌ | `KEY` | `test_input.py` |
| 28 | `input.type` | ✅ | §4.4:342 | :60 | ❌ | `KEYS` | `test_input.py` |
| 29 | `input.send_message` | ✅ | §4.4:343 | :61 | ❌ | ❌ | ❌ |
| 30 | `input.post_message` | ✅ | §4.4:344 | :62 | ❌ | ❌ | ❌ |

## `element.*` (14 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 31 | `element.list` | ✅ | §4.5:362 | :68 | ❌ | `ELEMENTS` | `test_element.py` |
| 32 | `element.tree` | ✅ | §4.5:363 | :69 | ❌ | `ELEMENT_TREE` | ❌ |
| 33 | `element.at` | ✅ | §4.5:364 | :70 | ❌ | `ELEMENT_AT` | ❌ |
| 34 | `element.find` | ✅ | §4.5:365 | :71 | ✅ (mock) | `ELEMENT_FIND` | `test_element.py` |
| 35 | `element.wait` | ✅ | §4.5:366 | :72 | ❌ | ❌ | `test_element.py` |
| 36 | `element.find_invoke` | ✅ | §4.5:367 | :73 | ❌ | ❌ | ❌ |
| 37 | `element.at_invoke` | ✅ | §4.5:368 | :74 | ❌ | ❌ | ❌ |
| 38 | `element.invoke` | ✅ | §4.5:369 | :75 | ❌ | `ELEMENT_INVOKE` | `test_element.py` |
| 39 | `element.toggle` | ✅ | §4.5:370 | :76 | ❌ | `ELEMENT_TOGGLE` | ❌ |
| 40 | `element.expand` | ✅ | §4.5:371 | :77 | ❌ | `ELEMENT_EXPAND` | ❌ |
| 41 | `element.collapse` | ✅ | §4.5:372 | :78 | ❌ | `ELEMENT_COLLAPSE` | ❌ |
| 42 | `element.focus` | ✅ | §4.5:373 | :79 | ❌ | `ELEMENT_FOCUS` | ❌ |
| 43 | `element.text` | ✅ | §4.5:374 | :80 | ❌ | `ELEMENT_TEXT` | ❌ |
| 44 | `element.set_text` | ✅ | §4.5:375 | :81 | ❌ | `ELEMENT_SET_TEXT` | ❌ |

## `file.*` (9 verbs)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 45 | `file.read` | ✅ | ✅ (mock) | `READ` | `test_file.py` |
| 46 | `file.write` | ✅ | ✅ (mock) | `WRITE` | `test_file.py` |
| 47 | `file.write_at` | ✅ | ❌ | ❌ | ❌ |
| 48 | `file.stat` | ✅ | ❌ | `STAT` | ❌ |
| 49 | `file.delete` | ✅ | ✅ (mock) | `DELETE` | `test_file.py` |
| 50 | `file.exists` | ✅ | ❌ | ❌ | `test_file.py` |
| 51 | `file.wait` | ✅ | ❌ | ❌ | ❌ |
| 52 | `file.rename` | ✅ | ❌ | `RENAME` | ❌ |
| 53 | `file.download` | ✅ | ✅ (mock) | ❌ | ❌ |

The PROTOCOL.md columns are dropped post-audit (PROTOCOL.md being deleted; mock-ups are the contract). `file.download` was previously listed as an "anomaly" — now formally part of the `file.*` namespace.

## `directory.*` (6 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 54 | `directory.list` | ✅ | §4.7:400 | :100 | ✅ (mock) | `LIST` (renamed from `file.list`) | `test_directory.py` |
| 55 | `directory.stat` | ✅ | §4.7:401 | :101 | ✅ (mock) | ❌ | `test_directory.py` |
| 56 | `directory.exists` | ✅ | §4.7:402 | :102 | ✅ (mock) | ❌ | `test_directory.py` |
| 57 | `directory.create` | ✅ | §4.7:403 | :103 | ✅ (mock) | `MKDIR` (renamed from `file.mkdir`) | `test_directory.py` |
| 58 | `directory.rename` | ✅ | §4.7:404 | :104 | ✅ (mock) | ❌ | `test_directory.py` |
| 59 | `directory.remove` | ✅ | §4.7:405 | :105 | ✅ (mock) | ❌ | `test_directory.py` |

## `process.*` (5 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 60 | `process.list` | ✅ | §4.8:413 | :111 | ❌ | `PS` | `test_process.py` |
| 61 | `process.start` | ✅ | §4.8:414 | :112 | ❌ | `EXEC` | `test_process.py` |
| 62 | `process.shell` | ✅ | §4.8:415 | :113 | ❌ | ❌ | ❌ |
| 63 | `process.kill` | ✅ | §4.8:416 | :114 | ❌ | `KILL` | `test_process.py` |
| 64 | `process.wait` | ✅ | §4.8:417 | :115 | ❌ | `WAIT` | `test_process.py` |

## `registry.*` (4 verbs, all Windows-specific)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 65 | `registry.read` | ✅ | §4.9:425 | :121 | ❌ | ❌ | `test_registry.py` |
| 66 | `registry.write` | ✅ | §4.9:426 | :122 | ❌ | ❌ | ❌ |
| 67 | `registry.delete` | ✅ | §4.9:427 | :123 | ❌ | ❌ | ❌ |
| 68 | `registry.wait` | ✅ | §4.9:428 | :124 | ❌ | ❌ | ❌ |

## `clipboard.*` (2 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 69 | `clipboard.get` | ✅ | §4.10:434 | :130 | ✅ (mock) | `CLIPGET` (renamed from `clipboard.read`) | `test_clipboard.py` |
| 70 | `clipboard.set` | ✅ | §4.10:435 | :131 | ✅ (mock) | `CLIPSET` (renamed from `clipboard.write`) | `test_clipboard.py` |

## `watch.*` (7 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 71 | `watch.region` | ✅ | §4.11:443 | :137 | ❌ | `WATCH` (screen-only — narrowed in v2) | `test_watch.py` |
| 72 | `watch.process` | ✅ | §4.11:444 | :138 | ❌ | ❌ | `test_watch.py` |
| 73 | `watch.window` | ✅ | §4.11:445 | :139 | ❌ | ❌ | `test_watch.py` |
| 74 | `watch.element` | ✅ | §4.11:446 | :140 | ❌ | ❌ | ❌ |
| 75 | `watch.file` | ✅ | §4.11:447 | :141 | ❌ | ❌ | ❌ |
| 76 | `watch.registry` | ✅ | §4.11:448 | :142 | ❌ | ❌ | ❌ |
| 77 | `watch.cancel` | ✅ | §4.11:449 | :143 | ❌ | `ABORT` (subscription-scoped only — see drops) | `test_watch.py` |

---

## Tally

| Status | Count |
|---|---|
| Total v2 verbs | 76 |
| With existing `spec/verbs/*.json` mock-ups | 20 |
| Without (need authoring from cold) | 56 |
| Currently exercised by conformance suite | 36 |
| With v1 ancestor verb(s) | 41 |
| v2-only (no v1 ancestor) | 35 |

(All 76 are ⬜ because the locked plan re-authors every verb from scratch; the "with mock-ups" column is informational, not a partial-credit ✅.)

---

## v1 capabilities not carried forward into v2 (today)

Two states: **hard drops** (no open re-introduction proposal) and **under reconsideration** (re-introduction is an open enhancement issue, decision pending). Authoring-pass authors check the second table before assuming a capability is permanently gone.

The v1 archive (`git show af6c413:PROTOCOL.md`) is the authoritative reference for original wire shapes.

### Hard drops

| v1 verb(s) | Capability | Reason for dropping |
|---|---|---|
| `IDLE` | User input idle time (since last keyboard / mouse) | Use-case never substantiated. Re-introducible if real demand appears. |
| `DRIVES` | Filesystem root list (drive letters / mount points) | Subsumable under `directory.list "\\"` (or equivalent). Standalone verb was an artefact of the v1 convention that filesystem roots were special. |
| `ENV` | Read environment variable | Composable via `process.start "cmd /c echo %VAR%"` or equivalent. v2 doesn't add a dedicated verb for what's a one-line shell read. |
| `WAITFOR` | Combined wait-on-screen / wait-on-file | v2 splits cleanly: `file.wait` for file paths, `watch.region --until-change` for screen regions. The v1 single verb conflated two semantically-different waits. |
| `ABORT` (global form) | Cancel all in-flight verbs on all connections | v2 `watch.cancel` cancels a single subscription by id. The v1 global form was a cross-connection denial-of-service vector; restricting to subscription-scope is the v2 safety improvement. |

### Under reconsideration (open enhancement issues)

| v1 verb(s) | Capability | v2 re-intro under | Issue |
|---|---|---|---|
| `MPOS` | Cursor position query | `input.position` | [#69](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/69) (high-priority) |
| `MOVEREL` | Relative cursor movement | `input.move` extension (relative offsets) | [#71](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/71) |
| `DCLICK` | Double-click primitive | `input.click` extension (atomic double-click) | [#72](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/72) |
| `MDOWN`, `MUP` | Mouse button hold / release | `input.mouse_down` / `input.mouse_up` | [#67](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/67) (high-priority) |
| `DRAG` | Drag primitive (move-while-held) | `input.drag` | [#68](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/68) (high-priority) |
| `KEYDOWN`, `KEYUP` | Key hold / release | `input.key_down` / `input.key_up` | [#70](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/70) |
| `SCREEN` | Per-monitor dimensions query | extension to `system.info.monitors` | [#74](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/74) (high-priority) |

When one of these issues is resolved, the row migrates either to the verb's `spec/verbs/<verb>.json` (with `x-since` set to the cut version) or to the hard-drops table above.

---

## Open enhancements per verb

Cross-reference of open GitHub enhancement issues that touch verbs in this manifest. When the verb's row comes up in the authoring pass, check the linked issue and decide whether to spec the current behaviour or the proposed extension.

| Verb | Open issues |
|---|---|
| `connection.hello` | [#77](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/77) — response body with protocol identity / session_id (mock-up shape, formalised in v2.1.0) |
| `screen.capture` | [#66](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/66) — optional cursor overlay (high-priority); [#83](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/83) — format/quality split + jpeg/heic forward-compat; [#91](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/91) — `encoding` selector (base64 default, binary opt-in) |
| `system.info` | [#74](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/74) — per-monitor dimensions in mock-up's `screens` field (high-priority); [#80](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/80) — `os_name` field; [#82](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/82) — `capabilities.wake_timer_supported` flag; [#86](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/86) — `capabilities.input_settings` for OS input-timing values |
| `system.hibernate` | [#82](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/82) — `wake_at` + `force` for scheduled wake (capability-gated for VMs) |
| `system.sleep` | [#82](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/82) — `wake_at` + `force` (same as hibernate) |
| `window.find` | [#75](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/75) — title-pattern semantics |
| `window.move` | [#73](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/73) — atomic move-and-foreground (formalised post-audit; `foreground` flag + `foreground_status` enum) |
| `input.click` | [#72](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/72) — atomic double-click (mock-up has `double` flag; lock the SendInput batch implementation); [#87](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/87) — `target_handle` + `actual_position` response fields |
| `input.move` | [#71](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/71) — relative offsets |
| `input.scroll` | [#88](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/88) — `horizontal: bool` for tilt-wheel / shift-wheel |
| `input.send_message` | [#89](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/89) — return LRESULT in response body |
| `element.find` / `element.wait` | [#90](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/90) — `automation_id` + `root` for stable matching and subtree scoping (mock-up already has these fields; #90 formalises them) |
| `element.list` / `element.find` / `element.at` / `element.tree` / `element.wait` | [#92](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/92) — `flags` array (UIA boolean state) on result-bearing verbs + `flags_required` matcher on element.wait |
| `process.wait` | [#76](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/77) — optional/indefinite timeout |
| _(new verb)_ | [#69](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/69) — `input.position` (high-priority) |
| _(new verb)_ | [#67](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/67) — `input.mouse_down` / `input.mouse_up` (high-priority) |
| _(new verb)_ | [#68](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/68) — `input.drag` (high-priority) |
| _(new verb)_ | [#70](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/70) — `input.key_down` / `input.key_up` |

**Closed during the audit** (PROTOCOL.md→mock-up alignment issues, obsoleted by PROTOCOL.md deletion): #78 (os/arch renames — mock-up already used `family`), #79 (integrity null→none — mock-up has no integrity field), #81 (PROTOCOL.md §4.1:291 logoff flags fix — PROTOCOL.md deleted), #84 (project-wide bounds standardization — mock-ups already consistent), #85 (window.list filter semantics — mock-up has no filter field).

Run `gh issue list --state open --label enhancement` before each verb's authoring round to catch any new issues this list doesn't yet reflect.

---

## Per-namespace conventions (established during the authoring pass)

Captures the load-bearing preferences confirmed for each namespace so the same questions don't get re-asked verb-by-verb. Apply automatically; only escalate when a verb breaks the pattern.

### Cross-cutting (apply to every verb)

- **Mock-up first.** When a `spec/verbs/<verb>.json` mock-up file exists at HEAD, treat it as the ratified contract. Do NOT strip fields, rename fields, or change shapes to match PROTOCOL.md (which is being deleted). When the mock-up shape and PROTOCOL.md disagree, follow the mock-up. PROTOCOL.md is loose-reference only.
- **Ask, don't assume.** When a mock-up has fields that look invented (encoding/offset/length on file.read, automation_id on element.find, etc.), ASK the user — those may be intentional design that PROTOCOL.md hasn't caught up to.
- **Description budget:** top-level `description` is 1–2 sentences, action-focused. `input_schema.properties.<f>.description` is similarly tight. Per-family description and per-output-schema field descriptions are richer (1–4 sentences, humans-only).
- **x-crudx letter:** R/C/U/D/X. Lifecycle verbs use `R` to preserve the lifecycle exemption.
- **x-errors:** only errors the verb's own handler returns. Errors raised by upstream layers (framing, lifecycle, validation) on behalf of the verb don't appear here.
- **x-implementations:** required on every verb. Backend names are short, grep-able, snake_case. `agent_native` for verbs handled inline by the agent process.
- **strict:false carve-out:** allowed for verbs with intrinsically open response shapes (e.g. open-ended maps); requires `x-strict-false-reason` field justifying the carve-out.
- **`handle` not `hwnd`:** cross-OS-friendly field name for window handles. Used across window.* and input.click's target_handle response field. The values still take Windows-specific forms like `win:0x...`.
- **Reserved-name guard:** filenames and `name` fields cross-checked against `spec/reserved-names.json` by `tests/check_spec.py`.
- **Wire changes get GitHub issues:** any genuine wire-shape addition (new field, new flag, new response key) lands as an issue tagged `enhancement`, milestoned to the next cut (currently v2.1.0). Issues that were tracking PROTOCOL.md→mock-up alignment are obsolete (close them).
- **VM / legacy-OS caveats:** go in `x-families.<f>.description`, never in the LLM-facing `description`.

### `connection.*` (5/5 done)

- **Lifecycle-mirror precedent:** per-family `description` is identical across `windows-modern` and `windows-classic` for verbs that have no Windows-specific behaviour. Single backend `agent_native`. Used for: hello, tier_raise, tier_drop, reset, close.
- **Token-file metadata** (path + ACL) lives in `spec/families.json` per family, not in `connection.tier_raise.json`. Validated as required by `tests/check_spec.py`.
- **Empty-body responses** declared as `x-output-schema: { type: "null", description: "Empty body — wire response is the literal `OK 0`." }`. Used for: tier_drop, reset, close.
- **Hello has a body** per the mock-up: `{protocol, version, server, server_version, session_id}`. Mock-up's input is single `client_version` arg.

### `system.*` (11/11 done)

- **Power-control template** (reboot, shutdown, logoff): mock-up shape — `delay_seconds: int` + `force: bool` + `reason: string`; `x-output-schema: {scheduled_at: ISO date-time}`; `x-errors: ["insufficient_privilege", "policy_blocked"]`; per-family API choice (`InitiateSystemShutdownExW` modern, `ExitWindowsEx(EWX_*)` classic).
- **system.info post-audit shape:** mock-up's 6 fields — `family, os_name (#80), os_version, hostname, screens, capabilities` — strict-authored. `screens` is the per-monitor array (issue #74). `capabilities` is the open-ended map (strict:false on the verb) carrying `wake_timer_supported` (#82), `input_settings` (#86), and family-specific feature flags.
- **strict:false** for verbs with open-ended response maps (`system.info.capabilities`, `system.capabilities`'s verb-name keys). x-strict-false-reason documents the carve-out.
- **`reason` flag format:** free string, accepting symbolic (`SHTDN_REASON_MAJOR_APPLICATION`) or numeric (`0x80000003`). Agent emitter parses.
- **windows-classic `implemented: false`** for verbs that genuinely require modern-only Win32 APIs (e.g. `system.shutdown_blockers` needs Vista+ `ShutdownBlockReasonQuery`). One-line `reason` field cites the missing capability.
- **windows-classic implemented across most family** for power/lock verbs that have NT-era equivalents. Family description notes the per-OS-version cliffs (e.g. NT 4 SP4+ for LockWorkStation; pre-XP silently ignores `reason`).
- **VM caveat** added to windows-modern description for verbs whose hypervisor behavior is unreliable (e.g. `system.hibernate`).
- **LLM operator already has x-since / x-crudx** for every verb at tool-registration time (from spec/verbs/*.json or compiled dist/verbs.json), so `system.capabilities` doesn't duplicate that metadata on the wire.

### `screen.*` (1/1 done)

- **Response encoding:** mock-up has `{type: string, format: byte}` (base64). Default kept as base64; `encoding: enum [base64, binary]` field added (#91) so callers can opt into raw bytes.
- **Mutually-exclusive selector pattern:** `region` / `window` / `monitor` are mutually exclusive; the agent captures the full virtual screen if none is supplied. Encoded as `x-mutually-exclusive: ["region", "window", "monitor"]`.
- **Object form for region:** schema uses `region: { x, y, w, h }` (object). Bridge handles wire serialisation.
- **Three-implementation chain:** `wgc` (modern WGC fast path), `print_window` (window-specific), `gdi_bitblt` (universal fallback).
- **format/quality split** (per #83): `format: enum [png,webp,bmp,jpeg,heic]` + optional `quality: int 1-100`. `jpeg`/`heic` are forward-compat for future macOS family — mock-up already had them in the enum.
- **`capture_path` per family:** ordered list of capture engines used (e.g. `["wgc", "gdi"]` modern, `["gdi"]` classic).
- **`formats` + `formats_runtime_extra` per family:** mock-up convention — `formats` is the always-supported set, `formats_runtime_extra` lists formats probed at startup (e.g. PNG via GDI+ on classic).

### `window.*` (6/6 done)

- **`handle` field name** (not `hwnd`) for window handles in inputs and outputs. Cross-OS-friendly — values like `win:0x1A2B` on Windows or `mac:42` on macOS when other families land.
- **`bounds: {x,y,w,h}` nested via `$ref: "#/$defs/Bounds"`** for return values. The `$defs.Bounds` block is duplicated in each verb file (no external refs allowed in strict mode).
- **window.list mock-up shape:** input is `visible_only: bool` (default true) + `pid: int`. Output is a BARE ARRAY of `{handle, title, pid, bounds}` items — no `{windows: [...]}` wrap.
- **window.find** (no mock-up): pattern-based finder using case-insensitive substring against window title (#75 convention). Returns single item shape matching window.list items.
- **window.move mock-up shape:** flat input `handle, x, y, w?, h?` (w/h optional — preserve when omitted). Returns `{bounds: {x,y,w,h}}` (final bounds). Per #73 the response also adds `prior_bounds` (for restore symmetry) and `foreground_status` enum (for the optional `foreground: bool` flag).
- **window.focus returns `prior_handle`** (parallel to window.move's `prior_bounds`) for restore-state symmetry.
- **UIPI caveat in family description**: any verb that posts messages or alters cross-process windows mentions UIPI's "post succeeds, delivery silently fails" failure mode in `windows-modern`'s description (window.close, window.move).

### `input.*` (7/7 done)

- **input.click mock-up shape:** `{x, y, button?, double?, modifiers?}` input; `{synthesised: bool}` response. `synthesised` defined as "reached user32" — false when the agent post-detects a UIPI silent-drop. Per #87 the response also gains `target_handle` + `actual_position` for target-moved-race + clamping diagnostics.
- **`modifiers: array of enum [ctrl, shift, alt, meta]`** convention used on input.click and input.key. Each modifier is synthesised down before the operation, up after.
- **input.move / input.scroll return `actual_position: {x,y}`** (per #71 and #88 lock-ins) — lets callers detect clamping. input.move also gains `relative: bool` per #71.
- **input.scroll** also gains `horizontal: bool` per #88 for tilt-wheel / shift-wheel.
- **input.send_message returns `lresult: integer`** (per #89) — the synchronous Win32 SendMessage return value. input.post_message stays empty body (PostMessage's BOOL is just post-success, not a meaningful response).
- **input.key / input.type return empty body** — no useful confirmation field for synth-only verbs that target the focused window implicitly.
- **RawInput / DirectInput limitation called out** in family description for input.key and input.type (per issue #64) — synthetic keyboard events don't reach Unity / DirectX game input loops.
- **Two-implementation chain pattern**: `send_input` (modern + classic NT 5+) preferred; `mouse_event` / `keybd_event` (classic NT 4 / 9x) fallback.
- **UIPI `post-check` mismatch detection** documented in windows-modern descriptions: agent verifies post-synth state (e.g. WindowFromPoint, GetForegroundWindow) and returns `ERR uipi_blocked` when the IL barrier silently dropped the event.
- **wparam / lparam encoding** (input.send_message, input.post_message): `integer` (signed 64-bit), description notes bridge accepts hex strings (`"0x..."`) for readability.

### `element.*` (14/14 done)

- **All UIA-based; `implemented: false` on windows-classic** — UIA is Vista+. Each verb's classic family slot uses `{ "implemented": false, "reason": "Requires UI Automation (Vista+)." }`. MSAA/IAccessible fallback explicitly out of scope.
- **`handle` field name** for element handles (`elt:N` form, connection-scoped) — same `handle` convention as window.*.
- **`bounds: {x,y,w,h}` nested via `$ref: "#/$defs/Bounds"`** for every element-result item. The `$defs.Bounds` block is duplicated in each verb file.
- **Standard element-result shape** (list, find, at, wait): `{handle, role?, name?, automation_id?, bounds, flags?}` — `handle` and `bounds` required; the rest optional. element.tree adds `depth`. find_invoke / at_invoke return empty body.
- **`automation_id` + `root` enhancement** (per #90, mock-up already had these on element.find): stable-identifier matching + subtree scoping. Applied to element.find_invoke and element.wait too.
- **`flags` + `flags_required`** (per #92): result-bearing verbs return `flags: array of enum` (universal UIA boolean state — `enabled`, `focused`, `offscreen`, `password`, `required`). element.wait gains `flags_required` input — polls until matching element exists AND its state includes those flags.
- **`name` field** (mock-up convention) for the matcher input, NOT `pattern`. Case-insensitive substring against UIA Name property.
- **All matcher fields optional** on element.find / element.wait — agent returns ERR invalid_args if all are omitted. Lets callers find-by-automation_id alone or find-by-role alone when sufficient.
- **`timeout_ms` on element.find** (mock-up convention, default 2000 ms) — built-in retry. element.wait is the explicit polling form for longer waits with `flags_required` matching.
- **State-returning action verbs** (toggle/expand/collapse): return `{new_state: enum}` so callers know post-action state without a follow-up read.
- **`uia_blind` vs `not_found`**: `uia_blind` = couldn't see across IL barrier; `not_found` = search ran cleanly but matched zero. Distinct codes for "elevate and retry" vs "the element doesn't exist".
- **`target_gone` for stale handles**; **`not_supported_by_target`** for elements lacking the relevant UIA pattern (invoke/toggle/expand/collapse/focus/set_text/text); **`readonly`** specifically when ValuePattern.IsReadOnly=true on set_text.

### `file.*`, `directory.*`, `process.*`, `registry.*`, `clipboard.*`, `watch.*`

Conventions to be established as each namespace is reached.

---

## Wire-change docket (queued for the next tag)

Authoring decisions made during the per-verb pass that are wire-protocol changes — not just spec authoring. These need PROTOCOL.md edits, CHANGELOG entries, conformance updates, and a coordinated agent-repo PR. They land together as the next wire-version cut (v2.2.0 since each is additive). The doc-mechanic migration (root PROTOCOL.md / VERBS.md → `dist/`-rendered) rides along with this tag per the locked plan.

| # | Verb | Change | PROTOCOL.md edits | CHANGELOG | Conformance | Agent repo |
|---|---|---|---|---|---|---|
| 1 | `connection.hello` ([#77](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/77)) | Mock-up's response body `{protocol, version, server, server_version, session_id}` becomes the formal contract. | "`connection.hello` response body formalised per the mock-up." | Field-presence assertions in `tests/conformance/test_connection.py` for the 5 fields. | Implement response body in modern + classic agents; bump version; update SUPPORTED.md. |
| 2 | `system.info` ([#74](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/74)) | Strict-author the mock-up's `screens` field as an array of per-monitor `{index, bounds: {x,y,w,h}, primary, scale?}`. | "`system.info.screens` strict-typed for per-monitor geometry." | Per-monitor geometry assertions in `tests/conformance/test_system.py`. | `EnumDisplayMonitors` + `GetMonitorInfo` + `GetDpiForMonitor` aggregation; classic agents skip `scale`. |
| 3 | `system.info` ([#80](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/80)) | Add required `os_name: string` field (companion to mock-up's existing `os_version: string`). | "`system.info` adds `os_name` field." | Assert `os_name` present and non-empty. | Implement via `RtlGetVersion` + product-name lookup (modern) / `GetVersionEx` (classic). |
| 4 | `system.hibernate` / `system.sleep` ([#82](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/82)) | Add `wake_at: int` + `force: bool` for scheduled wake-up; gate behind `system.info.capabilities.wake_timer_supported` (auto-false on detected VMs); `force: true` bypasses. | "`system.hibernate` and `system.sleep` gain `wake_at` + `force`; `system.info.capabilities.wake_timer_supported` advertises feasibility." | Bare-metal scheduled wake succeeds; VM gating returns `ERR not_supported` without `force`; `force: true` proceeds. | Modern + classic agents: VM detection (CPUID hypervisor bit, WMI Manufacturer match) + `SetWaitableTimerEx` arming. |
| 5 | `system.info` ([#86](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/86)) | Add `capabilities.input_settings: { double_click_time_ms, double_click_rect, keyboard_repeat_delay_ms, keyboard_repeat_rate_cps, wheel_scroll_lines? }`. | "`system.info.capabilities.input_settings` advertises OS input timing values." | Assert positive integer values for each timing field. | Modern: read GetDoubleClickTime + SPI_*. Classic NT 4 omits wheel_scroll_lines. |
| 6 | `screen.capture` ([#66](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/66)) | Add `cursor: bool` field (default false) for cursor overlay. | "`screen.capture` gains optional cursor overlay." | Cursor present when true, absent when false; off-region/hidden cursors no-op. | GetCursorInfo + DrawIcon composited onto bitmap before format encoding. |
| 7 | `screen.capture` ([#83](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/83)) | Split format-with-quality `webp:N` shorthand into `format: enum` + `quality: int 1-100`. | "`screen.capture` splits format/quality." | Replace webp:70 fixtures with format=webp + quality=70. | Parser update; `spec/families.json` carries per-family `formats` and `formats_runtime_extra` arrays. |
| 8 | `screen.capture` ([#91](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/91)) | Add `encoding: enum [base64, binary]` (default base64; binary opt-in) to let callers avoid 33% base64 inflation. | "`screen.capture.encoding` selector for raw-bytes opt-in." | Both encoding values produce the expected bytes. | Modern + classic agent emitters honour the field. |
| 9 | `window.move` ([#73](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/73)) | Add `foreground: bool` for atomic move-and-foreground; response also carries `prior_bounds` + `foreground_status` alongside the mock-up's `bounds`. | "`window.move` gains `foreground` flag; response carries `prior_bounds` + `foreground_status`." | Atomic move+foreground; lock_held partial-success path. | Modern + classic agents emit prior_bounds; SetForegroundWindow attempt with status capture. |
| 10 | `input.click` ([#87](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/87)) | Mock-up's `synthesised: bool` retained with "reached user32" semantics; response also gains `target_handle` + `actual_position` body. | "`input.click` response gains `target_handle` + `actual_position` (synthesised meaning locked)." | target_handle matches expected window; actual_position reports clamped coords. | Modern + classic agents: WindowFromPoint at synth time; UIPI mismatch detection. |
| 11 | `input.move` ([#71](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/71)) | Add `relative: bool` flag; response gains `actual_position: {x,y}`. | "`input.move` gains `relative` flag and `actual_position` response." | Relative + clamping conformance tests. | GetCursorPos + add + SendInput(MOUSEEVENTF_VIRTUALDESK \| MOUSEEVENTF_ABSOLUTE). |
| 12 | `input.scroll` ([#88](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/88)) | Add `horizontal: bool` for tilt-wheel / shift-wheel; response gains `actual_position`. | "`input.scroll` gains `horizontal` flag and `actual_position` response." | Horizontal scroll observed in horizontally-scrollable target. | MOUSEEVENTF_HWHEEL on Vista+; pre-Vista classic silently no-ops. |
| 13 | `input.send_message` ([#89](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/89)) | Return `lresult: integer` in response body (was `OK 0`). | "`input.send_message` returns LRESULT in response body." | Send WM_GETTEXTLENGTH; verify lresult equals title length. | Modern + classic agents emit lresult. |
| 14 | `element.find` / `element.wait` ([#90](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/90)) | Mock-up's `automation_id` + `root` fields formalised across find / wait / find_invoke. | "`element.find` / `element.wait` formalise `automation_id` + `root`." | find by automation_id; find scoped to a root window. | UIA `IUIAutomationCondition` for AutomationId; `ElementFromHandle` for root resolution. |
| 15 | `element.list` / `element.find` / `element.at` / `element.tree` / `element.wait` ([#92](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/92)) | `flags: array of enum [enabled, focused, offscreen, password, required]` on result-bearing verbs (output) + `flags_required` on element.wait (input). | "`element.*` gain UIA-state `flags` array on outputs; element.wait gains `flags_required` matcher." | Returned elements list correct flags; flags_required gates the wait. | Modern agent: 5 CurrentIs* COM queries per element; wait-state polling. |
