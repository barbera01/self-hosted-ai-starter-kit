# LivePortrait Quick Start Guide

Get started with LivePortrait portrait animation in minutes!

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed
- At least 8GB GPU VRAM (recommended)

## Step 1: Start the Service

```bash
# Navigate to the project root
cd self-hosted-ai-starter-kit

# Start LivePortrait with the avatar profile
docker compose --profile avatar up liveportrait -d

# Check logs
docker compose logs -f liveportrait
```

The first startup will take several minutes as it:
1. Builds the Docker image (~5-10 minutes)
2. Downloads pretrained models (~2GB, 5-10 minutes depending on connection)
3. Initializes the service

## Step 2: Verify Service is Running

```bash
# Check health
curl http://localhost:8012/health

# Expected response:
# {
#   "status": "healthy",
#   "models_downloaded": true,
#   "gpu_available": true
# }
```

## Step 3: Test with Example Files

### Option A: Using the Web Interface

Open your browser and navigate to:
```
http://localhost:8012/docs
```

This opens the interactive Swagger UI where you can:
1. Upload source images
2. Upload driving videos
3. Create animation jobs
4. Download results

### Option B: Using Command Line

```bash
# 1. Upload a source portrait
curl -X POST http://localhost:8012/api/v1/upload/source \
  -F "file=@/path/to/your/portrait.jpg" \
  > source_response.json

# Extract the path
SOURCE_PATH=$(cat source_response.json | jq -r '.path')

# 2. Upload a driving video
curl -X POST http://localhost:8012/api/v1/upload/driving \
  -F "file=@/path/to/your/driving.mp4" \
  > driving_response.json

# Extract the path
DRIVING_PATH=$(cat driving_response.json | jq -r '.path')

# 3. Create animation job
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d "{
    \"source_image\": \"$SOURCE_PATH\",
    \"driving_video\": \"$DRIVING_PATH\",
    \"flag_relative\": true,
    \"flag_do_crop\": true,
    \"flag_pasteback\": true,
    \"driving_multiplier\": 1.0
  }" \
  > job_response.json

# Extract job ID
JOB_ID=$(cat job_response.json | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# 4. Check job status (repeat until completed)
curl http://localhost:8012/api/v1/job/$JOB_ID

# 5. Download result when completed
curl -O http://localhost:8012/api/v1/download/$JOB_ID
```

## Step 4: Using with Shared Directory

You can also place files in the shared directory for easy access:

```bash
# Copy your files to shared directory
cp portrait.jpg ./shared/
cp driving.mp4 ./shared/

# Then reference them directly in the API
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "/app/shared/portrait.jpg",
    "driving_video": "/app/shared/driving.mp4",
    "flag_relative": true,
    "flag_do_crop": true,
    "flag_pasteback": true,
    "driving_multiplier": 1.0
  }'
```

## Common Use Cases

### 1. Simple Portrait Animation

Animate a static portrait with a driving video:

```bash
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "/app/shared/my_portrait.jpg",
    "driving_video": "/app/shared/expression.mp4",
    "flag_relative": true,
    "driving_multiplier": 1.0
  }'
```

### 2. Exaggerated Expressions

Increase motion intensity with `driving_multiplier`:

```bash
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "/app/shared/my_portrait.jpg",
    "driving_video": "/app/shared/expression.mp4",
    "flag_relative": true,
    "driving_multiplier": 1.5
  }'
```

### 3. Video-to-Video Editing

Transform a portrait video with new expressions:

```bash
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "/app/shared/my_video.mp4",
    "driving_video": "/app/shared/new_expression.mp4",
    "flag_relative": true,
    "flag_pasteback": true
  }'
```

## Tips for Best Results

### Source Images/Videos
- Use high-quality portraits (512x512 or higher)
- Ensure face is clearly visible and well-lit
- Front-facing or slight angle works best
- Neutral expression in source works best

### Driving Videos
- Use 1:1 aspect ratio (square videos)
- Focus on head/face area
- Minimize shoulder movement
- First frame should be frontal with neutral expression
- Enable `flag_crop_driving_video: true` for auto-cropping

### Performance Optimization
- Use smaller resolutions (256x256) for faster processing
- Keep driving videos short (5-10 seconds)
- Process one job at a time for best performance

## Monitoring and Logs

```bash
# View real-time logs
docker compose logs -f liveportrait

# Check resource usage
docker stats liveportrait

# List all jobs
curl http://localhost:8012/api/v1/jobs
```

## Stopping the Service

```bash
# Stop LivePortrait
docker compose stop liveportrait

# Stop and remove
docker compose down liveportrait

# Stop all avatar services
docker compose --profile avatar down
```

## Troubleshooting

### Service won't start
```bash
# Check logs for errors
docker compose logs liveportrait

# Rebuild the image
docker compose build --no-cache liveportrait
docker compose up liveportrait -d
```

### Models not downloading
```bash
# Manually trigger download
docker compose exec liveportrait /app/download-models.sh

# Check HuggingFace token
docker compose exec liveportrait env | grep HF_TOKEN
```

### Out of memory
```bash
# Check GPU memory
nvidia-smi

# Reduce memory usage by processing smaller images
# or increase memory limit in docker-compose.yml
```

## Next Steps

- Read the full [README.md](README.md) for detailed API documentation
- Explore the [Swagger UI](http://localhost:8012/docs) for interactive API testing
- Check out example workflows in the `examples/` directory
- Integrate with n8n for automated workflows

## Getting Help

- Check the [troubleshooting section](README.md#troubleshooting) in README
- View service logs: `docker compose logs liveportrait`
- Visit the [LivePortrait repository](https://github.com/KlingAIResearch/LivePortrait)
- Check the [project homepage](https://liveportrait.github.io)

Happy animating! 🎭✨
