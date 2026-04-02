"""MQTT client wrapper using paho-mqtt."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

import paho.mqtt.client as mqtt
import structlog

if TYPE_CHECKING:
    from myapp.drivers.base import SensorReading

logger = structlog.get_logger(__name__)


class MqttClient:
    """Async-friendly MQTT client for publishing sensor readings."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        topic_prefix: str = "myapp/sensors",
    ) -> None:
        self._broker = broker
        self._port = port
        self._topic_prefix = topic_prefix
        self._client: mqtt.Client | None = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to the MQTT broker."""
        loop = asyncio.get_running_loop()
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,  # type: ignore[attr-defined]
            client_id="myapp",
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        await loop.run_in_executor(None, self._client.connect, self._broker, self._port)
        self._client.loop_start()
        logger.info("mqtt_connected", broker=self._broker, port=self._port)

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        rc: Any,
        properties: Any = None,
    ) -> None:
        self._connected = True
        logger.info("mqtt_on_connect", rc=rc)

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        rc: Any,
        properties: Any = None,
    ) -> None:
        self._connected = False
        logger.warning("mqtt_on_disconnect", rc=rc)

    async def publish(self, reading: SensorReading) -> None:
        """Publish a sensor reading to MQTT."""
        if self._client is None:
            msg = "MQTT client not connected — call connect() first"
            raise RuntimeError(msg)
        topic = f"{self._topic_prefix}/{reading.name}"
        payload = json.dumps(reading.to_dict())
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._client.publish, topic, payload)
        logger.debug("mqtt_published", topic=topic)

    async def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
            self._connected = False
            logger.info("mqtt_disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected
