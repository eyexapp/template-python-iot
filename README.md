# 🔧 Python IoT/Hardware Template

Production-ready Python template for IoT sensor data collection, device control,
and edge computing. Supports Raspberry Pi (GPIO, I2C), ESP32 (via serial bridge),
and general-purpose IoT platforms.

## Features

- **6 Communication Protocols** — MQTT, Serial/UART, BLE, HTTP/REST, WebSocket
- **Hardware Abstraction** — ABC-based `SensorDriver` / `ActuatorDriver` with mock, GPIO, I2C implementations
- **Async + Thread Hybrid** — asyncio core with `asyncio.to_thread` for blocking I/O
- **Mock-First Development** — Runs 100% on desktop without hardware (`MOCK_MODE=true`)
- **SQLite Storage** — Time-series sensor data with cleanup and range queries
- **Structured Logging** — structlog (JSON in prod, colored in dev)
- **Typed Config** — pydantic-settings with `.env` file support
- **i18n** — Simple `t("key")` translation helper (EN/TR included)
- **Docker** — Multi-arch image (ARM64 + AMD64) with Mosquitto MQTT broker
- **Deployment** — systemd service, Grafana dashboard, OTA update script
- **CI/CD** — GitHub Actions (lint + test + Docker build), pre-commit hooks

## Quick Start

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone and enter the project
git clone <your-repo-url> myapp
cd myapp

# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
uv run python -m myapp
```

### Raspberry Pi (with GPIO/I2C)

```bash
# Install with RPi extras
uv sync --extra rpi

# Set MOCK_MODE=false in .env
# Configure GPIO/I2C pins in .env
uv run python -m myapp
```

## Project Structure

```
python-iot/
├── src/myapp/
│   ├── __init__.py              # Package root
│   ├── __main__.py              # Entry point
│   ├── app.py                   # Application orchestrator
│   ├── config.py                # Environment settings
│   ├── drivers/
│   │   ├── base.py              # SensorDriver & ActuatorDriver ABCs
│   │   ├── mock_driver.py       # Mock sensors (desktop development)
│   │   ├── gpio_driver.py       # Raspberry Pi GPIO (optional)
│   │   └── i2c_driver.py        # Raspberry Pi I2C (optional)
│   ├── protocols/
│   │   ├── mqtt_client.py       # MQTT (paho-mqtt v2)
│   │   ├── serial_client.py     # Serial/UART (pyserial)
│   │   ├── ble_client.py        # BLE (bleak)
│   │   ├── http_client.py       # HTTP/REST (httpx)
│   │   └── ws_client.py         # WebSocket (websockets)
│   ├── services/
│   │   ├── collector.py         # Sensor polling & dispatch
│   │   └── watchdog.py          # Health monitoring
│   ├── storage/
│   │   └── sqlite.py            # Time-series SQLite storage
│   ├── utils/
│   │   └── logger.py            # Structured logging setup
│   └── i18n/                    # Translations (en, tr)
├── tests/                       # pytest + pytest-asyncio
├── deploy/
│   ├── myapp.service            # systemd unit file
│   ├── grafana/dashboard.json   # Grafana sensor dashboard
│   ├── mosquitto/mosquitto.conf # MQTT broker config
│   └── ota/update.sh            # OTA update script
├── .github/
│   ├── workflows/ci.yml         # GitHub Actions CI
│   └── copilot-instructions.md  # AI assistant context
├── Dockerfile                   # Multi-arch Docker image
├── docker-compose.yml           # App + Mosquitto stack
├── pyproject.toml               # Dependencies & tool config
└── .pre-commit-config.yaml      # Pre-commit hooks
```

## Configuration

All settings are managed via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `myapp` | Application name |
| `APP_ENV` | `development` | Environment (`development` / `production`) |
| `LOG_LEVEL` | `INFO` | Log level |
| `LOCALE` | `en` | Language (`en` / `tr`) |
| `MOCK_MODE` | `true` | Use mock sensors (no hardware needed) |
| `POLL_INTERVAL_SECONDS` | `5.0` | Sensor polling interval |
| `MQTT_BROKER` | `localhost` | MQTT broker address |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_TOPIC_PREFIX` | `myapp/sensors` | MQTT topic prefix |
| `SERIAL_PORT` | `/dev/ttyUSB0` | Serial port path |
| `SERIAL_BAUDRATE` | `9600` | Serial baud rate |
| `HTTP_ENDPOINT` | `http://localhost:8080/api/readings` | HTTP endpoint |
| `WS_URL` | `ws://localhost:8765` | WebSocket URL |
| `DB_PATH` | `data/sensor_data.db` | SQLite database path |

## Development

### Running Tests

```bash
uv run pytest                    # All tests
uv run pytest -v                 # Verbose output
uv run pytest --tb=short -q      # Compact output
```

### Linting & Formatting

```bash
uv run ruff check src/ tests/    # Lint
uv run ruff check --fix src/     # Auto-fix
uv run ruff format src/ tests/   # Format
uv run mypy src/                 # Type checking
```

### Pre-commit Hooks

```bash
uv run pre-commit install        # Install hooks
uv run pre-commit run --all      # Run manually
```

## Adding Custom Hardware

### New Sensor

```python
# src/myapp/drivers/my_sensor.py
from myapp.drivers.base import SensorDriver, SensorReading

class MySensor(SensorDriver):
    @property
    def name(self) -> str:
        return "my_sensor"

    async def setup(self) -> None:
        # Initialize hardware
        ...

    async def teardown(self) -> None:
        # Cleanup resources
        ...

    async def read(self) -> SensorReading:
        value = ...  # Read from hardware
        return SensorReading(
            name=self.name,
            value=value,
            unit="°C",
        )
```

Then register it in `app.py`:

```python
def _create_sensors(self) -> list[SensorDriver]:
    if settings.mock_mode:
        return [MockTemperatureSensor(), MockHumiditySensor()]
    return [MySensor(), ...]
```

### New Protocol

```python
# src/myapp/protocols/my_protocol.py
class MyProtocolClient:
    async def connect(self) -> None: ...
    async def publish(self, topic: str, payload: str) -> None: ...
    async def disconnect(self) -> None: ...
```

## Deployment

### Docker

```bash
# Run with Docker Compose (app + Mosquitto MQTT)
docker compose up -d

# View logs
docker compose logs -f app

# Multi-arch build for Raspberry Pi
docker buildx build --platform linux/arm64 -t myapp .
```

### systemd (Raspberry Pi)

```bash
# Copy service file
sudo cp deploy/myapp.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now myapp

# Check status and logs
systemctl status myapp
journalctl -u myapp -f
```

### OTA Updates

```bash
# Manual update
sudo deploy/ota/update.sh

# Automatic via cron (daily at 3 AM)
# Add to crontab: 0 3 * * * /home/pi/myapp/deploy/ota/update.sh
```

### Grafana Dashboard

1. Install Grafana and the [SQLite datasource plugin](https://grafana.com/grafana/plugins/frser-sqlite-datasource/)
2. Add SQLite datasource pointing to `data/sensor_data.db`
3. Import `deploy/grafana/dashboard.json`

## Tech Stack

| Category | Tool |
|----------|------|
| Language | Python 3.11+ |
| Package Manager | UV |
| MQTT | paho-mqtt 2.x |
| Serial | pyserial |
| BLE | bleak |
| HTTP | httpx |
| WebSocket | websockets |
| GPIO | gpiozero (optional) |
| I2C | smbus2 (optional) |
| Storage | SQLite (stdlib) |
| Config | pydantic-settings |
| Logging | structlog |
| Testing | pytest + pytest-asyncio |
| Linting | Ruff |
| Type Checking | mypy (strict) |
| CI | GitHub Actions |
| Container | Docker (multi-arch) |

## License

MIT
