# LiveTalking Avatar Video Generator

Batch video generation service for creating virtual avatar/VTuber videos with lip-sync.

## Features

- 🎭 **Multiple Avatar Types**: Realistic humans, anime characters, custom 3D models
- 🗣️ **Text-to-Video**: Input text → Generate avatar speaking video
- 🎵 **Audio-to-Video**: Input audio → Generate lip-synced avatar video
- 🎨 **Custom Backgrounds**: Add backgrounds, effects, and branding
- 📹 **High Quality**: 1080p, 720p, or custom resolutions
- 🚀 **Fast Processing**: GPU-accelerated inference
- 🔌 **API-First**: RESTful API for easy integration

## Quick Start

### 1. Download Models

```bash
# Download wav2lip model from:
# https://pan.quark.cn/s/83a750323ef0
# Or Google Drive: https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ

# Place in: ./models/wav2lip.pth
```

### 2. Add Avatar

Create an avatar folder:

```bash
mkdir -p data/avatars/my-avatar
# Add your avatar image or video:
# - data/avatars/my-avatar/avatar.jpg (or .png)
# - data/avatars/my-avatar/avatar.mp4 (optional video loop)
```

### 3. Start Service

```bash
# From main project directory
docker compose --profile avatar up livetalking
```

### 4. Generate Video

```bash
# Using curl
curl -X POST http://localhost:8010/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! Welcome to my channel. Today we will discuss AI.",
    "avatar_id": "my-avatar",
    "model": "wav2lip",
    "voice": "af_heart",
    "resolution": "1280x720"
  }'

# Response: {"job_id": "abc-123", "status": "pending"}

# Check status
curl http://localhost:8010/job/abc-123

# Download when complete
curl http://localhost:8010/download/abc-123 -o video.mp4
```

## API Documentation

### Generate Video

**POST** `/generate`

```json
{
  "text": "Script text to speak",           // Optional if audio_url provided
  "audio_url": "http://example.com/audio.wav",  // Optional if text provided
  "avatar_id": "my-avatar",                // Avatar folder name
  "model": "wav2lip",                      // wav2lip, musetalk, ernerf
  "voice": "af_heart",                     // Kokoro TTS voice
  "background": "http://example.com/bg.jpg", // Optional background
  "resolution": "1280x720",                // 1920x1080, 1280x720, 854x480
  "fps": 25                                // Frame rate
}
```

### Check Job Status

**GET** `/job/{job_id}`

```json
{
  "job_id": "abc-123",
  "status": "completed",  // pending, processing, completed, failed
  "progress": 100,
  "video_url": "/download/abc-123",
  "error": null
}
```

### Download Video

**GET** `/download/{job_id}`

Returns MP4 video file.

### Upload Custom Avatar

**POST** `/upload-avatar`

```bash
curl -X POST http://localhost:8010/upload-avatar \
  -F "file=@avatar.jpg" \
  -F "avatar_id=my-new-avatar"
```

### List Available Models

**GET** `/models`

```json
{
  "models": ["wav2lip", "musetalk"],
  "avatars": ["default", "my-avatar", "anime-girl"]
}
```

## Avatar Types

### 1. Realistic Human (Photo)

Best for: Professional content, news, education

```
data/avatars/professional/
  └── avatar.jpg  (headshot photo, 512x512 or higher)
```

### 2. Anime/VTuber Character

Best for: Gaming, entertainment, casual content

```
data/avatars/anime-girl/
  └── avatar.png  (character portrait with transparency)
```

### 3. Video Loop Avatar

Best for: Dynamic backgrounds, full-body shots

```
data/avatars/full-body/
  └── avatar.mp4  (5-10 second loop of person in neutral pose)
```

## Integration with n8n

Create automated video workflows:

1. **Content Pipeline**: 
   - Trigger: New blog post published
   - Action: Generate summary → TTS → Avatar video
   - Output: Upload to YouTube

2. **Social Media Bot**:
   - Trigger: Scheduled daily
   - Action: Generate news summary → Avatar presents it
   - Output: Post to Twitter/TikTok

3. **Customer Support**:
   - Trigger: FAQ question
   - Action: Generate answer → Avatar explains
   - Output: Send video response

See `../n8n/workflows/avatar-video-generator.json` for examples.

## Performance

| GPU Model | Model | Resolution | FPS | Processing Time (1 min audio) |
|-----------|-------|------------|-----|-------------------------------|
| RTX 3060  | wav2lip | 720p | 60 | ~30 seconds |
| RTX 3080Ti | wav2lip | 1080p | 120 | ~15 seconds |
| RTX 4090  | musetalk | 1080p | 72 | ~20 seconds |

## Troubleshooting

### Model not found
```bash
# Check models directory
docker exec livetalking ls -la /app/models

# Download models manually
docker exec livetalking bash /app/download-models.sh
```

### GPU not detected
```bash
# Check GPU access
docker exec livetalking nvidia-smi

# Verify CUDA
docker exec livetalking python -c "import torch; print(torch.cuda.is_available())"
```

### Poor lip-sync quality
- Use higher quality avatar images (1024x1024+)
- Ensure clear audio with minimal background noise
- Try different models (musetalk for better quality)

## Advanced Usage

### Custom Voice Cloning

```bash
# Upload voice sample
curl -X POST http://kokoro-gpu:8880/v1/voices \
  -F "file=@voice-sample.wav" \
  -F "voice_id=my-voice"

# Use in video generation
curl -X POST http://localhost:8010/generate \
  -d '{"text": "...", "voice": "my-voice"}'
```

### Batch Processing

```python
import requests
import time

scripts = [
    "Welcome to episode 1",
    "Welcome to episode 2",
    "Welcome to episode 3"
]

jobs = []
for i, script in enumerate(scripts):
    resp = requests.post("http://localhost:8010/generate", json={
        "text": script,
        "avatar_id": "my-avatar",
        "model": "wav2lip"
    })
    jobs.append(resp.json()["job_id"])

# Wait for completion
for job_id in jobs:
    while True:
        status = requests.get(f"http://localhost:8010/job/{job_id}").json()
        if status["status"] == "completed":
            # Download video
            video = requests.get(f"http://localhost:8010/download/{job_id}")
            with open(f"video_{job_id}.mp4", "wb") as f:
                f.write(video.content)
            break
        time.sleep(5)
```

## Resources

- [LiveTalking GitHub](https://github.com/lipku/LiveTalking)
- [Model Downloads](https://pan.quark.cn/s/83a750323ef0)
- [Documentation](https://livetalking-doc.readthedocs.io/)
- [Community Forum](https://github.com/lipku/LiveTalking/discussions)

## License

This integration follows the LiveTalking Apache 2.0 license.
Videos must include LiveTalking watermark when published publicly.
