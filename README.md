# aioprotegewx

Async Python client for **ICT Protege WX** alarm and access controllers, through the controller's own **web interface**.

ICT's official integration route, the Automation and Control service, needs a paid licence that many WX controllers don't have. Every WX has a web interface, and this library speaks the same encrypted protocol as its pages. If you can log in to the controller in a browser, you can use this.

It powers the [ICT Protege WX integration for Home Assistant](https://github.com/olliemaller/ha-protege-wx).

- Areas: status, arm (away, stay, instant, force), disarm, silence, walk test.
- Doors: lock state and position, lock, unlock (timed or latched).
- Inputs and trouble inputs: open, closed, tamper, short, bypass (temporary or permanent).
- Outputs: on, off, timed.
- Event log pages, parsed into what happened, to what, and who did it.
- Health values (serial number, firmware, voltages) and health troubles.
- Both web protocol versions, detected automatically: **2.3.x** (HTTP POST with a controller session cookie) and older (HTTP GET with a client session).

Python 3.12 or later. Plain HTTP only: controllers whose web interface is HTTPS-only need the Automation and Control route.

## Install

```bash
pip install aioprotegewx
```

## Use

Create an **operator** on the controller for your program, with only the permissions it needs. Set its session timeout to about 15 minutes.

```python
import asyncio
import aiohttp
from aioprotegewx import ProtegeClient


async def main() -> None:
    # The controller issues its own session cookie, so give the client a jar that accepts it.
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        client = ProtegeClient(session, "192.168.1.10:7377", "homeassistant", "password")
        try:
            areas = await client.area_status()
            for rec_id, area in areas.items():
                print(rec_id, area.state, area.in_alarm)
            await client.arm_area(16, "stay")
        finally:
            await client.close()  # logs out


asyncio.run(main())
```

The client logs in on first use and keeps one session. Unknown or unreadable states come back as `None` or `unknown_<code>`, never as a reassuring *disarmed*, *locked* or *closed*.

## Being gentle with the controller

A controller whose session table filled with abandoned sessions has been seen to stall and reboot, so the client is careful:

- **One session**, logged out by `close()`.
- **Gentle reconnects.** A dropped session is re-established once. If the controller refuses straight away, logins pause for 30 s, doubling up to 10 minutes, and never exceed 6 in 10 minutes. Share one `LoginGuard` between clients for the same controller so restarts can't get round these limits.
- **No operator lockouts.** A wrong password stops all login attempts after at most two tries (`auth_failed` stays set).

## Command line

```bash
aioprotegewx status 192.168.1.10:7377 --username homeassistant --password ...
aioprotegewx events 192.168.1.10:7377 --username homeassistant --password ...
```

## Development

```bash
pip install -e ".[test,lint]"
pytest --cov=aioprotegewx
ruff check . && ruff format --check . && mypy
```

Releases are automatic: bump `__version__` in `src/aioprotegewx/__init__.py`, add a `CHANGELOG.md` section, and push to `main`.

## Credits and licence

Protocol work derived from [protege-wx-cli](https://github.com/mitchell-johnson/protege-wx-cli) by Mitchell Johnson (MIT), extended for web interface 2.3.x. [MIT](LICENSE); see [NOTICE](NOTICE).
