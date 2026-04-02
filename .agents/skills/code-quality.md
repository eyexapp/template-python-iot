---
name: code-quality
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
  - clean code
  - naming
  - lint
  - type hint
  - error handling
---

# Code Quality — Python IoT

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Driver | PascalCase + Driver | `SerialSensorDriver` |
| Protocol | PascalCase + Client/Proto | `MQTTClient` |
| Service | PascalCase + Service | `DataProcessor` |
| Model | PascalCase | `SensorReading` |
| Config | PascalCase + Config | `SensorConfig` |
| Mock | Mock + original name | `MockSensorDriver` |

## Data Models — Pydantic

```python
from pydantic import BaseModel, Field
from datetime import datetime

class SensorReading(BaseModel):
    device_id: str
    temperature: float = Field(ge=-40, le=85)
    humidity: float = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_mqtt_payload(self) -> bytes:
        return self.model_dump_json().encode()
```

## Error Handling

```python
# Hardware-specific errors
class DriverError(Exception): ...
class ConnectionLostError(DriverError): ...
class ReadTimeoutError(DriverError): ...

# Reconnection with backoff
async def resilient_read(driver: SensorDriver, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(driver.read(), timeout=5.0)
        except (ReadTimeoutError, ConnectionLostError):
            await asyncio.sleep(2 ** attempt)
            await driver.connect()
    raise MaxRetriesExceededError()
```

## Async Best Practices

- Use `asyncio.TaskGroup` (Python 3.11+) for structured concurrency.
- `asyncio.wait_for(coro, timeout=N)` — always timeout hardware ops.
- Never mix sync I/O in async code — blocks entire event loop.
- `async for` for streaming sensor data.

## Logging — structlog

```python
log = structlog.get_logger()
log.info("sensor_reading", device_id="sensor-01", temp=22.5, humidity=45.0)
log.warning("connection_retry", device_id="sensor-01", attempt=3)
```
