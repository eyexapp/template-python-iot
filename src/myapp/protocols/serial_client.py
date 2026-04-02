"""Serial (UART) client wrapper using pyserial."""

from __future__ import annotations

import asyncio

import serial
import structlog

logger = structlog.get_logger(__name__)


class SerialClient:
    """Async-friendly serial port communication client."""

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        timeout: float = 1.0,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._ser: serial.Serial | None = None

    async def open(self) -> None:
        """Open the serial port."""
        loop = asyncio.get_running_loop()
        self._ser = await loop.run_in_executor(
            None,
            lambda: serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
            ),
        )
        logger.info(
            "serial_opened",
            port=self._port,
            baudrate=self._baudrate,
        )

    async def read_line(self) -> str:
        """Read a line from the serial port."""
        if self._ser is None:
            msg = "Serial port not open — call open() first"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        raw = await loop.run_in_executor(None, self._ser.readline)
        line: str = raw.decode("utf-8", errors="replace").strip()
        logger.debug("serial_read", data=line)
        return line

    async def write(self, data: str) -> None:
        """Write data to the serial port."""
        if self._ser is None:
            msg = "Serial port not open — call open() first"
            raise RuntimeError(msg)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._ser.write, data.encode("utf-8"))
        logger.debug("serial_write", data=data)

    async def close(self) -> None:
        """Close the serial port."""
        if self._ser is not None and self._ser.is_open:
            self._ser.close()
            self._ser = None
            logger.info("serial_closed", port=self._port)

    @property
    def is_open(self) -> bool:
        return self._ser is not None and self._ser.is_open
