---
name: architecture
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
  - architecture
  - iot
  - hardware
  - sensor
  - driver
  - mqtt
  - protocol
---

# Architecture — Python IoT (Async + Hardware Abstraction)

## Async-First Design

All I/O is async — sensors, network, serial, BLE:

```python
import asyncio

async def main():
    sensor = await SensorDriver.connect("/dev/ttyUSB0")
    mqtt_client = await MQTTClient.connect("mqtt://broker:1883")

    async for reading in sensor.stream():
        await mqtt_client.publish("sensors/temp", reading.to_json())
```

## Hardware Abstraction Layer

```
src/
├── main.py              ← Entry point (asyncio.run)
├── config.py            ← pydantic-settings (device config)
├── drivers/             ← Hardware abstraction (one per device/protocol)
│   ├── base.py          ← Abstract driver interface
│   ├── serial_sensor.py ← Serial (pyserial-asyncio)
│   ├── ble_sensor.py    ← BLE (bleak)
│   ├── gpio_driver.py   ← GPIO (gpiozero / lgpio)
│   └── mock_sensor.py   ← Mock driver for testing/dev
├── protocols/           ← Communication protocols
│   ├── mqtt_client.py   ← MQTT pub/sub (aiomqtt)
│   ├── serial_proto.py  ← Serial framing/parsing
│   └── ble_proto.py     ← BLE GATT profiles
├── services/            ← Business logic
│   ├── data_processor.py ← Filtering, aggregation
│   └── alert_service.py  ← Threshold alerts
├── models/              ← Data models (Pydantic)
│   └── reading.py       ← SensorReading, DeviceStatus
└── utils/               ← Helpers
```

## Driver Interface Pattern

```python
# drivers/base.py
from abc import ABC, abstractmethod

class SensorDriver(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def read(self) -> SensorReading: ...

    @abstractmethod
    async def stream(self) -> AsyncIterator[SensorReading]: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

# drivers/mock_sensor.py
class MockSensorDriver(SensorDriver):
    """For testing without hardware."""
    async def read(self) -> SensorReading:
        return SensorReading(temperature=22.5, humidity=45.0)
```

## Mock Mode

- Every driver has a mock counterpart.
- `MOCK_MODE=true` env var switches to mock drivers.
- Factory function selects driver based on config:

```python
def get_sensor(config: SensorConfig) -> SensorDriver:
    if config.mock_mode:
        return MockSensorDriver()
    match config.protocol:
        case "serial": return SerialSensorDriver(config.port, config.baud)
        case "ble": return BLESensorDriver(config.mac_address)
```

## Protocol Handling

- **MQTT**: `aiomqtt` — async pub/sub for telemetry.
- **Serial**: `pyserial-asyncio` — async serial communication.
- **BLE**: `bleak` — cross-platform Bluetooth LE.
- Frame parsing separate from driver — testable independently.

## Rules

- All I/O operations must be async.
- Every hardware driver has a mock implementation.
- Protocol parsing is separate from transport.
- Use `asyncio.TaskGroup` for concurrent sensor management.
