#!/bin/bash
set -e

echo "🚀 LivePortrait Model Download Script"
echo "======================================"

MODELS_DIR="/app/pretrained_weights"

# Check if models already exist
if [ -f "$MODELS_DIR/liveportrait_base_models_v1.tar.gz.downloaded" ]; then
    echo "✅ Models already downloaded. Skipping download."
    exit 0
fi

echo "📥 Downloading LivePortrait pretrained weights..."

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

cd "$MODELS_DIR"

# Download using huggingface-cli if available, otherwise use wget
if command -v huggingface-cli &> /dev/null; then
    echo "Using huggingface-cli to download models..."
    
    # Set HuggingFace token if available
    if [ -n "$HF_TOKEN" ]; then
        export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
    fi
    
    # Download from HuggingFace
    huggingface-cli download KlingTeam/LivePortrait \
        --local-dir "$MODELS_DIR" \
        --exclude "*.git*" "README.md" "docs"
    
    echo "✅ Models downloaded successfully via huggingface-cli"
else
    echo "⚠️  huggingface-cli not found. Please install it with:"
    echo "    pip install -U 'huggingface_hub[cli]'"
    echo ""
    echo "Alternative: Download manually from:"
    echo "    https://huggingface.co/KlingTeam/LivePortrait"
    echo "    or"
    echo "    https://drive.google.com/drive/folders/1UtKgzKjFAOmZkhNK-OYT0caJ_w2XAnib"
    exit 1
fi

# Create marker file to indicate successful download
touch "$MODELS_DIR/liveportrait_base_models_v1.tar.gz.downloaded"

echo "✅ LivePortrait models download complete!"
echo "Models location: $MODELS_DIR"
