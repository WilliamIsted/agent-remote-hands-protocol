# system.apps.installed — long-form rationale

## Why uncategorised

The verb returns the Uninstall-key inventory as it is and does not group entries into browsers, editors or media players. Any category list the agent maintained would age badly, and the caller can filter by `name` or `publisher` itself. A normal Windows install has roughly 100 to 300 entries, which fits in one response; `pattern` exists for callers that only want one product.

## Filtering

The agent skips three kinds of entry: no `DisplayName`, `SystemComponent` set to 1, and `ParentKeyName` set. This is the subset of Programs and Features filtering the agent applies, not an exact mirror. The `ParentKeyName` rule and the way Programs and Features treats `ReleaseType` update entries have not been checked against a primary Microsoft source, so expect some differences from what Programs and Features shows.

## Store and MSIX apps

Packaged apps do not register under the Uninstall keys, so they are missing from this list. On Windows 11 that includes Notepad, Calculator and Photos. A later version can add them through the package manager with a `source` field on each entry; that is deliberately out of scope for 2.2.

## Pairing with system.apps.defaults

`system.apps.defaults` answers which app handles a URL scheme or file extension. This verb answers whether something is installed at all. A caller can combine them, for example to see that the default browser is Chrome and then check whether Firefox is also installed.
