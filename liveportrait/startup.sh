#!/bin/bash
# Startup script for LivePortrait service

set -e

echo "🚀 LivePortrait Service Starting..."
echo "===================================="

# Download models if needed
echo ""
echo "📦 Step 1: Checking pretrained models..."
/app/download-models.sh

# Setup driving videos if needed
echo ""
echo "🎬 Step 2: Checking driving videos..."
/app/download-driving-videos.sh

# Start the web service
echo ""
echo "🌐 Step 3: Starting web service..."
echo "===================================="
python /app/simple-idle-generator.py
