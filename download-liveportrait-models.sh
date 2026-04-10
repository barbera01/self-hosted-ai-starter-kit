#!/bin/bash
# Download LivePortrait models on the host machine
# Run this on your host (the remote GPU server), not in the container
#
# Usage: bash download-liveportrait-models.sh
#
# Models are downloaded to ./liveportrait_models/ which is bind-mounted
# into the container at /app/pretrained_weights

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/liveportrait_models"
BASE_MODELS_DIR="$MODELS_DIR/liveportrait/base_models"
RETARGET_DIR="$MODELS_DIR/liveportrait/retargeting_models"
INSIGHTFACE_DIR="$MODELS_DIR/insightface/models/buffalo_l"

BASE_URL="https://huggingface.co/KlingTeam/LivePortrait/resolve/main"

echo "======================================================"
echo " LivePortrait Model Downloader"
echo " Destination: $MODELS_DIR"
echo "======================================================"
echo ""

# Create directory structure
mkdir -p "$BASE_MODELS_DIR"
mkdir -p "$RETARGET_DIR"
mkdir -p "$INSIGHTFACE_DIR"

# Helper: download only if file doesn't exist or is zero-size
download() {
    local dest="$1"
    local url="$2"
    local label="$3"
    if [ -s "$dest" ]; then
        echo "  ✅ Already exists, skipping: $label"
    else
        echo "  ⬇️  Downloading $label..."
        wget -q --show-progress -O "$dest" "$url" || { echo "  ❌ FAILED: $label"; exit 1; }
        echo "  ✅ Done: $label"
    fi
}

echo "── Base models ──────────────────────────────────────"
download "$BASE_MODELS_DIR/appearance_feature_extractor.pth" \
    "$BASE_URL/liveportrait/base_models/appearance_feature_extractor.pth" \
    "appearance_feature_extractor.pth (~46 MB)"

download "$BASE_MODELS_DIR/motion_extractor.pth" \
    "$BASE_URL/liveportrait/base_models/motion_extractor.pth" \
    "motion_extractor.pth (~112 MB)"

download "$BASE_MODELS_DIR/warping_module.pth" \
    "$BASE_URL/liveportrait/base_models/warping_module.pth" \
    "warping_module.pth (~182 MB)"

download "$BASE_MODELS_DIR/spade_generator.pth" \
    "$BASE_URL/liveportrait/base_models/spade_generator.pth" \
    "spade_generator.pth (~222 MB)"

echo ""
echo "── Retargeting model ────────────────────────────────"
download "$RETARGET_DIR/stitching_retargeting_module.pth" \
    "$BASE_URL/liveportrait/retargeting_models/stitching_retargeting_module.pth" \
    "stitching_retargeting_module.pth (~9 MB)"

echo ""
echo "── Landmark detector ────────────────────────────────"
download "$MODELS_DIR/liveportrait/landmark.onnx" \
    "$BASE_URL/liveportrait/landmark.onnx" \
    "landmark.onnx (~115 MB)"

echo ""
echo "── InsightFace face detector ────────────────────────"
download "$INSIGHTFACE_DIR/det_10g.onnx" \
    "$BASE_URL/insightface/models/buffalo_l/det_10g.onnx" \
    "det_10g.onnx (face detector)"

download "$INSIGHTFACE_DIR/2d106det.onnx" \
    "$BASE_URL/insightface/models/buffalo_l/2d106det.onnx" \
    "2d106det.onnx (landmark 106pt)"

echo ""
echo "── Summary ──────────────────────────────────────────"
find "$MODELS_DIR" -name "*.pth" -o -name "*.onnx" | sort | while read f; do
    size=$(du -h "$f" | cut -f1)
    echo "  $size  ${f#$MODELS_DIR/}"
done

echo ""
echo "======================================================"
echo " ✅  All models ready!"
echo ""
echo " Next steps (on the server):"
echo "   docker compose --profile avatar restart liveportrait"
echo " Then open: https://liveportrait.lab.home-cloud.uk"
echo "======================================================"
