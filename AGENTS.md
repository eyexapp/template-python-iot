# AGENTS.md — Python IoT / Embedded Systems

## Project Identity

| Key | Value |
|-----|-------|
| Runtime | Python 3.12+ (asyncio) |
| Category | IoT / Edge Computing |
| Package Manager | UV |
| Config | Pydantic Settings (`.env`) |
| Logging | structlog (JSON prod, colored dev) |
| Testing | pytest + pytest-asyncio |
| Linting | Ruff (extensive rules) |
| Type Checking | mypy (strict mode) |
| Targets | Raspberry Pi, ESP32 (MicroPython bridge), desktop (mock mode) |

---

## Architecture — Async-First + Hardware Abstraction

```
src/myapp/
├── __init__.py          ← Package root
├── __main__.py          ← Entry: asyncio.run(Application().run())
├── app.py               ← Orchestrator: signal handling, lifecycle
├── config.py            ← Pydantic Settings (env vars)
├── drivers/
│   ├── base.py          ← ABCs: SensorDriver, ActuatorDriver
│   ├── mock_driver.py   ← Mock sensors/actuators (MOCK_MODE=true)
│   ├── gpio_driver.py   ← RPi GPIO (gpiozero) — optional
│   └── i2c_driver.py    ← RPi I2C (smbus2) — optional
├── protocols/
│   ├── mqtt_client.py   ← Paho MQTT v2
│   ├── serial_client.py ← PySerial async wrapper
│   ├── ble_client.py    ← Bleak BLE
│   ├── http_client.py   ← httpx async
│   └── ws_client.py     ← websockets async
├── services/
│   ├── collector.py     ← Sensor polling + dispatch
│   └── watchdog.py      ← Health monitoring
├── storage/
│   └── sqlite.py        ← SQLite time-series storage
├── utils/
│   └── logger.py        ← structlog setup
└── i18n/
    ├── __init__.py      ← t() helper
    ├── en.json
    └── tr.json
```

### Strict Layer Rules

| Layer | Can Import From | NEVER Imports |
|-------|----------------|---------------|
| `drivers/` | `config`, `utils/` | protocols/, services/ |
| `protocols/` | `config`, `utils/` | drivers/, services/ |
| `services/` | drivers/, protocols/, storage/, config, utils/ | app.py |
| `storage/` | config, utils/ | drivers/, protocols/, services/ |
| `app.py` | Everything (composition root) | — |

---

## Adding New Code — Where Things Go

### New Sensor Checklist
1. **Driver**: `src/myapp/drivers/new_sensor.py` implementing `SensorDriver` ABC
2. **Implement**: `name`, `setup()`, `teardown()`, `read()` → `SensorReading`
3. **Register**: Wire in `app.py` → `_create_sensors()` method
4. **Mock**: Add mock variant in `mock_driver.py`
5. **Test**: `tests/test_drivers.py`

### New Protocol Checklist
1. **Client**: `src/myapp/protocols/new_protocol.py`
2. **Implement**: `connect()`, `publish()` or `send()`, `disconnect()`
3. **Wire**: Connect in `app.py` if needed

### Driver ABC Pattern
```python
from abc import ABC, abstractmethod
from myapp.drivers.base import SensorDriver, SensorReading

class TemperatureSensor(SensorDriver):
    @property
    def name(self) -> str:
        return "bme280_temperature"

    async def setup(self) -> None:
        # Initialize hardware
        ...

    async def teardown(self) -> None:
        # Release hardware
        ...

    async def read(self) -> SensorReading:
        # asyncio.to_thread for blocking I/O
        raw = await asyncio.to_thread(self._read_i2c)
        return SensorReading(sensor=self.name, value=raw, unit="°C")
```

---

## Design & Architecture Principles

### Async-First — Blocking I/O via `to_thread`
```python
# ✅ Offload blocking GPIO/Serial/I2C to thread pool
value = await asyncio.to_thread(self._read_gpio)

# ❌ NEVER block the event loop
value = self._read_gpio()  # Blocks asyncio!
```

### Mock-First Development
```python
# MOCK_MODE=true in .env → runs 100% on desktop
# MockTemperatureSensor, MockHumiditySensor, MockLED
# Real drivers loaded only when MOCK_MODE=false
```

### ABC-Based Hardware Abstraction
- All sensors → `SensorDriver` ABC
- All actuators → `ActuatorDriver` ABC
- Factory in `app.py` selects mock vs real based on config
- Business logic (services/) depends on ABCs, never concrete drivers

### Protocol-Agnostic
- MQTT, Serial, BLE, HTTP, WS are independent modules
- Each protocol client has `connect()`, `disconnect()`, `send()`/`publish()`
- Services consume protocol interfaces, not implementations

---

## Error Handling

### Graceful Degradation for Hardware
```python
# Sensor failure → log + continue, don't crash the whole system
try:
    reading = await sensor.read()
except SensorError as e:
    logger.warning("sensor_read_failed", sensor=sensor.name, error=str(e))
    # Continue with other sensors
```

### Signal Handling
- `SIGINT` / `SIGTERM` → graceful shutdown
- Teardown all drivers → close protocols → flush storage
- Application.run() handles the full lifecycle

### Pydantic Settings — Fail Fast
```python
# Config validated at startup via Pydantic Settings
# Missing required env vars → immediate, clear error
from myapp.config import Settings
settings = Settings()  # Validates all env vars
```

---

## Code Quality

### Naming Conventions
| Artifact | Convention | Example |
|----------|-----------|---------|
| Driver | `snake_case.py` | `gpio_driver.py` |
| Protocol | `snake_case_client.py` | `mqtt_client.py` |
| ABC | PascalCase | `SensorDriver` |
| Config | PascalCase | `Settings` |
| Type hint | Always `from __future__ import annotations` | — |

### Python Standards
- `from __future__ import annotations` — every file
- UV for dependencies: `uv sync`, `uv run`
- structlog for all logging — never `print()` or `logging.basicConfig()`
- Ruff for linting + formatting
- mypy strict mode — no `Any`, no untyped defs

---

## Testing Strategy

| Level | What | Where | Tool |
|-------|------|-------|------|
| Unit | Drivers (mock), utilities | `tests/` | pytest |
| Async | Services, protocols | `tests/` | pytest-asyncio |
| Integration | Collector + mock drivers | `tests/` | pytest |

### Mock Drivers in Tests
```python
# conftest.py provides fixtures with mock drivers
# No hardware needed — MOCK_MODE=true
@pytest.fixture
def mock_sensor():
    return MockTemperatureSensor()

async def test_sensor_read(mock_sensor):
    reading = await mock_sensor.read()
    assert reading.unit == "°C"
```

---

## Security & Performance

### Security
- Pydantic validates all env config — no raw `os.getenv()`
- MQTT with TLS enabled in production
- Never hardcode credentials — always env vars
- Secrets via `.env` (gitignored)

### Performance
- asyncio event loop — non-blocking I/O
- `asyncio.to_thread()` for blocking hardware calls
- SQLite WAL mode for concurrent reads
- Batch sensor readings before network publish

---

## Commands

| Action | Command |
|--------|---------|
| Install | `uv sync` |
| Run | `uv run python -m myapp` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check src/` |
| Format | `uv run ruff format src/` |
| Type check | `uv run mypy src/` |

---

## Deployment

| Target | Method |
|--------|--------|
| Systemd | `deploy/myapp.service` |
| Docker | `Dockerfile` + `docker-compose.yml` (with Mosquitto) |
| OTA | `deploy/ota/update.sh` (git pull + uv sync + restart) |
| Grafana | `deploy/grafana/dashboard.json` |

---

## Prohibitions — NEVER Do These

1. **NEVER** block the asyncio event loop — use `asyncio.to_thread()` for I/O
2. **NEVER** use `print()` — structlog always
3. **NEVER** use `os.getenv()` directly — Pydantic Settings
4. **NEVER** import concrete drivers in services — depend on ABCs
5. **NEVER** hardcode sensor pins/addresses — config via env
6. **NEVER** skip `from __future__ import annotations`
7. **NEVER** use pip directly — UV only (`uv sync`, `uv run`)
8. **NEVER** skip mock driver when adding a new sensor
9. **NEVER** crash on single sensor failure — log and continue
10. **NEVER** use `Any` type — mypy strict mode
