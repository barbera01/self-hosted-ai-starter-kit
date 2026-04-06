#!/usr/bin/env bash
# ============================================================
# download-models.sh  —  MuseTalk v1.5 model downloader
# Run inside the container: bash /app/download-models.sh
# Total download: ~8 GB
# Uses huggingface-cli for HF files (handles LFS redirects correctly)
# ============================================================
set -euo pipefail

MODELS=/app/models
HF_TOKEN="${HF_TOKEN:-}"

# Configure huggingface-cli token if provided
if [ -n "$HF_TOKEN" ]; then
    huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential 2>/dev/null || true
fi

hf_dl() {
    # hf_dl <repo> <filename_in_repo> <local_dir>
    # Downloads a single file into local_dir, preserving its basename.
    local repo="$1" filename="$2" local_dir="$3"
    mkdir -p "$local_dir"
    local dest="$local_dir/$(basename "$filename")"
    if [ -f "$dest" ]; then
        echo "[skip] $dest already exists"
        return
    fi
    echo "[download] $repo  $filename"
    huggingface-cli download "$repo" "$filename" \
        --local-dir "$local_dir" \
        --local-dir-use-symlinks False \
        --quiet
    # huggingface-cli mirrors the full repo sub-path under local_dir;
    # flatten it so the file lands directly in local_dir.
    local mirrored="$local_dir/$filename"
    if [ -f "$mirrored" ] && [ "$mirrored" != "$dest" ]; then
        mv "$mirrored" "$dest"
        # Clean up empty parent dirs left by the mirror
        rmdir -p "$(dirname "$mirrored")" 2>/dev/null || true
    fi
    echo "[done]  $dest"
}

# ------------------------------------------------------------------
# 1. MuseTalk v1.5 UNet
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "models/musetalkV15/unet.pth"        "$MODELS/musetalkV15"
hf_dl "TMElyralab/MuseTalk" "models/musetalkV15/musetalk.json"   "$MODELS/musetalkV15"

# ------------------------------------------------------------------
# 2. MuseTalk v1.0 audio VAE (kept for compatibility)
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "models/musetalk/pytorch_model.bin"  "$MODELS/musetalk"
hf_dl "TMElyralab/MuseTalk" "models/musetalk/config.json"        "$MODELS/musetalk"

# ------------------------------------------------------------------
# 3. SyncNet (LatentSync)
# ------------------------------------------------------------------
hf_dl "ByteDance/LatentSync" "checkpoints/latentsync_syncnet.pt" "$MODELS/syncnet"

# ------------------------------------------------------------------
# 4. DWPose
# ------------------------------------------------------------------
hf_dl "yzd-v/DWPose" "dw-ll_ucoco_384.pth"                      "$MODELS/dwpose"

# ------------------------------------------------------------------
# 5. Face parsing BiSeNet (Google Drive — gdown required)
# ------------------------------------------------------------------
mkdir -p "$MODELS/face-parse-bisent"

if [ ! -f "$MODELS/face-parse-bisent/79999_iter.pth" ]; then
    echo "[download] face-parse-bisent/79999_iter.pth from Google Drive"
    gdown "https://drive.google.com/uc?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812" \
          -O "$MODELS/face-parse-bisent/79999_iter.pth"
else
    echo "[skip] face-parse-bisent/79999_iter.pth already exists"
fi

if [ ! -f "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" ]; then
    echo "[download] resnet18 backbone from pytorch.org"
    wget -q --show-progress \
         -O "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" \
         "https://download.pytorch.org/models/resnet18-5c106cde.pth"
else
    echo "[skip] resnet18-5c106cde.pth already exists"
fi

# ------------------------------------------------------------------
# 6. Stable Diffusion VAE
# ------------------------------------------------------------------
hf_dl "stabilityai/sd-vae-ft-mse" "config.json"                  "$MODELS/sd-vae"
hf_dl "stabilityai/sd-vae-ft-mse" "diffusion_pytorch_model.bin"  "$MODELS/sd-vae"

# ------------------------------------------------------------------
# 7. Whisper tiny
# ------------------------------------------------------------------
hf_dl "openai/whisper-tiny" "config.json"                        "$MODELS/whisper"
hf_dl "openai/whisper-tiny" "pytorch_model.bin"                  "$MODELS/whisper"
hf_dl "openai/whisper-tiny" "preprocessor_config.json"           "$MODELS/whisper"

echo ""
echo "========================================="
echo " MuseTalk models download complete ✓"
echo "========================================="
du -sh "$MODELS"/*/
