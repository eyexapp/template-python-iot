"""HTTP client for pushing sensor data to a cloud API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import structlog

if TYPE_CHECKING:
    from myapp.drivers.base import SensorReading

logger = structlog.get_logger(__name__)


class HttpClient:
    """Async HTTP client for cloud API communication."""

    def __init__(self, endpoint: str = "http://localhost:8080/api/readings") -> None:
        self._endpoint = endpoint
        self._client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Initialize the HTTP client session."""
        self._client = httpx.AsyncClient(timeout=10.0)
        logger.info("http_client_ready", endpoint=self._endpoint)

    async def post_reading(self, reading: SensorReading) -> int:
        """Post a sensor reading to the API. Returns HTTP status code."""
        if self._client is None:
            msg = "HTTP client not initialized — call connect() first"
            raise RuntimeError(msg)
        response = await self._client.post(
            self._endpoint,
            json=reading.to_dict(),
        )
        logger.debug(
            "http_posted",
            status=response.status_code,
            sensor=reading.name,
        )
        return response.status_code

    async def disconnect(self) -> None:
        """Close the HTTP client session."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("http_client_closed")
