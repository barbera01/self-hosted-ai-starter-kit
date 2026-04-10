# LivePortrait Integration

LivePortrait is an efficient portrait animation system that brings portraits to life with stitching and retargeting control. This integration provides a FastAPI-based service for animating portraits using driving videos or motion templates.

## Features

- 🎭 **Portrait Animation**: Animate static portraits using driving videos
- 🎬 **Video-to-Video**: Transform portrait videos with new expressions
- 🎯 **Motion Templates**: Use pre-recorded motion templates (.pkl files)
- 🔧 **Fine Control**: Adjust motion multipliers, cropping, and stitching
- 🚀 **GPU Accelerated**: Optimized for NVIDIA GPUs with CUDA 12.4
- 📡 **REST API**: Easy integration with other services via FastAPI

## Quick Start

### 1. Build and Start the Service

```bash
# Start with the avatar profile
docker compose --profile avatar up liveportrait -d

# Or build from scratch
docker compose --profile avatar build liveportrait
docker compose --profile avatar up liveportrait -d
```

### 2. Check Service Health

```bash
curl http://localhost:8012/health
```

### 3. Access the API

The LivePortrait API will be available at:
- Local: `http://localhost:8012`
- Domain: `https://${LIVEPORTRAIT_DOMAIN}` (if configured with Traefik)

## API Endpoints

### Health Check
```bash
GET /health
```

### Upload Source Image/Video
```bash
POST /api/v1/upload/source
Content-Type: multipart/form-data

# Example with curl
curl -X POST http://localhost:8012/api/v1/upload/source \
  -F "file=@/path/to/portrait.jpg"
```

### Upload Driving Video/Template
```bash
POST /api/v1/upload/driving
Content-Type: multipart/form-data

# Example with curl
curl -X POST http://localhost:8012/api/v1/upload/driving \
  -F "file=@/path/to/driving.mp4"
```

### Create Animation Job
```bash
POST /api/v1/animate
Content-Type: application/json

{
  "source_image": "/app/data/source/source_abc123.jpg",
  "driving_video": "/app/data/driving/driving_xyz789.mp4",
  "flag_relative": true,
  "flag_do_crop": true,
  "flag_pasteback": true,
  "flag_stitching": true,
  "driving_multiplier": 1.0,
  "flag_crop_driving_video": false
}
```

### Check Job Status
```bash
GET /api/v1/job/{job_id}

# Example
curl http://localhost:8012/api/v1/job/job_abc123def456
```

### Download Result
```bash
GET /api/v1/download/{job_id}

# Example
curl -O http://localhost:8012/api/v1/download/job_abc123def456
```

### List All Jobs
```bash
GET /api/v1/jobs
```

## Usage Examples

### Example 1: Animate a Portrait with a Driving Video

```bash
# 1. Upload source portrait
SOURCE_RESPONSE=$(curl -X POST http://localhost:8012/api/v1/upload/source \
  -F "file=@portrait.jpg")
SOURCE_PATH=$(echo $SOURCE_RESPONSE | jq -r '.path')

# 2. Upload driving video
DRIVING_RESPONSE=$(curl -X POST http://localhost:8012/api/v1/upload/driving \
  -F "file=@driving.mp4")
DRIVING_PATH=$(echo $DRIVING_RESPONSE | jq -r '.path')

# 3. Create animation job
JOB_RESPONSE=$(curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d "{
    \"source_image\": \"$SOURCE_PATH\",
    \"driving_video\": \"$DRIVING_PATH\",
    \"flag_relative\": true,
    \"flag_do_crop\": true,
    \"flag_pasteback\": true,
    \"driving_multiplier\": 1.0
  }")
JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')

# 4. Check status
curl http://localhost:8012/api/v1/job/$JOB_ID

# 5. Download result when completed
curl -O http://localhost:8012/api/v1/download/$JOB_ID
```

### Example 2: Using Python

```python
import requests
import time

API_URL = "http://localhost:8012"

# Upload source
with open("portrait.jpg", "rb") as f:
    source_resp = requests.post(
        f"{API_URL}/api/v1/upload/source",
        files={"file": f}
    )
source_path = source_resp.json()["path"]

# Upload driving video
with open("driving.mp4", "rb") as f:
    driving_resp = requests.post(
        f"{API_URL}/api/v1/upload/driving",
        files={"file": f}
    )
driving_path = driving_resp.json()["path"]

# Create animation job
job_resp = requests.post(
    f"{API_URL}/api/v1/animate",
    json={
        "source_image": source_path,
        "driving_video": driving_path,
        "flag_relative": True,
        "flag_do_crop": True,
        "flag_pasteback": True,
        "driving_multiplier": 1.0
    }
)
job_id = job_resp.json()["job_id"]

# Poll for completion
while True:
    status_resp = requests.get(f"{API_URL}/api/v1/job/{job_id}")
    status = status_resp.json()["status"]
    print(f"Status: {status}")
    
    if status == "completed":
        # Download result
        result = requests.get(f"{API_URL}/api/v1/download/{job_id}")
        with open(f"{job_id}_output.mp4", "wb") as f:
            f.write(result.content)
        print("Download complete!")
        break
    elif status == "failed":
        print("Job failed:", status_resp.json().get("error"))
        break
    
    time.sleep(2)
```

## Configuration Options

### Animation Parameters

- **source_image**: Path to source portrait image or video
- **driving_video**: Path to driving video or motion template (.pkl)
- **flag_relative**: Use relative motion (default: true)
- **flag_do_crop**: Auto-crop source image (default: true)
- **flag_pasteback**: Paste result back to original image (default: true)
- **flag_stitching**: Enable stitching for seamless results (default: true)
- **driving_multiplier**: Motion intensity multiplier (default: 1.0)
- **flag_crop_driving_video**: Auto-crop driving video (default: false)

### Environment Variables

Set these in your `.env` file:

```bash
# LivePortrait domain (for Traefik)
LIVEPORTRAIT_DOMAIN=liveportrait.lab.home-cloud.uk

# HuggingFace token (for model downloads)
HUGGINGFACE_TOKEN=hf_your_token_here
```

## Model Downloads

Models are automatically downloaded on first startup using the HuggingFace CLI. The download script will:

1. Check if models already exist
2. Download from HuggingFace: `KlingTeam/LivePortrait`
3. Store in the persistent volume: `liveportrait_models`

### Manual Model Download

If automatic download fails, you can manually download models:

```bash
# Option 1: Using huggingface-cli
docker compose exec liveportrait bash
huggingface-cli download KlingTeam/LivePortrait \
  --local-dir /app/pretrained_weights \
  --exclude "*.git*" "README.md" "docs"

# Option 2: Download from Google Drive
# Visit: https://drive.google.com/drive/folders/1UtKgzKjFAOmZkhNK-OYT0caJ_w2XAnib
# Extract to: ./liveportrait_models/
```

## Volumes

The service uses the following Docker volumes:

- `liveportrait_models`: Pretrained model weights (~2GB)
- `liveportrait_source`: Uploaded source images/videos
- `liveportrait_driving`: Uploaded driving videos/templates
- `liveportrait_output`: Generated animation results
- `liveportrait_input`: Additional input files
- `./shared`: Shared directory with other services

## Performance

### GPU Requirements

- **Minimum**: NVIDIA GPU with 6GB VRAM
- **Recommended**: NVIDIA GPU with 8GB+ VRAM (RTX 3060 or better)
- **CUDA**: 12.4 (compatible with 11.8+)

### Processing Times

Approximate times on RTX 4090:
- Portrait animation (256x256, 5s video): ~10-15 seconds
- Portrait animation (512x512, 5s video): ~20-30 seconds
- Video-to-video (512x512, 10s): ~40-60 seconds

## Troubleshooting

### Models Not Downloading

```bash
# Check logs
docker compose logs liveportrait

# Manually run download script
docker compose exec liveportrait /app/download-models.sh
```

### Out of Memory Errors

Reduce memory usage by:
1. Processing smaller images (256x256 instead of 512x512)
2. Using shorter driving videos
3. Increasing Docker memory limits in docker-compose.yml

### CUDA Errors

Ensure NVIDIA Docker runtime is installed:
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

## Integration with Other Services

### With n8n Workflows

LivePortrait can be integrated into n8n workflows using HTTP Request nodes:

1. Upload files using multipart/form-data
2. Create animation jobs
3. Poll for completion
4. Download results

### With Kokoro TTS

Combine with Kokoro TTS for talking avatars:
1. Generate speech with Kokoro
2. Create driving video from audio
3. Animate portrait with LivePortrait

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8012/docs`
- ReDoc: `http://localhost:8012/redoc`

## References

- **Original Repository**: https://github.com/KlingAIResearch/LivePortrait
- **Paper**: [LivePortrait: Efficient Portrait Animation with Stitching and Retargeting Control](https://arxiv.org/pdf/2407.03168)
- **Project Homepage**: https://liveportrait.github.io

## License

LivePortrait is licensed under the original project's license. Please refer to the [LivePortrait repository](https://github.com/KlingAIResearch/LivePortrait) for license details.

## Support

For issues specific to this integration, please check:
1. Docker logs: `docker compose logs liveportrait`
2. Service health: `curl http://localhost:8012/health`
3. API documentation: `http://localhost:8012/docs`

For LivePortrait-specific issues, refer to the [original repository](https://github.com/KlingAIResearch/LivePortrait).
