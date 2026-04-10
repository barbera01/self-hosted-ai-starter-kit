#!/usr/bin/env python3
"""
LivePortrait Batch Inference API
Provides a FastAPI service for portrait animation using LivePortrait
"""

import os
import sys
import json
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Add LivePortrait src to path
sys.path.insert(0, "/app/src")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LivePortrait API",
    description="Portrait animation API using LivePortrait",
    version="1.0.0",
)

# Directories
OUTPUT_DIR = Path("/app/output")
INPUT_DIR = Path("/app/input")
SOURCE_DIR = Path("/app/data/source")
DRIVING_DIR = Path("/app/data/driving")
SHARED_DIR = Path("/app/shared")

# Create directories
for dir_path in [OUTPUT_DIR, INPUT_DIR, SOURCE_DIR, DRIVING_DIR, SHARED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}

# LivePortrait inference function (lazy loaded)
liveportrait_pipeline = None


def get_pipeline():
    """Lazy load LivePortrait pipeline"""
    global liveportrait_pipeline
    if liveportrait_pipeline is None:
        logger.info("Loading LivePortrait pipeline...")
        try:
            from live_portrait_pipeline import LivePortraitPipeline
            from config.inference_config import InferenceConfig

            # Initialize configuration
            inference_cfg = InferenceConfig()
            liveportrait_pipeline = LivePortraitPipeline(inference_cfg=inference_cfg)
            logger.info("✅ LivePortrait pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LivePortrait pipeline: {e}")
            raise
    return liveportrait_pipeline


class AnimationRequest(BaseModel):
    """Request model for animation generation"""

    source_image: str = Field(..., description="Path to source image or video")
    driving_video: str = Field(
        ..., description="Path to driving video or motion template (.pkl)"
    )
    flag_relative: bool = Field(True, description="Use relative motion")
    flag_do_crop: bool = Field(True, description="Auto-crop source")
    flag_pasteback: bool = Field(True, description="Paste back to original image")
    flag_stitching: bool = Field(True, description="Enable stitching")
    driving_multiplier: float = Field(1.0, description="Driving motion multiplier")
    flag_crop_driving_video: bool = Field(False, description="Auto-crop driving video")


class JobStatus(BaseModel):
    """Job status response"""

    job_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LivePortrait API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "animate": "/api/v1/animate",
            "upload_source": "/api/v1/upload/source",
            "upload_driving": "/api/v1/upload/driving",
            "job_status": "/api/v1/job/{job_id}",
            "download": "/api/v1/download/{job_id}",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check if models are downloaded
        models_dir = Path("/app/pretrained_weights")
        models_exist = models_dir.exists() and any(models_dir.iterdir())

        return {
            "status": "healthy",
            "models_downloaded": models_exist,
            "gpu_available": os.system("nvidia-smi > /dev/null 2>&1") == 0,
        }
    except Exception as e:
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/api/v1/upload/source")
async def upload_source(file: UploadFile = File(...)):
    """Upload source image or video"""
    try:
        file_ext = Path(file.filename).suffix
        file_id = f"source_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = SOURCE_DIR / file_id

        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Source file uploaded: {file_path}")
        return {"file_id": file_id, "path": str(file_path), "size": len(content)}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload/driving")
async def upload_driving(file: UploadFile = File(...)):
    """Upload driving video or motion template"""
    try:
        file_ext = Path(file.filename).suffix
        file_id = f"driving_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = DRIVING_DIR / file_id

        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Driving file uploaded: {file_path}")
        return {"file_id": file_id, "path": str(file_path), "size": len(content)}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_animation_task(job_id: str, request: AnimationRequest):
    """Background task to run animation"""
    try:
        jobs[job_id]["status"] = "processing"
        logger.info(f"Starting animation job {job_id}")

        # Get pipeline
        pipeline = get_pipeline()

        # Prepare arguments
        args = {
            "source": request.source_image,
            "driving": request.driving_video,
            "flag_relative": request.flag_relative,
            "flag_do_crop": request.flag_do_crop,
            "flag_pasteback": request.flag_pasteback,
            "flag_stitching": request.flag_stitching,
            "driving_multiplier": request.driving_multiplier,
            "flag_crop_driving_video": request.flag_crop_driving_video,
        }

        # Generate output path
        output_filename = f"{job_id}_output.mp4"
        output_path = OUTPUT_DIR / output_filename
        args["output"] = str(output_path)

        # Run inference
        logger.info(f"Running LivePortrait inference for job {job_id}")

        # This is a simplified version - you'll need to adapt based on LivePortrait's actual API
        # The actual implementation would call LivePortrait's inference function
        from inference import main as liveportrait_inference

        # Create a mock args object
        class Args:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        inference_args = Args(**args)
        liveportrait_inference(inference_args)

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["output_path"] = str(output_path)

        logger.info(f"✅ Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.post("/api/v1/animate", response_model=JobStatus)
async def create_animation(
    request: AnimationRequest, background_tasks: BackgroundTasks
):
    """Create a new animation job"""
    try:
        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create job record
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "request": request.dict(),
        }

        # Add background task
        background_tasks.add_task(run_animation_task, job_id, request)

        logger.info(f"Created animation job: {job_id}")
        return JobStatus(**jobs[job_id])

    except Exception as e:
        logger.error(f"Failed to create animation job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(**jobs[job_id])


@app.get("/api/v1/download/{job_id}")
async def download_result(job_id: str):
    """Download animation result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job['status']}",
        )

    output_path = Path(job["output_path"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=output_path, media_type="video/mp4", filename=output_path.name
    )


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(jobs.values()), "total": len(jobs)}


if __name__ == "__main__":
    # Download models on startup
    logger.info("Checking for pretrained models...")
    models_dir = Path("/app/pretrained_weights")

    if not models_dir.exists() or not any(models_dir.iterdir()):
        logger.info("Models not found. Running download script...")
        os.system("/app/download-models.sh")
    else:
        logger.info("✅ Models already downloaded")

    # Start server
    logger.info("Starting LivePortrait API server...")
    uvicorn.run(app, host="0.0.0.0", port=8012, log_level="info")
