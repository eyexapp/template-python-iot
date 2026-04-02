"""GPIO drivers using gpiozero (Raspberry Pi only).

Requires the ``rpi`` optional dependency group::

    uv sync --extra rpi

On non-RPi systems, importing this module raises ``RuntimeError``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from myapp.drivers.base import ActuatorDriver, SensorDriver, SensorReading

if TYPE_CHECKING:
    from gpiozero import LED as GpiozeroLED  # noqa: N811

logger = structlog.get_logger(__name__)

try:
    from gpiozero import LED as _LED

    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False
    _LED = None


def _require_gpio() -> None:
    if not _GPIO_AVAILABLE:
        msg = "gpiozero is not installed. Install RPi dependencies: uv sync --extra rpi"
        raise RuntimeError(msg)


class GpioTemperatureSensor(SensorDriver):
    """Read temperature from a GPIO-connected sensor.

    This is a placeholder — replace with your actual sensor logic
    (e.g., DHT22 via adafruit-circuitpython-dht).
    """

    def __init__(self, pin: int = 4) -> None:
        _require_gpio()
        self._pin = pin

    @property
    def name(self) -> str:
        return f"gpio_temp_pin{self._pin}"

    async def setup(self) -> None:
        logger.info("gpio_sensor_setup", sensor=self.name, pin=self._pin)

    async def teardown(self) -> None:
        logger.info("gpio_sensor_teardown", sensor=self.name)

    async def read(self) -> SensorReading:
        # TODO: Replace with actual sensor reading logic
        msg = "Implement actual GPIO temperature reading"
        raise NotImplementedError(msg)


class GpioLED(ActuatorDriver):
    """Control an LED via GPIO pin using gpiozero."""

    def __init__(self, pin: int = 17) -> None:
        _require_gpio()
        self._pin = pin
        self._led: GpiozeroLED | None = None

    @property
    def name(self) -> str:
        return f"gpio_led_pin{self._pin}"

    async def setup(self) -> None:
        self._led = _LED(self._pin)
        logger.info("gpio_led_setup", actuator=self.name, pin=self._pin)

    async def teardown(self) -> None:
        if self._led is not None:
            self._led.close()
            self._led = None
        logger.info("gpio_led_teardown", actuator=self.name)

    async def write(self, value: float) -> None:
        if self._led is None:
            msg = "LED not initialized — call setup() first"
            raise RuntimeError(msg)
        if value > 0:
            self._led.on()
        else:
            self._led.off()
        logger.debug("gpio_led_write", actuator=self.name, value=value)
