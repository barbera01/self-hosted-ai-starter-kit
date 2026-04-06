#!/bin/bash
# Download wav2lip model from multiple sources

set -e

MODEL_DIR="./livetalking-data/models"
MODEL_FILE="$MODEL_DIR/wav2lip.pth"

echo "=========================================="
echo "Wav2Lip Model Downloader"
echo "=========================================="
echo ""

# Create directory
mkdir -p "$MODEL_DIR"

# Check if model already exists
if [ -f "$MODEL_FILE" ]; then
    echo "✓ Model already exists at: $MODEL_FILE"
    echo "  Size: $(du -h "$MODEL_FILE" | cut -f1)"
    read -p "Download again? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
fi

echo "Select download source:"
echo ""
echo "1) Official Wav2Lip (OneDrive) - Recommended"
echo "2) Hugging Face (numz/wav2lip)"
echo "3) Hugging Face (Xenova mirror)"
echo "4) Hugging Face (Wav2Lip GAN - higher quality)"
echo "5) Manual download (opens browser)"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Downloading from Official Wav2Lip repository..."
        wget --no-check-certificate \
            "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" \
            -O "$MODEL_FILE" \
            --progress=bar:force:noscroll
        ;;
    2)
        echo ""
        echo "Downloading from Hugging Face (numz/wav2lip)..."
        if ! command -v python3 &> /dev/null; then
            echo "Error: Python 3 is required"
            exit 1
        fi
        python3 << EOF
from huggingface_hub import hf_hub_download
import os
try:
    hf_hub_download(
        repo_id="numz/wav2lip",
        filename="wav2lip.pth",
        local_dir="$MODEL_DIR",
        local_dir_use_symlinks=False
    )
    # Rename if needed
    if os.path.exists("$MODEL_DIR/wav2lip.pth"):
        print("✓ Download complete!")
    else:
        print("Error: File not found after download")
        exit(1)
except Exception as e:
    print(f"Error: {e}")
    print("\nTry: pip install huggingface-hub")
    exit(1)
EOF
        ;;
    3)
        echo ""
        echo "Downloading from Hugging Face (Xenova mirror)..."
        wget https://huggingface.co/Xenova/wav2lip/resolve/main/wav2lip.pth \
            -O "$MODEL_FILE" \
            --progress=bar:force:noscroll
        ;;
    4)
        echo ""
        echo "Downloading Wav2Lip GAN (higher quality, larger file)..."
        wget https://huggingface.co/spaces/Rudrabha/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth \
            -O "$MODEL_FILE" \
            --progress=bar:force:noscroll
        ;;
    5)
        echo ""
        echo "Opening download links in browser..."
        echo ""
        echo "Download from one of these sources:"
        echo ""
        echo "1. Official OneDrive:"
        echo "   https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ"
        echo ""
        echo "2. Google Drive:"
        echo "   https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy"
        echo ""
        echo "3. Hugging Face:"
        echo "   https://huggingface.co/numz/wav2lip"
        echo ""
        echo "Then save the file to: $MODEL_FILE"
        echo ""
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "https://huggingface.co/numz/wav2lip" 2>/dev/null || true
        elif command -v open &> /dev/null; then
            open "https://huggingface.co/numz/wav2lip" 2>/dev/null || true
        fi
        
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Verify download
if [ -f "$MODEL_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$MODEL_FILE" 2>/dev/null || stat -c%s "$MODEL_FILE" 2>/dev/null)
    FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))
    
    echo ""
    echo "=========================================="
    echo "✓ Download Complete!"
    echo "=========================================="
    echo "File: $MODEL_FILE"
    echo "Size: ${FILE_SIZE_MB} MB"
    echo ""
    
    # Check if size is reasonable (should be around 150-200 MB)
    if [ $FILE_SIZE_MB -lt 50 ]; then
        echo "⚠️  Warning: File size seems too small (${FILE_SIZE_MB} MB)"
        echo "   Expected size: ~150-200 MB"
        echo "   The download may have failed."
        exit 1
    fi
    
    echo "Model ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. Add avatar image: livetalking-data/avatars/default/avatar.jpg"
    echo "2. Start service: docker compose --profile avatar up livetalking -d"
    echo "3. Generate video: python livetalking/examples/generate-avatar-video.py \"Hello!\""
else
    echo ""
    echo "❌ Download failed"
    echo "Please try another source or download manually"
    exit 1
fi
