#!/usr/bin/env python3
"""
Batch Video Generation API for LiveTalking
Simplified interface for creating pre-rendered avatar videos
"""

import os
import sys
import json
import uuid
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import asyncio
import aiofiles

app = FastAPI(title="Avatar Video Generator", version="1.0.0")

# Configuration
OUTPUT_DIR = Path("/app/output")
INPUT_DIR = Path("/app/input")
MODELS_DIR = Path("/app/models")
AVATARS_DIR = Path("/app/data/avatars")
SHARED_DIR = Path("/app/shared")

# Ensure directories exist
for directory in [OUTPUT_DIR, INPUT_DIR, MODELS_DIR, AVATARS_DIR, SHARED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class VideoRequest(BaseModel):
    """Request model for video generation"""

    text: Optional[str] = None
    audio_url: Optional[str] = None
    avatar_id: str = "default"
    model: str = "wav2lip"  # wav2lip, musetalk, ernerf
    voice: str = "af_heart"  # Kokoro voice
    background: Optional[str] = None
    resolution: str = "1280x720"  # 1920x1080, 1280x720, 854x480
    fps: int = 25


class JobStatus(BaseModel):
    """Job status response"""

    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    video_url: Optional[str] = None
    error: Optional[str] = None


# In-memory job tracking (use Redis/DB for production)
jobs: Dict[str, JobStatus] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_available": list_available_models(),
        "avatars_available": list_available_avatars(),
    }


@app.get("/models")
async def list_models():
    """List available avatar models"""
    return {"models": list_available_models(), "avatars": list_available_avatars()}


@app.post("/generate")
async def generate_video(request: VideoRequest):
    """
    Generate avatar video from text or audio

    Workflow:
    1. If text provided: Generate audio via TTS (Kokoro)
    2. Load avatar and model
    3. Generate lip-synced video
    4. Apply background/effects if requested
    5. Return video file
    """
    job_id = str(uuid.uuid4())

    # Initialize job
    jobs[job_id] = JobStatus(job_id=job_id, status="pending", progress=0)

    # Start background processing
    asyncio.create_task(process_video_job(job_id, request))

    return {"job_id": job_id, "status": "pending"}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and download URL when complete"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download generated video"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(status_code=400, detail=f"Job status: {job.status}")

    video_path = OUTPUT_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=video_path, media_type="video/mp4", filename=f"avatar_{job_id}.mp4"
    )


@app.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), avatar_id: str = Form(...)):
    """Upload custom avatar image or video"""
    avatar_path = AVATARS_DIR / avatar_id
    avatar_path.mkdir(parents=True, exist_ok=True)

    file_extension = Path(file.filename).suffix
    save_path = avatar_path / f"avatar{file_extension}"

    async with aiofiles.open(save_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {
        "avatar_id": avatar_id,
        "file": str(save_path),
        "message": "Avatar uploaded successfully",
    }


@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job and associated files"""
    if job_id in jobs:
        # Delete video file
        video_path = OUTPUT_DIR / f"{job_id}.mp4"
        if video_path.exists():
            video_path.unlink()

        # Delete job record
        del jobs[job_id]
        return {"message": "Job deleted"}

    raise HTTPException(status_code=404, detail="Job not found")


# Helper functions


def list_available_models() -> list:
    """List available lip-sync models"""
    models = []
    if (MODELS_DIR / "wav2lip.pth").exists():
        models.append("wav2lip")
    if (MODELS_DIR / "musetalk").exists():
        models.append("musetalk")
    if (MODELS_DIR / "ernerf").exists():
        models.append("ernerf")
    return models


def list_available_avatars() -> list:
    """List available avatar IDs"""
    if not AVATARS_DIR.exists():
        return []
    return [d.name for d in AVATARS_DIR.iterdir() if d.is_dir()]


async def process_video_job(job_id: str, request: VideoRequest):
    """Background task to process video generation"""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10

        # Step 1: Generate or download audio
        audio_file = await get_audio(job_id, request)
        jobs[job_id].progress = 30

        # Step 2: Run LiveTalking inference
        video_file = await run_livetalking_inference(
            job_id=job_id,
            audio_file=audio_file,
            avatar_id=request.avatar_id,
            model=request.model,
        )
        jobs[job_id].progress = 80

        # Step 3: Post-processing (background, resolution, etc.)
        final_video = await post_process_video(
            video_file=video_file,
            background=request.background,
            resolution=request.resolution,
            fps=request.fps,
        )
        jobs[job_id].progress = 100

        # Update job status
        jobs[job_id].status = "completed"
        jobs[job_id].video_url = f"/download/{job_id}"

    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
        print(f"Job {job_id} failed: {e}")


async def get_audio(job_id: str, request: VideoRequest) -> Path:
    """Get audio file from text (TTS) or URL"""
    audio_path = INPUT_DIR / f"{job_id}.wav"

    if request.audio_url:
        # Download audio from URL
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(request.audio_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(audio_path, "wb") as f:
                        await f.write(await resp.read())

    elif request.text:
        # Generate audio via Kokoro TTS
        tts_url = os.getenv("KOKORO_TTS_URL", "http://kokoro-gpu:8880/v1")

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{tts_url}/audio/speech",
                json={
                    "model": "kokoro",
                    "input": request.text,
                    "voice": request.voice,
                    "response_format": "wav",
                },
            ) as resp:
                if resp.status == 200:
                    async with aiofiles.open(audio_path, "wb") as f:
                        await f.write(await resp.read())
                else:
                    raise Exception(f"TTS failed: {await resp.text()}")
    else:
        raise ValueError("Either text or audio_url must be provided")

    return audio_path


async def run_livetalking_inference(
    job_id: str, audio_file: Path, avatar_id: str, model: str
) -> Path:
    """Run LiveTalking inference to generate lip-synced video"""
    output_file = OUTPUT_DIR / f"{job_id}_raw.mp4"
    avatar_path = AVATARS_DIR / avatar_id

    # Build command based on model type
    if model == "wav2lip":
        cmd = [
            "python",
            "inference.py",
            "--driven_audio",
            str(audio_file),
            "--source_image",
            str(avatar_path / "avatar.jpg"),  # or avatar.mp4
            "--result_dir",
            str(OUTPUT_DIR),
            "--checkpoint_dir",
            str(MODELS_DIR),
            "--output",
            str(output_file),
        ]
    else:
        # Add support for other models (musetalk, ernerf)
        raise NotImplementedError(f"Model {model} not yet implemented")

    # Run inference
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Inference failed: {stderr.decode()}")

    return output_file


async def post_process_video(
    video_file: Path, background: Optional[str], resolution: str, fps: int
) -> Path:
    """Post-process video: add background, adjust resolution, etc."""
    output_file = OUTPUT_DIR / f"{video_file.stem.replace('_raw', '')}.mp4"

    # Build ffmpeg command
    width, height = resolution.split("x")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_file),
        "-vf",
        f"scale={width}:{height}",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(output_file),
    ]

    # TODO: Add background compositing if background is provided

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    await process.communicate()

    # Clean up raw video
    if video_file.exists():
        video_file.unlink()

    return output_file


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)
