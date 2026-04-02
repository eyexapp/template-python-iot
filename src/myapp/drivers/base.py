"""Abstract base classes for hardware drivers."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class SensorReading:
    """Standardized sensor data format across all drivers."""

    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, object]:
        """Serialize to a plain dict for JSON/MQTT/HTTP payloads."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
        }


class SensorDriver(abc.ABC):
    """Abstract base for all sensor drivers.

    Subclass this and implement ``read`` to create a new sensor driver.
    """

    @abc.abstractmethod
    async def read(self) -> SensorReading:
        """Take a single reading from the sensor."""

    @abc.abstractmethod
    async def setup(self) -> None:
        """Initialize hardware resources."""

    @abc.abstractmethod
    async def teardown(self) -> None:
        """Release hardware resources."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable sensor name."""


class ActuatorDriver(abc.ABC):
    """Abstract base for all actuator drivers.

    Subclass this and implement ``write`` to create a new actuator driver.
    """

    @abc.abstractmethod
    async def write(self, value: float) -> None:
        """Send a value/command to the actuator."""

    @abc.abstractmethod
    async def setup(self) -> None:
        """Initialize hardware resources."""

    @abc.abstractmethod
    async def teardown(self) -> None:
        """Release hardware resources."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable actuator name."""
