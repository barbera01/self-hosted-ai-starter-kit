# Virtual Avatar/VTuber Video Generator Setup

Complete guide to setting up LiveTalking for creating virtual presenter videos.

## Overview

This integration adds **LiveTalking** to your AI starter kit, enabling you to create:

- 📹 **Virtual Presenter Videos** - Professional talking head videos
- 🎭 **VTuber Content** - Anime/cartoon character videos  
- 🎬 **Automated Video Production** - Text → Video pipeline
- 🗣️ **Multi-language Content** - Using Kokoro TTS voices

## What You Get

### Input Options
1. **Text Script** → Auto-generate voice → Video
2. **Audio File** → Lip-sync to existing audio → Video
3. **n8n Workflow** → Automated batch processing

### Avatar Types
1. **Realistic Human** - Photo-realistic talking heads
2. **Anime/VTuber** - 2D/3D animated characters
3. **Custom Avatars** - Upload your own images/videos

### Output
- High-quality MP4 videos (720p, 1080p)
- Ready for YouTube, TikTok, Instagram
- Customizable backgrounds and effects

## Quick Start (5 Minutes)

### Step 1: Download Models

```bash
# Download wav2lip model (required)
# Option A: Quark Cloud Drive
# Visit: https://pan.quark.cn/s/83a750323ef0
# Download: wav2lip256.pth

# Option B: Google Drive  
# Visit: https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ
# Download: wav2lip256.pth

# Place the file in:
mkdir -p ./livetalking-data/models
# Copy wav2lip256.pth to ./livetalking-data/models/wav2lip.pth
```

### Step 2: Create Your First Avatar

```bash
# Create avatar directory
mkdir -p ./livetalking-data/avatars/my-first-avatar

# Add an avatar image (option 1: use your photo)
# - Take a clear headshot photo (face forward, neutral expression)
# - Save as: ./livetalking-data/avatars/my-first-avatar/avatar.jpg

# OR download sample avatars from:
# https://pan.quark.cn/s/83a750323ef0
# Extract to: ./livetalking-data/avatars/
```

### Step 3: Start the Service

```bash
# Make sure you have .env configured
cp .env.example .env
# Edit .env and set LIVETALKING_DOMAIN if needed

# Start LiveTalking (with avatar profile)
docker compose --profile avatar up livetalking -d

# Check logs
docker compose logs -f livetalking

# Wait for "Application startup complete" message
```

### Step 4: Generate Your First Video

```bash
# Test the API
curl -X POST http://localhost:8010/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! This is my first virtual avatar video. Pretty cool, right?",
    "avatar_id": "my-first-avatar",
    "model": "wav2lip",
    "voice": "af_heart",
    "resolution": "1280x720"
  }'

# You'll get a response like:
# {"job_id": "abc-123-def-456", "status": "pending"}

# Check status (repeat until completed)
curl http://localhost:8010/job/abc-123-def-456

# Download video when complete
curl http://localhost:8010/download/abc-123-def-456 -o my-first-video.mp4

# Open the video!
open my-first-video.mp4  # macOS
# or: xdg-open my-first-video.mp4  # Linux
```

## Detailed Setup

### Avatar Creation Guide

#### Option 1: Realistic Human Avatar (Photo)

**Best for:** Professional content, education, business

```bash
# Requirements:
# - Clear headshot photo (512x512 or larger)
# - Face forward, neutral expression
# - Good lighting, plain background
# - JPG or PNG format

# Create avatar
mkdir -p ./livetalking-data/avatars/professional
cp your-photo.jpg ./livetalking-data/avatars/professional/avatar.jpg
```

**Tips for best results:**
- Use high-resolution images (1024x1024 recommended)
- Ensure face is well-lit and in focus
- Avoid extreme angles or expressions
- Plain background works best

#### Option 2: Anime/VTuber Character

**Best for:** Gaming, entertainment, casual content

```bash
# Requirements:
# - Character portrait (PNG with transparency preferred)
# - Face clearly visible
# - Anime/cartoon style

# Create avatar
mkdir -p ./livetalking-data/avatars/anime-character
cp character.png ./livetalking-data/avatars/anime-character/avatar.png
```

**Where to get anime avatars:**
- Generate with ComfyUI/Automatic1111 (already in your stack!)
- Commission from artists
- Use royalty-free character designs
- Download from LiveTalking community

#### Option 3: Video Loop Avatar

**Best for:** Dynamic backgrounds, full-body shots

```bash
# Requirements:
# - 5-10 second video loop
# - Person in neutral pose
# - Minimal movement
# - MP4 format

# Create avatar
mkdir -p ./livetalking-data/avatars/full-body
cp video-loop.mp4 ./livetalking-data/avatars/full-body/avatar.mp4
```

### Voice Selection

Your stack includes **Kokoro TTS** with multiple voices:

```python
# Available voices:
voices = [
    "af_heart",      # Female, warm and friendly
    "af_bella",      # Female, professional
    "af_sarah",      # Female, energetic
    "am_adam",       # Male, deep and authoritative
    "am_michael",    # Male, friendly
    "bf_emma",       # British Female
    "bm_george",     # British Male
]

# Use in API call:
{
  "text": "Your script here",
  "voice": "af_heart"  # Choose voice
}
```

### Resolution & Quality Settings

```python
# Resolution options:
resolutions = {
    "1920x1080": "Full HD (best quality, slower)",
    "1280x720":  "HD (balanced, recommended)",
    "854x480":   "SD (fast, smaller files)",
}

# FPS options:
fps_options = {
    25: "Standard (recommended)",
    30: "Smooth (larger files)",
    24: "Cinematic"
}

# Example API call:
{
  "text": "Your script",
  "resolution": "1280x720",
  "fps": 25
}
```

## Integration with Existing Services

### Using ComfyUI to Generate Avatars

```bash
# 1. Generate character image in ComfyUI (http://localhost:8188)
# 2. Download the generated image
# 3. Upload as avatar:

curl -X POST http://localhost:8010/upload-avatar \
  -F "file=@generated-character.png" \
  -F "avatar_id=comfyui-character"

# 4. Use in video generation:
curl -X POST http://localhost:8010/generate \
  -d '{"text": "...", "avatar_id": "comfyui-character"}'
```

### Using Ollama for Script Generation

```bash
# Generate script with Ollama
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.3",
  "prompt": "Write a 30-second YouTube intro script about AI",
  "stream": false
}'

# Use the generated script in video:
# (Extract the response text and pass to LiveTalking)
```

### n8n Automation Workflows

Import the workflow: `n8n/workflows/avatar-video-generator.json`

**Example workflows:**

1. **Daily News Video**
   - Trigger: Schedule (daily at 9 AM)
   - Fetch: Latest news from RSS
   - Generate: Summary with Ollama
   - Create: Avatar video
   - Upload: To YouTube

2. **Blog Post to Video**
   - Trigger: New blog post webhook
   - Extract: Article content
   - Summarize: With Ollama
   - Generate: Avatar reading summary
   - Post: To social media

3. **FAQ Video Generator**
   - Trigger: Manual/API
   - Input: List of FAQs
   - Loop: Each question
   - Generate: Avatar answering
   - Combine: All videos into series

## API Reference

### Generate Video

**POST** `/generate`

```json
{
  "text": "Script text (optional if audio_url provided)",
  "audio_url": "http://example.com/audio.wav (optional if text provided)",
  "avatar_id": "my-avatar",
  "model": "wav2lip",
  "voice": "af_heart",
  "background": "http://example.com/bg.jpg (optional)",
  "resolution": "1280x720",
  "fps": 25
}
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "pending"
}
```

### Check Job Status

**GET** `/job/{job_id}`

```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "progress": 100,
  "video_url": "/download/abc-123-def-456",
  "error": null
}
```

Status values: `pending`, `processing`, `completed`, `failed`

### Download Video

**GET** `/download/{job_id}`

Returns MP4 file.

### Upload Avatar

**POST** `/upload-avatar`

Form data:
- `file`: Image or video file
- `avatar_id`: Unique identifier

### List Resources

**GET** `/models`

```json
{
  "models": ["wav2lip", "musetalk"],
  "avatars": ["default", "my-avatar", "anime-girl"]
}
```

## Production Tips

### Batch Processing

```python
import requests
import time

# Generate multiple videos
scripts = [
    "Episode 1: Introduction to AI",
    "Episode 2: Machine Learning Basics",
    "Episode 3: Neural Networks Explained"
]

for i, script in enumerate(scripts):
    # Generate video
    resp = requests.post("http://localhost:8010/generate", json={
        "text": script,
        "avatar_id": "my-avatar",
        "voice": "af_heart",
        "resolution": "1920x1080"
    })
    
    job_id = resp.json()["job_id"]
    
    # Wait for completion
    while True:
        status = requests.get(f"http://localhost:8010/job/{job_id}").json()
        if status["status"] == "completed":
            # Download
            video = requests.get(f"http://localhost:8010/download/{job_id}")
            with open(f"episode_{i+1}.mp4", "wb") as f:
                f.write(video.content)
            break
        elif status["status"] == "failed":
            print(f"Failed: {status['error']}")
            break
        time.sleep(5)
```

### GPU Resource Management

LiveTalking shares GPU with other services. To optimize:

```yaml
# In docker-compose.yml, adjust memory limits:
livetalking:
  deploy:
    resources:
      limits:
        memory: 8G  # Increase if you have more RAM
```

**Tips:**
- Stop other GPU services when batch processing
- Use `docker compose --profile avatar up` to run only avatar services
- Monitor GPU usage: `docker exec livetalking nvidia-smi`

### Storage Management

Videos can be large. Clean up old jobs:

```bash
# Delete old videos (older than 7 days)
find ./livetalking-data/output -name "*.mp4" -mtime +7 -delete

# Or use API:
curl -X DELETE http://localhost:8010/job/{job_id}
```

## Troubleshooting

### Model Not Found

```bash
# Check if model exists
docker exec livetalking ls -la /app/models

# Should show: wav2lip.pth

# If missing, download and copy:
# 1. Download from https://pan.quark.cn/s/83a750323ef0
# 2. Copy to ./livetalking-data/models/wav2lip.pth
# 3. Restart: docker compose restart livetalking
```

### Avatar Not Found

```bash
# List available avatars
curl http://localhost:8010/models

# Check avatar directory
docker exec livetalking ls -la /app/data/avatars

# Each avatar should have:
# avatars/my-avatar/avatar.jpg (or .png or .mp4)
```

### Poor Lip-Sync Quality

**Solutions:**
1. Use higher resolution avatar images (1024x1024+)
2. Ensure clear audio (no background noise)
3. Try different models (musetalk for better quality)
4. Check avatar image quality (well-lit, in-focus face)

### Slow Processing

**Optimizations:**
1. Reduce resolution (use 720p instead of 1080p)
2. Lower FPS (25 instead of 30)
3. Ensure GPU is being used: `docker exec livetalking nvidia-smi`
4. Stop other GPU services temporarily
5. Increase GPU memory allocation in docker-compose.yml

### GPU Out of Memory

```bash
# Check GPU usage
docker exec livetalking nvidia-smi

# Solutions:
# 1. Stop other GPU services
docker compose stop ollama-gpu comfyui automatic1111

# 2. Reduce batch size in LiveTalking
# 3. Use lower resolution
# 4. Restart Docker to clear GPU memory
docker compose restart livetalking
```

## Advanced Features

### Custom Voice Cloning

(Coming soon - requires additional setup)

### Multiple Avatars in One Video

(Coming soon - requires video editing pipeline)

### Real-time Streaming

For live streaming instead of pre-rendered videos, see:
`livetalking/README.md` for WebRTC setup.

## Resources

- **LiveTalking GitHub**: https://github.com/lipku/LiveTalking
- **Model Downloads**: https://pan.quark.cn/s/83a750323ef0
- **Documentation**: https://livetalking-doc.readthedocs.io/
- **Community**: https://github.com/lipku/LiveTalking/discussions

## Next Steps

1. ✅ Generate your first video
2. 📸 Create multiple avatars (different styles)
3. 🎬 Build n8n automation workflows
4. 🚀 Set up batch processing for content series
5. 📱 Integrate with social media APIs for auto-posting

## Support

For issues specific to this integration, open an issue in this repo.
For LiveTalking-specific questions, visit the [LiveTalking community](https://github.com/lipku/LiveTalking/discussions).
