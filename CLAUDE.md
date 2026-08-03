# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Python script (`dry-check.py`) that polls the Open-Meteo API for
rain status at a fixed location and sends a `notify-send` desktop
notification the moment rain stops. It runs as a long-lived foreground loop
(or backgrounded with `nohup`), not a daemon/service.

## Commands

Run it:
```bash
uv sync
uv run dry-check.py
```

Run the test suite:
```bash
uv run --with pytest pytest -q
```

`tests/test_smoke.py` only checks that the script byte-compiles — there is no
functional test coverage of `get_rain_status()` or the poll loop.

## Configuration

`config.yaml` (gitignored, copy from `config.yaml.example`) holds:
- `latitude` / `longitude` — required, no defaults
- `check_interval` — seconds between polls, defaults to 300
- `alert_once` — if true, notify only on the first dry transition, defaults to true

`load_config()` in `dry-check.py` raises if `config.yaml` is missing or lacks
lat/lon — there is no fallback location.

## Architecture

Everything lives in `dry-check.py`:
- `get_rain_status(lat, lon)` — calls Open-Meteo, prefers the `current`
  precipitation/rain fields, falls back to the first `hourly` entry if
  `current` is absent from the response.
- `main()` — owns the poll loop and the rain-state machine: it assumes it
  `was_raining = True` at startup (so a dry state on the very first check
  still fires a notification), tracks the transition from raining to dry,
  and calls `notify()` on that edge. Network/parse errors are caught per-loop
  iteration and logged, not raised, so a single bad API response doesn't kill
  the loop.
- `notify()` shells out to `notify-send`; failures are logged, not fatal.

Runtime dependency: `notify-send` (Linux, `libnotify-bin`) must be on PATH.

## CI and dependency updates

- `.github/workflows/ci.yml` runs the test suite on push/PR to `main`.
- `.github/dependabot.yml` opens weekly PRs for `uv` and GitHub Actions dependencies.
- `.github/workflows/dependabot-auto-merge.yml` enables auto-merge on
  Dependabot PRs; they merge once the required `test` status check passes
  (enforced by branch protection on `main`).
