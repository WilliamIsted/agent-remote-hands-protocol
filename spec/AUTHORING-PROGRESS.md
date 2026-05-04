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

The per-row **Conformance** columns below name the test file that exercises each verb when there is one. They were last refreshed before the 2026-05-03 conformance backfill — at this point `tests/check_spec.py` enforces that every verb in `spec/verbs/` has at least one `needs_verb(capabilities, "<verb>")` gate somewhere under `tests/conformance/test_*.py`, so any ❌ in the rows below is stale-and-will-be-reconciled rather than a real coverage gap. Authoritative source-of-truth: run `python tests/check_spec.py`.

---

## `connection.*` (5 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 1 | `connection.hello` | ✅ | §4.12:457 | :149 | ✅ (mock) | ❌ | `test_connection.py` |
| 2 | `connection.tier_raise` | ✅ | §4.12:458 | :150 | ❌ | ❌ | `test_connection.py` |
| 3 | `connection.tier_drop` | ✅ | §4.12:459 | :151 | ❌ | ❌ | (inferred — no explicit test) |
| 4 | `connection.reset` | ✅ | §4.12:460 | :152 | ❌ | ❌ | ❌ |
| 5 | `connection.close` | ✅ | §4.12:461 | :153 | ❌ | `QUIT` / `EXIT` / `BYE` (consolidated) | `test_connection.py` |

## `system.*` (3 verbs)

| # | Verb | Status | PROTOCOL.md | VERBS.md | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|---|---|
| 6 | `system.info` | ✅ | §4.1:284 | :23 | ✅ (mock) | `INFO` | `test_system.py` |
| 7 | `system.capabilities` | ✅ | §4.1:285 | :24 | ❌ | `CAPS` | `test_system.py` |
| 8 | `system.health` | ✅ | §4.1:286 | :25 | ❌ | `PING` | `test_system.py` |

## `system.power.*` (8 verbs — migrated from `system.*` in v2.1.0-rc.2)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 9 | `system.power.shutdown` | ✅ | ✅ (renamed from `system.shutdown`) | `SHUTDOWN` | `test_system.py` |
| 10 | `system.power.reboot` | ✅ | ✅ (renamed from `system.reboot`) | `REBOOT` | `test_system.py` |
| 11 | `system.power.logoff` | ✅ | ✅ (renamed from `system.logoff`) | `LOGOFF` | ❌ |
| 12 | `system.power.hibernate` | ✅ | ✅ (renamed from `system.hibernate`; gained `delay_seconds`+`reason`; `force`→`bypass_vm_check`) | ❌ | ❌ |
| 13 | `system.power.sleep` | ✅ | ✅ (renamed from `system.sleep`; gained `delay_seconds`+`reason`; `force`→`bypass_vm_check`) | ❌ | ❌ |
| 14 | `system.power.cancel` | ✅ | ✅ (CRUDX X→U) | ❌ | `test_system.py` |
| 15 | `system.power.blockers` | ✅ | ✅ (renamed from `system.shutdown_blockers`; output `hwnd`→`handle`) | ❌ | `test_system.py` |
| 16 | `system.power.lock` | ✅ | ✅ (renamed from `system.lock`; CRUDX R→X) | `LOCK` | ❌ |

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

## `input.*` (3 top-level verbs after the v2.1.0-rc.3 split)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 24 | `input.position` | ✅ | ✅ (NEW in rc.3 — closes #69) | `MPOS` | ❌ |
| 25 | `input.send_message` | ✅ | ✅ | ❌ | ❌ |
| 26 | `input.post_message` | ✅ | ✅ | ❌ | ❌ |

## `input.mouse.*` (6 verbs — sub-namespace introduced in v2.1.0-rc.3)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 27 | `input.mouse.click` | ✅ | ✅ (renamed from `input.click`; gained `duration_ms` 0-1000ms) | `CLICK` | `test_input.py` |
| 28 | `input.mouse.move` | ✅ | ✅ (renamed from `input.move`) | `MOVE` | `test_input.py` |
| 29 | `input.mouse.scroll` | ✅ | ✅ (renamed from `input.scroll`) | `WHEEL` | ❌ |
| 30 | `input.mouse.press` | ✅ | ✅ (NEW in rc.3 — closes #67 indefinite-hold half) | `MDOWN` | ❌ |
| 31 | `input.mouse.release` | ✅ | ✅ (NEW in rc.3 — closes #67 release half; idempotent) | `MUP` | ❌ |
| 32 | `input.mouse.drag` | ✅ | ✅ (NEW in rc.3 — closes #68) | `DRAG` | ❌ |

## `input.keyboard.*` (4 verbs — sub-namespace introduced in v2.1.0-rc.3)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 33 | `input.keyboard.key` | ✅ | ✅ (renamed from `input.key`; gained `duration_ms` 0-1000ms) | `KEY` | `test_input.py` |
| 34 | `input.keyboard.type` | ✅ | ✅ (renamed from `input.type`) | `KEYS` | `test_input.py` |
| 35 | `input.keyboard.key_down` | ✅ | ✅ (NEW in rc.3 — closes #70 hold half) | `KEYDOWN` | ❌ |
| 36 | `input.keyboard.key_up` | ✅ | ✅ (NEW in rc.3 — closes #70 release half; idempotent) | `KEYUP` | ❌ |

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

## `file.*` (10 verbs — narrowed to files-only in v2.1.0-rc.2; `file.write` split)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 45 | `file.read` | ✅ | ✅ (mock; output `size`→`bytes_read`) | `READ` | `test_file.py` |
| 46 | `file.create` | ✅ | ✅ (NEW; split out of `file.write`'s `create_only: true`) | ❌ | ❌ |
| 47 | `file.write` | ✅ | ✅ (narrowed to U-only; `create_only` flag dropped; ERR not_found if missing) | `WRITE` | `test_file.py` |
| 48 | `file.write_at` | ✅ | ✅ (auto-create-on-offset-0 dropped; ERR not_found if missing; new `x-conditional` truncate↔offset) | ❌ | ❌ |
| 49 | `file.stat` | ✅ | ✅ (files-only; timestamps `*_unix`→`*_unix_s`) | `STAT` | ❌ |
| 50 | `file.delete` | ✅ | ✅ (files-only; `recursive`/`not_empty` removed — use `directory.delete`) | `DELETE` | `test_file.py` |
| 51 | `file.exists` | ✅ | ✅ (files-only) | ❌ | `test_file.py` |
| 52 | `file.wait` | ✅ | ✅ (files-only) | ❌ | ❌ |
| 53 | `file.rename` | ✅ | ✅ (files-only — use `directory.rename` for directories) | `RENAME` | ❌ |
| 54 | `file.download` | ✅ | ✅ (mock; `dest_path`→`local_path`; `file.mkdir`→`directory.create` ref) | ❌ | ❌ |

The PROTOCOL.md columns are dropped post-audit (PROTOCOL.md being deleted; mock-ups are the contract). `file.download` was previously listed as an "anomaly" — now formally part of the `file.*` namespace.

## `directory.*` (6 verbs — `directory.remove`→`directory.delete` rename in v2.1.0-rc.2)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 55 | `directory.list` | ✅ | ✅ (gained `recursive`+`pattern`+`limit` inputs; per-entry `ctime_unix_s`+`atime_unix_s`; `_unix`→`_unix_s` suffix) | `LIST` (renamed from `file.list`) | `test_directory.py` |
| 56 | `directory.stat` | ✅ | ✅ (mock; `_unix`→`_unix_s`; `type: const`→`enum`) | ❌ | `test_directory.py` |
| 57 | `directory.exists` | ✅ | ✅ (mock) | ❌ | `test_directory.py` |
| 58 | `directory.create` | ✅ | ✅ (mock; `mode` field moved to per-family `fields_ignored` overlay; x-since 2.0→2.1; x-renamed-from `file.mkdir`) | `MKDIR` (renamed from `file.mkdir`) | `test_directory.py` |
| 59 | `directory.rename` | ✅ | ✅ (mock) | ❌ | `test_directory.py` |
| 60 | `directory.delete` | ✅ | ✅ (renamed from `directory.remove`; `removed: true` always-true field dropped) | ❌ | `test_directory.py` |

## `process.*` (5 verbs)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 61 | `process.list` | ✅ | ✅ (gained `include_counters` flag with full counter cookbook; `filter`→`pattern`) | `PS` | `test_process.py` |
| 62 | `process.start` | ✅ | ✅ (stripped future-extension note; narrative file added) | `EXEC` | `test_process.py` |
| 63 | `process.shell` | ✅ | ✅ (output `pid` widened to `[integer, null]`) | ❌ | ❌ |
| 64 | `process.kill` | ✅ | ❌ | `KILL` | `test_process.py` |
| 65 | `process.wait` | ✅ | ✅ (stripped `Per issue #76:` prefix from description) | `WAIT` | `test_process.py` |

## `registry.*` (6 verbs — restructured to resource-first CRUD in v2.1.0-rc.2; `registry.wait` consolidated into `watch.registry`)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 66 | `registry.value.read` | ✅ | ✅ (NEW; split out of `registry.read`'s single-value mode) | ❌ | `test_registry.py` |
| 67 | `registry.value.create` | ✅ | ✅ (NEW; split out of `registry.write` upsert; errors with `already_exists`) | ❌ | ❌ |
| 68 | `registry.value.update` | ✅ | ✅ (NEW; split out of `registry.write` upsert; errors with `not_found`) | ❌ | ❌ |
| 69 | `registry.value.delete` | ✅ | ✅ (NEW; split out of `registry.delete`'s single-value mode; `deleted: true` field dropped) | ❌ | ❌ |
| 70 | `registry.key.read` | ✅ | ✅ (NEW; split out of `registry.read`'s whole-key mode; returns names+types of values, not data) | ❌ | ❌ |
| 71 | `registry.key.delete` | ✅ | ✅ (NEW; split out of `registry.delete`'s whole-key mode; `recursive` flag preserved) | ❌ | ❌ |

## `clipboard.*` (2 verbs)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 72 | `clipboard.get` | ✅ | ✅ (mock; x-since 2.0→2.1; x-renamed-from `clipboard.read`) | `CLIPGET` (renamed from `clipboard.read`) | `test_clipboard.py` |
| 73 | `clipboard.set` | ✅ | ✅ (mock; x-since 2.0→2.1; x-renamed-from `clipboard.write`; output gained `format` echo) | `CLIPSET` (renamed from `clipboard.write`) | `test_clipboard.py` |

## `watch.*` (7 verbs)

| # | Verb | Status | spec/verbs | v1 archive | Conformance |
|---|---|---|---|---|---|
| 74 | `watch.region` | ✅ | ✅ (gained `encoding` input enum [binary, base64]; binary mode emits raw bytes, base64 mode emits JSON envelope) | `WATCH` (screen-only — narrowed in v2) | `test_watch.py` |
| 75 | `watch.process` | ✅ | ✅ (event payload reconciled with framing) | ❌ | `test_watch.py` |
| 76 | `watch.window` | ✅ | ✅ (event payload reconciled with framing) | ❌ | `test_watch.py` |
| 77 | `watch.element` | ✅ | ✅ (event payload `reason` enum kept verbatim; framing updated) | ❌ | ❌ |
| 78 | `watch.file` | ✅ | ✅ (event payload `old_path` made optional) | ❌ | ❌ |
| 79 | `watch.registry` | ✅ | ✅ (gained `until_change` flag — consolidates the v2.0 `registry.wait` sync verb) | ❌ | ❌ |
| 80 | `watch.cancel` | ✅ | ❌ | `ABORT` (subscription-scoped only — see drops) | `test_watch.py` |

---

## Tally

| Status | Count |
|---|---|
| Total v2.1 verbs (post-rc.3) | 86 |
| Currently exercised by conformance suite | 86 (every verb has a `needs_verb(capabilities, "<verb>")` gate; enforced by `tests/check_spec.py`) |
| With v1 ancestor verb(s) | 47 |
| v2-only (no v1 ancestor) | 39 |

Verb-count history: rc.1 had 77; rc.2 took it to 80 (file.write split, registry restructure); rc.3 takes it to 86 (input.* split into input.mouse.* + input.keyboard.* sub-namespaces, plus 6 new verbs to close v1.0.0 milestone parity issues).

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

All previously-listed entries here have been resolved — the v1.0.0 milestone closure in v2.1.0-rc.3 carried `MPOS` (→ `input.position`), `MDOWN`/`MUP` (→ `input.mouse.press` + `input.mouse.release`), `DRAG` (→ `input.mouse.drag`), `KEYDOWN`/`KEYUP` (→ `input.keyboard.key_down` + `input.keyboard.key_up`); v2.1.0-rc.2 carried `MOVEREL` (→ `input.move` `relative` flag, now `input.mouse.move`), `DCLICK` (→ `input.click.double`, now `input.mouse.click`), `SCREEN` (→ `system.info.screens`).

When future issues add verbs, the row migrates either to the verb's `spec/verbs/<verb>.json` (with `x-since` set to the cut version) or to the hard-drops table above.

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
| `window.move` | [#73](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/73) — atomic move-and-foreground (formalised post-audit; `foreground` flag + `foreground_status` enum) |
| `input.click` | [#72](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/72) — atomic double-click (mock-up has `double` flag; lock the SendInput batch implementation); [#87](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/87) — `target_handle` + `actual_position` response fields |
| `input.move` | [#71](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/71) — relative offsets |
| `input.scroll` | [#88](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/88) — `horizontal: bool` for tilt-wheel / shift-wheel |
| `input.send_message` | [#89](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/89) — return LRESULT in response body |
| `element.find` / `element.wait` | [#90](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/90) — `automation_id` + `root` for stable matching and subtree scoping (mock-up already has these fields; #90 formalises them) |
| `element.list` / `element.find` / `element.at` / `element.tree` / `element.wait` | [#92](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/92) — `flags` array (UIA boolean state) on result-bearing verbs + `flags_required` matcher on element.wait |
| `process.wait` | [#76](https://github.com/WilliamIsted/agent-remote-hands-protocol/issues/77) — optional/indefinite timeout |

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

### `file.*` (10/10 done)

- **Files-only narrowing in v2.1.0-rc.2:** all directory primitives moved to `directory.*`; the `file.*` namespace handles regular files exclusively. `file.list` was renamed to `directory.list`; `file.mkdir` to `directory.create`. The narrowed `file.delete` no longer accepts `recursive`/`not_empty` flags.
- **CRUDX split for write-side verbs:** `file.create` is the C verb (errors `already_exists` if the file is present); `file.write` is U-only (errors `not_found` if absent — no auto-create). The split formalises the create-vs-overwrite intent at the caller.
- **`file.write_at` is the chunked-upload primitive.** `truncate: true` is conditional on `offset: 0` (encoded as `x-conditional` — invalid otherwise). Returns `new_size` so callers know where to set the next chunk's offset.
- **Encoding enum is uniform across read/write/create/write_at:** `[utf-8, utf-16le, utf-16be, ascii, latin-1, cp1252, binary]`. `binary` means base64 in/out for raw bytes.
- **Atomic writes by default.** `file.create` and `file.write` default to `atomic: true` (write to temp + rename); `false` is opt-in for files held open by other processes via FILE_SHARE_WRITE.
- **Timestamp suffix is `_unix_s`** (not `_unix`). Consistent with `directory.*` post-rc.2 timestamp normalisation.
- **`flags` array per #93** (file.stat, directory.list, directory.stat): drawn from a closed enum of Win32 `FILE_ATTRIBUTE_*` flag names. Cloud-file flags (`recall_on_*`) are Windows 10+; older Windows omits them rather than reporting absent ones.
- **`file.download.local_path`** (not `dest_path`): cross-platform-friendly destination path naming. Three-tier implementation chain on modern (curl → wget → powershell-bits); error_unsupported on classic when no transfer tool is installed.
- **`file.rename` returns `{renamed, fallback_used}`** where `fallback_used: copy_delete` flags non-atomic cross-FS path; `none` for atomic same-volume.

### `directory.*` (6/6 done)

- **Carved out of `file.*` in v2.1.0-rc.2.** New verbs: `directory.create` (renamed from `file.mkdir`), `directory.list` (renamed from `file.list`), `directory.stat`, `directory.exists`, `directory.rename`, `directory.delete` (renamed from `directory.remove`).
- **`removed: true` field dropped** on `directory.delete` response — the OK status already conveys success. Only `entries_removed: int` remains.
- **`directory.list` defaults are non-recursive.** Pass `recursive: true` to walk the subtree depth-first; reparse points (junctions/symlinks) appear as `link`-type entries but are NOT followed (cycle protection). `pattern` is glob-style (`*`/`?`); `limit` caps the walk.
- **Per-entry shape includes `flags` array** (per #93 — same enum as file.stat). All three timestamps (`mtime_unix_s`, `ctime_unix_s`, `atime_unix_s`) on every entry; expensive only if very large directory.
- **`directory.stat.type` is a const enum** containing only `"directory"` — non-directories return `ERR not_a_directory` rather than reporting a different type. This is unlike `file.stat.type` which uses the open `file/directory/link/other` enum.
- **`directory.exists` is non-polymorphic.** Returns `false` for files (use `file.exists` for the polymorphic test).
- **`directory.rename` returns `{renamed, fallback_used}`** mirroring `file.rename`; `cross_fs: true` opts into copy+delete on cross-volume moves.
- **`mode` field on `directory.create` is silently ignored on Windows** (NTFS uses ACLs, not POSIX bits) — encoded via per-family `fields_ignored: ["mode"]` overlay.

### `process.*` (5/5 done)

- **`process.list` filter is `pattern`** (renamed from `filter` pre-rc.2). Case-insensitive substring against the image name.
- **`include_counters: true` adds CPU/memory/handle counts** (`cpu_percent`, `rss_bytes`, `working_set_bytes`, `private_bytes`, `thread_count`, `handle_count`, `start_time_unix_s`). Modest cost (per-pid OpenProcess + GetProcessTimes + GetProcessMemoryInfo + GetProcessHandleCount), so opt-in. Protected processes report empty/zero values.
- **`process.start.argv` is a string array** — agent assembles `lpCommandLine` correctly, avoiding shell-escape hazards. For path-with-spaces / unicode-name / shell-verb cases (open, runas, print, edit, explore, find), use `process.shell` instead.
- **`process.shell.pid` may be null** when no process spawns (e.g. `print` on a file that opens in an existing handler instance). Caller MUST null-check before passing to `process.kill`/`process.wait` (both require `pid >= 1`).
- **`process.wait` exit-code cache (per #16):** the agent retains the spawned process handle so `process.wait` returns the exit code even after the OS reaped the process. Without the cache this would return `ERR target_gone` after a fast exit.
- **`process.kill` is hard kill** (TerminateProcess) — no graceful shutdown signal. Children are NOT cascaded; callers wanting tree-kill must enumerate descendants and kill individually first (job-object pattern is out of scope for this verb).
- **CRUDX D for kill, R for list/wait, C for start/shell.** wait is read-tier (it observes; doesn't change state).

### `registry.*` (6/6 done)

- **Resource-first CRUD restructure in v2.1.0-rc.2.** `registry.read`/`write`/`delete` were replaced by separate verb sets for values vs. keys: `registry.value.{read, create, update, delete}` for individual values, `registry.key.{read, delete}` for whole keys. Pre-rc.2 names are reserved (`spec/reserved-names.json`) and won't be reintroduced.
- **`registry.value.create` vs. `update` are explicit** at the verb layer. create errors with `already_exists` when the value is present; update errors with `not_found` when it's missing. RegSetValueExW itself doesn't distinguish — the agent does a probe RegQueryValueExW first to surface the right error.
- **`registry.key.read` returns names + types only**, not data. Callers use `registry.value.read` to fetch a specific value's data. This split prevents accidental large-payload responses for keys with many values.
- **`registry.value.delete` dropped the always-true `deleted` field.** OK status already conveys success.
- **`registry.wait` consolidated into `watch.registry --until-change`.** The standalone `registry.wait` verb was removed in v2.1.0-rc.2; same semantics now live in `watch.registry` with the `until_change: true` flag (synchronous one-shot wait).
- **Hive abbreviations expanded server-side:** `HKLM`, `HKCU`, `HKCR`, `HKU`, `HKCC`. Accepted in any path argument; case-insensitive.
- **Type enum is the full Win32 set:** `REG_SZ`, `REG_EXPAND_SZ`, `REG_BINARY`, `REG_DWORD`, `REG_DWORD_BIG_ENDIAN`, `REG_LINK`, `REG_MULTI_SZ`, `REG_QWORD`, `REG_NONE`. Pre-9x agents may return `ERR not_supported` for `REG_QWORD` / `REG_LINK`.
- **`registry.key.delete --recursive` mirrors directory.delete.** Without the flag, deleting a key with subkeys returns `ERR not_empty`.

### `clipboard.*` (2/2 done)

- **Renamed in v2.1.0:** `clipboard.read` → `clipboard.get`; `clipboard.write` → `clipboard.set`. Old names are reserved.
- **`x-since: 2.1` plus `x-renamed-from`** on each. v1 ancestors are `CLIPGET`/`CLIPSET`.
- **Bytes-on-the-wire payload semantics.** The clipboard data is the wire payload (after the verb header line), not a JSON-wrapped string — preserves binary fidelity for non-text formats (CF_DIB, CF_HDROP, etc.).
- **`clipboard.set` echoes `format`** in its response body — confirms the agent honoured the requested format (no silent fallback).
- **CRUDX:** R for get, U for set (clipboard is shared OS state — set is not creating a new resource).
- **Tier:** read for get, update for set. `set` writes; gating prevents unprivileged callers from clobbering active clipboard contents.

### `watch.*` (7/7 done)

- **Subscription-id format is `sub:N`** (connection-scoped). Allocated per subscription; reusable after `watch.cancel`.
- **`watch.cancel` is idempotent.** Cancellation of a subscription that doesn't exist returns `OK 0` (not `ERR not_found`) — matches the cleanup-fail-safe pattern used by `input.*.release` / `input.keyboard.key_up`. The connection-cancel event from the framing layer signals every `watch.*` worker thread on connection close, so subscriptions don't leak.
- **`watch.cancel` is subscription-scoped only.** The v1 global `ABORT` form is a hard-drop — it was a cross-connection denial-of-service vector. Sub-scoped cancellation is the v2 safety improvement.
- **EVENT-payload reconciliation per-verb.** Every `watch.*` verb declares an `x-event-schema` for the EVENT-frame body shape; framing-section §3 documents the EVENT envelope.
- **`watch.region` was narrowed to screen-only in v2.** The v1 `WATCH` had broader semantics; v2.0+ restricts it to a single concern. Recursive directory watches live on `watch.file --recursive`.
- **`watch.region.encoding` enum is `[binary, base64]`** (added in rc.2 along with the matching `screen.capture.encoding` flag). Binary mode emits raw bytes; base64 emits a JSON envelope.
- **`watch.registry --until-change`** is the synchronous one-shot wait that subsumed v2.0's `registry.wait`. With the flag set, the verb blocks the connection until the first change fires (or `timeout_ms` expires); without it, returns a `subscription_id` immediately and emits EVENTs until cancelled.
- **`watch.process` events use `kind: started/exited`** plus the affected pid. `watch.window` events use `kind: created/destroyed/renamed` plus the affected handle. `watch.file` events use `kind: created/modified/deleted/renamed` with `path` and optional `old_path` (only for `renamed`).
- **`watch.element` is one-shot.** Emits a single EVENT on element invalidation (destroyed / reparented / structure_changed), then auto-cancels. Differs from the streaming subscriptions on the other watch.* verbs.

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
