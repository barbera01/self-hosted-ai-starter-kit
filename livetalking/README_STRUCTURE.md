# LiveTalking Directory Structure

All LiveTalking integration files are organized in this directory.

## 📁 Directory Structure

```
livetalking/
├── Documentation
│   ├── QUICKSTART_AVATAR.md       ⭐ START HERE - 3-step quick start
│   ├── AVATAR_SETUP.md            📖 Complete setup guide  
│   ├── INTEGRATION_SUMMARY.md     🔧 Technical architecture
│   └── README.md                  📚 Service API documentation
│
├── Setup & Configuration
│   ├── setup-avatar.sh            🚀 Automated setup script
│   ├── Dockerfile                 🐳 Docker image definition
│   ├── requirements.txt           📦 Python dependencies
│   └── download-models.sh         ⬇️  Model download helper
│
├── Application Code
│   └── batch-inference.py         🎬 FastAPI video generation service
│
├── Examples
│   └── examples/
│       └── generate-avatar-video.py  💡 Python CLI example
│
└── Workflows
    └── n8n-workflows/
        └── avatar-video-generator.json  🤖 n8n automation workflow
```

## 🚀 Getting Started

1. **Read the Quick Start**: [QUICKSTART_AVATAR.md](QUICKSTART_AVATAR.md)
2. **Run the setup**: `./setup-avatar.sh`
3. **Generate a video**: `python examples/generate-avatar-video.py "Hello!"`

## 📖 Documentation Order

1. **QUICKSTART_AVATAR.md** - Get up and running in 3 steps
2. **AVATAR_SETUP.md** - Detailed setup with examples and troubleshooting
3. **INTEGRATION_SUMMARY.md** - Architecture and technical details
4. **README.md** - API reference and service documentation

## 🔗 Quick Links

- Main project README: [../README.md](../README.md)
- Docker Compose: [../docker-compose.yml](../docker-compose.yml)
- Environment config: [../.env.example](../.env.example)

## 💡 Usage Examples

### Command Line
```bash
python examples/generate-avatar-video.py "Your script here"
```

### API
```bash
curl -X POST http://localhost:8010/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "avatar_id": "default"}'
```

### n8n Workflow
Import `n8n-workflows/avatar-video-generator.json` into n8n

---

**Start here**: [QUICKSTART_AVATAR.md](QUICKSTART_AVATAR.md) 🎬
