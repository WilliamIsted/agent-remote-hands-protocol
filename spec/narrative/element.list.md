# element.list — long-form rationale

## Why `windows-classic` implements this verb through MSAA

Earlier versions declared `element.list` `implemented: false` on classic and suggested a separate `element.list_msaa` if classic-stack enumeration were ever needed, on the grounds that MSAA lacks AutomationId, walks a different tree and has no content-view filter. Protocol issue #106 reversed that; see `element.find.md` for the full reasoning.

How classic covers each original concern:

- **AutomationId.** Always `""`, which the contract already allows.
- **Tree walker.** Classic enumerates visible top-level windows itself (skipping hung ones) and walks each with `AccessibleChildren`. Window wrapper objects are walked through rather than reported, so the result lists controls, not HWND layers.
- **Content-view filtering.** Approximated: hidden containers are skipped with their subtree, scrolled-off items are kept and flagged `offscreen`, and anonymous unfocusable containers are left out as non-interactable. It is not identical to UIA's content view; it matched `directory.list` and `process.list` item for item in Explorer and Task Manager.

## Paging on classic

A classic response carries at most about 1000 elements, so that every returned handle is still live (PROTOCOL.md §10.3). It can also stop early at the response-size cap. Page on with `offset` until a page comes back with fewer elements than were asked for.

## Renderer note

The generator (`Tools/gen.py`) excludes `implemented: false` verbs from the relevant family's `dist/verbs-<family>.md` catalogue.
