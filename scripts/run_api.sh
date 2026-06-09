#!/usr/bin/env bash
set -euo pipefail
uvicorn serverforge.api.app:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8080}"
