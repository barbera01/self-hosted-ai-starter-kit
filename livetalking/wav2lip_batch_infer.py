#!/usr/bin/env python3
"""
Standalone batch Wav2Lip inference for LiveTalking.

Generates a lip-synced video from an audio file and a preprocessed avatar.
Avatar must be preprocessed first via avatars/wav2lip/genavatar.py.

Usage:
    python /app/wav2lip_batch_infer.py \
        --avatar_id rowan \
        --audio /app/input/job.wav \
        --output /app/output/job_raw.mp4 \
        --model /app/models/Wav2Lip-SD-GAN.pt \
        --avatars_dir /app/data/avatars
"""

import os
import sys
import cv2
import copy
import argparse
import numpy as np
import pickle
import glob
import torch
from tqdm import tqdm

# Ensure LiveTalking modules are importable
sys.path.insert(0, "/app")

from avatars.wav2lip.models import Wav2Lip
from avatars.wav2lip import audio as wav2lip_audio
from utils.image import mirror_index

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MEL_STEP_SIZE = 16
IMG_SIZE = 96  # Wav2Lip-SD was traced at 96x96

print(f"[wav2lip_batch_infer] Using {DEVICE} for inference. IMG_SIZE={IMG_SIZE}")


# ---------------------------------------------------------------------------
# Model / avatar loading
# ---------------------------------------------------------------------------


def load_model(checkpoint_path: str):
    print(f"[wav2lip] Loading checkpoint: {checkpoint_path}")

    # Try TorchScript archive first (Wav2Lip-SD .pt files)
    try:
        model = torch.jit.load(checkpoint_path, map_location=DEVICE)
        print("[wav2lip] Loaded as TorchScript model.")
        return model.eval()
    except Exception:
        pass

    # Fall back to standard state_dict checkpoint (wav2lip.pth)
    model = Wav2Lip()
    ckpt = torch.load(checkpoint_path, map_location=DEVICE, weights_only=False)
    s = {k.replace("module.", ""): v for k, v in ckpt["state_dict"].items()}
    model.load_state_dict(s)
    print("[wav2lip] Loaded as standard state_dict checkpoint.")
    return model.to(DEVICE).eval()


def load_avatar(avatar_id: str, avatars_dir: str = "/app/data/avatars"):
    avatar_path = os.path.join(avatars_dir, avatar_id)
    coords_path = os.path.join(avatar_path, "coords.pkl")

    if not os.path.exists(coords_path):
        raise FileNotFoundError(
            f"Avatar '{avatar_id}' not preprocessed yet. "
            f"Expected {coords_path}. Run genavatar.py first."
        )

    with open(coords_path, "rb") as f:
        coords = pickle.load(f)

    def _sorted_imgs(folder):
        imgs = glob.glob(os.path.join(folder, "*.[jpJP][pnPN]*[gG]"))
        return sorted(imgs, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

    full_frames = [
        cv2.imread(p) for p in _sorted_imgs(os.path.join(avatar_path, "full_imgs"))
    ]
    face_frames = [
        cv2.imread(p) for p in _sorted_imgs(os.path.join(avatar_path, "face_imgs"))
    ]

    if not full_frames or not face_frames:
        raise RuntimeError(
            f"Avatar '{avatar_id}' has no frames in full_imgs / face_imgs."
        )

    return full_frames, face_frames, coords


# ---------------------------------------------------------------------------
# Audio → mel chunks
# ---------------------------------------------------------------------------


def audio_to_mel_chunks(audio_path: str, fps: int = 25):
    """Load audio and slice into mel spectrogram chunks, one per video frame."""
    from avatars.wav2lip.hparams import hparams

    wav = wav2lip_audio.load_wav(audio_path, hparams.sample_rate)
    mel = wav2lip_audio.melspectrogram(wav)  # shape: (80, T)

    mel_idx_mul = 80.0 / fps  # 3.2 mel columns per frame at 25 fps
    chunks = []
    i = 0
    while True:
        start = int(i * mel_idx_mul)
        if start + MEL_STEP_SIZE > mel.shape[1]:
            # Last partial chunk — pad from the end
            chunks.append(mel[:, mel.shape[1] - MEL_STEP_SIZE :])
            break
        chunks.append(mel[:, start : start + MEL_STEP_SIZE])
        i += 1

    return chunks  # list of (80, 16) arrays


# ---------------------------------------------------------------------------
# Main inference
# ---------------------------------------------------------------------------


@torch.no_grad()
def run_inference(
    avatar_id: str,
    audio_path: str,
    output_path: str,
    model_path: str = "/app/models/Wav2Lip-SD-GAN.pt",
    avatars_dir: str = "/app/data/avatars",
    batch_size: int = 8,
    fps: int = 25,
):
    model = load_model(model_path)
    full_frames, face_frames, coords = load_avatar(avatar_id, avatars_dir)
    mel_chunks = audio_to_mel_chunks(audio_path, fps)

    n_frames = len(mel_chunks)
    av_len = len(face_frames)
    h, w = full_frames[0].shape[:2]

    print(
        f"[wav2lip] {n_frames} frames | avatar '{avatar_id}' "
        f"({av_len} face frames) | output {w}x{h}"
    )

    # --- write silent video first, merge audio at the end ---
    tmp_path = output_path.replace(".mp4", "_noaudio.mp4")
    writer = cv2.VideoWriter(tmp_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    for bs in tqdm(range(0, n_frames, batch_size), desc="[wav2lip] inferring"):
        be = min(bs + batch_size, n_frames)

        img_batch, mel_batch, idxs = [], [], []
        for i in range(be - bs):
            idx = mirror_index(av_len, bs + i)
            face = cv2.resize(face_frames[idx].copy(), (IMG_SIZE, IMG_SIZE))
            img_batch.append(face)
            mel_batch.append(mel_chunks[bs + i])
            idxs.append(bs + i)

        img_batch = np.array(img_batch)  # (B, 96, 96, 3)
        mel_batch = np.array(mel_batch)  # (B, 80, 16)

        # Mask lower half of face for the conditioned input
        masked = img_batch.copy()
        masked[:, IMG_SIZE // 2 :] = 0
        img_input = (
            np.concatenate((masked, img_batch), axis=3) / 255.0
        )  # (B, 96, 96, 6)
        mel_input = mel_batch[:, np.newaxis, :, :]  # (B, 1, 80, 16)

        img_t = torch.FloatTensor(img_input.transpose(0, 3, 1, 2)).to(
            DEVICE
        )  # (B, 6, 96, 96)
        mel_t = torch.FloatTensor(mel_input).to(DEVICE)  # (B, 1, 80, 16)

        pred = model(mel_t, img_t)  # (B, 3, 96, 96)
        pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.0  # (B, 96, 96, 3)

        for j, orig_idx in enumerate(idxs):
            av_idx = mirror_index(av_len, orig_idx)
            full_frame = copy.deepcopy(full_frames[av_idx])
            y1, y2, x1, x2 = coords[av_idx % len(coords)]
            resized = cv2.resize(pred[j].astype(np.uint8), (x2 - x1, y2 - y1))
            full_frame[y1:y2, x1:x2] = resized
            writer.write(full_frame)

    writer.release()
    print("[wav2lip] Frames done. Merging audio with ffmpeg...")

    ret = os.system(
        f'ffmpeg -y -i "{tmp_path}" -i "{audio_path}" '
        f'-c:v copy -c:a aac -b:a 128k -shortest "{output_path}" 2>&1'
    )
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    if ret != 0:
        raise RuntimeError(f"ffmpeg audio mux failed (exit {ret})")

    print(f"[wav2lip] Output saved: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Wav2Lip-SD inference")
    parser.add_argument("--avatar_id", required=True, help="Avatar directory name")
    parser.add_argument("--audio", required=True, help="Input audio (.wav)")
    parser.add_argument("--output", required=True, help="Output video (.mp4)")
    parser.add_argument("--model", default="/app/models/Wav2Lip-SD-GAN.pt")
    parser.add_argument("--avatars_dir", default="/app/data/avatars")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--fps", type=int, default=25)
    args = parser.parse_args()

    run_inference(
        avatar_id=args.avatar_id,
        audio_path=args.audio,
        output_path=args.output,
        model_path=args.model,
        avatars_dir=args.avatars_dir,
        batch_size=args.batch_size,
        fps=args.fps,
    )
