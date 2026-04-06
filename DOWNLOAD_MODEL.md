# Download Wav2Lip Model

## ✅ Recommended Sources

Use one of these verified Wav2Lip sources instead of Hugging Face.

---

## 🚀 Without Token (Alternative Sources)

```bash
cd livetalking && ./download-model-simple.sh
```

This will show you options for Google Drive, OneDrive, or Quark Cloud.

---

## 📥 Manual Download

### Google Drive (Official)
1. Visit: https://drive.google.com/drive/folders/153HLrqlBNxzZcHi17PEvP09kkAfzRshM?usp=share_link
2. Click: `wav2lip.pth`
3. Download and save to: `livetalking-data/models/wav2lip.pth`

### Official OneDrive (wget/curl)
```bash
mkdir -p livetalking-data/models
wget --no-check-certificate \
  "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" \
  -O livetalking-data/models/wav2lip.pth
```

### Quark Cloud (Mirror)
1. Visit: https://pan.quark.cn/s/83a750323ef0
2. Download: `wav2lip256.pth`
3. Rename it to: `wav2lip.pth`
4. Save to: `livetalking-data/models/wav2lip.pth`

---

## ✅ Verify Download

```bash
ls -lh livetalking-data/models/wav2lip.pth
# Should show: ~150M
```

---

## 🎬 Complete Setup (Copy/Paste)

### Using Google Drive
```bash
# 1. Create directories
mkdir -p livetalking-data/models livetalking-data/avatars/default

# 2. Download from Google Drive
# Visit: https://drive.google.com/drive/folders/153HLrqlBNxzZcHi17PEvP09kkAfzRshM?usp=share_link
# Download wav2lip.pth to: livetalking-data/models/wav2lip.pth

# 3. Add your avatar photo
# Copy to: livetalking-data/avatars/default/avatar.jpg

# 4. Start services
docker compose --profile avatar up -d

# 5. Generate video
python livetalking/examples/generate-avatar-video.py "Hello world!"
```

Done! 🎉
