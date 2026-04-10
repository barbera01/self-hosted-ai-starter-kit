#!/bin/bash
# Download only essential models for human portraits (not animals)
# This is much faster and more reliable

set -e

echo "🚀 Downloading Essential LivePortrait Models (Humans Only)"
echo "=========================================================="

MODELS_DIR="/app/pretrained_weights"
BASE_MODELS_DIR="$MODELS_DIR/liveportrait/base_models"

# Check if already downloaded
if [ -f "$MODELS_DIR/.downloaded" ]; then
    echo "✅ Models already downloaded"
    exit 0
fi

# Create directories
mkdir -p "$BASE_MODELS_DIR"
mkdir -p "$MODELS_DIR/liveportrait"

echo ""
echo "📥 Downloading essential model files..."
echo "This will download ~500MB (humans only, no animals)"
echo ""

# Download individual files with wget (more reliable than hf)
cd "$BASE_MODELS_DIR"

# Base URL for direct downloads
BASE_URL="https://huggingface.co/KlingTeam/LivePortrait/resolve/main"

# Essential files for human portraits
declare -A FILES=(
    ["appearance_feature_extractor.pth"]="liveportrait/base_models/appearance_feature_extractor.pth"
    ["motion_extractor.pth"]="liveportrait/base_models/motion_extractor.pth"
    ["warping_module.pth"]="liveportrait/base_models/warping_module.pth"
    ["spade_generator.pth"]="liveportrait/base_models/spade_generator.pth"
    ["stitching_retargeting_module.pth"]="liveportrait/base_models/stitching_retargeting_module.pth"
)

# Download landmark detector
echo "1/6 Downloading landmark detector..."
wget -q --show-progress -O "$MODELS_DIR/liveportrait/landmark.onnx" \
    "$BASE_URL/liveportrait/landmark.onnx" || {
    echo "⚠️  Failed to download landmark.onnx, trying alternative..."
    curl -L -o "$MODELS_DIR/liveportrait/landmark.onnx" \
        "$BASE_URL/liveportrait/landmark.onnx"
}

# Download base models
i=2
for file in "${!FILES[@]}"; do
    echo "$i/6 Downloading $file..."
    
    if [ -f "$file" ] && [ -s "$file" ]; then
        echo "   ✅ Already exists, skipping"
    else
        wget -q --show-progress -O "$file" \
            "$BASE_URL/${FILES[$file]}" || {
            echo "⚠️  wget failed, trying curl..."
            curl -L -o "$file" "$BASE_URL/${FILES[$file]}"
        }
    fi
    
    ((i++))
done

echo ""
echo "✅ Essential models downloaded!"
echo ""
echo "📋 Downloaded files:"
ls -lh "$BASE_MODELS_DIR"
ls -lh "$MODELS_DIR/liveportrait/"

# Mark as downloaded
touch "$MODELS_DIR/.downloaded"

echo ""
echo "=========================================================="
echo "✅ Setup complete! You can now generate idle animations."
echo "=========================================================="
