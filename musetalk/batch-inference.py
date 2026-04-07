#!/usr/bin/env python3
"""
Batch Video Generation API for MuseTalk v1.5
Same API shape as livetalking/batch-inference.py — swap URL only.

Endpoints:
  GET  /health
  GET  /models
  POST /generate          { avatar_id, text|audio_url, voice?, speed?, fps?, resolution? }
  GET  /job/{id}
  GET  /download/{id}
  POST /upload-avatar     multipart: file + avatar_id
  DELETE /job/{id}
"""

import os
import sys
import uuid
import asyncio
import aiofiles
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="MuseTalk Avatar Video Generator", version="1.5.0")

# ── Paths ────────────────────────────────────────────────────────────────────
MODELS_DIR = Path("/app/models")
AVATARS_DIR = Path("/app/data/avatars")
OUTPUT_DIR = Path("/app/output_jobs")  # per-job sub-dirs keep coords next to output
INPUT_DIR = Path("/app/input")
SHARED_DIR = Path("/app/shared")

for d in [MODELS_DIR, AVATARS_DIR, OUTPUT_DIR, INPUT_DIR, SHARED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Per-avatar Kokoro TTS voice configs ──────────────────────────────────────
# voice follows Kokoro's weighted-blend syntax: "voice1(w)+voice2(w)+..."
AVATAR_VOICE_CONFIGS: Dict[str, Dict] = {
    "rowan": {"voice": "bm_daniel(7)+bm_lewis(3)", "speed": 0.95},
    "eve": {"voice": "bf_lily(7)+bf_emma(2)+af_bella(1)+af_heart(1)", "speed": 0.95},
}
DEFAULT_VOICE_CONFIG: Dict = {"voice": "af_heart", "speed": 1.0}

# ── MuseTalk model paths ──────────────────────────────────────────────────────
UNET_PATH = str(MODELS_DIR / "musetalkV15" / "unet.pth")
UNET_CONFIG = str(MODELS_DIR / "musetalkV15" / "musetalk.json")
WHISPER_DIR = str(MODELS_DIR / "whisper")

# ── In-memory job store ───────────────────────────────────────────────────────
jobs: Dict[str, Any] = {}


# ── Pydantic models ───────────────────────────────────────────────────────────


class VideoRequest(BaseModel):
    text: Optional[str] = None
    audio_url: Optional[str] = None
    avatar_id: str = "default"
    # voice / speed: None → use per-avatar default from AVATAR_VOICE_CONFIGS
    voice: Optional[str] = None
    speed: Optional[float] = None
    resolution: str = "1280x720"
    fps: int = 25
    batch_size: int = 4


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | processing | completed | failed
    progress: int  # 0-100
    avatar_id: Optional[str] = None  # stored so download endpoint can find the file
    video_url: Optional[str] = None
    error: Optional[str] = None


# ── Health / info ─────────────────────────────────────────────────────────────


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "musetalk-v1.5",
        "models_ready": _models_ready(),
        "avatars_available": _list_avatars(),
    }


@app.get("/models")
async def list_models():
    return {
        "engine": "musetalk-v1.5",
        "models_ready": _models_ready(),
        "avatars": _list_avatars(),
    }


# ── Generate ──────────────────────────────────────────────────────────────────


@app.post("/generate")
async def generate_video(request: VideoRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = JobStatus(
        job_id=job_id, status="pending", progress=0, avatar_id=request.avatar_id
    )
    asyncio.create_task(_process_job(job_id, request))
    return {"job_id": job_id, "status": "pending"}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job status: {job.status}")
    # Video lives at OUTPUT_DIR / avatar_id / job_id / output.mp4
    avatar_id = job.avatar_id or job_id  # fallback for old jobs without avatar_id
    video_path = OUTPUT_DIR / avatar_id / job_id / "output.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(
        path=video_path, media_type="video/mp4", filename=f"avatar_{job_id}.mp4"
    )


@app.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), avatar_id: str = Form(...)):
    avatar_path = AVATARS_DIR / avatar_id
    avatar_path.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix.lower()
    save_path = avatar_path / f"avatar{ext}"
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(await file.read())

    # Invalidate cached face coordinates — they are source-specific.
    # A pkl from a single-frame image is incompatible with a multi-frame video and vice versa.
    coords_pkl = OUTPUT_DIR / avatar_id / "avatar.pkl"
    if coords_pkl.exists():
        coords_pkl.unlink()
        print(f"[upload-avatar] Invalidated stale coords cache: {coords_pkl}")

    return {
        "avatar_id": avatar_id,
        "file": str(save_path),
        "coords_cache_cleared": coords_pkl.exists() is False,
        "message": "Avatar uploaded successfully",
    }


@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    import shutil

    job = jobs[job_id]
    avatar_id = job.avatar_id or job_id
    job_dir = OUTPUT_DIR / avatar_id / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    del jobs[job_id]
    return {"message": "Job deleted"}


# ── Background processing ─────────────────────────────────────────────────────


async def _process_job(job_id: str, request: VideoRequest):
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10

        # 1. Get audio
        audio_file = await _get_audio(job_id, request)
        jobs[job_id].progress = 30

        # 2. Run MuseTalk inference
        await _run_musetalk(job_id, audio_file, request)
        jobs[job_id].progress = 90

        # 3. Verify output exists at the correct avatar_id/job_id path
        video_path = OUTPUT_DIR / request.avatar_id / job_id / "output.mp4"
        if not video_path.exists():
            raise RuntimeError("MuseTalk did not produce output.mp4")

        jobs[job_id].progress = 100
        jobs[job_id].status = "completed"
        jobs[job_id].video_url = f"/download/{job_id}"

    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
        print(f"[job {job_id}] FAILED: {e}")


# ── TTS ───────────────────────────────────────────────────────────────────────


async def _get_audio(job_id: str, request: VideoRequest) -> Path:
    audio_path = INPUT_DIR / f"{job_id}.wav"

    if request.audio_url:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(request.audio_url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Audio download failed: {resp.status}")
                async with aiofiles.open(audio_path, "wb") as f:
                    await f.write(await resp.read())

    elif request.text:
        av_cfg = AVATAR_VOICE_CONFIGS.get(request.avatar_id, DEFAULT_VOICE_CONFIG)
        voice = request.voice if request.voice is not None else av_cfg["voice"]
        speed = request.speed if request.speed is not None else av_cfg["speed"]

        print(f"[tts] avatar={request.avatar_id} voice={voice!r} speed={speed}")

        tts_url = os.getenv("KOKORO_TTS_URL", "http://kokoro-gpu:8880/v1")
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{tts_url}/audio/speech",
                json={
                    "model": "kokoro",
                    "input": request.text,
                    "voice": voice,
                    "speed": speed,
                    "response_format": "wav",
                },
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(
                        f"TTS failed ({resp.status}): {await resp.text()}"
                    )
                async with aiofiles.open(audio_path, "wb") as f:
                    await f.write(await resp.read())
    else:
        raise ValueError("Either text or audio_url must be provided")

    return audio_path


# ── MuseTalk inference ────────────────────────────────────────────────────────


async def _unload_ollama_models():
    """
    Ask Ollama to evict all loaded models from VRAM before we run inference.
    This is important on RTX 3060 (12 GB) because Kokoro + Whisper + an active
    Ollama model can already consume ~5.8 GB, leaving MuseTalk starved.
    Failures are non-fatal — we log and continue.
    """
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama-gpu:11434")
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ollama_url}/api/ps") as resp:
                if resp.status != 200:
                    print(
                        f"[musetalk] Ollama /api/ps returned {resp.status} — skipping unload"
                    )
                    return
                data = await resp.json()
                loaded = [
                    m.get("name", "") for m in data.get("models", []) if m.get("name")
                ]

        if not loaded:
            print("[musetalk] No Ollama models loaded — nothing to unload")
            return

        async with aiohttp.ClientSession() as session:
            for name in loaded:
                try:
                    await session.post(
                        f"{ollama_url}/api/generate",
                        json={"model": name, "keep_alive": 0},
                    )
                    print(f"[musetalk] Unloaded Ollama model: {name}")
                except Exception as e:
                    print(f"[musetalk] Failed to unload {name}: {e}")

    except Exception as e:
        print(
            f"[musetalk] Could not reach Ollama ({ollama_url}): {e} — continuing anyway"
        )


async def _run_musetalk(job_id: str, audio_file: Path, request: VideoRequest):
    """
    Build the inference YAML config and call MuseTalk's scripts.inference module.

    Output layout  (using avatar_id sub-dir so coords.pkl is reused across jobs):
      /app/output_jobs/{avatar_id}/{job_id}/output.mp4
      /app/output_jobs/{avatar_id}/avatar.pkl          ← reused on next run
    """
    avatar_id = request.avatar_id
    avatar_img = _find_avatar_source(avatar_id)
    # coords are stored one level above the job dir, keyed by avatar_id
    avatar_result_dir = OUTPUT_DIR / avatar_id / job_id
    avatar_result_dir.mkdir(parents=True, exist_ok=True)

    coords_pkl = OUTPUT_DIR / avatar_id / "avatar.pkl"
    use_saved = coords_pkl.exists()

    # Write per-job YAML config expected by scripts.inference
    cfg_path = INPUT_DIR / f"{job_id}.yaml"
    cfg = {"task_0": {"video_path": str(avatar_img), "audio_path": str(audio_file)}}
    with open(cfg_path, "w") as f:
        yaml.dump(cfg, f)

    cmd = [
        "python",
        "-m",
        "scripts.inference",
        "--inference_config",
        str(cfg_path),
        "--result_dir",
        str(avatar_result_dir),
        "--unet_model_path",
        UNET_PATH,
        "--unet_config",
        UNET_CONFIG,
        "--whisper_dir",
        WHISPER_DIR,
        "--version",
        "v15",
        "--batch_size",
        str(request.batch_size),
        "--fps",
        str(request.fps),
        "--use_float16",
        "--saved_coord",  # always save coords for reuse
    ]
    if use_saved:
        cmd.append("--use_saved_coord")
        print(f"[musetalk] Using cached coords: {coords_pkl}")
    else:
        print(
            f"[musetalk] First run for '{avatar_id}' — computing face coords (will be cached)"
        )

    env = os.environ.copy()
    env["PYTHONPATH"] = "/app"
    # Note: PYTORCH_CUDA_ALLOC_CONF=expandable_segments is PyTorch ≥2.1 only.
    # This container uses PyTorch 2.0.1 (required for mmcv cu118 wheel), so we omit it.

    # Free VRAM held by Ollama before launching GPU-heavy inference
    await _unload_ollama_models()

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="/app",
        env=env,
    )
    stdout, stderr = await process.communicate()
    if stdout:
        print(stdout.decode())
    if process.returncode != 0:
        raise RuntimeError(f"MuseTalk inference failed:\n{stderr.decode()}")

    # MuseTalk writes the final video as {result_dir}/{task_0}/output.mp4
    # or directly as {result_dir}/output.mp4 — find and normalise to output.mp4
    produced = list(avatar_result_dir.rglob("*.mp4"))
    if not produced:
        raise RuntimeError(
            f"No .mp4 found under {avatar_result_dir}\nSTDERR: {stderr.decode()}"
        )

    final_mp4 = avatar_result_dir / "output.mp4"
    if produced[0] != final_mp4:
        produced[0].rename(final_mp4)

    # Clean up temp files
    if cfg_path.exists():
        cfg_path.unlink()
    audio_file.unlink(missing_ok=True)

    print(f"[musetalk] Output: {final_mp4}")


# ── Helpers ───────────────────────────────────────────────────────────────────


def _find_avatar_source(avatar_id: str) -> Path:
    """
    Return the avatar source file for this avatar_id.
    MP4 video is preferred over static images — MuseTalk handles both natively.
    Priority: avatar.mp4 > avatar.png > avatar.jpg > avatar.jpeg
    """
    avatar_path = AVATARS_DIR / avatar_id
    for name in ["avatar.mp4", "avatar.png", "avatar.jpg", "avatar.jpeg"]:
        candidate = avatar_path / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No avatar source found in {avatar_path}. "
        f"Upload avatar.mp4 (or avatar.png) via /upload-avatar."
    )


def _models_ready() -> bool:
    return (
        Path(UNET_PATH).exists()
        and Path(UNET_CONFIG).exists()
        and Path(WHISPER_DIR, "pytorch_model.bin").exists()
    )


def _list_avatars() -> list:
    if not AVATARS_DIR.exists():
        return []
    return [d.name for d in AVATARS_DIR.iterdir() if d.is_dir()]


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8011)
