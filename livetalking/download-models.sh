#!/bin/bash
# Download LiveTalking models and sample avatars

set -e

MODELS_DIR="/app/models"
AVATARS_DIR="/app/data/avatars"

echo "==================================="
echo "LiveTalking Model Downloader"
echo "==================================="

# Create directories
mkdir -p "$MODELS_DIR"
mkdir -p "$AVATARS_DIR"

# Download wav2lip model
echo "Downloading wav2lip model..."
if [ ! -f "$MODELS_DIR/wav2lip.pth" ]; then
    # Option 1: From Quark Cloud Drive (requires manual download)
    echo "Please download wav2lip256.pth from:"
    echo "https://pan.quark.cn/s/83a750323ef0"
    echo "And place it in: $MODELS_DIR/wav2lip.pth"
    echo ""
    
    # Option 2: From Google Drive (requires gdown)
    # pip install gdown
    # gdown --id YOUR_FILE_ID -O "$MODELS_DIR/wav2lip.pth"
    
    # Option 3: From Hugging Face
    if [ -n "$HF_TOKEN" ]; then
        echo "Attempting to download from Hugging Face..."
        pip install huggingface_hub
        python3 << EOF
from huggingface_hub import hf_hub_download
try:
    hf_hub_download(
        repo_id="lipku/LiveTalking-models",
        filename="wav2lip256.pth",
        local_dir="$MODELS_DIR",
        token="$HF_TOKEN"
    )
    import shutil
    shutil.move("$MODELS_DIR/wav2lip256.pth", "$MODELS_DIR/wav2lip.pth")
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Download failed: {e}")
    print("Please download manually from the links above")
EOF
    fi
else
    echo "wav2lip model already exists"
fi

# Download sample avatar
echo "Setting up sample avatar..."
SAMPLE_AVATAR="$AVATARS_DIR/default"
mkdir -p "$SAMPLE_AVATAR"

if [ ! -f "$SAMPLE_AVATAR/avatar.jpg" ]; then
    echo "Please add your avatar image to: $SAMPLE_AVATAR/avatar.jpg"
    echo "Or download sample avatars from:"
    echo "https://pan.quark.cn/s/83a750323ef0"
    echo ""
    echo "Avatar can be:"
    echo "  - A single image (avatar.jpg or avatar.png)"
    echo "  - A short video loop (avatar.mp4)"
fi

echo "==================================="
echo "Setup Instructions:"
echo "==================================="
echo "1. Download models from: https://pan.quark.cn/s/83a750323ef0"
echo "2. Place wav2lip256.pth in: $MODELS_DIR/wav2lip.pth"
echo "3. Extract avatar folders to: $AVATARS_DIR/"
echo "4. Restart the container"
echo ""
echo "For more models and avatars, see:"
echo "https://github.com/lipku/LiveTalking/blob/main/README-EN.md"
echo "==================================="
