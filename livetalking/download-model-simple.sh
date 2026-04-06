#!/bin/bash
# Simple download script for wav2lip model - no Python required

set -e

echo "=========================================="
echo "Wav2Lip Model Downloader"
echo "=========================================="
echo ""

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

echo "Available download sources:"
echo ""
echo "1) Google Drive (Recommended)"
echo "2) Official Wav2Lip (OneDrive direct download)"
echo "3) Quark Cloud Drive"
echo ""
read -p "Select source (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Opening Google Drive in browser..."
        echo ""
        echo "Manual steps:"
        echo "1. Download from: https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy"
        echo "2. Click on 'wav2lip.pth'"
        echo "3. Click 'Download'"
        echo "4. Save to: livetalking-data/models/wav2lip.pth"
        echo ""
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy" 2>/dev/null || true
        elif command -v open &> /dev/null; then
            open "https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy" 2>/dev/null || true
        fi
        
        echo "Press Enter after you've downloaded the file..."
        read
        ;;
    2)
        echo ""
        echo "Downloading from Official Wav2Lip repository..."
        echo "This may take a few minutes (~150 MB)..."
        echo ""

        if command -v wget &> /dev/null; then
            wget --no-check-certificate \
                 --show-progress \
                 --progress=bar:force:noscroll \
                 "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" \
                 -O livetalking-data/models/wav2lip.pth
        elif command -v curl &> /dev/null; then
            curl -L --progress-bar \
                 "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" \
                 -o livetalking-data/models/wav2lip.pth
        else
            echo "❌ Error: Neither wget nor curl is installed"
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "Opening Quark Cloud Drive in browser..."
        echo ""
        echo "Manual steps:"
        echo "1. Download from: https://pan.quark.cn/s/83a750323ef0"
        echo "2. Download 'wav2lip256.pth'"
        echo "3. Rename to 'wav2lip.pth'"
        echo "4. Save to: livetalking-data/models/wav2lip.pth"
        echo ""
        
        # Try to open browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "https://pan.quark.cn/s/83a750323ef0" 2>/dev/null || true
        elif command -v open &> /dev/null; then
            open "https://pan.quark.cn/s/83a750323ef0" 2>/dev/null || true
        fi
        
        echo "Press Enter after you've downloaded the file..."
        read
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

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
    echo "❌ Model file not found"
    echo ""
    echo "Please download manually from one of these sources:"
    echo ""
    echo "1. Google Drive:"
    echo "   https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy"
    echo ""
    echo "2. Quark Cloud:"
    echo "   https://pan.quark.cn/s/83a750323ef0"
    echo ""
    echo "Then save to: livetalking-data/models/wav2lip.pth"
    exit 1
fi
