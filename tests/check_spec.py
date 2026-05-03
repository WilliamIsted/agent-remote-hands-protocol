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
  - x-families values reference families that exist in spec/families.json.
  - spec/families.json families have the required keys.

Exit code: 0 on success, 1 on the first failure batch (all failures printed).
"""

from __future__ import annotations

import json
import pathlib
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
    "x-families",
)
REQUIRED_FAMILY_KEYS = (
    "description",
    "capabilities",
    "protocol_versions_spoken",
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

    # strict is True.
    if spec.get("strict") is not True:
        _err(failures, path, f"`strict` must be true (got {spec.get('strict')!r})")

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


def main() -> int:
    root = _repo_root()
    spec_dir = root / "spec"
    if not spec_dir.is_dir():
        print(f"FAIL: {spec_dir} is not a directory", file=sys.stderr)
        return 1

    failures: list[str] = []
    families = check_families_json(spec_dir, failures)

    verbs_dir = spec_dir / "verbs"
    if not verbs_dir.is_dir():
        print(f"FAIL: {verbs_dir} is not a directory", file=sys.stderr)
        return 1

    verb_files = sorted(verbs_dir.glob("*.json"))
    for vf in verb_files:
        check_verb_file(vf, families.keys(), failures)

    print(f"check_spec: {len(verb_files)} verb files, "
          f"{len(families)} families")

    if failures:
        print(f"\n{len(failures)} failure(s):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
