"""SQLite storage for sensor readings."""

from __future__ import annotations

import asyncio
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import structlog

from myapp.drivers.base import SensorReading

logger = structlog.get_logger(__name__)


class SensorDataStore:
    """Persist sensor readings to a local SQLite database."""

    def __init__(self, db_path: str = "data/sensors.db") -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    async def setup(self) -> None:
        """Create the database directory and table."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._setup_sync)

    def _setup_sync(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings(timestamp)"
        )
        self._conn.commit()
        logger.info("sqlite_ready", path=self._db_path)

    async def insert(self, reading: SensorReading) -> None:
        """Insert a sensor reading."""
        if self._conn is None:
            msg = "Database not initialized — call setup() first"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._insert_sync, reading)

    def _insert_sync(self, reading: SensorReading) -> None:
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO readings (name, value, unit, timestamp) VALUES (?, ?, ?, ?)",
            (reading.name, reading.value, reading.unit, reading.timestamp.isoformat()),
        )
        self._conn.commit()

    async def query_range(
        self,
        start: datetime,
        end: datetime | None = None,
        name: str | None = None,
    ) -> list[SensorReading]:
        """Query readings within a time range."""
        if self._conn is None:
            msg = "Database not initialized — call setup() first"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._query_range_sync, start, end, name
        )

    def _query_range_sync(
        self,
        start: datetime,
        end: datetime | None,
        name: str | None,
    ) -> list[SensorReading]:
        assert self._conn is not None
        query = "SELECT name, value, unit, timestamp FROM readings WHERE timestamp >= ?"
        params: list[str] = [start.isoformat()]
        if end is not None:
            query += " AND timestamp <= ?"
            params.append(end.isoformat())
        if name is not None:
            query += " AND name = ?"
            params.append(name)
        query += " ORDER BY timestamp ASC"
        rows = self._conn.execute(query, params).fetchall()
        return [
            SensorReading(
                name=row[0],
                value=row[1],
                unit=row[2],
                timestamp=datetime.fromisoformat(row[3]).replace(tzinfo=UTC),
            )
            for row in rows
        ]

    async def cleanup_old(self, before: datetime) -> int:
        """Delete readings older than the given datetime. Returns count."""
        if self._conn is None:
            msg = "Database not initialized — call setup() first"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._cleanup_sync, before)

    def _cleanup_sync(self, before: datetime) -> int:
        assert self._conn is not None
        cursor = self._conn.execute(
            "DELETE FROM readings WHERE timestamp < ?",
            (before.isoformat(),),
        )
        self._conn.commit()
        count = cursor.rowcount
        logger.info("sqlite_cleanup", deleted=count)
        return count

    async def teardown(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("sqlite_closed")
