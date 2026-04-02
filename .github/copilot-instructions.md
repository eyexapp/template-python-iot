# IoT/Hardware Python Template — Copilot Instructions

## Project Overview

This is a **Python IoT/Hardware** template for sensor data collection, device
control, and edge computing. It targets Raspberry Pi, ESP32 (via MicroPython
bridge), and general-purpose IoT platforms.

## Architecture

- **Async-first**: Core loop runs on `asyncio`. Blocking I/O (GPIO, Serial, I2C)
  is offloaded via `asyncio.to_thread`.
- **ABC-based hardware abstraction**: All sensors implement `SensorDriver`, all
  actuators implement `ActuatorDriver` (see `drivers/base.py`).
- **Mock-first development**: The app runs 100% on desktop using `MockTemperatureSensor`,
  `MockHumiditySensor`, `MockLED`. Set `MOCK_MODE=true` in `.env`.
- **Protocol-agnostic**: MQTT, Serial, BLE, HTTP, WebSocket clients are independent
  modules under `protocols/`.

## Key Conventions

- **Package manager**: UV (`uv sync`, `uv run`)
- **Config**: Pydantic Settings via environment variables (`.env` file)
- **Logging**: structlog — JSON in production, colored in development
- **i18n**: Simple `t("key")` helper with JSON locale files
- **Type safety**: mypy strict mode, `from __future__ import annotations`
- **Linting**: Ruff with extensive rule set (see `pyproject.toml`)

## File Layout

```
src/myapp/
├── __init__.py          # Package root
├── __main__.py          # Entry: asyncio.run(Application().run())
├── app.py               # Application orchestrator, signal handling
├── config.py            # Settings (pydantic-settings, env vars)
├── drivers/
│   ├── base.py          # SensorDriver, ActuatorDriver ABCs
│   ├── mock_driver.py   # Mock sensors/actuators for desktop dev
│   ├── gpio_driver.py   # RPi GPIO (gpiozero) — optional
│   └── i2c_driver.py    # RPi I2C (smbus2) — optional
├── protocols/
│   ├── mqtt_client.py   # Paho MQTT v2
│   ├── serial_client.py # PySerial async wrapper
│   ├── ble_client.py    # Bleak BLE
│   ├── http_client.py   # httpx async
│   └── ws_client.py     # websockets async
├── services/
│   ├── collector.py     # Sensor polling + dispatch
│   └── watchdog.py      # Health monitoring
├── storage/
│   └── sqlite.py        # SQLite time-series storage
├── utils/
│   └── logger.py        # structlog setup
└── i18n/
    ├── __init__.py      # t() helper
    ├── en.json
    └── tr.json
```

## Adding a New Sensor

1. Create a class in `drivers/` implementing `SensorDriver`
2. Implement `name`, `setup()`, `teardown()`, `read()` → `SensorReading`
3. Register it in `app.py` `_create_sensors()` method
4. Add corresponding test in `tests/test_drivers.py`

## Adding a New Protocol

1. Create an async client in `protocols/`
2. Implement `connect()`, `publish()` or `send()`, `disconnect()`
3. Wire it in `app.py` if needed (like MQTT)

## Commands

```bash
uv sync                    # Install deps
uv run python -m myapp     # Run the app
uv run pytest              # Run tests
uv run ruff check src/     # Lint
uv run mypy src/           # Type check
```

## Testing

- Tests live in `tests/` and use pytest + pytest-asyncio
- Mock drivers are used — no hardware needed
- `conftest.py` provides reusable fixtures

## Deployment

- **Systemd**: `deploy/myapp.service`
- **Docker**: `Dockerfile` + `docker-compose.yml` (with Mosquitto)
- **OTA**: `deploy/ota/update.sh` (git pull + uv sync + restart)
- **Grafana**: `deploy/grafana/dashboard.json`
