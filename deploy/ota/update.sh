#!/usr/bin/env bash
# OTA (Over-The-Air) update script for myapp IoT application.
#
# Usage:
#   sudo deploy/ota/update.sh
#
# What it does:
#   1. Pulls latest code from git
#   2. Syncs dependencies with uv
#   3. Runs database migrations (if any)
#   4. Restarts the systemd service
#
# Schedule with cron for automatic updates:
#   0 3 * * * /home/pi/myapp/deploy/ota/update.sh >> /var/log/myapp-ota.log 2>&1

set -euo pipefail

APP_DIR="${APP_DIR:-/home/pi/myapp}"
SERVICE_NAME="${SERVICE_NAME:-myapp}"
BRANCH="${BRANCH:-main}"
LOG_TAG="[myapp-ota]"

log() {
    echo "${LOG_TAG} $(date '+%Y-%m-%d %H:%M:%S') $*"
}

cd "${APP_DIR}"

log "Starting OTA update..."

# 1. Pull latest changes
log "Pulling latest from ${BRANCH}..."
BEFORE=$(git rev-parse HEAD)
git fetch origin "${BRANCH}"
git reset --hard "origin/${BRANCH}"
AFTER=$(git rev-parse HEAD)

if [ "${BEFORE}" = "${AFTER}" ]; then
    log "Already up to date (${BEFORE}). No restart needed."
    exit 0
fi

log "Updated: ${BEFORE} -> ${AFTER}"

# 2. Sync dependencies
log "Syncing dependencies..."
uv sync --frozen

# 3. Run any post-update hooks
if [ -f "${APP_DIR}/deploy/ota/post-update.sh" ]; then
    log "Running post-update hook..."
    bash "${APP_DIR}/deploy/ota/post-update.sh"
fi

# 4. Restart service
log "Restarting ${SERVICE_NAME}..."
systemctl restart "${SERVICE_NAME}"

# 5. Verify service is running
sleep 3
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    log "Service ${SERVICE_NAME} is running. OTA update complete."
else
    log "WARNING: Service ${SERVICE_NAME} failed to start after update!"
    log "Rolling back to ${BEFORE}..."
    git reset --hard "${BEFORE}"
    uv sync --frozen
    systemctl restart "${SERVICE_NAME}"
    log "Rolled back to ${BEFORE}."
    exit 1
fi
