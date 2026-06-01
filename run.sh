#!/usr/bin/env bash

SCRIPT_PATH="$(readlink -f "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_PATH")"

cd "$PROJECT_DIR" || exit 1
exec "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/AOV.py" "$@"