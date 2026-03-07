# LiveTalking Virtual Avatar Video Generator

**Create virtual avatar/VTuber videos with AI-powered lip-sync!**

## 📁 All Files Moved to `livetalking/` Directory

All LiveTalking integration files are now organized in the `livetalking/` directory:

```
livetalking/
├── QUICKSTART_AVATAR.md          ⭐ START HERE - 3-step quick start
├── AVATAR_SETUP.md                📖 Complete setup guide
├── INTEGRATION_SUMMARY.md         🔧 Technical architecture
├── README.md                      📚 Service documentation
├── setup-avatar.sh                🚀 Automated setup script
├── Dockerfile                     🐳 Docker image
├── batch-inference.py             🎬 Video generation API
├── requirements.txt               📦 Python dependencies
├── download-models.sh             ⬇️  Model download helper
├── examples/
│   └── generate-avatar-video.py   💡 Python example
└── n8n-workflows/
    └── avatar-video-generator.json 🤖 n8n automation workflow
```

## 🚀 Quick Start

```bash
# 1. Download models (one-time)
# Visit: https://pan.quark.cn/s/83a750323ef0
# Download: wav2lip256.pth
# Save to: livetalking-data/models/wav2lip.pth

# 2. Add avatar image (one-time)
mkdir -p livetalking-data/avatars/default
# Copy your headshot photo to:
# livetalking-data/avatars/default/avatar.jpg

# 3. Run setup
cd livetalking
./setup-avatar.sh

# 4. Generate video
cd ..
python livetalking/examples/generate-avatar-video.py "Hello world!"
```

## 📖 Documentation

- **Quick Start**: [`livetalking/QUICKSTART_AVATAR.md`](livetalking/QUICKSTART_AVATAR.md) - Get started in 3 steps
- **Full Setup**: [`livetalking/AVATAR_SETUP.md`](livetalking/AVATAR_SETUP.md) - Complete guide with examples
- **Architecture**: [`livetalking/INTEGRATION_SUMMARY.md`](livetalking/INTEGRATION_SUMMARY.md) - Technical details
- **API Docs**: [`livetalking/README.md`](livetalking/README.md) - Service documentation

## 🎯 What Can You Build?

- 🎥 **YouTube Videos** - Educational content, channel intros
- 📱 **Social Media** - TikTok/Instagram Reels, Twitter videos
- 💼 **Business** - Training videos, product demos, FAQs
- 🤖 **Automation** - Daily news, blog-to-video, scheduled content

## 🔧 Features

- ✅ Multiple avatar types (realistic, anime, custom)
- ✅ Text-to-speech with multiple voices (via Kokoro)
- ✅ High-quality lip-sync (via Wav2Lip)
- ✅ Multiple resolutions (720p, 1080p)
- ✅ Batch processing
- ✅ n8n workflow automation
- ✅ RESTful API

## 🌐 API

Once running, access:
- **API Docs**: http://localhost:8010/docs
- **Generate Video**: `POST http://localhost:8010/generate`
- **Check Status**: `GET http://localhost:8010/job/{id}`
- **Download**: `GET http://localhost:8010/download/{id}`

## 💡 Example Usage

```python
import requests

# Generate video
response = requests.post("http://localhost:8010/generate", json={
    "text": "Hello! Welcome to my channel.",
    "avatar_id": "default",
    "voice": "af_heart",
    "resolution": "1280x720"
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8010/job/{job_id}").json()

# Download when complete
if status["status"] == "completed":
    video = requests.get(f"http://localhost:8010/download/{job_id}")
    with open("video.mp4", "wb") as f:
        f.write(video.content)
```

## 🆘 Support

- **Issues**: Open an issue in this repository
- **LiveTalking**: https://github.com/lipku/LiveTalking
- **Models**: https://pan.quark.cn/s/83a750323ef0

---

**Ready to create virtual avatar videos?** Start with [`livetalking/QUICKSTART_AVATAR.md`](livetalking/QUICKSTART_AVATAR.md)! 🎬
