#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")

SCRIPTS=(
  "./scripts/fetch-fs-data/fetch_food_entries.py"
  "./scripts/fetch-fs-data/fetch_exercise_entries.py"
  "./scripts/fetch-fs-data/fetch_weight.py"
)

for SCRIPT in "${SCRIPTS[@]}"; do
  SCRIPT_NAME=$(basename "$SCRIPT" .py)

  LOG_DIR="./output/logs/$SCRIPT_NAME"
  mkdir -p "$LOG_DIR"

  python3 "$SCRIPT" >> "$LOG_DIR/${SCRIPT_NAME}_$DATE.log" 2>&1
done

find ./output/logs/ -type f -name "*.log" -mtime +7 -delete
