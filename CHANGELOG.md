# Changelog

## 0.1.2

Released 2026-11-24.

- Changed: `set_bypass` raises `ValueError` for an unknown mode, as `arm_area` does, instead of `KeyError`.
- New: the command-line tool reads the password from the `PROTEGE_PASSWORD` environment variable, or asks for it, when `--password` isn't given. `--password` still works, but it shows in your shell history.
- README: badges, and a warning about passwords on the command line.
- CI: `actions/checkout` v5.

## 0.1.1

Released 2026-11-22.

- Fixed: on a controller set to month/day dates, event times from the 1st to the 12th of a month were read as day/month (4 March became 3 April). The weekday the controller prints in front of each event now decides which it is.

## 0.1.0

Released 2026-11-20.

First release, moved out of the [ICT Protege WX integration for Home Assistant](https://github.com/olliemaller/ha-protege-wx) so it can be used on its own.

- `ProtegeClient`: login (both web protocol versions, auto-detected), status for areas, doors, inputs, trouble inputs and outputs, controls, event log, health values and troubles, with `LoginGuard` limits that protect the controller.
- `EventParser`: event log lines into kind, subject, type, user and method.
- Fixed: when two names overlap (doors "Front" and "Front Door"), an event for the longer one is no longer matched to the shorter.
- `aioprotegewx` command-line tool: `status`, `events`.
- Fully typed (`mypy --strict`), 97% test coverage.
