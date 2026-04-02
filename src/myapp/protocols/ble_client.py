"""Bluetooth Low Energy (BLE) client using bleak."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from bleak import BleakClient, BleakScanner

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice

logger = structlog.get_logger(__name__)


class BleClient:
    """Async BLE client for scanning and reading characteristics."""

    def __init__(self) -> None:
        self._client: BleakClient | None = None
        self._device: BLEDevice | None = None

    async def scan(self, timeout: float = 5.0) -> list[BLEDevice]:
        """Scan for nearby BLE devices."""
        devices = await BleakScanner.discover(timeout=timeout)
        logger.info("ble_scan_complete", count=len(devices))
        return devices

    async def connect(self, address: str) -> None:
        """Connect to a BLE device by address."""
        self._client = BleakClient(address)
        await self._client.connect()
        logger.info("ble_connected", address=address)

    async def read_characteristic(self, uuid: str) -> bytes:
        """Read a BLE characteristic by UUID."""
        if self._client is None or not self._client.is_connected:
            msg = "BLE client not connected — call connect() first"
            raise RuntimeError(msg)
        data = await self._client.read_gatt_char(uuid)
        logger.debug("ble_read", uuid=uuid, size=len(data))
        return bytes(data)

    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if self._client is not None and self._client.is_connected:
            await self._client.disconnect()
            logger.info("ble_disconnected")
        self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected
