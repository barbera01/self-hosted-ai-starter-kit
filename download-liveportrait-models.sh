#!/bin/bash
# Download LivePortrait models on the host machine
# Run this on your host, not in the container

set -e

echo "🚀 Downloading LivePortrait Models (Host)"
echo "=========================================="

MODELS_DIR="./liveportrait_models"
BASE_MODELS_DIR="$MODELS_DIR/liveportrait/base_models"

# Create directories
mkdir -p "$BASE_MODELS_DIR"
mkdir -p "$MODELS_DIR/liveportrait"

echo ""
echo "📥 Downloading essential model files to: $MODELS_DIR"
echo "This will download ~500MB (humans only)"
echo ""

# Base URL
BASE_URL="https://huggingface.co/KlingTeam/LivePortrait/resolve/main"

# Download landmark detector
echo "1/6 Downloading landmark detector (115MB)..."
wget --show-progress -O "$MODELS_DIR/liveportrait/landmark.onnx" \
    "$BASE_URL/liveportrait/landmark.onnx"

# Download base models
echo ""
echo "2/6 Downloading appearance_feature_extractor (46MB)..."
wget --show-progress -O "$BASE_MODELS_DIR/appearance_feature_extractor.pth" \
    "$BASE_URL/liveportrait/base_models/appearance_feature_extractor.pth"

echo ""
echo "3/6 Downloading motion_extractor (112MB)..."
wget --show-progress -O "$BASE_MODELS_DIR/motion_extractor.pth" \
    "$BASE_URL/liveportrait/base_models/motion_extractor.pth"

echo ""
echo "4/6 Downloading warping_module (182MB)..."
wget --show-progress -O "$BASE_MODELS_DIR/warping_module.pth" \
    "$BASE_URL/liveportrait/base_models/warping_module.pth"

echo ""
echo "5/6 Downloading spade_generator (222MB)..."
wget --show-progress -O "$BASE_MODELS_DIR/spade_generator.pth" \
    "$BASE_URL/liveportrait/base_models/spade_generator.pth"

echo ""
echo "6/6 Downloading stitching_retargeting_module (9MB)..."
wget --show-progress -O "$BASE_MODELS_DIR/stitching_retargeting_module.pth" \
    "$BASE_URL/liveportrait/base_models/stitching_retargeting_module.pth"

echo ""
echo "✅ All models downloaded!"
echo ""
echo "📋 Downloaded files:"
ls -lh "$BASE_MODELS_DIR"
ls -lh "$MODELS_DIR/liveportrait/"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart LivePortrait: docker compose restart liveportrait"
echo "2. Open http://localhost:8012"
echo "3. Upload an image and generate idle animation!"
echo "=========================================="
