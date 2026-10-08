# element.find — long-form rationale

## Why `windows-classic` implements this verb through MSAA

Until protocol issue #106, `windows-classic` declared `element.*` as `implemented: false`, reasoning that MSAA (`IAccessible`, the only accessibility API before Vista) maps poorly to the UIA-shaped contract and that a separate verb (`element.find_msaa`) would be cleaner than squeezing two models into one.

That decision was reversed in October 2026 after an MSAA implementation was built and measured on XP SP3. The objections didn't hold up in practice:

- **No `automation_id` analogue.** The contract already allows `automation_id` to be the empty string "when the element doesn't expose one". Classic returns `""` and never invents a value; a query on `automation_id` returns `ERR not_found`. Nothing is fabricated.
- **UIA's expressiveness would be constrained.** No UIA field or behaviour changed. The modern family entry is untouched.
- **The models differ.** They do, and the differences that callers can see are recorded rather than hidden: the role mapping, the treatment of window wrappers, hidden versus scrolled-off items, and the hung-window rule are in PROTOCOL.md §10.7 and the classic family entry.

Against that, separate verbs would force every client to branch on OS family for every element call, and the MCP bridge to carry a second set of tools for the same actions. In the measured runs (Notepad, Calculator, Explorer, Task Manager, and building an app inside the VS6 IDE, all without screenshots) the same calls worked across families.

## Find semantics on classic

FindFirst semantics match modern: the root itself is a candidate, then a depth-first walk. `name` is a case-insensitive substring match; `role` compares the mapped UIA control-type name. A `root` handle that names a simple MSAA child (no subtree, e.g. a list item) is rejected with `ERR invalid_args` rather than silently searching its parent.

## Renderer note

The generator (`Tools/gen.py`) excludes `implemented: false` verbs from the relevant family's `dist/verbs-<family>.md` catalogue. On classic, whether the verb is actually available depends on `oleacc.dll` being present at runtime; `system.capabilities` is the gate, and lists `element.*` only when it is.
