"""Command-line tool: ``python -m aioprotegewx`` or ``aioprotegewx``.

Examples::

    aioprotegewx status 192.168.1.10:7377 --username homeassistant
    PROTEGE_PASSWORD=... aioprotegewx events 192.168.1.10:7377 --username homeassistant

The password comes from --password, else the PROTEGE_PASSWORD environment
variable, else a prompt.
"""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence
from dataclasses import asdict
import getpass
import json
import logging
import os
import sys
from typing import Any

import aiohttp

from . import ProtegeClient, ProtegeError


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str))


async def _run(args: argparse.Namespace) -> None:
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        client = ProtegeClient(session, args.host, args.username, args.password)
        try:
            await client.login()
            if args.command == "status":
                _print(
                    {
                        "health": await client.health_values(),
                        "areas": {k: v.state for k, v in (await client.area_status()).items()},
                        "doors": {
                            k: {"lock": v.lock, "position": v.position}
                            for k, v in (await client.door_status()).items()
                        },
                        "inputs": {k: v.state for k, v in (await client.input_status()).items()},
                    }
                )
            else:
                _print([asdict(event) for event in await client.events()])
        finally:
            # Always log out: the controller has a small session table.
            await client.close()


def main(argv: Sequence[str] | None = None) -> None:
    """Run the command-line tool."""
    parser = argparse.ArgumentParser(prog="aioprotegewx", description=__doc__.splitlines()[0])
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, text in (
        ("status", "read areas, doors, inputs and health"),
        ("events", "read the newest page of the event log"),
    ):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("host", help="address and port, e.g. 192.168.1.10:7377")
        cmd.add_argument("--username", required=True)
        cmd.add_argument(
            "--password",
            help="shows in your shell history and process list; "
            "prefer PROTEGE_PASSWORD or the prompt",
        )
    args = parser.parse_args(argv)
    if args.password is None:
        args.password = os.environ.get("PROTEGE_PASSWORD") or getpass.getpass("Password: ")
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)
    try:
        asyncio.run(_run(args))
    except ProtegeError as err:
        print(f"error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
