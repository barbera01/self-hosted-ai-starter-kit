#!/bin/bash
# Setup driving videos for idle animations
# This script helps you get the driving videos needed for idle motions

set -e

echo "🎬 LivePortrait Driving Videos Setup"
echo "====================================="
echo ""

DRIVING_DIR="./shared/liveportrait_driving"
mkdir -p "$DRIVING_DIR"

echo "📁 Driving videos will be stored in: $DRIVING_DIR"
echo ""
echo "You need driving videos for these idle motions:"
echo "  1. idle_combined.mp4 - Combined idle (blink + breathing + movement)"
echo "  2. blink.mp4 - Natural blinking"
echo "  3. breathing.mp4 - Subtle breathing motion"
echo "  4. head_nod.mp4 - Gentle head nod"
echo ""
echo "Options to get driving videos:"
echo ""
echo "A) Use LivePortrait's example videos (recommended)"
echo "   - Clone LivePortrait repo and copy examples"
echo "   - Location: LivePortrait/assets/examples/driving/"
echo ""
echo "B) Record your own"
echo "   - Record yourself doing each motion"
echo "   - 512x512 resolution, 2-5 seconds each"
echo "   - Front-facing, well-lit"
echo ""
echo "C) Download from shared sources"
echo "   - Check LivePortrait GitHub releases"
echo "   - Community-shared driving videos"
echo ""

read -p "Do you want to download LivePortrait examples? (y/n): " choice

if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo ""
    echo "📥 Downloading LivePortrait repository examples..."
    
    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Clone just the examples
    echo "Cloning LivePortrait (this may take a few minutes)..."
    git clone --depth 1 --filter=blob:none --sparse https://github.com/KlingAIResearch/LivePortrait.git
    cd LivePortrait
    git sparse-checkout set assets/examples/driving
    
    # Copy driving videos
    if [ -d "assets/examples/driving" ]; then
        echo "✅ Found driving videos!"
        
        # Copy all driving videos
        cp assets/examples/driving/*.mp4 "$DRIVING_DIR/" 2>/dev/null || true
        cp assets/examples/driving/*.pkl "$DRIVING_DIR/" 2>/dev/null || true
        
        # List what we got
        echo ""
        echo "📋 Downloaded driving videos:"
        ls -lh "$DRIVING_DIR"
        
        # Create symlinks with standard names if they don't exist
        cd "$DRIVING_DIR"
        
        # Map example videos to our standard names
        # Note: You'll need to adjust these based on what's actually in the repo
        if [ -f "d0.mp4" ] && [ ! -f "idle_combined.mp4" ]; then
            ln -s d0.mp4 idle_combined.mp4
            echo "✅ Created idle_combined.mp4"
        fi
        
        if [ -f "d5.mp4" ] && [ ! -f "blink.mp4" ]; then
            ln -s d5.mp4 blink.mp4
            echo "✅ Created blink.mp4"
        fi
        
        echo ""
        echo "✅ Setup complete!"
    else
        echo "❌ Could not find driving videos in repository"
    fi
    
    # Cleanup
    cd /
    rm -rf "$TEMP_DIR"
else
    echo ""
    echo "📝 Manual setup instructions:"
    echo ""
    echo "1. Get driving videos from one of these sources:"
    echo "   - LivePortrait GitHub: https://github.com/KlingAIResearch/LivePortrait"
    echo "   - Record your own (see tips below)"
    echo ""
    echo "2. Place them in: $DRIVING_DIR"
    echo ""
    echo "3. Name them:"
    echo "   - idle_combined.mp4"
    echo "   - blink.mp4"
    echo "   - breathing.mp4"
    echo "   - head_nod.mp4"
    echo ""
    echo "📹 Tips for recording your own:"
    echo "   - Use 512x512 or 256x256 resolution"
    echo "   - 2-5 seconds duration"
    echo "   - Front-facing, well-lit"
    echo "   - Neutral expression at start and end (for looping)"
    echo "   - One motion type per video"
    echo ""
    echo "Example with ffmpeg:"
    echo "  ffmpeg -i your_video.mp4 -vf scale=512:512 -t 5 idle_combined.mp4"
fi

echo ""
echo "====================================="
echo "Next steps:"
echo ""
echo "1. Verify driving videos are in: $DRIVING_DIR"
echo "2. Update docker-compose.yml to mount this directory"
echo "3. Start LivePortrait: docker compose --profile avatar up liveportrait -d"
echo "4. Open http://localhost:8012 and create idle animations!"
echo ""
