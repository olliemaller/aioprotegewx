"""The command-line tool, against the fake controller."""

from __future__ import annotations

import argparse
import json

import pytest

from aioprotegewx.__main__ import _run, main

from .fake_controller import FakeController
from .test_client import server_factory  # noqa: F401


async def test_status_and_events(server_factory, capsys) -> None:  # noqa: F811
    host = await server_factory(FakeController())
    args = argparse.Namespace(host=host, username="Home Assistant", password="secret")
    args.command = "status"
    await _run(args)
    status = json.loads(capsys.readouterr().out)
    assert status["doors"]["0"]["lock"] == "locked"
    args.command = "events"
    await _run(args)
    assert json.loads(capsys.readouterr().out)[-1]["text"].startswith("Area Alarm")


def test_error_exits(capsys, monkeypatch) -> None:
    from aioprotegewx import ProtegeConnectionError
    import aioprotegewx.__main__ as cli

    async def fail(_args) -> None:
        raise ProtegeConnectionError("nope")

    monkeypatch.setattr(cli, "_run", fail)
    with pytest.raises(SystemExit):
        main(["-v", "status", "h", "--username", "u", "--password", "p"])
    assert "error: nope" in capsys.readouterr().err
