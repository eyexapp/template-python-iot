"""Shared pytest fixtures for IoT tests."""

from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING

import pytest

from myapp.drivers.mock_driver import (
    MockHumiditySensor,
    MockLED,
    MockTemperatureSensor,
)
from myapp.i18n import set_locale
from myapp.storage.sqlite import SensorDataStore

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


@pytest.fixture(autouse=True)
def _reset_locale() -> Iterator[None]:
    """Reset locale to 'en' before each test."""
    set_locale("en")
    yield
    set_locale("en")


@pytest.fixture
def mock_temp_sensor() -> MockTemperatureSensor:
    return MockTemperatureSensor()


@pytest.fixture
def mock_humidity_sensor() -> MockHumiditySensor:
    return MockHumiditySensor()


@pytest.fixture
def mock_led() -> MockLED:
    return MockLED()


@pytest.fixture
async def tmp_store() -> AsyncIterator[SensorDataStore]:
    """Create a temporary SQLite store for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SensorDataStore(db_path=f"{tmpdir}/test.db")
        await store.setup()
        yield store
        await store.teardown()
