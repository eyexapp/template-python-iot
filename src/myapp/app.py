"""Application orchestrator — wires config, drivers, protocols, and services."""

from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING

import structlog

from myapp.config import settings
from myapp.drivers.mock_driver import (
    MockHumiditySensor,
    MockLED,
    MockTemperatureSensor,
)
from myapp.protocols.mqtt_client import MqttClient
from myapp.services.collector import CollectorService
from myapp.services.watchdog import WatchdogService
from myapp.storage.sqlite import SensorDataStore
from myapp.utils.logger import setup_logging

if TYPE_CHECKING:
    from myapp.drivers.base import SensorDriver

logger = structlog.get_logger(__name__)


class Application:
    """Main application — assembles and runs all components."""

    def __init__(self) -> None:
        self._store = SensorDataStore(db_path=settings.db_path)
        self._mqtt = MqttClient(
            broker=settings.mqtt_broker,
            port=settings.mqtt_port,
            topic_prefix=settings.mqtt_topic_prefix,
        )
        self._watchdog = WatchdogService()
        self._sensors: list[SensorDriver] = []
        self._led = MockLED()
        self._collector: CollectorService | None = None
        self._tasks: list[asyncio.Task[None]] = []

    def _create_sensors(self) -> list[SensorDriver]:
        """Create sensor drivers based on config."""
        if settings.mock_mode:
            logger.info("using_mock_drivers")
            return [MockTemperatureSensor(), MockHumiditySensor()]
        # Non-mock: import real drivers here
        logger.info("using_real_drivers")
        return [MockTemperatureSensor(), MockHumiditySensor()]

    async def setup(self) -> None:
        """Initialize all components."""
        setup_logging(
            log_level=settings.log_level,
            environment=settings.app_env,
        )
        logger.info(
            "app_starting",
            app=settings.app_name,
            env=settings.app_env,
            mock=settings.mock_mode,
        )

        await self._store.setup()

        self._sensors = self._create_sensors()
        for sensor in self._sensors:
            await sensor.setup()
        await self._led.setup()

        try:
            await self._mqtt.connect()
        except Exception:
            logger.warning("mqtt_connect_failed — running without MQTT")

        self._collector = CollectorService(
            sensors=self._sensors,
            store=self._store,
            dispatchers=[self._mqtt] if self._mqtt.is_connected else [],
            poll_interval=settings.poll_interval_seconds,
        )

    async def run(self) -> None:
        """Run the application event loop."""
        await self.setup()

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        def _signal_handler() -> None:
            logger.info("shutdown_signal_received")
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _signal_handler)

        assert self._collector is not None
        self._tasks = [
            asyncio.create_task(self._collector.start()),
            asyncio.create_task(self._watchdog.start()),
            asyncio.create_task(self._heartbeat_loop(stop_event)),
        ]

        logger.info("app_running", poll=settings.poll_interval_seconds)
        await stop_event.wait()
        await self.shutdown()

    async def _heartbeat_loop(self, stop_event: asyncio.Event) -> None:
        """Send periodic heartbeats to the watchdog."""
        while not stop_event.is_set():
            self._watchdog.heartbeat()
            await asyncio.sleep(10.0)

    async def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        logger.info("app_shutting_down")

        if self._collector is not None:
            await self._collector.stop()
        await self._watchdog.stop()

        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

        for sensor in self._sensors:
            await sensor.teardown()
        await self._led.teardown()

        await self._mqtt.disconnect()
        await self._store.teardown()

        logger.info("app_shutdown_complete")
