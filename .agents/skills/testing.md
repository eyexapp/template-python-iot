---
name: testing
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
  - test
  - pytest
  - mock driver
  - hardware test
---

# Testing — Python IoT (pytest + asyncio)

## Async Testing

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```python
async def test_sensor_reading():
    driver = MockSensorDriver()
    await driver.connect()
    reading = await driver.read()
    assert 0 <= reading.temperature <= 85
    assert 0 <= reading.humidity <= 100
```

## Mock Driver Tests

```python
async def test_data_processor_filters_outliers():
    mock = MockSensorDriver(readings=[
        SensorReading(device_id="s1", temperature=22.0, humidity=45.0),
        SensorReading(device_id="s1", temperature=999.0, humidity=45.0),  # outlier
        SensorReading(device_id="s1", temperature=23.0, humidity=46.0),
    ])
    processor = DataProcessor(driver=mock)
    results = await processor.collect(count=3)
    assert len(results) == 2  # outlier filtered
```

## Protocol Testing

```python
async def test_mqtt_publish(mocker):
    mock_mqtt = mocker.AsyncMock()
    client = MQTTClient(connection=mock_mqtt)
    reading = SensorReading(device_id="s1", temperature=22.0, humidity=45.0)
    await client.publish("sensors/temp", reading)
    mock_mqtt.publish.assert_called_once()

def test_serial_frame_parsing():
    raw = b"\x02\x00\x16\x00\x2d\x03"  # STX, temp=22, hum=45, ETX
    reading = SerialProtocol.parse_frame(raw)
    assert reading.temperature == 22.0
    assert reading.humidity == 45.0
```

## Integration Testing (Optional Hardware)

```python
@pytest.mark.hardware  # Skip in CI
async def test_real_sensor():
    driver = SerialSensorDriver("/dev/ttyUSB0", baud=9600)
    await driver.connect()
    reading = await driver.read()
    assert reading.temperature is not None
```

## Rules

- All tests use mock drivers by default.
- `@pytest.mark.hardware` for tests requiring real devices.
- Test protocol parsing as pure functions (no I/O).
- Test reconnection logic with simulated failures.
