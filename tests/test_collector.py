"""Tests for the collector service."""

from __future__ import annotations

import asyncio
import contextlib
from datetime import UTC
from typing import TYPE_CHECKING

from myapp.drivers.mock_driver import MockTemperatureSensor
from myapp.services.collector import CollectorService

if TYPE_CHECKING:
    from myapp.drivers.base import SensorReading
    from myapp.storage.sqlite import SensorDataStore


class _FakeDispatcher:
    """Captures dispatched readings for testing."""

    def __init__(self) -> None:
        self.readings: list[SensorReading] = []

    async def publish(self, reading: SensorReading) -> None:
        self.readings.append(reading)


class TestCollectorService:
    async def test_single_poll(self, tmp_store: SensorDataStore) -> None:
        sensor = MockTemperatureSensor()
        await sensor.setup()
        dispatcher = _FakeDispatcher()
        collector = CollectorService(
            sensors=[sensor],
            store=tmp_store,
            dispatchers=[dispatcher],
            poll_interval=0.1,
        )
        # Run one poll manually
        await collector._poll_once()

        # Check storage
        from datetime import datetime, timedelta

        results = await tmp_store.query_range(
            start=datetime.now(UTC) - timedelta(seconds=5)
        )
        assert len(results) == 1

        # Check dispatch
        assert len(dispatcher.readings) == 1
        assert dispatcher.readings[0].unit == "°C"

        await sensor.teardown()

    async def test_start_stop(self, tmp_store: SensorDataStore) -> None:
        sensor = MockTemperatureSensor()
        await sensor.setup()
        collector = CollectorService(
            sensors=[sensor],
            store=tmp_store,
            poll_interval=0.05,
        )
        task = asyncio.create_task(collector.start())
        await asyncio.sleep(0.15)
        await collector.stop()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

        assert not collector.is_running
        await sensor.teardown()
