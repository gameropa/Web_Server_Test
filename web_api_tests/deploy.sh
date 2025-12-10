#!/bin/bash
# Deploy script for Watchtower auto-updates
# Place in /opt/web-api-tests/deploy.sh on RPi5

set -e

REPO_PATH="/opt/web-api-tests"
COMPOSE_FILE="docker-compose-rpi.yml"

echo "[$(date)] Starting deployment..."

cd "$REPO_PATH"
git pull origin main
docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans
docker image prune -f

echo "[$(date)] Deployment complete"
