---
name: version-control
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers:
  - git
  - commit
  - ci
  - deploy
  - raspberry pi
---

# Version Control — Python IoT

## Commits (Conventional)

- `feat(drivers): add BLE sensor driver`
- `fix(mqtt): reconnect on broker disconnect`
- `feat(protocols): add serial frame CRC validation`

## CI Pipeline

1. `uv sync`
2. `uv run ruff check . && ruff format --check .`
3. `uv run mypy src/`
4. `uv run pytest -m "not hardware" --cov` — skip hardware tests
5. Build Docker image for target platform

## .gitignore

```
__pycache__/
*.pyc
.venv/
.env
*.log
data/
```

## Deployment (Embedded/Edge)

```bash
# Cross-platform Docker
docker buildx build --platform linux/arm64 -t iot-app .

# Direct deploy to Raspberry Pi
rsync -avz src/ pi@device:/opt/iot-app/src/
ssh pi@device "cd /opt/iot-app && uv sync && systemctl restart iot-app"
```

## Systemd Service

```ini
[Unit]
Description=IoT Sensor Service
After=network.target

[Service]
ExecStart=/opt/iot-app/.venv/bin/python -m mypackage
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
