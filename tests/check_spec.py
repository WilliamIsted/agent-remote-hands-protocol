#!/usr/bin/env python3
#   Copyright 2026 William Isted and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Static validator for the spec/ tree.

Run from the repo root:

    python tests/check_spec.py

Designed to be CI-cheap (parses JSON files, no network, no subprocesses) and
to catch the structural mistakes that are hard to spot on visual review:

  - spec/verbs/<verb>.json filename matches the verb's `name` field.
  - Every verb file has the required strict-tool keys plus the protocol's
    x-* extensions.
  - x-crudx is one of R / C / U / D / X.
  - x-namespace matches the dotted prefix of the verb name.
  - input_schema declares additionalProperties: false at the root.
  - `strict: true` (or `strict: false` with `x-strict-false-reason` set).
  - x-families values reference families that exist in spec/families.json.
  - spec/families.json families have the required keys.
  - No verb file or verb `name` collides with spec/reserved-names.json
    (v1 verbs that were renamed or dropped, plus v2.0 dotted names that
    v2.1 superseded).
  - Every verb in spec/verbs/ has at least one `needs_verb(capabilities,
    "<verb>")` reference somewhere in tests/conformance/test_*.py — the
    conformance suite is the wire-protocol contract; new verbs must land
    with a test gating call.
  - Hand-written spec markdown (spec/framing/, spec/operators/,
    spec/narrative/, spec/AUTHORING-*.md, root README/CHANGELOG/CLAUDE,
    docs/) doesn't contain backticked dotted tokens (`<a>.<b>` or
    `<a>.<b>.<c>`) that look like verb-name references but don't resolve
    to a live verb in spec/verbs/ — and aren't explicitly listed in
    spec/reserved-names.json as historical / superseded names. Catches
    stale verb-name mentions in prose after renames.

Exit code: 0 on success, 1 on the first failure batch (all failures printed).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Iterable


VALID_CRUDX = {"R", "C", "U", "D", "X"}
REQUIRED_VERB_KEYS = (
    "name",
    "strict",
    "description",
    "input_schema",
    "x-crudx",
    "x-since",
    "x-namespace",
    "x-output-schema",
    "x-errors",
    "x-implementations",
    "x-families",
)
REQUIRED_FAMILY_KEYS = (
    "description",
    "capabilities",
    "protocol_versions_spoken",
    "token_file_path",
    "token_file_acl",
)


def _err(failures: list[str], path: pathlib.Path, msg: str) -> None:
    failures.append(f"{path.relative_to(_repo_root())}: {msg}")


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def check_families_json(spec_dir: pathlib.Path,
                        failures: list[str]) -> dict[str, dict]:
    fpath = spec_dir / "families.json"
    if not fpath.is_file():
        _err(failures, fpath, "missing")
        return {}
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(failures, fpath, f"JSON parse error: {e}")
        return {}
    families = data.get("families")
    if not isinstance(families, dict):
        _err(failures, fpath, "top-level 'families' object missing or not a dict")
        return {}
    for name, body in families.items():
        if not isinstance(body, dict):
            _err(failures, fpath, f"family {name!r} is not an object")
            continue
        # Placeholder families are allowed; they only need a description.
        if body.get("_placeholder") is True:
            if "description" not in body:
                _err(failures, fpath,
                     f"placeholder family {name!r} must still carry a description")
            continue
        for key in REQUIRED_FAMILY_KEYS:
            if key not in body:
                _err(failures, fpath,
                     f"family {name!r} missing required key {key!r}")
    return families


def load_reserved_names(spec_dir: pathlib.Path,
                        failures: list[str]) -> dict[str, dict]:
    """Return {reserved_name: entry_dict} indexed by name. Empty dict on
    parse errors (errors recorded in `failures`)."""
    fpath = spec_dir / "reserved-names.json"
    if not fpath.is_file():
        _err(failures, fpath, "missing")
        return {}
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(failures, fpath, f"JSON parse error: {e}")
        return {}
    entries = data.get("reserved")
    if not isinstance(entries, list):
        _err(failures, fpath, "top-level 'reserved' array missing or not a list")
        return {}
    out: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            _err(failures, fpath, f"reserved entry is not an object: {entry!r}")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            _err(failures, fpath, f"reserved entry missing/invalid 'name': {entry!r}")
            continue
        if name in out:
            _err(failures, fpath, f"reserved name {name!r} appears more than once")
            continue
        out[name] = entry
    return out


def check_reserved_collisions(verb_files: list[pathlib.Path],
                              reserved: dict[str, dict],
                              failures: list[str]) -> None:
    """Fail if any spec/verbs/<reserved>.json exists or any verb's `name`
    collides with a reserved name."""
    for path in verb_files:
        stem = path.stem  # filename without .json
        if stem in reserved:
            entry = reserved[stem]
            replacement = entry.get("replacement")
            hint = (f" Use {replacement!r} instead." if replacement
                    else " This v1 capability was deliberately dropped — see spec/AUTHORING-PROGRESS.md.")
            _err(failures, path,
                 f"filename collides with reserved name {stem!r} "
                 f"(kind: {entry.get('kind', '?')}, reason: {entry.get('reason', '?')}).{hint}")
        # Also check the file's `name` field — guard against a renamed file
        # whose `name` field still carries the reserved value.
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # parse error already reported by check_verb_file
        name = spec.get("name")
        if isinstance(name, str) and name in reserved and name != stem:
            entry = reserved[name]
            replacement = entry.get("replacement")
            hint = (f" Use {replacement!r} instead." if replacement
                    else " This v1 capability was deliberately dropped — see spec/AUTHORING-PROGRESS.md.")
            _err(failures, path,
                 f"`name` field {name!r} collides with reserved name "
                 f"(kind: {entry.get('kind', '?')}, reason: {entry.get('reason', '?')}).{hint}")


def check_verb_file(path: pathlib.Path,
                    families: Iterable[str],
                    failures: list[str]) -> None:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(failures, path, f"JSON parse error: {e}")
        return

    # Required top-level keys.
    for key in REQUIRED_VERB_KEYS:
        if key not in spec:
            _err(failures, path, f"missing required key {key!r}")

    # Filename matches verb name.
    name = spec.get("name")
    if isinstance(name, str):
        expected = f"{name}.json"
        if path.name != expected:
            _err(failures, path,
                 f"filename does not match `name` field "
                 f"(name={name!r}, expected file {expected!r})")

        # x-namespace matches the dotted prefix of the name.
        ns = spec.get("x-namespace")
        if isinstance(ns, str) and "." in name:
            prefix = name.split(".", 1)[0]
            if ns != prefix:
                _err(failures, path,
                     f"x-namespace {ns!r} doesn't match name prefix {prefix!r}")

    # CRUDX letter is in the allowed set.
    crudx = spec.get("x-crudx")
    if crudx is not None and crudx not in VALID_CRUDX:
        _err(failures, path,
             f"x-crudx {crudx!r} is not one of {sorted(VALID_CRUDX)}")

    # strict is True, OR strict is False with a documented reason. Per Option
    # 13 design subsection C, strict mode is per-tool — a verb that genuinely
    # needs JSON Schema features outside the strict-tool subset (recursion,
    # open-ended object maps, etc.) MAY declare `strict: false` provided it
    # also declares `x-strict-false-reason: <string>` explaining why.
    strict = spec.get("strict")
    if strict is True:
        pass
    elif strict is False:
        reason = spec.get("x-strict-false-reason")
        if not (isinstance(reason, str) and reason.strip()):
            _err(failures, path,
                 "`strict: false` requires a non-empty `x-strict-false-reason` "
                 "string explaining the carve-out (Option 13 design §C).")
    else:
        _err(failures, path, f"`strict` must be true or false (got {strict!r})")

    # input_schema has additionalProperties: false at the root.
    schema = spec.get("input_schema")
    if isinstance(schema, dict):
        if schema.get("type") != "object":
            _err(failures, path,
                 f"input_schema.type must be 'object' "
                 f"(got {schema.get('type')!r})")
        if schema.get("additionalProperties") is not False:
            _err(failures, path,
                 "input_schema.additionalProperties must be false")

    # x-families references families that exist (or is empty).
    fam_map = spec.get("x-families")
    known = set(families)
    if isinstance(fam_map, dict):
        for fam_name in fam_map.keys():
            if fam_name not in known:
                _err(failures, path,
                     f"x-families references unknown family {fam_name!r} "
                     f"(known: {sorted(known)})")
    elif fam_map is not None:
        _err(failures, path, "x-families must be an object")

    # x-errors is a list of strings.
    errors_list = spec.get("x-errors")
    if errors_list is not None and not (
            isinstance(errors_list, list)
            and all(isinstance(e, str) for e in errors_list)):
        _err(failures, path, "x-errors must be an array of strings")


def load_error_dictionary(spec_dir: pathlib.Path,
                          failures: list[str]) -> set[str]:
    """Parse spec/framing/05-errors.md and return the set of error codes
    declared in the §5.1 and §5.2 tables. Codes are recognised as backticked
    identifiers in the first column of the markdown tables."""
    errors_path = spec_dir / "framing" / "05-errors.md"
    if not errors_path.is_file():
        _err(failures, errors_path, "missing — error-code dictionary required")
        return set()
    text = errors_path.read_text(encoding="utf-8")
    codes: set[str] = set()
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        # Detect markdown table rows; first cell with a backticked identifier.
        if stripped.startswith("| `") and stripped.endswith("|"):
            in_table = True
            # Extract first cell between `...`
            try:
                first = stripped.split("|", 2)[1].strip()
                if first.startswith("`") and "`" in first[1:]:
                    code = first[1:].split("`", 1)[0]
                    if code and " " not in code:
                        codes.add(code)
            except (IndexError, ValueError):
                pass
        elif in_table and not stripped.startswith("|"):
            in_table = False
    return codes


def check_error_codes(verb_files: list[pathlib.Path],
                      dictionary: set[str],
                      failures: list[str]) -> None:
    """For each verb's x-errors, verify every code is in the dictionary."""
    if not dictionary:
        return
    for path in verb_files:
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        errors_list = spec.get("x-errors", [])
        if not isinstance(errors_list, list):
            continue
        for code in errors_list:
            if not isinstance(code, str):
                continue
            if code not in dictionary:
                _err(failures, path,
                     f"x-errors contains {code!r} which is not declared in "
                     f"spec/framing/05-errors.md. Add it to the dictionary "
                     f"(or fix the verb's x-errors entry).")


def load_shared_types(spec_dir: pathlib.Path,
                      failures: list[str]) -> dict[str, dict]:
    """Return {shape_name: {"schema": ..., "validation": "exact"|"structure-only"}}.
    Loaded from spec/types/*.json. Empty dict if directory missing."""
    types_dir = spec_dir / "types"
    if not types_dir.is_dir():
        return {}
    out: dict[str, dict] = {}
    for path in sorted(types_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            _err(failures, path, f"JSON parse error: {e}")
            continue
        if not isinstance(data.get("schema"), dict):
            _err(failures, path, "missing or non-object 'schema' key")
            continue
        out[path.stem] = {
            "schema": data["schema"],
            "validation": data.get("_validation", "exact"),
        }
    return out


def _check_shape_match(canonical: dict, observed: dict, mode: str) -> str | None:
    """Return None on match, or an error message string on mismatch."""
    if mode == "exact":
        if canonical != observed:
            return "inline shape diverges from canonical (exact match required)"
        return None
    if mode == "structure-only":
        # Compare type, required, additionalProperties, and property keys.
        for key in ("type", "additionalProperties"):
            if canonical.get(key) != observed.get(key):
                return f"`{key}` differs (canonical={canonical.get(key)!r}, observed={observed.get(key)!r})"
        if sorted(canonical.get("required", [])) != sorted(observed.get("required", [])):
            return "`required` array differs"
        canonical_keys = sorted((canonical.get("properties") or {}).keys())
        observed_keys = sorted((observed.get("properties") or {}).keys())
        if canonical_keys != observed_keys:
            return f"property keys differ (canonical={canonical_keys}, observed={observed_keys})"
        for prop_key in canonical_keys:
            ct = (canonical["properties"][prop_key] or {}).get("type")
            ot = (observed["properties"][prop_key] or {}).get("type")
            if ct != ot:
                return f"property `{prop_key}` type differs (canonical={ct!r}, observed={ot!r})"
        return None
    return f"unknown validation mode {mode!r}"


def check_shared_types(verb_files: list[pathlib.Path],
                       shared_types: dict[str, dict],
                       failures: list[str]) -> None:
    """For each verb, if it declares $defs.<TypeName> matching a shared type,
    verify the inline shape matches the canonical."""
    if not shared_types:
        return
    for path in verb_files:
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # parse error already reported
        defs = spec.get("$defs")
        if not isinstance(defs, dict):
            continue
        for type_name, type_meta in shared_types.items():
            if type_name not in defs:
                continue
            err = _check_shape_match(
                type_meta["schema"], defs[type_name], type_meta["validation"]
            )
            if err is not None:
                _err(failures, path,
                     f"$defs.{type_name} {err} — see spec/types/{type_name}.json")


def check_conformance_coverage(verb_files: list[pathlib.Path],
                               root: pathlib.Path,
                               failures: list[str]) -> int:
    """Every verb in spec/verbs/common/<verb>.json or spec/verbs/windows/<verb>.json
    must have at least one `needs_verb(capabilities, "<verb>")` call somewhere under
    tests/conformance/test_*.py. The conformance suite is the wire-protocol
    contract — adding a verb without a gating call is a contract change
    without verification.

    A verb may also be exercised via `client.<wrapper>()` convenience
    methods on `WireClient` (e.g. `connection.hello`, `system.info`,
    `system.capabilities`); those wrappers are recognised here too.

    Returns the count of covered verbs.
    """
    conf_dir = root / "tests" / "conformance"
    if not conf_dir.is_dir():
        # No conformance suite to check against; skip rather than fail.
        return 0

    # Concatenate every test_*.py source file once.
    sources = []
    for path in sorted(conf_dir.glob("test_*.py")):
        try:
            sources.append(path.read_text(encoding="utf-8"))
        except OSError:
            continue
    blob = "\n".join(sources)

    # Verbs invoked through WireClient convenience wrappers rather than
    # through `needs_verb(capabilities, ...)`. Keep this set tight — the
    # default expectation is a `needs_verb` gating call.
    wrapper_covered = {
        "connection.hello",      # exercised by every test via client.hello()
        "connection.tier_raise", # exercised by *_client elevation fixtures
        "system.info",           # exercised by client.info()
        "system.capabilities",   # exercised by client.capabilities()
    }

    covered = 0
    for path in verb_files:
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        name = spec.get("name")
        if not isinstance(name, str):
            continue
        token = f'needs_verb(capabilities, "{name}")'
        if token in blob or name in wrapper_covered:
            covered += 1
            continue
        _err(failures, path,
             f"verb {name!r} has no `needs_verb(capabilities, {name!r})` "
             f"reference in tests/conformance/test_*.py — every verb in "
             f"spec/verbs/ must be exercised by the conformance suite. "
             f"Add a tier-gate or arg-validation test to the relevant "
             f"test_<namespace>.py.")
    return covered


def check_doc_verb_references(verb_files: list[pathlib.Path],
                              reserved: dict[str, dict],
                              root: pathlib.Path,
                              failures: list[str]) -> None:
    """Scan hand-written spec markdown for backticked dotted tokens that
    look like verb-name references but don't resolve to a live verb in
    spec/verbs/ (and aren't explicitly listed in spec/reserved-names.json
    as historical / superseded names).

    Catches: stale verb-name mentions in prose after renames or removals
    (e.g. `registry.read` after the rc.2 split into registry.value.read /
    registry.key.read).

    Misses: stale field-path mentions (e.g. system.info.protocol vs
    system.info.agent_protocol). Distinguishing field paths from verb
    names without an authoritative field-set is unreliable, so the rule
    accepts any 3-segment token whose first two segments form a live
    verb name (treating it as a field path under that verb).

    Allowlist: the rule's `KNOWN_NON_VERB_TOKENS` set carries dotted
    identifiers that match the regex but are deliberately not verbs
    (e.g. `agents/windows-modern/src/verbs/input.cpp` mentioned in prose,
    or shorthand like `pip.install` in setup steps).
    """
    valid_verbs = {p.stem for p in verb_files}

    # Tokens that match the verb-name shape but are deliberately not verbs.
    # Add to this set when prose legitimately needs a dotted identifier the
    # rule would otherwise flag.
    KNOWN_NON_VERB_TOKENS = {
        # Conformance-suite test-file names appearing in prose
        "test_input.py", "test_input_mouse.py", "test_input_keyboard.py",
        "test_connection.py", "test_system.py", "test_window.py",
        "test_screen.py", "test_element.py", "test_clipboard.py",
        "test_directory.py", "test_file.py", "test_process.py",
        "test_registry.py", "test_watch.py", "test_vision.py",
        "test_websocket.py",
        # MCP JSON-RPC field paths referenced in framing prose (not ARH verbs)
        "params.name", "params.arguments",
        # Tooling references
        "agent_client.py", "wire.py", "gen.py", "check_spec.py", "families.json",
        # File-name references in prose
        "input.cpp", "PROTOCOL.md", "VERBS.md",
        # Process / executable names in operational prose
        "explorer.exe", "remote-hands.exe", "msiexec.exe",
        # Hypothetical future verbs mentioned in narrative (not yet authored)
        "element.find_msaa", "element.list_msaa",
        "vision.describe", "vision.find", "vision.ocr_tesseract",
        # Placeholder examples in AUTHORING-CHECKLIST naming-convention prose
        "foo.bar.baz", "foo.bar_baz",
        # Pre-rc.3 verb names appearing in v1→v2 migration narratives. The
        # 2-segment forms are caught by reserved-names.json; these 3-segment
        # forms are intermediate names captured in the rc.2/rc.3 audit prose.
        "input.click.double",
    }

    # Markdown files to scan.
    targets: list[pathlib.Path] = []
    for sub in ("framing", "operators", "narrative"):
        d = root / "spec" / sub
        if d.is_dir():
            targets.extend(p for p in sorted(d.glob("*.md")) if p.name != "README.md")
    for filename in ("spec/AUTHORING-CHECKLIST.md",
                     "spec/AUTHORING-PROGRESS.md",
                     "README.md", "CHANGELOG.md", "CLAUDE.md",
                     "LLM-OPERATORS.md"):
        p = root / filename
        if p.is_file():
            targets.append(p)
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        targets.extend(sorted(docs_dir.glob("*.md")))

    # Backticked-token regex: capture `foo.bar` or `foo.bar.baz` where each
    # segment is alphanumeric+underscore. Limit to 2-3 segments.
    token_pat = re.compile(
        r"`([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)?)`"
    )

    for path in targets:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in token_pat.finditer(content):
            tok = match.group(1)
            if tok in valid_verbs:
                continue
            if tok in reserved:
                continue
            if tok in KNOWN_NON_VERB_TOKENS:
                continue
            # Three-segment token whose `<a>.<b>` head is a live verb is
            # treated as a field path under that verb (e.g.
            # `system.info.capabilities`).
            head = tok.split(".")
            if len(head) == 3 and ".".join(head[:2]) in valid_verbs:
                continue
            line_no = content[: match.start()].count("\n") + 1
            _err(failures, path,
                 f"line {line_no}: backticked token `{tok}` doesn't resolve "
                 f"to a verb in spec/verbs/ or a reserved name in "
                 f"spec/reserved-names.json. If this is meant as a verb "
                 f"reference, fix the name. If it's a non-verb identifier "
                 f"(test file, library, etc.), add it to "
                 f"check_doc_verb_references.KNOWN_NON_VERB_TOKENS.")


def main() -> int:
    root = _repo_root()
    spec_dir = root / "spec"
    if not spec_dir.is_dir():
        print(f"FAIL: {spec_dir} is not a directory", file=sys.stderr)
        return 1

    failures: list[str] = []
    families = check_families_json(spec_dir, failures)
    reserved = load_reserved_names(spec_dir, failures)
    shared_types = load_shared_types(spec_dir, failures)
    error_dict = load_error_dictionary(spec_dir, failures)

    verbs_dir = spec_dir / "verbs"
    if not verbs_dir.is_dir():
        print(f"FAIL: {verbs_dir} is not a directory", file=sys.stderr)
        return 1

    verb_files = sorted(verbs_dir.glob("**/*.json"))
    for vf in verb_files:
        check_verb_file(vf, families.keys(), failures)
    check_reserved_collisions(verb_files, reserved, failures)
    check_shared_types(verb_files, shared_types, failures)
    check_error_codes(verb_files, error_dict, failures)
    covered = check_conformance_coverage(verb_files, root, failures)
    check_doc_verb_references(verb_files, reserved, root, failures)

    print(f"check_spec: {len(verb_files)} verb files "
          f"({covered} with conformance coverage), "
          f"{len(families)} families, "
          f"{len(reserved)} reserved names, "
          f"{len(shared_types)} shared types, "
          f"{len(error_dict)} error codes")

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
