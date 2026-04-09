# MuseTalk API Reference

API documentation for the MuseTalk v1.5 Avatar Video Generator.

**Base URL:** `http://172.16.106.81:8011`

---

## Quick Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Health check | GET | `/health` |
| List models | GET | `/models` |
| List all jobs | GET | `/jobs` |
| Upload avatar | POST | `/upload-avatar` |
| Generate video | POST | `/generate` |
| Check job status | GET | `/job/{job_id}` |
| Download video | GET | `/download/{job_id}` |
| Delete job | DELETE | `/job/{job_id}` |

---

## Health & Status

### Check API Health

```bash
curl http://172.16.106.81:8011/health
```

**Response:**
```json
{
  "status": "healthy",
  "engine": "musetalk-v1.5",
  "models_ready": true,
  "avatars_available": ["eve", "rowan", "office-goblin"]
}
```

### List Models

```bash
curl http://172.16.106.81:8011/models
```

**Response:**
```json
{
  "engine": "musetalk-v1.5",
  "models_ready": true,
  "avatars": ["eve", "rowan", "office-goblin"]
}
```

---

## Avatar Management

### Upload New Avatar

Upload an image (PNG/JPG) or video (MP4) as an avatar source.

```bash
# Upload video (recommended)
curl -X POST http://172.16.106.81:8011/upload-avatar \
  -F "file=@/path/to/avatar.mp4" \
  -F "avatar_id=my-avatar"

# Upload image
curl -X POST http://172.16.106.81:8011/upload-avatar \
  -F "file=@/path/to/avatar.png" \
  -F "avatar_id=my-avatar"
```

**Response:**
```json
{
  "avatar_id": "my-avatar",
  "file": "/app/data/avatars/my-avatar/avatar.mp4",
  "coords_cache_cleared": true,
  "message": "Avatar uploaded successfully"
}
```

### Supported Avatar Formats

| Priority | Filename | Type | Recommended |
|----------|----------|------|-------------|
| 1st | `avatar.mp4` | Video | Best |
| 2nd | `avatar.png` | Image | Good |
| 3rd | `avatar.jpg` | Image | Good |
| 4th | `avatar.jpeg` | Image | Good |

### Avatar Source Requirements

| Parameter | Recommendation |
|-----------|----------------|
| Frame rate | 25 fps |
| Resolution | 1080p or 720p |
| Duration | 5-8 seconds (video) |
| Expression | Neutral, mouth closed |
| Angle | Front-facing, direct eye contact |
| Face | Clearly visible, no obstructions |

---

## Video Generation

### Generate Video from Text

```bash
curl -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "eve",
    "text": "Hello, I am Eve Calloway, technical architect at Herb Hub 365."
  }'
```

**Response:**
```json
{
  "job_id": "27e57f39-8f00-44d4-b6f6-1775e0a27542",
  "status": "pending"
}
```

### Generate Video from Audio URL

```bash
curl -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "rowan",
    "audio_url": "https://example.com/audio.wav"
  }'
```

### Full Request Options

```bash
curl -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "eve",
    "text": "Your text here",
    "voice": "bf_lily",
    "speed": 1.0,
    "resolution": "1280x720",
    "fps": 25,
    "batch_size": 4
  }'
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `avatar_id` | string | `"default"` | Avatar to use |
| `text` | string | null | Text to speak (uses TTS) |
| `audio_url` | string | null | URL to audio file (alternative to text) |
| `voice` | string | per-avatar | Kokoro voice code |
| `speed` | float | per-avatar | Speech speed (1.0 = normal) |
| `resolution` | string | `"1280x720"` | Output resolution |
| `fps` | int | `25` | Frames per second |
| `batch_size` | int | `4` | Processing batch size |

---

## Job Management

### List All Jobs

```bash
curl http://172.16.106.81:8011/jobs
```

**Response:**
```json
{
  "total": 2,
  "jobs": [
    {
      "job_id": "abc-123",
      "status": "completed",
      "progress": 100,
      "avatar_id": "eve",
      "video_url": "/download/abc-123",
      "error": null
    },
    {
      "job_id": "def-456",
      "status": "processing",
      "progress": 45,
      "avatar_id": "rowan",
      "video_url": null,
      "error": null
    }
  ]
}
```

### Check Job Status

```bash
curl http://172.16.106.81:8011/job/JOB_ID
```

**Response:**
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "progress": 100,
  "avatar_id": "eve",
  "video_url": "/download/abc-123",
  "error": null
}
```

### Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job queued, not started |
| `processing` | Job in progress |
| `completed` | Job finished successfully |
| `failed` | Job failed (check `error` field) |

### Watch Job Progress (Auto-refresh)

```bash
# Replace JOB_ID with your job ID
watch -n 2 'curl -s http://172.16.106.81:8011/job/JOB_ID'
```

### Loop Until Complete

```bash
JOB_ID="your-job-id-here"
while true; do
  STATUS=$(curl -s http://172.16.106.81:8011/job/$JOB_ID)
  echo $STATUS
  echo $STATUS | grep -q '"status":"completed"' && break
  echo $STATUS | grep -q '"status":"failed"' && break
  sleep 3
done
```

### Download Completed Video

```bash
curl http://172.16.106.81:8011/download/JOB_ID -o output.mp4
```

### Delete Job

```bash
curl -X DELETE http://172.16.106.81:8011/job/JOB_ID
```

**Response:**
```json
{
  "message": "Job deleted"
}
```

---

## Complete Workflow Examples

### Example 1: Generate Eve Video

```bash
# 1. Generate
JOB_ID=$(curl -s -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": "eve", "text": "Hello, I am Eve Calloway."}' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Watch progress
watch -n 2 "curl -s http://172.16.106.81:8011/job/$JOB_ID"

# 3. Download when complete
curl http://172.16.106.81:8011/download/$JOB_ID -o eve_video.mp4
```

### Example 2: Generate Rowan Video

```bash
# 1. Generate
JOB_ID=$(curl -s -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": "rowan", "text": "The sensor tells you the number. The number tells you something is happening."}' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Watch progress
watch -n 2 "curl -s http://172.16.106.81:8011/job/$JOB_ID"

# 3. Download when complete
curl http://172.16.106.81:8011/download/$JOB_ID -o rowan_video.mp4
```

### Example 3: Office Goblin (Fast & Frantic)

```bash
# 1. Generate
JOB_ID=$(curl -s -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": "office-goblin", "text": "Deadline ASAP! Why is nobody panicking? This is fine. Everything is fine!"}' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Watch progress
watch -n 2 "curl -s http://172.16.106.81:8011/job/$JOB_ID"

# 3. Download when complete
curl http://172.16.106.81:8011/download/$JOB_ID -o office_goblin_video.mp4
```

### Example 4: All-in-One Script

```bash
#!/bin/bash
# generate-avatar-video.sh

AVATAR="${1:-eve}"
TEXT="${2:-Hello world}"
OUTPUT="${3:-output.mp4}"
API="http://172.16.106.81:8011"

echo "Generating video for $AVATAR..."

# Generate
JOB_ID=$(curl -s -X POST "$API/generate" \
  -H "Content-Type: application/json" \
  -d "{\"avatar_id\": \"$AVATAR\", \"text\": \"$TEXT\"}" | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Wait for completion
while true; do
  STATUS=$(curl -s "$API/job/$JOB_ID")
  PROGRESS=$(echo $STATUS | jq -r '.progress')
  STATE=$(echo $STATUS | jq -r '.status')
  
  echo "Status: $STATE ($PROGRESS%)"
  
  [ "$STATE" = "completed" ] && break
  [ "$STATE" = "failed" ] && { echo "Error: $(echo $STATUS | jq -r '.error')"; exit 1; }
  
  sleep 3
done

# Download
curl -s "$API/download/$JOB_ID" -o "$OUTPUT"
echo "Downloaded: $OUTPUT"
```

**Usage:**
```bash
chmod +x generate-avatar-video.sh
./generate-avatar-video.sh eve "Hello, I am Eve!" eve_hello.mp4
./generate-avatar-video.sh rowan "The plants are growing well." rowan_plants.mp4
./generate-avatar-video.sh office-goblin "Deadline ASAP!" goblin_panic.mp4
```

---

## Voice Configuration

### Current Avatar Voices

| Avatar | Voice | Speed | Style |
|--------|-------|-------|-------|
| `rowan` | `bm_daniel(7)+bm_lewis(3)` | 0.95 | Warm, measured British male |
| `eve` | `bf_lily(7)+bf_emma(2)+af_bella(1)+af_heart(1)` | 0.95 | Clear, precise British female |
| `office-goblin` | `bf_v0isabella` | 1.4 | Fast, frantic British female |

### Available Kokoro Voices

#### British Voices
| Code | Gender | Description |
|------|--------|-------------|
| `bf_alice` | Female | British |
| `bf_emma` | Female | British |
| `bf_lily` | Female | British |
| `bf_v0emma` | Female | British (v0) |
| `bf_v0isabella` | Female | British (v0) |
| `bm_daniel` | Male | British |
| `bm_fable` | Male | British |
| `bm_george` | Male | British |
| `bm_lewis` | Male | British |
| `bm_v0george` | Male | British (v0) |
| `bm_v0lewis` | Male | British (v0) |

#### American Voices
| Code | Gender | Description |
|------|--------|-------------|
| `af_alloy` | Female | American |
| `af_bella` | Female | American |
| `af_heart` | Female | American |
| `af_jessica` | Female | American |
| `af_nicole` | Female | American |
| `af_nova` | Female | American |
| `af_river` | Female | American |
| `af_sarah` | Female | American |
| `af_sky` | Female | American |
| `am_adam` | Male | American |
| `am_echo` | Male | American |
| `am_eric` | Male | American |
| `am_liam` | Male | American |
| `am_michael` | Male | American |
| `am_onyx` | Male | American |
| `am_puck` | Male | American |

### Voice Blending

Combine voices with weighted blending:

```
"voice": "bf_lily(7)+bf_emma(3)"  # 70% Lily, 30% Emma
"voice": "bm_daniel(5)+bm_lewis(5)"  # 50/50 blend
```

### Speed Settings

| Speed | Effect |
|-------|--------|
| `0.8` | Slow, deliberate |
| `0.95` | Slightly slower than normal |
| `1.0` | Normal speed |
| `1.2` | Noticeably faster |
| `1.4` | Fast, hurried |
| `1.5+` | Very fast, frantic |

### Override Voice in Request

```bash
curl -X POST http://172.16.106.81:8011/generate \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_id": "eve",
    "text": "Speaking with a different voice!",
    "voice": "af_nova",
    "speed": 1.2
  }'
```

---

## Troubleshooting

### Job Failed - Check Error

```bash
curl http://172.16.106.81:8011/job/JOB_ID | jq '.error'
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Voice 'xxx' not found` | Invalid voice code | Check available voices list |
| `No avatar source found` | Avatar not uploaded | Upload avatar first |
| `TTS failed` | Kokoro TTS issue | Check Kokoro service is running |
| `MuseTalk inference failed` | GPU/model issue | Check container logs |

### Check Container Logs

```bash
docker compose logs musetalk --tail 100
```

### Restart Service

```bash
docker compose restart musetalk
```

---

## Notes

- Jobs are stored in memory and lost on container restart
- First generation for a new avatar takes longer (computing face coordinates)
- Subsequent generations reuse cached coordinates and are faster
- Uploading a new avatar clears the coordinate cache automatically
