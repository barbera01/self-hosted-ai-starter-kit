# LivePortrait + MuseTalk Pipeline Guide

Complete guide for creating realistic talking avatars with idle animations using LivePortrait and MuseTalk.

## Overview

This pipeline combines two powerful tools:
- **LivePortrait**: Creates idle animations (blinking, breathing, head nods)
- **MuseTalk**: Adds audio-driven lip-sync and facial expressions

The result: Realistic talking avatars with natural idle movements.

## Workflow

```
Source Image/Video
       ↓
   LivePortrait (Add idle animations)
       ↓
   Idle Animation Video (loopable)
       ↓
   MuseTalk (Add audio-driven lip-sync)
       ↓
   Final Talking Avatar Video
```

## Step-by-Step Guide

### Phase 1: Prepare Your Source

#### Option A: Static Image
```bash
# Use a high-quality portrait image
# Requirements:
# - Front-facing or slight angle
# - Clear face visibility
# - Good lighting
# - Neutral expression
# - 512x512 or higher resolution

source_image="portrait.jpg"
```

#### Option B: Existing Video
```bash
# Use a short video clip
# Requirements:
# - Clear face throughout
# - Minimal movement
# - Good lighting
# - 1-5 seconds duration

source_video="portrait_clip.mp4"
```

### Phase 2: Create Idle Animation with LivePortrait

#### Quick Method: Use the Helper Script

```bash
# Start LivePortrait service
docker compose --profile avatar up liveportrait -d

# Run the idle animation creator
python liveportrait/create-idle-animation.py
```

Follow the prompts to:
1. Upload your source image/video
2. Choose motion type (blink, breathing, head_nod, idle_combined)
3. Generate loopable idle animation

#### Manual Method: Using API Directly

```bash
# 1. Upload source
SOURCE_RESPONSE=$(curl -X POST http://localhost:8012/api/v1/upload/source \
  -F "file=@portrait.jpg")
SOURCE_PATH=$(echo $SOURCE_RESPONSE | jq -r '.path')

# 2. Create idle animation (using shared directory for motion template)
curl -X POST http://localhost:8012/api/v1/animate \
  -H "Content-Type: application/json" \
  -d "{
    \"source_image\": \"$SOURCE_PATH\",
    \"driving_video\": \"/app/shared/idle_motion.mp4\",
    \"flag_relative\": true,
    \"flag_do_crop\": true,
    \"flag_pasteback\": true,
    \"flag_stitching\": true,
    \"driving_multiplier\": 0.8,
    \"flag_crop_driving_video\": false
  }" > job.json

JOB_ID=$(cat job.json | jq -r '.job_id')

# 3. Wait and download
# Check status
curl http://localhost:8012/api/v1/job/$JOB_ID

# Download when complete
curl -O http://localhost:8012/api/v1/download/$JOB_ID
```

### Phase 3: Add Audio with MuseTalk

Now use the idle animation as input to MuseTalk:

```bash
# Start MuseTalk service
docker compose --profile avatar up musetalk -d

# Use the idle animation from LivePortrait
curl -X POST http://localhost:8011/api/v1/generate \
  -F "video=@idle_animation.mp4" \
  -F "audio=@speech.wav" \
  -F "bbox_shift=0"
```

## Recommended Motion Types for Different Use Cases

### For Continuous Idle/Waiting State
```python
motion_types = ["idle_combined", "breathing", "blink"]
multiplier = 0.7 - 0.9  # Subtle, natural
```

**Use case**: Avatar waiting for user input, background video loops

### For Engaging/Active State
```python
motion_types = ["head_nod", "idle_combined"]
multiplier = 1.0 - 1.2  # More pronounced
```

**Use case**: Avatar actively listening, showing engagement

### For Minimal/Professional State
```python
motion_types = ["blink", "breathing"]
multiplier = 0.5 - 0.7  # Very subtle
```

**Use case**: Professional presentations, news anchors

## Motion Template Details

### Available Templates

| Template | Description | Duration | Loop-Friendly | Best For |
|----------|-------------|----------|---------------|----------|
| `blink` | Natural eye blinking | 2-3s | ✅ Yes | All use cases |
| `breathing` | Subtle chest/shoulder movement | 4-5s | ✅ Yes | Realistic idle |
| `head_nod` | Gentle affirmative nod | 3-4s | ✅ Yes | Engagement |
| `idle_combined` | Blink + breathing + micro-movements | 5-6s | ✅ Yes | Natural idle |
| `wink` | Playful wink | 2s | ❌ No | Special moments |

### Creating Custom Motion Templates

You can create your own motion templates:

1. **Record a driving video** with desired motions
2. **Process with LivePortrait** to extract motion
3. **Save as .pkl template** for reuse

```bash
# Example: Create custom idle motion
# 1. Record yourself doing subtle idle movements
# 2. Use LivePortrait to create template
python liveportrait/create-motion-template.py \
  --input driving_video.mp4 \
  --output custom_idle.pkl
```

## Optimization Tips

### For Best Quality

1. **Source Preparation**
   - Use high-resolution images (512x512 minimum)
   - Ensure good lighting
   - Front-facing pose works best
   - Neutral expression in source

2. **LivePortrait Settings**
   ```json
   {
     "flag_relative": true,      // Use relative motion
     "flag_do_crop": true,       // Auto-crop for best framing
     "flag_pasteback": true,     // Paste back to original
     "flag_stitching": true,     // Smooth stitching
     "driving_multiplier": 0.8   // Subtle for idle (0.5-1.0)
   }
   ```

3. **MuseTalk Settings**
   ```bash
   bbox_shift=0        # No bbox adjustment (LivePortrait already optimized)
   batch_size=8        # Balance speed/quality
   ```

### For Loopable Videos

1. **Choose loop-friendly motions**
   - blink, breathing, idle_combined

2. **Adjust duration**
   - 3-5 seconds for short loops
   - 8-10 seconds for natural loops

3. **Seamless looping**
   ```bash
   # Use ffmpeg to create seamless loop
   ffmpeg -i idle_animation.mp4 -filter_complex \
     "[0:v]split[v0][v1];[v0]trim=0:4[v0t];[v1]trim=4:5,reverse[v1r];[v0t][v1r]concat=n=2:v=1[outv]" \
     -map "[outv]" seamless_loop.mp4
   ```

### For Performance

1. **Batch Processing**
   ```python
   # Create multiple idle variations at once
   python liveportrait/create-idle-animation.py
   # Choose option 2 or 3 for batch creation
   ```

2. **Reuse Templates**
   - Create motion templates once
   - Reuse for multiple avatars
   - Store in shared directory

3. **GPU Memory Management**
   - Process one service at a time
   - Or use different GPU devices:
     ```yaml
     # docker-compose.yml
     liveportrait:
       environment:
         - CUDA_VISIBLE_DEVICES=0
     musetalk:
       environment:
         - CUDA_VISIBLE_DEVICES=0  # Same GPU, sequential
     ```

## Complete Example Workflow

### Example 1: Simple Talking Avatar

```bash
# 1. Start services
docker compose --profile avatar up liveportrait musetalk -d

# 2. Create idle animation
python liveportrait/create-idle-animation.py
# Select: portrait.jpg, idle_combined motion

# 3. Generate speech with Kokoro
curl -X POST http://localhost:8880/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kokoro",
    "input": "Hello! I am your AI assistant.",
    "voice": "af_heart"
  }' \
  --output speech.wav

# 4. Combine with MuseTalk
curl -X POST http://localhost:8011/api/v1/generate \
  -F "video=@idle_combined.mp4" \
  -F "audio=@speech.wav" \
  -F "bbox_shift=0" \
  --output talking_avatar.mp4

# 5. Done! You have a talking avatar with idle animations
```

### Example 2: Multiple Idle Variations

```bash
# Create several idle variations for variety
python liveportrait/create-idle-animation.py
# Choose option 2: Create all loop-friendly animations

# This creates:
# - idle_blink.mp4
# - idle_breathing.mp4
# - idle_head_nod.mp4
# - idle_idle_combined.mp4

# Use different ones for different contexts
# - Waiting: idle_breathing.mp4
# - Listening: idle_head_nod.mp4
# - Default: idle_idle_combined.mp4
```

### Example 3: Automated Pipeline with n8n

See `liveportrait/n8n-workflow-example.json` for a complete n8n workflow that:
1. Accepts source image upload
2. Creates idle animation with LivePortrait
3. Generates speech with Kokoro TTS
4. Combines with MuseTalk
5. Returns final talking avatar

## Troubleshooting

### Issue: Idle animation looks unnatural

**Solutions:**
- Reduce `driving_multiplier` (try 0.5-0.8)
- Use more subtle motion templates (breathing, blink)
- Ensure source has neutral expression
- Check that source is well-lit and clear

### Issue: MuseTalk doesn't sync well with idle animation

**Solutions:**
- Use `bbox_shift=0` (LivePortrait already optimized framing)
- Ensure idle animation is stable (no large movements)
- Use subtle idle motions (multiplier < 1.0)
- Check that face is clearly visible in idle animation

### Issue: Video is not loopable

**Solutions:**
- Use loop-friendly motion templates
- Create seamless loop with ffmpeg (see above)
- Keep duration short (3-5 seconds)
- Ensure motion returns to starting position

### Issue: GPU memory errors

**Solutions:**
- Process LivePortrait and MuseTalk sequentially (not simultaneously)
- Reduce video resolution
- Reduce batch size in MuseTalk
- Clear GPU memory between jobs:
  ```bash
  docker compose restart liveportrait musetalk
  ```

## Advanced Techniques

### 1. Custom Motion Blending

Combine multiple motion templates:
```python
# Create subtle idle with occasional nod
# 1. Generate base breathing animation
# 2. Generate head nod animation
# 3. Blend with ffmpeg or video editing software
```

### 2. Emotion-Specific Idle States

Create different idle animations for different emotions:
- Happy: Slight smile, more head movement (multiplier: 1.0)
- Sad: Minimal movement, slow breathing (multiplier: 0.5)
- Excited: More frequent blinking, head nods (multiplier: 1.2)

### 3. Context-Aware Switching

Use different idle animations based on context:
```python
# Pseudo-code for n8n workflow
if user_is_speaking:
    use_idle_animation("head_nod")  # Show listening
elif waiting_for_input:
    use_idle_animation("breathing")  # Calm waiting
elif processing:
    use_idle_animation("blink")  # Minimal distraction
```

## Best Practices

### ✅ Do's

- ✅ Use neutral expressions in source images
- ✅ Keep idle motions subtle (multiplier 0.5-1.0)
- ✅ Test different motion types for your use case
- ✅ Create loop-friendly animations for continuous use
- ✅ Use high-quality source images (512x512+)
- ✅ Process LivePortrait first, then MuseTalk
- ✅ Store motion templates for reuse

### ❌ Don'ts

- ❌ Don't use extreme multipliers (>1.5) for idle
- ❌ Don't combine too many motion types at once
- ❌ Don't use low-quality or blurry source images
- ❌ Don't skip the idle animation step (MuseTalk alone lacks natural idle)
- ❌ Don't process both services simultaneously (GPU memory)
- ❌ Don't use non-loop-friendly motions for continuous loops

## Performance Benchmarks

On RTX 4090:

| Task | Duration | GPU Memory |
|------|----------|------------|
| LivePortrait idle (512x512, 5s) | ~20-30s | ~4GB |
| MuseTalk lip-sync (512x512, 10s) | ~40-60s | ~6GB |
| **Total Pipeline** | ~60-90s | ~6GB peak |

## Resources

- **LivePortrait Documentation**: `liveportrait/README.md`
- **MuseTalk Documentation**: `musetalk/API_REFERENCE.md`
- **Example Scripts**: `liveportrait/create-idle-animation.py`
- **n8n Workflows**: `liveportrait/n8n-workflows/`

## Next Steps

1. **Test the pipeline** with your own images
2. **Create motion templates** for your specific use cases
3. **Build n8n workflows** for automation
4. **Experiment with settings** to find optimal quality
5. **Create a library** of idle animations for reuse

---

**Happy creating! 🎭✨**

For questions or issues, check:
- LivePortrait: `docker compose logs liveportrait`
- MuseTalk: `docker compose logs musetalk`
- API docs: http://localhost:8012/docs (LivePortrait), http://localhost:8011/docs (MuseTalk)
