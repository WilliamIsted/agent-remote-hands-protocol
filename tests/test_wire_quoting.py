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

"""Pure-Python round-trip tests for the canonical wire-quoting helpers in
`tests/conformance/wire.py`. No socket, no agent — runs in CI in milliseconds.

The conformance suite proper exercises these against a live agent; this file
catches regressions in the reference grammar without needing a Windows runner."""

from __future__ import annotations

import pathlib
import sys

import pytest

# Make the conformance/ directory importable regardless of where pytest is
# invoked from.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "conformance"))

from wire import WireError, _quote, _tokenize  # noqa: E402


# ---------------------------------------------------------------------------
# Round-trip cases — args -> rendered header -> parsed args

ROUND_TRIPS = [
    (["simple"],                            "simple"),
    (["a", "b"],                            "a b"),
    (["path with space"],                   '"path with space"'),
    (["", ""],                              '"" ""'),
    (["a", "has space", "b"],               'a "has space" b'),
    (["C:\\Program Files\\App"],            '"C:\\Program Files\\App"'),
    (["C:\\Windows\\System32"],             "C:\\Windows\\System32"),
    (["no_space_at_all"],                   "no_space_at_all"),
    (["src dir", "dst dir"],                '"src dir" "dst dir"'),
    (["src", "--overwrite", "dst"],         "src --overwrite dst"),
]


@pytest.mark.parametrize("args,expected", ROUND_TRIPS)
def test_round_trip_render_then_parse(args: list[str], expected: str) -> None:
    rendered = " ".join(_quote(a) for a in args)
    assert rendered == expected, f"render: got {rendered!r}, expected {expected!r}"
    parsed = _tokenize(rendered)
    assert parsed == args, f"parse: got {parsed!r}, expected {args!r}"


# ---------------------------------------------------------------------------
# Error paths

def test_unmatched_quote_raises() -> None:
    with pytest.raises(WireError, match="unmatched quote"):
        _tokenize('verb "unclosed')


def test_embedded_quote_in_arg_raises_on_send() -> None:
    """Args containing a literal `"` cannot be represented on the header line.
    The grammar has no escape mechanism inside quotes; verbs that need raw
    bytes containing `"` use the length-prefixed payload form."""
    with pytest.raises(WireError, match="literal double quote"):
        _quote('has"quote')


def test_empty_args_round_trip() -> None:
    """Empty args are representable as `""`."""
    assert _quote("") == '""'
    assert _tokenize('verb "" "" tail') == ["verb", "", "", "tail"]


def test_backslashes_inside_quotes_are_literal() -> None:
    """No escape mechanism — backslash is a literal byte. Critical for
    Windows paths: `"C:\\Program Files\\App"` round-trips intact."""
    raw = "C:\\foo\\bar"
    rendered = _quote(raw)
    parsed = _tokenize(rendered)
    assert parsed == [raw], (rendered, parsed)


def test_runs_of_spaces_collapse() -> None:
    """Multiple spaces between unquoted tokens collapse — runs of spaces
    don't produce empty tokens."""
    assert _tokenize("a    b   c") == ["a", "b", "c"]
