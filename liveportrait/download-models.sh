#!/bin/bash
set -e

echo "🚀 LivePortrait Model Download Script"
echo "======================================"

MODELS_DIR="/app/pretrained_weights"

# Check if models already exist
if [ -f "$MODELS_DIR/.downloaded" ]; then
    echo "✅ Models already downloaded. Skipping download."
    exit 0
fi

# Check if essential model files exist
if [ -f "$MODELS_DIR/appearance_feature_extractor.pth" ] && \
   [ -f "$MODELS_DIR/motion_extractor.pth" ] && \
   [ -f "$MODELS_DIR/warping_module.pth" ]; then
    echo "✅ Essential model files found. Marking as downloaded."
    touch "$MODELS_DIR/.downloaded"
    exit 0
fi

echo "📥 Downloading LivePortrait pretrained weights..."
echo "⏱️  This will take 5-10 minutes depending on your connection..."

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

cd "$MODELS_DIR"

# Download using huggingface-cli if available
if command -v huggingface-cli &> /dev/null; then
    echo "Using huggingface-cli to download models..."
    
    # Set HuggingFace token if available
    if [ -n "$HF_TOKEN" ]; then
        export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
    fi
    
    # Download from HuggingFace with progress
    echo "Starting download... (this may take several minutes)"
    huggingface-cli download KlingTeam/LivePortrait \
        --local-dir "$MODELS_DIR" \
        --exclude "*.git*" "README.md" "docs" 2>&1 | while read line; do
        echo "$line"
    done
    
    echo "✅ Models downloaded successfully via huggingface-cli"
else
    echo "⚠️  huggingface-cli not found."
    echo "Attempting to install..."
    pip install -q huggingface_hub[cli]
    
    if command -v huggingface-cli &> /dev/null; then
        echo "✅ Installed huggingface-cli, retrying download..."
        exec "$0" "$@"
    else
        echo "❌ Could not install huggingface-cli"
        echo ""
        echo "Alternative: Download manually from:"
        echo "    https://huggingface.co/KlingTeam/LivePortrait"
        echo "    or"
        echo "    https://drive.google.com/drive/folders/1UtKgzKjFAOmZkhNK-OYT0caJ_w2XAnib"
        exit 1
    fi
fi

# Create marker file to indicate successful download
touch "$MODELS_DIR/.downloaded"

echo "✅ LivePortrait models download complete!"
echo "Models location: $MODELS_DIR"
ls -lh "$MODELS_DIR" | head -20
