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

"""pytest fixtures for the conformance suite."""

from __future__ import annotations

import json
import os
import pathlib
from typing import Iterator

import pytest

from wire import ErrResponse, OkResponse, WireClient, WsWireClient


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--host",
        default=os.environ.get("REMOTE_HANDS_HOST", "127.0.0.1"),
        help="Agent host (default: REMOTE_HANDS_HOST or 127.0.0.1).",
    )
    parser.addoption(
        "--port",
        type=int,
        default=int(os.environ.get("REMOTE_HANDS_PORT", "8765")),
        help="Agent port (default: REMOTE_HANDS_PORT or 8765).",
    )
    parser.addoption(
        "--token-path",
        default=os.environ.get(
            "REMOTE_HANDS_TOKEN_PATH",
            r"C:\ProgramData\AgentRemoteHands\token",
        ),
        help="Path to the agent's elevation token file.",
    )


@pytest.fixture(scope="session")
def host(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("host")


@pytest.fixture(scope="session")
def port(pytestconfig: pytest.Config) -> int:
    return pytestconfig.getoption("port")


@pytest.fixture(scope="session")
def token(pytestconfig: pytest.Config) -> str:
    p = pathlib.Path(pytestconfig.getoption("token_path"))
    if not p.exists():
        pytest.skip(f"token file not readable at {p}")
    return p.read_text(encoding="ascii").strip()


@pytest.fixture(scope="session")
def capabilities(host: str, port: int) -> dict:
    """Map of verb name -> {'tier': '<read|create|update|delete|extra_risky>'}."""
    with WireClient(host, port) as c:
        c.hello()
        return c.capabilities()


@pytest.fixture
def client(host: str, port: int) -> Iterator[WireClient]:
    """Per-test connection at read tier (the default on a fresh hello)."""
    with WireClient(host, port) as c:
        c.hello()
        yield c


@pytest.fixture
def create_client(client: WireClient, token: str) -> WireClient:
    """Per-test connection elevated to create tier."""
    r = client.tier_raise("create", token)
    if isinstance(r, ErrResponse):
        pytest.skip(f"could not elevate to create: {r.code} {r.detail}")
    return client


@pytest.fixture
def update_client(client: WireClient, token: str) -> WireClient:
    """Per-test connection elevated to update tier (subsumes create + read)."""
    r = client.tier_raise("update", token)
    if isinstance(r, ErrResponse):
        pytest.skip(f"could not elevate to update: {r.code} {r.detail}")
    return client


@pytest.fixture
def delete_client(client: WireClient, token: str) -> WireClient:
    """Per-test connection elevated to delete tier (subsumes update + create + read)."""
    r = client.tier_raise("delete", token)
    if isinstance(r, ErrResponse):
        pytest.skip(f"could not elevate to delete: {r.code} {r.detail}")
    return client


@pytest.fixture
def extra_risky_client(client: WireClient, token: str) -> WireClient:
    """Per-test connection elevated to extra_risky tier (top of the ladder)."""
    r = client.tier_raise("extra_risky", token)
    if isinstance(r, ErrResponse):
        pytest.skip(f"could not elevate to extra_risky: {r.code} {r.detail}")
    return client


@pytest.fixture
def ws_client(host: str, port: int) -> Iterator[WsWireClient]:
    """Per-test connection using `--framing ws` (RFC 6455 binary frames).

    Skips if `system.info.framings` does not advertise `"ws"` (probed via a
    short-lived MCP `client` connection)."""
    # Probe framings via the standard MCP client first.
    with WireClient(host, port) as probe:
        probe.hello()
        info = probe.info()
        if "ws" not in info.get("framings", []):
            pytest.skip("agent does not advertise 'ws' framing")
    with WsWireClient(host, port) as c:
        c.hello()
        yield c


def needs_verb(capabilities: dict, verb: str) -> None:
    """Helper for tests: skip if the agent does not advertise the verb."""
    if verb not in capabilities:
        pytest.skip(f"agent does not advertise {verb}")


@pytest.fixture(scope="session")
def verb_defs(host: str, port: int, capabilities: dict) -> dict:
    """Verb name -> strict-tool definition, from `system.verbs` (v2.2+).
    Empty when the agent does not advertise `system.verbs`."""
    if "system.verbs" not in capabilities:
        return {}
    with WireClient(host, port) as c:
        c.hello()
        r = c.request("system.verbs")
    if not isinstance(r, OkResponse):
        return {}
    return json.loads(r.payload).get("verbs", {})


def needs_arg(verb_defs: dict, verb: str, arg: str) -> None:
    """Helper for tests of an argument added to an existing verb: skip
    unless the agent's own definition of `verb` declares `arg`."""
    props = verb_defs.get(verb, {}).get("input_schema", {}).get("properties", {})
    if arg not in props:
        pytest.skip(f"agent's {verb} does not declare {arg}")
