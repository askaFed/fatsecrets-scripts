#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE=$(date +"%Y-%m-%d_%H-%M")
SCRIPT="./scripts/fetch-fs-data/share_meals.py"

source "$SCRIPT_DIR/venv/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"

SCRIPT_NAME=$(basename "$SCRIPT" .py)
LOG_DIR="$SCRIPT_DIR/output/logs/$SCRIPT_NAME"
mkdir -p "$LOG_DIR"

# Pass all command line arguments to the Python script
python "$SCRIPT_DIR/$SCRIPT" "$@" >> "$LOG_DIR/${SCRIPT_NAME}_$DATE.log" 2>&1

deactivate