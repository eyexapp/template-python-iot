"""Mock drivers for desktop development without real hardware."""

from __future__ import annotations

import random

import structlog

from myapp.drivers.base import ActuatorDriver, SensorReading

from .base import SensorDriver

logger = structlog.get_logger(__name__)


class MockTemperatureSensor(SensorDriver):
    """Generates random temperature readings (18-30 °C)."""

    @property
    def name(self) -> str:
        return "mock_temperature"

    async def setup(self) -> None:
        logger.info("mock_sensor_setup", sensor=self.name)

    async def teardown(self) -> None:
        logger.info("mock_sensor_teardown", sensor=self.name)

    async def read(self) -> SensorReading:
        value = round(random.uniform(18.0, 30.0), 2)
        reading = SensorReading(name=self.name, value=value, unit="°C")
        logger.debug("mock_sensor_read", reading=reading.to_dict())
        return reading


class MockHumiditySensor(SensorDriver):
    """Generates random humidity readings (30-80 %)."""

    @property
    def name(self) -> str:
        return "mock_humidity"

    async def setup(self) -> None:
        logger.info("mock_sensor_setup", sensor=self.name)

    async def teardown(self) -> None:
        logger.info("mock_sensor_teardown", sensor=self.name)

    async def read(self) -> SensorReading:
        value = round(random.uniform(30.0, 80.0), 2)
        reading = SensorReading(name=self.name, value=value, unit="%")
        logger.debug("mock_sensor_read", reading=reading.to_dict())
        return reading


class MockLED(ActuatorDriver):
    """Simulates an LED on/off (value > 0 = on)."""

    def __init__(self) -> None:
        self._state: float = 0.0

    @property
    def name(self) -> str:
        return "mock_led"

    async def setup(self) -> None:
        logger.info("mock_actuator_setup", actuator=self.name)

    async def teardown(self) -> None:
        self._state = 0.0
        logger.info("mock_actuator_teardown", actuator=self.name)

    async def write(self, value: float) -> None:
        self._state = value
        state_str = "ON" if value > 0 else "OFF"
        logger.debug("mock_actuator_write", actuator=self.name, state=state_str)

    @property
    def state(self) -> float:
        """Current LED state (for testing)."""
        return self._state
