# LivePortrait - Simple Idle Animation Generator

**One job**: Turn a static image into a loopable idle video for MuseTalk.

## What It Does

Upload an image → Get a video with natural idle movements (blinking, breathing, head nods)

Perfect for creating base videos to use with MuseTalk for talking avatars!

## Quick Start

### 1. Start the Service

```bash
docker compose --profile avatar up liveportrait -d
```

First startup takes ~10-15 minutes (downloads models).

### 2. Open the Web Interface

```bash
open http://localhost:8012
```

### 3. Create Your Idle Animation

1. **Upload** your portrait image (drag & drop or click)
2. **Select** motion type:
   - **Combined Idle** (recommended) - Blink + breathing + subtle movement
   - **Blink Only** - Just natural eye blinking
   - **Breathing** - Subtle chest/shoulder movement  
   - **Head Nod** - Gentle affirmative nod
3. **Click** "Generate Idle Animation"
4. **Wait** 30-60 seconds
5. **Download** your idle video!

## Motion Types Explained

| Motion | What It Does | Best For | Loop-Friendly |
|--------|-------------|----------|---------------|
| **Combined Idle** | Blink + breathing + micro-movements | General use, most realistic | ✅ Yes |
| **Blink Only** | Natural eye blinking | Minimal, professional look | ✅ Yes |
| **Breathing** | Subtle chest/shoulder movement | Calm, waiting state | ✅ Yes |
| **Head Nod** | Gentle affirmative nod | Showing engagement | ✅ Yes |

## Using with MuseTalk

Once you have your idle animation:

```bash
# Use it as the base video for MuseTalk
curl -X POST http://localhost:8011/api/v1/generate \
  -F "video=@idle_animation.mp4" \
  -F "audio=@speech.wav"
```

The idle animation gives your talking avatar natural movements even when not speaking!

## Tips for Best Results

### Source Images
- ✅ Use 512x512 or higher resolution
- ✅ Front-facing or slight angle
- ✅ Good lighting
- ✅ Clear face visibility
- ✅ Neutral expression works best

### Motion Selection
- **For continuous loops**: Use "Combined Idle" or "Breathing"
- **For professional/minimal**: Use "Blink Only"
- **For engagement**: Use "Head Nod"

## Troubleshooting

### Service won't start
```bash
# Check logs
docker compose logs liveportrait

# Restart
docker compose restart liveportrait
```

### Models not downloading
```bash
# Manually download
docker compose exec liveportrait /app/download-models.sh
```

### Out of memory
- Use smaller images (512x512 instead of 1024x1024)
- Restart service: `docker compose restart liveportrait`

## That's It!

No complex workflows, no API calls, no configuration files.

Just:
1. Upload image
2. Select motion
3. Get idle video
4. Use with MuseTalk

**Simple.** 🎭✨
