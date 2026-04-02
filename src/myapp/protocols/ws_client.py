"""WebSocket client for realtime sensor data streaming."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import structlog
import websockets

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from websockets.asyncio.client import ClientConnection

    from myapp.drivers.base import SensorReading

logger = structlog.get_logger(__name__)


class WsClient:
    """Async WebSocket client for streaming sensor data."""

    def __init__(self, url: str = "ws://localhost:8765") -> None:
        self._url = url
        self._ws: ClientConnection | None = None

    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        self._ws = await websockets.connect(self._url)
        logger.info("ws_connected", url=self._url)

    async def send(self, reading: SensorReading) -> None:
        """Send a sensor reading as JSON."""
        if self._ws is None:
            msg = "WebSocket not connected — call connect() first"
            raise RuntimeError(msg)
        payload = json.dumps(reading.to_dict())
        await self._ws.send(payload)
        logger.debug("ws_sent", sensor=reading.name)

    async def receive_stream(self) -> AsyncIterator[str]:
        """Receive messages as an async iterator."""
        if self._ws is None:
            msg = "WebSocket not connected — call connect() first"
            raise RuntimeError(msg)
        async for message in self._ws:
            if isinstance(message, bytes):
                yield message.decode("utf-8")
            else:
                yield message

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
            logger.info("ws_disconnected")

    @property
    def is_connected(self) -> bool:
        return self._ws is not None
