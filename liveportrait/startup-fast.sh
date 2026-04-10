#!/bin/bash
# Fast startup - skip model download, do it on first use

set -e

echo ""
echo "=========================================="
echo "🚀 LivePortrait Service Starting (Fast Mode)"
echo "=========================================="
echo ""

# Just setup driving videos (fast)
echo "🎬 Setting up driving videos..."
echo "------------------------------------------"
/app/download-driving-videos.sh || {
    echo "⚠️  Driving video setup skipped"
}

# Start the web service immediately
echo ""
echo "🌐 Starting web service..."
echo "=========================================="
echo ""
echo "⚠️  Note: Models will download on first use"
echo "   This may take 5-10 minutes for the first generation"
echo ""
python /app/simple-idle-generator.py
