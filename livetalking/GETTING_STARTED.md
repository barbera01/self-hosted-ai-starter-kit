# Getting Started - Simple Steps

From zero to video in under 10 minutes.

## Prerequisites

- Docker with GPU support installed
- NVIDIA GPU (RTX 3060 or better)

## Step-by-Step

### 1. Clone the repository
```bash
git clone https://github.com/n8n-io/self-hosted-ai-starter-kit.git
cd self-hosted-ai-starter-kit
```

### 2. Create network
```bash
docker network create aistack
```

### 3. Copy environment file
```bash
cp .env.example .env
```

### 4. Download the wav2lip model
```bash
# Visit: https://pan.quark.cn/s/83a750323ef0
# Download: wav2lip256.pth
# Then run:
mkdir -p livetalking-data/models
# Move the downloaded file to: livetalking-data/models/wav2lip.pth
```

### 5. Add your avatar image
```bash
mkdir -p livetalking-data/avatars/default
# Copy your headshot photo to: livetalking-data/avatars/default/avatar.jpg
# (Use a clear front-facing photo with neutral expression)
```

### 6. Start the services
```bash
docker compose --profile avatar up -d
```

### 7. Wait for services to be ready (~2-3 minutes)
```bash
docker compose logs -f livetalking
# Wait for: "Application startup complete"
# Press Ctrl+C to exit logs
```

### 8. Generate your first video
```bash
python livetalking/examples/generate-avatar-video.py "Hello! This is my first virtual avatar video."
```

### 9. Find your video
```bash
ls -lh avatar_video_*.mp4
# Open it: open avatar_video_*.mp4  (macOS)
# Or: xdg-open avatar_video_*.mp4  (Linux)
```

## Done! 🎉

You now have a working virtual avatar video generator.

## Quick Commands

```bash
# Generate another video
python livetalking/examples/generate-avatar-video.py "Your text here"

# Use different voice
python livetalking/examples/generate-avatar-video.py "Hello!" --voice am_adam

# High resolution
python livetalking/examples/generate-avatar-video.py "Hello!" --resolution 1920x1080

# Stop services
docker compose --profile avatar down

# Restart services
docker compose --profile avatar restart

# View logs
docker compose logs -f livetalking
```

## Troubleshooting

**Model not found?**
```bash
ls -la livetalking-data/models/wav2lip.pth
# If missing, download from: https://pan.quark.cn/s/83a750323ef0
```

**Avatar not found?**
```bash
ls -la livetalking-data/avatars/default/avatar.jpg
# Add a clear headshot photo
```

**Service not starting?**
```bash
docker compose logs livetalking
# Check for errors
```

## Next Steps

- Read full guide: `livetalking/AVATAR_SETUP.md`
- Try different avatars
- Set up n8n automation
- Create batch videos

---

**Need help?** See `livetalking/QUICKSTART_AVATAR.md` for more details.
