#!/usr/bin/env bash
# ============================================================
# download-models.sh  —  MuseTalk v1.5 model downloader
# Run inside the container: bash /app/download-models.sh
# Total download: ~8 GB
# ============================================================
set -euo pipefail

MODELS=/app/models
HF_TOKEN="${HF_TOKEN:-}"

if [ -n "$HF_TOKEN" ]; then
    huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential 2>/dev/null || true
fi

hf_dl() {
    # hf_dl <repo> <remote_path_in_repo> <local_dest_file>
    local repo="$1" remote_path="$2" local_dest="$3"
    if [ -f "$local_dest" ]; then
        echo "[skip] $local_dest"
        return
    fi
    mkdir -p "$(dirname "$local_dest")"
    local tmpdir
    tmpdir=$(mktemp -d)
    echo "[download] $repo  $remote_path"
    huggingface-cli download "$repo" "$remote_path" \
        --local-dir "$tmpdir" \
        --quiet
    # huggingface-cli mirrors the full repo path under tmpdir; move to dest
    mv "$tmpdir/$remote_path" "$local_dest"
    rm -rf "$tmpdir"
    echo "[done]    $local_dest"
}

# ------------------------------------------------------------------
# 1. MuseTalk v1.5 UNet  (paths verified against HF repo siblings)
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "musetalkV15/unet.pth"         "$MODELS/musetalkV15/unet.pth"
hf_dl "TMElyralab/MuseTalk" "musetalkV15/musetalk.json"    "$MODELS/musetalkV15/musetalk.json"

# ------------------------------------------------------------------
# 2. MuseTalk v1.0 audio encoder
# ------------------------------------------------------------------
hf_dl "TMElyralab/MuseTalk" "musetalk/pytorch_model.bin"   "$MODELS/musetalk/pytorch_model.bin"
hf_dl "TMElyralab/MuseTalk" "musetalk/musetalk.json"       "$MODELS/musetalk/musetalk.json"

# ------------------------------------------------------------------
# 3. SyncNet (LatentSync) — file is at repo root, not in checkpoints/
# ------------------------------------------------------------------
hf_dl "ByteDance/LatentSync" "latentsync_syncnet.pt"       "$MODELS/syncnet/latentsync_syncnet.pt"

# ------------------------------------------------------------------
# 4. DWPose
# ------------------------------------------------------------------
hf_dl "yzd-v/DWPose" "dw-ll_ucoco_384.pth"                "$MODELS/dwpose/dw-ll_ucoco_384.pth"

# ------------------------------------------------------------------
# 5. Face parsing BiSeNet (Google Drive)
# ------------------------------------------------------------------
mkdir -p "$MODELS/face-parse-bisent"

if [ ! -f "$MODELS/face-parse-bisent/79999_iter.pth" ]; then
    echo "[download] face-parse-bisent/79999_iter.pth from Google Drive"
    gdown "https://drive.google.com/uc?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812" \
          -O "$MODELS/face-parse-bisent/79999_iter.pth"
else
    echo "[skip] $MODELS/face-parse-bisent/79999_iter.pth"
fi

if [ ! -f "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" ]; then
    echo "[download] resnet18 backbone from pytorch.org"
    wget -q --show-progress \
         -O "$MODELS/face-parse-bisent/resnet18-5c106cde.pth" \
         "https://download.pytorch.org/models/resnet18-5c106cde.pth"
else
    echo "[skip] $MODELS/face-parse-bisent/resnet18-5c106cde.pth"
fi

# ------------------------------------------------------------------
# 6. Stable Diffusion VAE (sd-vae-ft-mse)
# ------------------------------------------------------------------
hf_dl "stabilityai/sd-vae-ft-mse" "config.json"                 "$MODELS/sd-vae/config.json"
hf_dl "stabilityai/sd-vae-ft-mse" "diffusion_pytorch_model.bin" "$MODELS/sd-vae/diffusion_pytorch_model.bin"

# ------------------------------------------------------------------
# 7. Whisper tiny
# ------------------------------------------------------------------
hf_dl "openai/whisper-tiny" "config.json"                       "$MODELS/whisper/config.json"
hf_dl "openai/whisper-tiny" "pytorch_model.bin"                 "$MODELS/whisper/pytorch_model.bin"
hf_dl "openai/whisper-tiny" "preprocessor_config.json"          "$MODELS/whisper/preprocessor_config.json"

echo ""
echo "========================================="
echo " MuseTalk models download complete ✓"
echo "========================================="
du -sh "$MODELS"/*/
