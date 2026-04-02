"""Watchdog service — health monitoring and auto-restart."""

from __future__ import annotations

import asyncio
import time

import structlog

logger = structlog.get_logger(__name__)


class WatchdogService:
    """Monitors application health and tracks uptime."""

    def __init__(
        self,
        check_interval: float = 30.0,
        max_failures: int = 3,
    ) -> None:
        self._check_interval = check_interval
        self._max_failures = max_failures
        self._start_time: float = 0.0
        self._last_heartbeat: float = 0.0
        self._failure_count: int = 0
        self._running = False

    async def start(self) -> None:
        """Start the watchdog monitoring loop."""
        self._running = True
        self._start_time = time.monotonic()
        self._last_heartbeat = time.monotonic()
        logger.info("watchdog_started", interval=self._check_interval)
        while self._running:
            await asyncio.sleep(self._check_interval)
            self._check_health()

    def heartbeat(self) -> None:
        """Record a heartbeat from the main application."""
        self._last_heartbeat = time.monotonic()
        self._failure_count = 0

    def _check_health(self) -> None:
        elapsed = time.monotonic() - self._last_heartbeat
        if elapsed > self._check_interval * 2:
            self._failure_count += 1
            logger.warning(
                "watchdog_missed_heartbeat",
                elapsed=round(elapsed, 1),
                failures=self._failure_count,
            )
            if self._failure_count >= self._max_failures:
                logger.critical(
                    "watchdog_max_failures",
                    failures=self._failure_count,
                )
        else:
            logger.debug("watchdog_healthy", uptime=round(self.uptime, 1))

    async def stop(self) -> None:
        """Stop the watchdog."""
        self._running = False
        logger.info("watchdog_stopped", uptime=round(self.uptime, 1))

    @property
    def uptime(self) -> float:
        """Seconds since watchdog started."""
        if self._start_time == 0.0:
            return 0.0
        return time.monotonic() - self._start_time

    @property
    def is_healthy(self) -> bool:
        return self._failure_count < self._max_failures
