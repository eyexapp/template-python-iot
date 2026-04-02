"""Tests for SQLite sensor data storage."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from myapp.drivers.base import SensorReading

if TYPE_CHECKING:
    from myapp.storage.sqlite import SensorDataStore


class TestSensorDataStore:
    async def test_insert_and_query(self, tmp_store: SensorDataStore) -> None:
        now = datetime.now(UTC)
        reading = SensorReading(name="temp", value=22.5, unit="°C", timestamp=now)
        await tmp_store.insert(reading)
        results = await tmp_store.query_range(start=now - timedelta(seconds=1))
        assert len(results) == 1
        assert results[0].name == "temp"
        assert results[0].value == 22.5

    async def test_query_by_name(self, tmp_store: SensorDataStore) -> None:
        now = datetime.now(UTC)
        await tmp_store.insert(
            SensorReading(name="temp", value=22.0, unit="°C", timestamp=now)
        )
        await tmp_store.insert(
            SensorReading(name="hum", value=55.0, unit="%", timestamp=now)
        )
        results = await tmp_store.query_range(
            start=now - timedelta(seconds=1), name="temp"
        )
        assert len(results) == 1
        assert results[0].name == "temp"

    async def test_cleanup_old(self, tmp_store: SensorDataStore) -> None:
        old = datetime.now(UTC) - timedelta(days=30)
        new = datetime.now(UTC)
        await tmp_store.insert(
            SensorReading(name="old", value=1.0, unit="x", timestamp=old)
        )
        await tmp_store.insert(
            SensorReading(name="new", value=2.0, unit="x", timestamp=new)
        )
        deleted = await tmp_store.cleanup_old(
            before=datetime.now(UTC) - timedelta(days=1)
        )
        assert deleted == 1
        remaining = await tmp_store.query_range(start=old - timedelta(seconds=1))
        assert len(remaining) == 1
        assert remaining[0].name == "new"
