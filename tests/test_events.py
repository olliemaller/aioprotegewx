"""Event log parsing: every kind of line the controller writes."""

from __future__ import annotations

from datetime import datetime

import pytest

from aioprotegewx.events import (
    EventParser,
    ProtegeEvent,
    parse_event_reply,
    parse_line,
)

PARSER = EventParser(
    areas=["House", "Panic Room", ""],
    doors=["Front Door", "Front"],
    inputs=["Lounge PIR"],
    troubles=["Mains Fail"],
)


def _parse(text: str):
    return PARSER.parse(ProtegeEvent(None, text))


@pytest.mark.parametrize(
    ("text", "kind", "subject", "event_type", "extra"),
    [
        ("Area House Armed By User Jane", "area", "House", "armed", {"mode": "away", "by": "Jane"}),
        ("Area House Stay Armed By User Jane", "area", "House", "armed", {"mode": "stay"}),
        ("Area House Instant Arming", "area", "House", "arming_started", {"mode": "instant"}),
        ("Area House Arming Cancelled", "area", "House", "arming_cancelled", {"mode": None}),
        ("Area House Failure To Arm", "area", "House", "failed_to_arm", {}),
        ("Area House Disarmed By ", "area", "House", "disarmed", {"by": None}),
        ("Area House Siren On", "area", "House", "alarm", {}),
        ("Area House Something Else", "area", "House", "other", {}),
        ("Area Panic Room Armed", "area", "Panic Room", "armed", {}),
        ("Area House Duress By User Jane", "emergency", "House", "duress", {"by": "Jane"}),
        ("Area Unknown Armed", "system", None, "other", {}),
        ("Trouble Input Mains Fail Open", "trouble", "Mains Fail", "trouble", {}),
        ("Trouble Input Mains Fail Closed", "trouble", "Mains Fail", "trouble_restored", {}),
        ("Trouble Input Mains Fail Bypassed", "trouble", "Mains Fail", "other", {}),
        ("Input Lounge PIR Open", "input", "Lounge PIR", "open", {}),
        ("Input Lounge PIR", "input", "Lounge PIR", "other", {}),
        ("Door Front Door Forced Open", "door", "Front Door", "forced_open", {}),
        ("Door Front Door Left Open", "door", "Front Door", "left_open", {}),
        ("Door Front Door Unlocked By User Jane", "door", "Front Door", "unlocked", {"by": "Jane"}),
        ("Door Front Door Locked", "door", "Front Door", "locked", {}),
        ("Door Front Door Opened", "door", "Front Door", "opened", {}),
        ("Door Front Door Closed", "door", "Front Door", "closed", {}),
        ("Door Front Door Beeped", "door", "Front Door", "other", {}),
        ("Door Front", "door", "Front", "other", {}),
        (
            "User Jane Entry Granted Front Door Using Card And PIN",
            "access",
            "Front Door",
            "access_granted",
            {"user": "Jane", "method": "card_and_pin"},
        ),
        (
            "User Jane Exit Denied Front Door Using PIN",
            "access",
            "Front Door",
            "access_denied",
            {"method": "pin"},
        ),
        (
            "User Jane Access Granted Back Gate Using Credential",
            "access",
            "Back Gate",
            "access_granted",
            {"method": "card"},
        ),
        (
            "User Jane Access Granted Front Door Using Face Scan",
            "access",
            "Front Door",
            "access_granted",
            {"method": "face_scan"},
        ),
        (
            "User Jane Access Granted Front Door",
            "access",
            "Front Door",
            "access_granted",
            {"method": None},
        ),
        ("User Jane Medical Alarm", "emergency", None, "medical", {"by": "Jane"}),
        ("User Jane Logged In", "system", None, "other", {}),
        ("Duress Alarm At Keypad 1", "emergency", None, "duress", {}),
        ("Hold-Up Alarm By User Bob", "emergency", None, "panic", {"by": "Bob"}),
        ("System Power Up", "system", None, "power_up", {}),
        ("Output Siren On", "noise", None, "other", {}),
    ],
)
def test_parse(text: str, kind: str, subject: str | None, event_type: str, extra: dict) -> None:
    parsed = _parse(text)
    assert (parsed.kind, parsed.subject, parsed.event_type) == (kind, subject, event_type)
    for key, value in extra.items():
        assert getattr(parsed, key) == value


@pytest.mark.parametrize(
    ("line", "when"),
    [
        ("20/11/2026 15:04:05 Area House Armed", datetime(2026, 11, 20, 15, 4, 5)),
        ("Fri 11/20/2026 15:04:05 Area House Armed", datetime(2026, 11, 20, 15, 4, 5)),
        ("2026-11-20 15:04:05 Area House Armed", datetime(2026, 11, 20, 15, 4, 5)),
        ("2026/11/20 15:04:05 Area House Armed", datetime(2026, 11, 20, 15, 4, 5)),
        ("99/99/9999 15:04:05 Area House Armed", None),
        ("no timestamp here", None),
    ],
)
def test_timestamps(line: str, when: datetime | None) -> None:
    event = parse_line(line)
    assert event.time == when
    if when is not None:
        assert event.text == "Area House Armed"


def test_reply_is_sorted_and_skips_junk() -> None:
    reply = (
        "Event0=20/11/2026 15:00:02 Second&"
        "Event1=20/11/2026 15:00:01 First&"
        "Event2=&EventCodes0=1,2&junk&Eventx=nope&"
        "Event3=No time"
    )
    texts = [event.text for event in parse_event_reply(reply)]
    assert texts == ["No time", "First", "Second"]
