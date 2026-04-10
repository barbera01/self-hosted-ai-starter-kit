#!/bin/bash
# Download example driving videos from LivePortrait repository

set -e

DRIVING_DIR="/app/data/driving"
ASSETS_DIR="/app/assets/examples/driving"

echo "🎬 Checking for driving videos..."

# Check if we already have driving videos
if [ -f "$DRIVING_DIR/.downloaded" ]; then
    echo "✅ Driving videos already downloaded"
    exit 0
fi

echo "📥 Downloading example driving videos from LivePortrait..."

# The LivePortrait repo should already be cloned in /app
# Just copy the example driving videos to our driving directory

if [ -d "$ASSETS_DIR" ]; then
    echo "✅ Found example driving videos in LivePortrait repo"
    
    # Copy all driving videos
    cp "$ASSETS_DIR"/*.mp4 "$DRIVING_DIR/" 2>/dev/null || true
    cp "$ASSETS_DIR"/*.pkl "$DRIVING_DIR/" 2>/dev/null || true
    
    # Create standard named symlinks for common motions
    cd "$DRIVING_DIR"
    
    # Map LivePortrait examples to our standard names
    # d0.mp4  - long general expression (good for idle_combined)
    # d6.mp4  - another general expression (good for breathing / head_nod)
    # d18.mp4 - very short clip (good for blink - minimal motion)
    # d11.mp4 - short clip (also good for subtle motion)

    if [ -f "d0.mp4" ]; then
        ln -sf d0.mp4 idle_combined.mp4
        echo "✅ Created idle_combined.mp4 -> d0.mp4"
    fi

    if [ -f "d18.mp4" ]; then
        ln -sf d18.mp4 blink.mp4
        echo "✅ Created blink.mp4 -> d18.mp4"
    elif [ -f "d11.mp4" ]; then
        ln -sf d11.mp4 blink.mp4
        echo "✅ Created blink.mp4 -> d11.mp4"
    fi

    if [ -f "d6.mp4" ]; then
        ln -sf d6.mp4 breathing.mp4
        echo "✅ Created breathing.mp4 -> d6.mp4"
    fi

    if [ -f "d3.mp4" ]; then
        ln -sf d3.mp4 head_nod.mp4
        echo "✅ Created head_nod.mp4 -> d3.mp4"
    elif [ -f "d0.mp4" ]; then
        ln -sf d0.mp4 head_nod.mp4
        echo "✅ Created head_nod.mp4 -> d0.mp4"
    fi
    
    # Mark as downloaded
    touch "$DRIVING_DIR/.downloaded"
    
    echo "✅ Driving videos setup complete!"
    ls -lh "$DRIVING_DIR"
else
    echo "⚠️  Warning: LivePortrait example videos not found"
    echo "   Expected location: $ASSETS_DIR"
    echo ""
    echo "   The service will still work if you provide your own driving videos."
    echo "   Place them in: $DRIVING_DIR"
    echo "   Named as: idle_combined.mp4, blink.mp4, breathing.mp4, head_nod.mp4"
fi
