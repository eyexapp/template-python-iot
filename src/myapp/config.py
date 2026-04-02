"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────
    app_name: str = "myapp"
    app_env: str = "development"
    log_level: str = "info"
    locale: str = "en"

    # ── Hardware ──────────────────────────────────────────────────────────
    mock_mode: bool = True
    poll_interval_seconds: float = 5.0

    # ── MQTT ──────────────────────────────────────────────────────────────
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "myapp/sensors"

    # ── Serial ────────────────────────────────────────────────────────────
    serial_port: str = "/dev/ttyUSB0"
    serial_baudrate: int = 9600

    # ── HTTP ──────────────────────────────────────────────────────────────
    http_endpoint: str = "http://localhost:8080/api/readings"

    # ── WebSocket ─────────────────────────────────────────────────────────
    ws_url: str = "ws://localhost:8765"

    # ── Database ──────────────────────────────────────────────────────────
    db_path: str = "data/sensors.db"


settings = Settings()
