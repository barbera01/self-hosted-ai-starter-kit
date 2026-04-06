#!/usr/bin/env bash
# ============================================================
# download-models.sh  —  MuseTalk v1.5 model downloader
# Run inside the container: bash /app/download-models.sh
# Total download: ~8 GB
# ============================================================
set -euo pipefail

MODELS=/app/models
HF_TOKEN="${HF_TOKEN:-}"

hf_dl() {
    # hf_dl <repo> <remote_path> <local_path>
    local repo="$1" rpath="$2" lpath="$3"
    mkdir -p "$(dirname "$lpath")"
    if [ -f "$lpath" ]; then
        echo "[skip] $lpath already exists"
        return
    fi
    echo "[download] $repo/$rpath → $lpath"
    local url="https://huggingface.co/$repo/resolve/main/$rpath"
    local auth_flag=()
    if [ -n "$HF_TOKEN" ]; then
        auth_flag=(--header "Authorization: Bearer $HF_TOKEN")
    fi
    wget -q --show-progress "${auth_flag[@]+"${auth_flag[@]}"}" -O "$lpath" "$url"
}

# ------------------------------------------------------------------
# 1. MuseTalk v1.5 UNet
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "models/musetalkV15/unet.pth"           "$MODELS/musetalkV15/unet.pth"
hf_dl "TMElyralab/MuseTalk" "models/musetalkV15/musetalk.json"      "$MODELS/musetalkV15/musetalk.json"

# ------------------------------------------------------------------
# 2. MuseTalk v1.0 audio VAE (kept for compatibility)
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "models/musetalk/pytorch_model.bin"     "$MODELS/musetalk/pytorch_model.bin"
hf_dl "TMElyralab/MuseTalk" "models/musetalk/config.json"           "$MODELS/musetalk/config.json"

# ------------------------------------------------------------------
# 3. SyncNet (LatentSync) for lip-sync quality
# ------------------------------------------------------------------
hf_dl "ByteDance/LatentSync" "checkpoints/latentsync_syncnet.pt"    "$MODELS/syncnet/latentsync_syncnet.pt"

# ------------------------------------------------------------------
# 4. DWPose body/face estimator
# ------------------------------------------------------------------
mkdir -p "$MODELS/dwpose"
hf_dl "yzd-v/DWPose" "dw-ll_ucoco_384.pth"                         "$MODELS/dwpose/dw-ll_ucoco_384.pth"

# ------------------------------------------------------------------
# 5. Face parsing BiSeNet
# ------------------------------------------------------------------
mkdir -p "$MODELS/face-parse-bisent"

if [ ! -f "$MODELS/face-parse-bisent/79999_iter.pth" ]; then
    echo "[download] face-parse-bisent/79999_iter.pth from Google Drive"
    pip install -q gdown
    gdown "https://drive.google.com/uc?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812" \
          -O "$MODELS/face-parse-bisent/79999_iter.pth"
else
    echo "[skip] face-parse-bisent/79999_iter.pth already exists"
fi

if [ ! -f "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" ]; then
    echo "[download] resnet18 backbone"
    wget -q --show-progress \
         -O "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" \
         "https://download.pytorch.org/models/resnet18-5c106cde.pth"
else
    echo "[skip] resnet18-5c106cde.pth already exists"
fi

# ------------------------------------------------------------------
# 6. Stable Diffusion VAE (sd-vae-ft-mse)
# ------------------------------------------------------------------
hf_dl "stabilityai/sd-vae-ft-mse" "config.json"                     "$MODELS/sd-vae/config.json"
hf_dl "stabilityai/sd-vae-ft-mse" "diffusion_pytorch_model.bin"     "$MODELS/sd-vae/diffusion_pytorch_model.bin"

# ------------------------------------------------------------------
# 7. Whisper tiny (audio encoder for MuseTalk)
# ------------------------------------------------------------------
hf_dl "openai/whisper-tiny" "config.json"                           "$MODELS/whisper/config.json"
hf_dl "openai/whisper-tiny" "pytorch_model.bin"                     "$MODELS/whisper/pytorch_model.bin"
hf_dl "openai/whisper-tiny" "preprocessor_config.json"              "$MODELS/whisper/preprocessor_config.json"

echo ""
echo "========================================="
echo " MuseTalk models download complete ✓"
echo "========================================="
ls -lh "$MODELS"/*/
