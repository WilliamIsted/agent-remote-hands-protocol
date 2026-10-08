# system.apps.defaults — long-form rationale

## Why associations rather than categories

The question "which browser should I use" is already answered by Windows through URL-scheme and file-extension associations. Returning those needs no agent-side list of which apps count as browsers or editors, which would go stale as new apps appear.

## Output as an array

The natural shape is a map from key to handler, but the strict-tool subset does not allow open-ended object maps. Each entry therefore carries its `key`.

## Protocols and the user's choice

On Windows 8 and later the user's choice of default app lives in a per-user record that `AssocQueryString` only consults for protocols when it is called with `ASSOCF_IS_PROTOCOL`. Without that flag the lookup reads the machine-wide `HKCR` command for the scheme, which is often a different browser from the one the user picked. Extension lookups honour the user's choice without a flag. Older Windows has no such flag, so on `windows-classic` the protocol answer comes from `HKCR`.

## Store app handlers

When the handler is a packaged app there is usually no executable path to return, so `exe` is omitted. Whether a friendly `name` resolves depends on the agent passing `ASSOCF_APP_TO_APP`; a handler with no name is left out of the response.

## Classic availability

`AssocQueryStringA` ships in `shlwapi.dll` from Windows 2000, or wherever IE5 is installed. The agent resolves it at runtime. On a system without it the verb is not advertised.
