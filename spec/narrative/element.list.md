# element.list — long-form rationale

## Why `windows-classic` is `implemented: false`

The verb requires UI Automation (Vista+). Classic Windows (NT 4 / 2000 / XP) has only MSAA / `IAccessible`, which doesn't map cleanly to the UIA-based element model in this spec — there's no analogue to UIA's `AutomationId` property, the tree-walker abstraction differs, and content-view filtering is UIA-specific.

## Future enhancement

If classic-stack element enumeration is needed, the cleanest path is a separate MSAA-backed verb (e.g. `element.list_msaa`) with its own contract reflecting MSAA's shape. Squeezing two accessibility models into the same verb's contract would either constrain UIA's expressiveness or fabricate fields MSAA can't populate. No such verb exists today; add only when there's demand.

## Renderer note

The generator (`Tools/gen.py`) excludes `implemented: false` verbs from the relevant family's `dist/<family>/VERBS.md` catalogue.
