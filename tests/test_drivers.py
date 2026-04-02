"""Tests for hardware drivers (mock mode)."""

from __future__ import annotations

import pytest

from myapp.drivers.base import ActuatorDriver, SensorDriver, SensorReading
from myapp.drivers.mock_driver import (
    MockHumiditySensor,
    MockLED,
    MockTemperatureSensor,
)


class TestSensorReading:
    def test_to_dict(self) -> None:
        r = SensorReading(name="test", value=25.5, unit="°C")
        d = r.to_dict()
        assert d["name"] == "test"
        assert d["value"] == 25.5
        assert d["unit"] == "°C"
        assert "timestamp" in d

    def test_frozen(self) -> None:
        r = SensorReading(name="test", value=1.0, unit="x")
        with pytest.raises(AttributeError):
            r.name = "changed"  # type: ignore[misc]


class TestMockTemperatureSensor:
    async def test_implements_abc(self) -> None:
        sensor = MockTemperatureSensor()
        assert isinstance(sensor, SensorDriver)

    async def test_name(self) -> None:
        sensor = MockTemperatureSensor()
        assert sensor.name == "mock_temperature"

    async def test_read_returns_reading(self) -> None:
        sensor = MockTemperatureSensor()
        await sensor.setup()
        reading = await sensor.read()
        assert isinstance(reading, SensorReading)
        assert reading.unit == "°C"
        assert 18.0 <= reading.value <= 30.0
        await sensor.teardown()


class TestMockHumiditySensor:
    async def test_read_returns_reading(self) -> None:
        sensor = MockHumiditySensor()
        await sensor.setup()
        reading = await sensor.read()
        assert reading.unit == "%"
        assert 30.0 <= reading.value <= 80.0
        await sensor.teardown()


class TestMockLED:
    async def test_implements_abc(self) -> None:
        led = MockLED()
        assert isinstance(led, ActuatorDriver)

    async def test_write_on_off(self) -> None:
        led = MockLED()
        await led.setup()
        await led.write(1.0)
        assert led.state == 1.0
        await led.write(0.0)
        assert led.state == 0.0
        await led.teardown()
        assert led.state == 0.0
