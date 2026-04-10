# LivePortrait - Idle Animation Generator

**Simple**: Upload image → Get idle video → Use with MuseTalk

No APIs, no workflows, no complexity. Just a web interface.

## What You Get

A simple web page where you:
1. Upload a portrait image
2. Click a button
3. Download an idle animation video (with blinking, breathing, head nods)

Perfect for creating base videos for MuseTalk talking avatars!

## Setup (One Time)

### Step 1: Get Driving Videos

Driving videos are example videos that show the motions (blinking, breathing, etc).

**Option A - Quick (Recommended)**:
```bash
cd liveportrait
./setup-driving-videos.sh
```

**Option B - Manual**:
1. Download from LivePortrait GitHub: https://github.com/KlingAIResearch/LivePortrait/tree/main/assets/examples/driving
2. Place in `./shared/liveportrait_driving/`
3. Rename to: `idle_combined.mp4`, `blink.mp4`, `breathing.mp4`, `head_nod.mp4`

### Step 2: Start the Service

```bash
docker compose --profile avatar up liveportrait -d
```

First time takes ~10-15 minutes (downloads AI models).

## Usage (Every Time)

### Open the Web Interface

```bash
open http://localhost:8012
```

Or visit: `http://localhost:8012` in your browser

### Create Idle Animation

1. **Drag & drop** your image (or click to upload)
2. **Select motion type**:
   - Combined Idle (recommended) - natural idle with blink + breathing
   - Blink Only - just eye blinking
   - Breathing - subtle chest movement
   - Head Nod - gentle nod
3. **Click "Generate"**
4. **Wait** ~30-60 seconds
5. **Download** your idle video!

### Use with MuseTalk

```bash
# Your idle video is now ready for MuseTalk!
curl -X POST http://localhost:8011/api/v1/generate \
  -F "video=@idle_animation.mp4" \
  -F "audio=@speech.wav"
```

## That's It!

No configuration files.  
No API documentation.  
No complex workflows.  

Just upload → generate → download.

## Troubleshooting

**Service won't start?**
```bash
docker compose logs liveportrait
docker compose restart liveportrait
```

**No driving videos?**
```bash
cd liveportrait
./setup-driving-videos.sh
```

**Out of memory?**
- Use smaller images (512x512)
- Restart: `docker compose restart liveportrait`

## Tips

- **Best images**: 512x512+, front-facing, good lighting, neutral expression
- **For loops**: Use "Combined Idle" or "Breathing"
- **For professional**: Use "Blink Only"
- **Processing time**: 30-60 seconds per image

---

**That's the whole guide.** Simple! 🎭✨
