---
name: security-performance
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
  - security
  - performance
  - memory
  - power
  - tls
  - resource
---

# Security & Performance — Python IoT

## Performance

### Memory Efficiency

- Use generators for sensor streams — don't buffer all readings.
- `__slots__` on data classes for reduced memory per instance.
- Circular buffers for rolling averages — fixed memory.
- Profile with `tracemalloc` on target device.

### Async Concurrency

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(sensor_loop(sensor1))
    tg.create_task(sensor_loop(sensor2))
    tg.create_task(mqtt_publisher(queue))
```

- One task per sensor, one for MQTT publishing.
- Message queue (`asyncio.Queue`) between producers and publisher.
- Backpressure: bounded queue prevents memory overflow.

### Power/Resource Constraints

- Sleep between readings: `await asyncio.sleep(interval)`.
- Batch MQTT publishes — reduce network round-trips.
- Adjust polling frequency based on battery level.

## Security

### Communication Security

- MQTT over TLS: `MQTTClient(tls=True, ca_cert="/path/to/ca.pem")`.
- Client certificates for device authentication.
- Never transmit credentials in MQTT topic or payload.

### Device Security

- Rotate API keys/tokens periodically.
- Read-only filesystem except for data directory.
- No SSH password auth — keys only.
- `SecretStr` from Pydantic for sensitive config values.

### Input Validation

- Validate sensor data ranges (temperature -40 to 85, etc.).
- Reject physically impossible readings.
- Rate-limit incoming MQTT commands.

### Firmware/Update Security

- Signed updates — verify before applying.
- Rollback mechanism if update fails.
- `hashlib` for integrity checks on downloaded binaries.
