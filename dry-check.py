#!/usr/bin/env python3
import sys
import time
import json
import requests
import subprocess
import yaml
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.yaml"

def log(msg):
    # Unbuffered, timestamped logging
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r") as f:
        cfg = yaml.safe_load(f) or {}
    if "latitude" not in cfg or "longitude" not in cfg:
        raise ValueError("config.yaml must contain 'latitude' and 'longitude'")
    # Defaults
    cfg.setdefault("check_interval", 300)
    cfg.setdefault("alert_once", True)
    return cfg

def get_rain_status(lat, lon):
    """
    Return (raining: bool, details: str).
    Prefer 'current' fields; fallback to first hourly value if needed.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=precipitation,rain"
        "&hourly=precipitation"
        "&forecast_days=1"
        "&timezone=UTC"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    # Try current first
    current = data.get("current")
    if current and ("precipitation" in current or "rain" in current):
        precip = float(current.get("precipitation", 0.0) or 0.0)
        rain = float(current.get("rain", 0.0) or 0.0)
        raining = (precip > 0.0) or (rain > 0.0)
        detail = f"current precip={precip}mm, rain={rain}mm"
        return raining, detail

    # Fallback: first hourly precipitation entry
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    precs = hourly.get("precipitation", [])
    if precs:
        precip0 = float(precs[0] or 0.0)
        t0 = times[0] if times else "unknown"
        raining = precip0 > 0.0
        detail = f"hourly[0] {t0} precip={precip0}mm"
        return raining, detail

    # If API shape unexpected
    return False, "no precipitation fields found"

def notify(title, message):
    # Best-effort notification; log failures instead of crashing
    try:
        subprocess.run(["notify-send", title, message], check=False)
    except Exception as e:
        log(f"notify-send failed: {e}")

def main():
    # Ensure unbuffered stdout (also works if launched without -u)
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    log("Starting dry-check…")
    try:
        cfg = load_config()
    except Exception as e:
        log(f"Config error: {e}")
        sys.exit(1)

    lat = cfg["latitude"]
    lon = cfg["longitude"]
    interval = int(cfg["check_interval"])
    alert_once = bool(cfg["alert_once"])

    log(f"Config: lat={lat}, lon={lon}, interval={interval}s, alert_once={alert_once}")

    # Assume it was raining until proven otherwise, so we can catch the first dry break.
    was_raining = True
    notified = False

    while True:
        try:
            raining, detail = get_rain_status(lat, lon)
            status = "🌧️ Raining" if raining else "🌤️ Dry"
            log(f"{status} ({detail})")

            if was_raining and not raining:
                if not notified or not alert_once:
                    notify("Dry Now", "Rain stopped — time to go out!")
                    log("Sent notification: Dry Now")
                    if alert_once:
                        notified = True

            was_raining = raining
        except requests.RequestException as e:
            log(f"Network/API error: {e}")
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            log(f"Parse error: {e}")
        except Exception as e:
            log(f"Unexpected error: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    main()
