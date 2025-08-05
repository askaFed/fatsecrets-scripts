#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DATE=$(date +"%Y-%m-%d_%H-%M")

SCRIPTS=(
  "./scripts/fetch-fs-data/fetch_food_entries.py"
  "./scripts/fetch-fs-data/fetch_exercise_entries.py"
  "./scripts/fetch-fs-data/fetch_weight.py"
  "./scripts/enrich-nutrition-details/ai-estimate-nutrition-details.py"
)

source "$SCRIPT_DIR/venv/bin/activate"

for SCRIPT in "${SCRIPTS[@]}"; do
  SCRIPT_NAME=$(basename "$SCRIPT" .py)

  LOG_DIR="$SCRIPT_DIR/output/logs/$SCRIPT_NAME"
  mkdir -p "$LOG_DIR"

  python "$SCRIPT_DIR/$SCRIPT" >> "$LOG_DIR/${SCRIPT_NAME}_$DATE.log" 2>&1

done

deactivate

find "$SCRIPT_DIR/output/logs/" -type f -name "*.log" -mtime +7 -delete
