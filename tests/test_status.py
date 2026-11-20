"""Status replies: areas, doors, inputs and outputs."""

from __future__ import annotations

from aioprotegewx.status import (
    NO_RECORD,
    parse_areas,
    parse_doors,
    parse_inputs,
    parse_outputs,
    split_records,
)


def test_split_records_skips_junk_and_sentinel() -> None:
    raw = f"Area1=0,0,0&Area{NO_RECORD}=0,0,0&junk&Bad=1&Area2=1,2,3\n"
    assert split_records(raw) == {1: "0,0,0", 2: "1,2,3"}


def test_areas() -> None:
    areas = parse_areas("Area1=0,0,0&Area2=0,128,2&Area3=0,130,1&Area4=0,1,x&Area5=0,99,0")
    disarmed, siren, entry_alarm, garbage, odd = (areas[i] for i in range(1, 6))
    assert disarmed.known and disarmed.state == "disarmed"
    assert not disarmed.not_ready and not disarmed.is_armed_or_arming and not disarmed.in_alarm
    assert siren.state == "armed" and siren.in_alarm and siren.is_armed_or_arming
    assert entry_alarm.state == "entry_delay" and entry_alarm.in_alarm
    assert garbage.not_ready and not garbage.known  # flags unreadable
    assert odd.state == "unknown_99" and not odd.known


def test_doors() -> None:
    doors = parse_doors("Door1=0,0&Door2=4,1&Door3=255,255&Door4=77,9&Door5=")
    locked, latched, unknown, odd, empty = (doors[i] for i in range(1, 6))
    assert (locked.lock, locked.position) == ("locked", "closed")
    assert locked.is_locked and not locked.is_latched and locked.is_open is False
    assert latched.is_latched and not latched.is_locked and latched.is_open
    assert unknown.is_locked is None and unknown.is_latched is None and unknown.is_open is None
    assert odd.lock == "unknown_77" and odd.position == "unknown_9"
    assert odd.is_locked is None and odd.is_open is None
    assert empty.lock == "unknown_None"


def test_inputs() -> None:
    inputs = parse_inputs("Input1=0,0&Input2=1,1&Input3=2,2&Input4=3,3&Input5=9,0")
    closed, open_, tamper, short, odd = (inputs[i] for i in range(1, 6))
    assert closed.is_open is False and closed.is_tampered is False and closed.bypass == "none"
    assert open_.is_open and open_.bypass == "temporary" and open_.state == "open"
    assert tamper.is_tampered and tamper.bypass == "permanent"
    assert short.is_tampered and short.is_open
    assert odd.is_open is None and odd.is_tampered is None and odd.state == "unknown_9"


def test_outputs() -> None:
    outputs = parse_outputs("Output1=0&Output2=3&Output3=8")
    assert outputs[1].is_on is False and outputs[1].state == "off"
    assert outputs[2].is_on and outputs[2].state == "on_timed"
    assert outputs[3].is_on is None and outputs[3].state == "unknown_8"
