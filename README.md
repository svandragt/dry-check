# 🌤 dry-check

A tiny Python utility that notifies you **the next time it stops raining** — perfect for deciding when to take the dog out.

Powered by [Open-Meteo](https://open-meteo.com) and `notify-send`, built for Linux (tested on ElementaryOS 7 / Ubuntu 22.04).

---

## 🧩 Features

- Checks your local weather periodically using Open-Meteo  
- Sends a desktop notification via `notify-send` when it becomes dry  
- Configurable interval, latitude/longitude, and single/recurring alerts  
- YAML-based config (no code changces needed)  
- Runs cleanly with [uv](https://docs.astral.sh/uv/) or system Python

---

## ⚙️ Installation

### Prerequisites

```bash
sudo apt install libnotify-bin
````

### Clone & setup

```bash
git clone https://github.com/<your-username>/dry-check.git
cd dry-check
```

Create a virtual environment with **uv** (recommended):

```bash
uv sync
```

---

## 🧾 Configuration

Edit `config.yaml`:

```yaml
latitude: 51.538
longitude: 0.711
check_interval: 300  # seconds between checks
alert_once: true     # notify only the first time it’s dry
```

---

## ▶️ Usage

Run directly:

```bash
uv run dry_check.py
```

Or in the background:

```bash
nohup uv run dry_check.py &
```

You’ll see console logs like:

```
[2025-12-09 17:12:00] 🌧️ Raining (current precip=0.3mm)
[2025-12-09 17:17:00] 🌤️ Dry (current precip=0.0mm)
```

When rain stops, you’ll get a desktop notification:

> 🌤 Dry Now — Rain stopped, time to go out!

---

## 🧰 Tech notes

* Weather data: [Open-Meteo API](https://open-meteo.com/)
* Notifications: `notify-send` (`libnotify-bin`)
* Dependencies: `requests`, `PyYAML`
* Compatible with Python ≥ 3.8


---

Would you like me to add the **“run-once” mode instructions** and flag to the README (so users can use it from cron without a loop)?
```
