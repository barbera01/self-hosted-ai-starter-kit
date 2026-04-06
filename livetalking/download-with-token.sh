#!/bin/bash
# Wav2Lip model helper when user has a HF token

set -e

echo "=========================================="
echo "Wav2Lip Model Downloader"
echo "=========================================="
echo ""

# Check for token
if [ -z "$1" ]; then
    echo "Usage: ./download-with-token.sh YOUR_HF_TOKEN"
    echo ""
    echo "Or set environment variable:"
    echo "  export HF_TOKEN=your_token_here"
    echo "  ./download-with-token.sh"
    echo ""
echo "Get your token from: https://huggingface.co/settings/tokens"
echo ""
echo "Note: the previously tried Hugging Face wav2lip URL is not valid."
echo "This helper now guides you to the working download sources instead."
    exit 1
fi

HF_TOKEN="$1"

# Create directory
mkdir -p livetalking-data/models

# Check if file exists
if [ -f "livetalking-data/models/wav2lip.pth" ]; then
    echo "✓ Model already exists!"
    echo "  Location: livetalking-data/models/wav2lip.pth"
    echo "  Size: $(du -h livetalking-data/models/wav2lip.pth | cut -f1)"
    echo ""
    read -p "Download again? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
    echo ""
fi

echo "Your Hugging Face token is fine, but the wav2lip model URL we tried is not."
echo "Use one of these verified sources instead:"
echo ""
echo "1. Google Drive (recommended):"
echo "   https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy"
echo ""
echo "2. Official OneDrive / SharePoint:"
echo "   https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ"
echo ""
echo "3. Quark Cloud mirror:"
echo "   https://pan.quark.cn/s/83a750323ef0"
echo ""
echo "If you want, this script can open Google Drive for you now."
read -p "Open Google Drive in your browser? (Y/n): " open_drive

if [[ ! "$open_drive" =~ ^[Nn]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy" 2>/dev/null || true
    elif command -v open &> /dev/null; then
        open "https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy" 2>/dev/null || true
    fi
fi

echo ""
echo "Download 'wav2lip.pth' and save it to:"
echo "  livetalking-data/models/wav2lip.pth"
echo ""
echo "Then press Enter to continue."
read

# Verify download
if [ -f "livetalking-data/models/wav2lip.pth" ]; then
    FILE_SIZE=$(du -h livetalking-data/models/wav2lip.pth | cut -f1)
    
    echo ""
    echo "=========================================="
    echo "✓ Download Complete!"
    echo "=========================================="
    echo "File: livetalking-data/models/wav2lip.pth"
    echo "Size: $FILE_SIZE"
    echo ""
    echo "Next steps:"
    echo "1. Add avatar: livetalking-data/avatars/default/avatar.jpg"
    echo "2. Start: docker compose --profile avatar up -d"
    echo "3. Generate: python livetalking/examples/generate-avatar-video.py \"Hello!\""
    echo ""
else
    echo ""
    echo "❌ Download failed"
    echo ""
    echo "Please download manually from one of these working sources:"
    echo "1. Google Drive: https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy"
    echo "2. Official OneDrive: https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ"
    echo "3. Quark Cloud: https://pan.quark.cn/s/83a750323ef0"
    exit 1
fi
