"""Entry point for ``python -m myapp``."""

from __future__ import annotations

import asyncio


def main() -> None:
    """Run the IoT application."""
    from myapp.app import Application

    app = Application()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
