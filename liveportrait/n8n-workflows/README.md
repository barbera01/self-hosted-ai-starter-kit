# n8n Workflows for LivePortrait + MuseTalk

This directory contains example n8n workflows for creating talking avatars with idle animations.

## Available Workflows

### 1. Simple Idle Animation Creator
**File**: `idle-animation-creator.json`

Creates idle animations from uploaded images using LivePortrait.

**Features:**
- Upload source image via webhook
- Select motion type (blink, breathing, head_nod, idle_combined)
- Adjust motion multiplier
- Download result

**Endpoints:**
- POST `/webhook/create-idle` - Create idle animation

### 2. Complete Talking Avatar Pipeline
**File**: `talking-avatar-pipeline.json`

Full pipeline: Image → Idle Animation → Speech → Talking Avatar

**Features:**
- Upload source image
- Generate idle animation with LivePortrait
- Generate speech with Kokoro TTS
- Combine with MuseTalk for lip-sync
- Return final talking avatar video

**Endpoints:**
- POST `/webhook/talking-avatar` - Create talking avatar

### 3. Batch Idle Animation Generator
**File**: `batch-idle-generator.json`

Creates multiple idle animation variations from one source.

**Features:**
- Upload one source image
- Generate all loop-friendly idle animations
- Return ZIP file with all variations

**Endpoints:**
- POST `/webhook/batch-idle` - Generate batch idle animations

## How to Import

1. Open n8n (http://localhost:5678)
2. Click "Workflows" → "Import from File"
3. Select the JSON file
4. Configure the workflow settings
5. Activate the workflow

## Workflow Details

### Simple Idle Animation Creator

```
Webhook (Receive Image)
    ↓
Upload to LivePortrait
    ↓
Create Animation Job
    ↓
Poll for Completion
    ↓
Download Result
    ↓
Return to User
```

**Example Request:**
```bash
curl -X POST http://localhost:5678/webhook/create-idle \
  -F "image=@portrait.jpg" \
  -F "motion_type=idle_combined" \
  -F "multiplier=0.8"
```

### Complete Talking Avatar Pipeline

```
Webhook (Receive Image + Text)
    ↓
Upload to LivePortrait
    ↓
Create Idle Animation
    ↓
Generate Speech (Kokoro TTS)
    ↓
Upload to MuseTalk
    ↓
Create Talking Avatar
    ↓
Return Final Video
```

**Example Request:**
```bash
curl -X POST http://localhost:5678/webhook/talking-avatar \
  -F "image=@portrait.jpg" \
  -F "text=Hello! I am your AI assistant." \
  -F "voice=af_heart" \
  -F "motion_type=idle_combined"
```

### Batch Idle Animation Generator

```
Webhook (Receive Image)
    ↓
Upload to LivePortrait
    ↓
Create Multiple Animations (Parallel)
    ├─ Blink
    ├─ Breathing
    ├─ Head Nod
    └─ Idle Combined
    ↓
Download All Results
    ↓
Create ZIP Archive
    ↓
Return ZIP to User
```

**Example Request:**
```bash
curl -X POST http://localhost:5678/webhook/batch-idle \
  -F "image=@portrait.jpg" \
  -o idle_animations.zip
```

## Configuration

### Required Services

Make sure these services are running:
```bash
docker compose --profile avatar up liveportrait musetalk kokoro-gpu -d
```

### Service URLs

Update these in the workflow if your setup differs:
- LivePortrait: `http://liveportrait:8012`
- MuseTalk: `http://musetalk:8011`
- Kokoro TTS: `http://kokoro-gpu:8880`

### Environment Variables

No additional environment variables needed if using default configuration.

## Customization

### Adjust Motion Settings

In the LivePortrait nodes, modify:
```json
{
  "flag_relative": true,
  "flag_do_crop": true,
  "flag_pasteback": true,
  "flag_stitching": true,
  "driving_multiplier": 0.8,  // Adjust this (0.5-1.5)
  "flag_crop_driving_video": false
}
```

### Change Voice Settings

In the Kokoro TTS nodes, modify:
```json
{
  "model": "kokoro",
  "voice": "af_heart",  // Change voice
  "speed": 1.0          // Adjust speed
}
```

### Adjust MuseTalk Settings

In the MuseTalk nodes, modify:
```json
{
  "bbox_shift": 0,      // Usually 0 for LivePortrait input
  "batch_size": 8       // Adjust for performance
}
```

## Troubleshooting

### Workflow fails at LivePortrait step

**Check:**
- LivePortrait service is running: `docker compose ps liveportrait`
- Models are downloaded: `curl http://localhost:8012/health`
- Service URL is correct in workflow

### Workflow fails at MuseTalk step

**Check:**
- MuseTalk service is running: `docker compose ps musetalk`
- Idle animation was created successfully
- Audio file is valid

### Timeout errors

**Solutions:**
- Increase timeout in HTTP Request nodes (default: 300s)
- Process smaller images/videos
- Check GPU memory: `nvidia-smi`

### Memory errors

**Solutions:**
- Process workflows sequentially (not parallel)
- Restart services: `docker compose restart liveportrait musetalk`
- Reduce batch size in MuseTalk

## Performance Tips

1. **Reuse Idle Animations**
   - Create idle animations once
   - Store in shared directory
   - Reuse for multiple talking avatars

2. **Parallel Processing**
   - Process multiple sources in parallel
   - But keep LivePortrait and MuseTalk sequential per job

3. **Caching**
   - Cache generated speech audio
   - Cache idle animations
   - Use n8n's built-in caching features

## Example Use Cases

### 1. Customer Service Avatar
```
User uploads company representative photo
→ Generate professional idle animation (subtle breathing + blink)
→ Generate greeting message with TTS
→ Create talking avatar
→ Use in customer service interface
```

### 2. Educational Content
```
Upload instructor photo
→ Generate engaging idle animation (head nods + blink)
→ Generate lesson script with TTS
→ Create talking instructor
→ Use in online courses
```

### 3. Social Media Content
```
Upload creator photo
→ Generate multiple idle variations
→ Generate different messages
→ Create multiple talking avatars
→ Post to social media
```

## Advanced Workflows

### Conditional Motion Selection

Add a Switch node to select motion based on context:
```
IF user_emotion == "happy"
  → Use head_nod (engaging)
ELSE IF user_emotion == "calm"
  → Use breathing (subtle)
ELSE
  → Use idle_combined (default)
```

### Multi-Language Support

Add language detection and voice selection:
```
Detect language from text
→ Select appropriate Kokoro voice
→ Generate speech
→ Create talking avatar
```

### Quality Control

Add validation steps:
```
Check image quality
→ Validate face detection
→ Verify animation quality
→ Retry if needed
```

## Support

For issues with workflows:
1. Check n8n execution logs
2. Verify service health endpoints
3. Test individual nodes
4. Check service logs: `docker compose logs liveportrait musetalk`

## Contributing

To contribute new workflows:
1. Create workflow in n8n
2. Export as JSON
3. Add to this directory
4. Update this README
5. Submit pull request

---

**Happy automating! 🤖✨**
