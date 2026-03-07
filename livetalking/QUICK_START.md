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

# 5. Download model (MANUAL STEP - visit link below)
# https://pan.quark.cn/s/83a750323ef0
# Download wav2lip256.pth and save to: livetalking-data/models/wav2lip.pth

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

```bash
git clone https://github.com/n8n-io/self-hosted-ai-starter-kit.git && \
cd self-hosted-ai-starter-kit && \
docker network create aistack && \
cp .env.example .env && \
mkdir -p livetalking-data/models livetalking-data/avatars/default && \
echo "📥 Now download model from: https://pan.quark.cn/s/83a750323ef0" && \
echo "   Save to: livetalking-data/models/wav2lip.pth" && \
echo "📸 Add your photo to: livetalking-data/avatars/default/avatar.jpg" && \
echo "▶️  Then run: docker compose --profile avatar up -d"
```

After downloading model and adding avatar:

```bash
docker compose --profile avatar up -d && \
sleep 60 && \
python livetalking/examples/generate-avatar-video.py "Hello world!"
```

---

## Model Download Links

**Option 1 (Recommended):** https://pan.quark.cn/s/83a750323ef0  
**Option 2:** https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ

Download: `wav2lip256.pth`  
Save to: `livetalking-data/models/wav2lip.pth`

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

**Full guide:** `livetalking/GETTING_STARTED.md`
