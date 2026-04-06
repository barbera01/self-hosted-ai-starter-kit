# Quick Start - One-Line Steps

## From Clone to Video in 9 Commands

```bash
# 1. Clone repo
git clone https://github.com/n8n-io/self-hosted-ai-starter-kit.git && cd self-hosted-ai-starter-kit

# 2. Create Docker network
docker network create aistack

# 3. Setup environment
cp .env.example .env

# 4. Create directories
mkdir -p livetalking-data/models livetalking-data/avatars/default

# 5. Download model (automatic via wget)
cd livetalking && ./download-model-simple.sh && cd ..

# 6. Add avatar image (MANUAL STEP)
# Copy your headshot photo to: livetalking-data/avatars/default/avatar.jpg

# 7. Start all services
docker compose --profile avatar up -d

# 8. Wait for ready (check logs)
docker compose logs -f livetalking
# Look for: "Application startup complete" then press Ctrl+C

# 9. Generate video
python livetalking/examples/generate-avatar-video.py "Hello! This is my first video."
```

## That's It! 🎬

Your video is saved as `avatar_video_*.mp4`

---

## Even Simpler - Copy/Paste Block

**First block (setup):**
```bash
git clone https://github.com/n8n-io/self-hosted-ai-starter-kit.git && \
cd self-hosted-ai-starter-kit && \
docker network create aistack && \
cp .env.example .env && \
mkdir -p livetalking-data/models livetalking-data/avatars/default
```

**Second block (download model):**
```bash
cd livetalking && ./download-model-simple.sh && cd ..
```

**Then manually:**
- Add photo: Your headshot → `livetalking-data/avatars/default/avatar.jpg`

**Final block (start and generate):**
```bash
docker compose --profile avatar up -d && \
sleep 60 && \
python livetalking/examples/generate-avatar-video.py "Hello world!"
```

---

## Alternative: Manual Model Download

If the script doesn't work, download manually:

```bash
# Using official OneDrive
wget --no-check-certificate \
  "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" \
  -O livetalking-data/models/wav2lip.pth

# OR download manually from Google Drive
# https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy
```

---

## Avatar Image Tips

✅ Clear headshot photo  
✅ Face forward, neutral expression  
✅ Good lighting  
✅ Plain background  
✅ JPG or PNG format  
✅ 512x512 or larger  

Save to: `livetalking-data/avatars/default/avatar.jpg`

---

## Quick Commands Reference

```bash
# Download model only
cd livetalking && ./download-model-simple.sh

# Start services
docker compose --profile avatar up -d

# Check status
docker compose ps

# View logs
docker compose logs -f livetalking

# Stop services
docker compose --profile avatar down

# Generate another video
python livetalking/examples/generate-avatar-video.py "Your text here"

# Different voice
python livetalking/examples/generate-avatar-video.py "Hello!" --voice am_adam

# High resolution
python livetalking/examples/generate-avatar-video.py "Hello!" --resolution 1920x1080
```

---

**Full guide:** `livetalking/GETTING_STARTED.md`  
**Model download help:** `livetalking/MODEL_DOWNLOAD.md`
