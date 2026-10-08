## 10. Behaviour notes

### 10.1 Concurrency

Verbs from a single connection are serialised — the agent processes them in receive order and responses arrive in the same order. Verbs across different connections may run concurrently.

### 10.2 Idempotency

Most verbs are not idempotent. Callers that require at-most-once semantics SHOULD wrap retry logic with appropriate guards.

`watch.cancel` is idempotent: cancelling an already-cancelled subscription returns `OK 0`.

### 10.3 Element id stability

Element IDs are stable for the connection lifetime unless the underlying UI element is destroyed or invalidated. After invalidation, calls referencing the ID return `ERR target_gone`. The ID is not reused for a different element on the same connection.

Exception, `windows-classic`: the agent keeps the 1024 most recently issued IDs live. An older ID is invalidated (`ERR target_gone`) once 1024 newer ones exist, even if its element still exists, and is never reissued. A single response never carries more than about 1000 IDs, so every ID in a response is live when the caller receives it. Callers holding IDs across many large `element.list` / `element.tree` calls should re-find rather than reuse them.

### 10.4 Foreground locks

Windows enforces foreground-window locks to prevent applications from stealing focus. When `window.focus` is denied by this mechanism, the agent returns `OK` with `focused_status: "lock_held"` in the response body — the verb call itself succeeded, only the focus change was denied. The same `lock_held` status appears in `window.move.foreground_status` when the optional `--foreground` attempt is denied. Callers may retry after granting their own process the foreground privilege via `AllowSetForegroundWindow`.

Other verbs (`input.*`, `element.*`, the screen / file / process / registry namespaces) do not encounter foreground-lock policy and have no `lock_held` path.

### 10.5 UIPI behaviour

See §8 for the full discussion of integrity-level interactions. Briefly: synthetic input verbs (`input.*`, `element.invoke`) and UIA-based search verbs (`element.find`, `element.wait`) surface cross-IL barriers explicitly via `ERR uipi_blocked` and `ERR uia_blind` rather than silently succeeding.

### 10.6 Wire-desync recovery

If a client sends a malformed request (mis-stated payload length, header exceeding 65 535 bytes, etc.), the agent SHOULD return `ERR wire_desync` and discard the inbound buffer. The client recovers by sending `connection.reset` and resuming.

### 10.7 MSAA element model (windows-classic)

`windows-classic` implements `element.*` through Microsoft Active Accessibility (`oleacc.dll`, `IAccessible`) rather than UI Automation. The verbs, inputs and outputs are the same as on the UIA families; this section records where MSAA's model shows through. Per-verb details are in each verb's `windows-classic` family entry.

**Availability.** MSAA ships with Windows 98, 2000 and XP, and as the Active Accessibility redistributable for 95 and NT 4 SP6. The agent resolves it at runtime (`detect: {"type": "dll"}`, see the authoring checklist). When it loads, `system.info.capabilities.ui_automation` is `msaa`. When it is missing the agent still starts, `ui_automation` is `no`, `element.*` is absent from `system.capabilities`, and calls return `ERR not_supported`.

**Roles.** `role` reports the UIA control-type name, mapped from the MSAA role:

| MSAA role | `role` | MSAA role | `role` |
|---|---|---|---|
| `PUSHBUTTON`, `BUTTONMENU` | `Button` | `CHECKBUTTON` | `CheckBox` |
| `RADIOBUTTON` | `RadioButton` | `TEXT`, `HOTKEYFIELD` | `Edit` |
| `STATICTEXT` | `Text` | `COMBOBOX`, `DROPLIST` | `ComboBox` |
| `LIST` | `List` | `LISTITEM` | `ListItem` |
| `OUTLINE` | `Tree` | `OUTLINEITEM` | `TreeItem` |
| `PAGETABLIST` | `Tab` | `PAGETAB` | `TabItem` |
| `MENUBAR` | `MenuBar` | `MENUPOPUP` | `Menu` |
| `MENUITEM` | `MenuItem` | `TOOLBAR` | `ToolBar` |
| `STATUSBAR` | `StatusBar` | `TITLEBAR` | `TitleBar` |
| `SCROLLBAR` | `ScrollBar` | `GRIP`, `INDICATOR` | `Thumb` |
| `PROGRESSBAR` | `ProgressBar` | `SLIDER`, `DIAL` | `Slider` |
| `SPINBUTTON` | `Spinner` | `BUTTONDROPDOWN` | `SplitButton` |
| `LINK` | `Hyperlink` | `GRAPHIC`, `ANIMATION`, `CHART` | `Image` |
| `TABLE` | `Table` | `COLUMNHEADER`, `ROWHEADER` | `HeaderItem` |
| `ROW`, `CELL` | `DataItem` | `GROUPING` | `Group` |
| `SEPARATOR` | `Separator` | `TOOLTIP`, `HELPBALLOON` | `ToolTip` |
| `DOCUMENT` | `Document` | `APPLICATION` | `Window` |
| `CLIENT`, `PANE`, `PROPERTYPAGE`, `ALERT` | `Pane` | `WINDOW`, `DIALOG` | `Window` if top-level, `Pane` if a child window |

Any other role reports `Custom`. Embedded HTML (MSHTML, e.g. Explorer's web view) exposes links as `Hyperlink` or `Button` depending on markup; match such elements by name.

**automation_id.** MSAA has no AutomationId. Classic always returns `""`, and a query that matches on `automation_id` returns `ERR not_found` at once.

**flags.** `enabled`, `focused`, `offscreen` and `password` come from the MSAA state word (`UNAVAILABLE`, `FOCUSED`, `OFFSCREEN`, `PROTECTED`). `required` has no MSAA source and is never set.

**Tree shape.** MSAA wraps every child window in a `ROLE_SYSTEM_WINDOW` object whose children are its client area, scrollbars and title bar. Classic walks through these wrappers without reporting them: their children take the wrapper's depth. A nested control therefore costs one level, not two, and appears once.

**Hidden elements.** An element flagged INVISIBLE without OFFSCREEN is hidden; hidden containers are skipped with their whole subtree (this removes the invisible title-bar buttons MSAA gives every child window). List and tree items scrolled out of view report INVISIBLE and OFFSCREEN together; they are kept and flagged `offscreen`, as UIA does. MSAA cannot tell when an element is covered by another window or an overlay, so covered elements are reported as visible.

**Hung windows.** Classic serves requests on one thread. Before any call that resolves an object from a window or a point, the agent pings the window with `SendMessageTimeout(WM_NULL, SMTO_ABORTIFHUNG)`. Hung windows are skipped in walks (each adds about 0.5 s) and give `ERR target_gone` on direct calls. Accessibility servers that answer over COM rather than window messages (Office, Internet Explorer, Java bridges) are not covered by the ping.

**Limits.** Each walk is bounded by node count, recursion depth, 8192 children per container and 10 s of wall-clock time. `element.tree` reports `truncated` when any of these, its element cap or the response-size cap stops it. See §10.3 for ID lifetime.

### 10.8 Element roles

`role` in every `element.*` response is a UI Automation control-type name in CamelCase: the `ControlType` programmatic name without its `ControlType.` prefix. The set is `AppBar`, `Button`, `Calendar`, `CheckBox`, `ComboBox`, `Custom`, `DataGrid`, `DataItem`, `Document`, `Edit`, `Group`, `Header`, `HeaderItem`, `Hyperlink`, `Image`, `List`, `ListItem`, `Menu`, `MenuBar`, `MenuItem`, `Pane`, `ProgressBar`, `RadioButton`, `ScrollBar`, `SemanticZoom`, `Separator`, `Slider`, `Spinner`, `SplitButton`, `StatusBar`, `Tab`, `TabItem`, `Table`, `Text`, `Thumb`, `TitleBar`, `ToolBar`, `ToolTip`, `Tree`, `TreeItem` and `Window`. An element whose control type is outside this set reports `Custom`. Families without UI Automation map their native roles onto these names.

The `role` input on `element.find`, `element.find_invoke` and `element.wait` is matched case-insensitively, so `button` and `Button` select the same elements. Responses always use the CamelCase form.
