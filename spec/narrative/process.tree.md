# process.tree — long-form rationale

## The installer case

An installer often ends by launching the app it installed and then exiting. The caller only knows the installer's pid. Windows keeps each child's recorded parent id after the parent exits, so walking from the installer's pid still finds the launched app. That is why an exited root is not an error.

## Pid reuse

Windows recycles pids, so a recorded parent id can point at an unrelated, newer process. On `windows-modern` the agent drops a link when the child was created before its supposed parent, which can only happen after reuse. When a creation time can't be read (protected processes) the link is kept rather than dropped. When the root has exited there is no creation time to compare against, so its direct children are matched by pid alone; in rare cases that includes children of an earlier process with the same pid.

## Snapshot only

The verb lists processes alive at the moment of the call. It can't show a child that started and exited between calls, including an app that crashed on launch. `watch.process` with `descendants: true` reports spawns and exits as they happen.

## Classic availability

Toolhelp is resolved from `kernel32.dll` at runtime. It exists on Windows 9x and 2000 and later. NT 4 has neither Toolhelp nor a parent id in PSAPI, so the verb is not advertised there.
