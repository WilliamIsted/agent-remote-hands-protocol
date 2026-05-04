# element.find — long-form rationale

## Why `windows-classic` is `implemented: false`

The verb requires UI Automation (Vista+). Earlier Windows families (NT 4 / 2000 / XP) ship only MSAA / `IAccessible`, which exposes a different and narrower object model than UIA. The verb's input shape (role + automation_id + name) and output shape (`automation_id`, UIA `flags` enum) map directly to UIA properties; rebuilding the same shape on top of MSAA would either lose information (no `automation_id` analogue on `IAccessible`) or fabricate it.

A future MSAA-backed verb under a different name (e.g. `element.find_msaa`) is the cleanest path if classic-stack support is needed; squeezing two accessibility models into one verb's contract degrades both.

## Renderer note

The generator (`Tools/gen.py`) excludes `implemented: false` verbs from the relevant family's `dist/verbs-<family>.md` catalogue, so a windows-classic agent's tools/list does not include element.find. `system.info.capabilities.ui_automation: no` on a classic agent gives callers the gate.
