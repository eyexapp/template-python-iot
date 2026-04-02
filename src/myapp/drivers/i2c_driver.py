"""I2C drivers using smbus2 (Raspberry Pi only).

Requires the ``rpi`` optional dependency group::

    uv sync --extra rpi

On non-RPi systems, importing this module raises ``RuntimeError``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from myapp.drivers.base import SensorDriver, SensorReading

if TYPE_CHECKING:
    from smbus2 import SMBus

logger = structlog.get_logger(__name__)

try:
    from smbus2 import SMBus as _SMBus

    _I2C_AVAILABLE = True
except ImportError:
    _I2C_AVAILABLE = False
    _SMBus = None


def _require_i2c() -> None:
    if not _I2C_AVAILABLE:
        msg = "smbus2 is not installed. Install RPi dependencies: uv sync --extra rpi"
        raise RuntimeError(msg)


class I2CTemperatureSensor(SensorDriver):
    """Read temperature from an I2C sensor (e.g., BMP280, SHT31).

    This is a placeholder — replace ``_read_raw`` with your sensor's
    register addresses and conversion logic.
    """

    def __init__(
        self,
        bus_number: int = 1,
        address: int = 0x76,
    ) -> None:
        _require_i2c()
        self._bus_number = bus_number
        self._address = address
        self._bus: SMBus | None = None

    @property
    def name(self) -> str:
        return f"i2c_temp_0x{self._address:02x}"

    async def setup(self) -> None:
        self._bus = _SMBus(self._bus_number)
        logger.info(
            "i2c_sensor_setup",
            sensor=self.name,
            bus=self._bus_number,
            address=hex(self._address),
        )

    async def teardown(self) -> None:
        if self._bus is not None:
            self._bus.close()
            self._bus = None
        logger.info("i2c_sensor_teardown", sensor=self.name)

    async def read(self) -> SensorReading:
        if self._bus is None:
            msg = "I2C bus not initialized — call setup() first"
            raise RuntimeError(msg)
        # TODO: Replace with actual I2C register read + conversion
        msg = "Implement actual I2C temperature reading"
        raise NotImplementedError(msg)
