# Virtual Avatar Video Generator - Quick Start

**Generate talking head videos in 3 steps!**

## Prerequisites

- ✅ Docker with GPU support
- ✅ NVIDIA GPU (RTX 3060 or better)
- ✅ 20GB free disk space
- ✅ Self-hosted AI starter kit already set up

## Step 1: Download Model (One-time, ~5 minutes)

```bash
# Download wav2lip model from one of these sources:

# Option A: Quark Cloud Drive (Recommended)
# Visit: https://pan.quark.cn/s/83a750323ef0
# Download: wav2lip256.pth

# Option B: Google Drive
# Visit: https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ
# Download: wav2lip256.pth

# Create directory and move file
mkdir -p livetalking-data/models
# Move downloaded file to: livetalking-data/models/wav2lip.pth
# (Rename from wav2lip256.pth to wav2lip.pth)
```

## Step 2: Add Avatar Image (One-time, ~2 minutes)

```bash
# Create avatar directory
mkdir -p livetalking-data/avatars/default

# Add your avatar image (choose one):

# Option A: Use your own photo
# - Take a clear headshot (face forward, neutral expression)
# - Save as: livetalking-data/avatars/default/avatar.jpg

# Option B: Download sample avatars
# Visit: https://pan.quark.cn/s/83a750323ef0
# Extract to: livetalking-data/avatars/
```

## Step 3: Start Service & Generate Video (~2 minutes)

```bash
# Start LiveTalking
docker compose --profile avatar up livetalking -d

# Wait for service to be ready (~30 seconds)
docker compose logs -f livetalking
# Look for: "Application startup complete"

# Generate your first video!
python examples/generate-avatar-video.py \
  "Hello! Welcome to my channel. Today we're going to discuss AI technology."

# Video will be saved as: avatar_video_*.mp4
```

## That's It! 🎉

You now have a working virtual avatar video generator!

## What You Can Do Now

### Generate More Videos

```bash
# Different voice
python examples/generate-avatar-video.py \
  "Hello from a male voice!" \
  --voice am_adam

# Higher resolution
python examples/generate-avatar-video.py \
  "High quality video!" \
  --resolution 1920x1080

# Custom avatar
python examples/generate-avatar-video.py \
  "Using my custom avatar!" \
  --avatar my-custom-avatar
```

### Create Multiple Avatars

```bash
# Professional presenter
mkdir -p livetalking-data/avatars/professional
cp professional-photo.jpg livetalking-data/avatars/professional/avatar.jpg

# Casual host
mkdir -p livetalking-data/avatars/casual
cp casual-photo.jpg livetalking-data/avatars/casual/avatar.jpg

# Use them
python examples/generate-avatar-video.py \
  "Professional content" \
  --avatar professional
```

### Automate with n8n

```bash
# 1. Open n8n: http://localhost:5678
# 2. Import workflow: n8n/workflows/avatar-video-generator.json
# 3. Customize and activate!
```

## Common Commands

```bash
# Check service status
docker compose ps livetalking

# View logs
docker compose logs -f livetalking

# Restart service
docker compose restart livetalking

# Stop service
docker compose stop livetalking

# List available avatars
curl http://localhost:8010/models
```

## API Quick Reference

```bash
# Generate video
curl -X POST http://localhost:8010/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your script here",
    "avatar_id": "default",
    "voice": "af_heart",
    "resolution": "1280x720"
  }'
# Returns: {"job_id": "abc-123", "status": "pending"}

# Check status
curl http://localhost:8010/job/abc-123
# Returns: {"status": "completed", "progress": 100, ...}

# Download video
curl http://localhost:8010/download/abc-123 -o video.mp4
```

## Available Voices

- **Female**: `af_heart`, `af_bella`, `af_sarah`
- **Male**: `am_adam`, `am_michael`
- **British**: `bf_emma`, `bm_george`

## Resolutions

- **1920x1080** - Full HD (best quality, slower)
- **1280x720** - HD (recommended, balanced)
- **854x480** - SD (fastest, smaller files)

## Troubleshooting

### "Model not found"
```bash
# Check if model exists
ls -la livetalking-data/models/wav2lip.pth

# If missing, download from:
# https://pan.quark.cn/s/83a750323ef0
```

### "Avatar not found"
```bash
# Check if avatar exists
ls -la livetalking-data/avatars/default/

# Should contain: avatar.jpg (or .png or .mp4)
```

### "Service not responding"
```bash
# Check if service is running
docker compose ps livetalking

# Check logs for errors
docker compose logs livetalking

# Restart service
docker compose restart livetalking
```

### "GPU not detected"
```bash
# Check GPU access
docker exec livetalking nvidia-smi

# If error, ensure nvidia-docker is installed:
# https://github.com/NVIDIA/nvidia-docker
```

## Next Steps

📖 **Full Documentation**: See `AVATAR_SETUP.md` for detailed guide  
🔧 **API Reference**: Visit http://localhost:8010/docs  
🤖 **Automation**: Import n8n workflows  
🎨 **Custom Avatars**: Use ComfyUI to generate characters  

## Need Help?

- **Setup Issues**: See `AVATAR_SETUP.md`
- **API Questions**: See `livetalking/README.md`
- **Integration Summary**: See `INTEGRATION_SUMMARY.md`
- **GitHub Issues**: Open an issue in this repository

---

**Happy creating! 🎬**
