#!/bin/bash
# Download models in background without blocking startup

MODELS_DIR="/app/pretrained_weights"
LOG_FILE="/app/output/model-download.log"

echo "Starting background model download..." > "$LOG_FILE"
echo "Check progress: docker compose exec liveportrait cat /app/output/model-download.log" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run the download in background
nohup /app/download-models.sh >> "$LOG_FILE" 2>&1 &

echo "Background download started (PID: $!)"
echo "Monitor progress: docker compose exec liveportrait tail -f /app/output/model-download.log"
