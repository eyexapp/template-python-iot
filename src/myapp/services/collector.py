"""Sensor data collector — poll loop that reads, stores, and dispatches."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Protocol

import structlog

if TYPE_CHECKING:
    from myapp.drivers.base import SensorDriver, SensorReading
    from myapp.storage.sqlite import SensorDataStore

logger = structlog.get_logger(__name__)


class ReadingDispatcher(Protocol):
    """Protocol for anything that can publish a sensor reading."""

    async def publish(self, reading: SensorReading) -> None: ...


class CollectorService:
    """Periodically reads sensors, stores to SQLite, dispatches to protocols."""

    def __init__(
        self,
        sensors: list[SensorDriver],
        store: SensorDataStore,
        dispatchers: list[ReadingDispatcher] | None = None,
        poll_interval: float = 5.0,
    ) -> None:
        self._sensors = sensors
        self._store = store
        self._dispatchers = dispatchers or []
        self._poll_interval = poll_interval
        self._running = False

    async def start(self) -> None:
        """Start the polling loop."""
        self._running = True
        logger.info(
            "collector_started",
            sensors=len(self._sensors),
            interval=self._poll_interval,
        )
        while self._running:
            await self._poll_once()
            await asyncio.sleep(self._poll_interval)

    async def _poll_once(self) -> None:
        """Read all sensors, store, and dispatch."""
        for sensor in self._sensors:
            try:
                reading = await sensor.read()
                await self._store.insert(reading)
                for dispatcher in self._dispatchers:
                    try:
                        await dispatcher.publish(reading)
                    except Exception:
                        logger.exception(
                            "dispatch_error",
                            sensor=sensor.name,
                        )
            except Exception:
                logger.exception("sensor_read_error", sensor=sensor.name)

    async def stop(self) -> None:
        """Stop the polling loop."""
        self._running = False
        logger.info("collector_stopped")

    @property
    def is_running(self) -> bool:
        return self._running
