#!/bin/bash
# Startup script for LivePortrait service

set -e

echo ""
echo "=========================================="
echo "🚀 LivePortrait Service Starting..."
echo "=========================================="
echo ""

# Setup driving videos (fast)
echo "🎬 Setting up driving videos..."
echo "------------------------------------------"
/app/download-driving-videos.sh || {
    echo "⚠️  Driving video setup skipped"
}

# Check if models exist, but don't download on startup
echo ""
echo "📦 Checking for pretrained models..."
echo "------------------------------------------"
if [ -f "/app/pretrained_weights/.downloaded" ] || \
   [ -f "/app/pretrained_weights/appearance_feature_extractor.pth" ]; then
    echo "✅ Models found"
else
    echo "⚠️  Models not found - will download on first use"
    echo "   First generation will take 5-10 minutes"
    echo ""
    echo "   To download now, run:"
    echo "   docker compose exec liveportrait /app/download-models.sh"
fi

# Start the web service immediately
echo ""
echo "🌐 Starting web service..."
echo "=========================================="
echo ""
python /app/simple-idle-generator.py
