"""Async client for ICT Protege WX controllers, through their web interface.

Speaks the same encrypted protocol as the controller's own web pages, so no
Automation and Control licence is needed. Protocol work derived from
protege-wx-cli by Mitchell Johnson (MIT licence), extended for web UI 2.3.x
controllers.
"""

from __future__ import annotations

from .client import (
    PROTOCOL_AUTO,
    PROTOCOL_LEGACY,
    PROTOCOL_POST,
    TBL_AREAS,
    TBL_DOORS,
    TBL_INPUT_TYPES,
    TBL_INPUTS,
    TBL_OUTPUTS,
    TBL_TROUBLE_INPUTS,
    LoginGuard,
    ProtegeAuthError,
    ProtegeClient,
    ProtegeCommandError,
    ProtegeConnectionError,
    ProtegeError,
    ProtegeSessionError,
    normalise_host,
)
from .events import EventParser, ParsedEvent, ProtegeEvent
from .status import NO_RECORD, AreaStatus, DoorStatus, InputStatus, OutputStatus

__version__ = "0.1.1"

__all__ = [
    "NO_RECORD",
    "PROTOCOL_AUTO",
    "PROTOCOL_LEGACY",
    "PROTOCOL_POST",
    "TBL_AREAS",
    "TBL_DOORS",
    "TBL_INPUTS",
    "TBL_INPUT_TYPES",
    "TBL_OUTPUTS",
    "TBL_TROUBLE_INPUTS",
    "AreaStatus",
    "DoorStatus",
    "EventParser",
    "InputStatus",
    "LoginGuard",
    "OutputStatus",
    "ParsedEvent",
    "ProtegeAuthError",
    "ProtegeClient",
    "ProtegeCommandError",
    "ProtegeConnectionError",
    "ProtegeError",
    "ProtegeEvent",
    "ProtegeSessionError",
    "__version__",
    "normalise_host",
]
