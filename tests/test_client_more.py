"""More of ProtegeClient: records, health, events and error paths."""

from __future__ import annotations

import aiohttp
import pytest

from aioprotegewx import (
    TBL_AREAS,
    TBL_DOORS,
    ProtegeClient,
    ProtegeCommandError,
    ProtegeConnectionError,
    ProtegeSessionError,
)
from aioprotegewx import client as client_module

from .fake_controller import FakeController
from .test_client import _client, server_factory  # noqa: F401


async def test_records_health_and_events(server_factory) -> None:  # noqa: F811
    controller = FakeController()
    controller.health_troubles = ["Mains failure"]
    host = await server_factory(controller)
    client, session = await _client(host)
    try:
        await client.login()
        assert client.logged_in
        assert (await client.list_records(TBL_DOORS))[0] == "Front Door"
        assert await client.get_record(TBL_AREAS, 16)
        assert "SerialNumber" in await client.health_values()
        assert await client.health_troubles() == ["Mains failure"]
        events = await client.events()
        assert events[-1].text == "Area Alarm Disarmed By Home Assistant"
        assert await client.trouble_input_status()
        await client.disarm_area(16)
        await client.lock_door(0)
        await client.set_output(120, True)
        await client.set_output(120, False)
        await client.set_bypass(3, "none")
    finally:
        await client.close()
        await session.close()


async def test_details_not_permitted(server_factory) -> None:  # noqa: F811
    controller = FakeController(permit_details=False)
    host = await server_factory(controller)
    client, session = await _client(host)
    try:
        await client.login()
        assert await client.get_record(TBL_AREAS, 16) == {}
    finally:
        await client.close()
        await session.close()


async def test_offline_controller(server_factory) -> None:  # noqa: F811
    controller = FakeController()
    controller.offline = True
    host = await server_factory(controller)
    client, session = await _client(host)
    try:
        with pytest.raises(ProtegeConnectionError, match="HTTP 503"):
            await client.login()
    finally:
        await client.close()
        await session.close()


async def test_retries_run_out(server_factory, monkeypatch) -> None:  # noqa: F811
    controller = FakeController()
    host = await server_factory(controller)
    client, session = await _client(host)
    try:
        await client.login()
        controller.retry_replies = 100
        with pytest.raises(ProtegeCommandError):
            await client.area_status()
    finally:
        controller.retry_replies = 0
        await client.close()
        await session.close()


async def test_closed_session_and_not_logged_in() -> None:
    session = aiohttp.ClientSession()
    client = ProtegeClient(session, "127.0.0.1:1", "u", "p")
    assert not client.logged_in
    with pytest.raises(ProtegeSessionError):
        await client._query_once("Request&Type=Health&SubType=Values")
    await session.close()
    with pytest.raises(ProtegeConnectionError, match="closed"):
        await client._send("x", client_module.PROTOCOL_POST)


def test_bad_protocol() -> None:
    with pytest.raises(ValueError, match="protocol"):
        ProtegeClient(None, "host", "u", "p", protocol="nope")  # type: ignore[arg-type]


async def test_walk_test_and_silence(server_factory) -> None:  # noqa: F811
    controller = FakeController()
    host = await server_factory(controller)
    client, session = await _client(host)
    try:
        await client.walk_test(16, True)
        await client.walk_test(16, False)
        await client.silence_area(16)
    finally:
        await client.close()
        await session.close()
