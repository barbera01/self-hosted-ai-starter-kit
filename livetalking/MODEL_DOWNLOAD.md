# Wav2Lip Model Download Guide

Multiple ways to download the wav2lip model for avatar video generation.

## 🚀 Quick Download (Automated Script)

```bash
cd livetalking
./download-model-simple.sh
```

The script will prompt you to choose a download source.

## 📥 Manual Download Options

### Option 1: Official Wav2Lip Repository (Recommended)

**Direct download link:**
```bash
wget "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -O livetalking-data/models/wav2lip.pth
```

**Source:** https://github.com/Rudrabha/Wav2Lip

### Option 2: Google Drive (Official)

1. Visit: https://drive.google.com/drive/folders/1s4Sj-C2vJRRkEwZhVMRPRPJWqJNLwHWy
2. Download: `wav2lip.pth`
3. Save to: `livetalking-data/models/wav2lip.pth`

### Option 3: Quark Cloud Drive (Chinese Mirror)

1. Visit: https://pan.quark.cn/s/83a750323ef0
2. Download: `wav2lip256.pth`
3. Rename to: `wav2lip.pth`
4. Save to: `livetalking-data/models/wav2lip.pth`

> Note: previously suggested Hugging Face wav2lip URLs were not valid for this model.
> Use Google Drive, the official OneDrive/SharePoint link, or Quark instead.

## 📊 Model Comparison

| Model | Size | Quality | Speed | Recommended |
|-------|------|---------|-------|-------------|
| wav2lip.pth | ~150MB | Good | Fast | ✅ Yes |

## ✅ Verify Download

After downloading, verify the file:

```bash
# Check file exists
ls -lh livetalking-data/models/wav2lip.pth

# Check file size (should be ~150-200 MB)
du -h livetalking-data/models/wav2lip.pth
```

Expected output:
```
-rw-r--r--  1 user  staff   150M  Mar  7 12:00 wav2lip.pth
```

## 🔧 Troubleshooting

### Download Failed / Incomplete

**Symptoms:**
- File size < 50 MB
- Error when starting LiveTalking

**Solutions:**
1. Delete partial download: `rm livetalking-data/models/wav2lip.pth`
2. Try different download source
3. Check internet connection
4. Use the automated script: `./download-model-simple.sh`

### File Not Found Error

**Error:** `Model not found at /app/models/wav2lip.pth`

**Solution:**
```bash
# Check file location
ls -la livetalking-data/models/

# File should be named exactly: wav2lip.pth
# If named differently, rename it:
mv livetalking-data/models/wav2lip256.pth livetalking-data/models/wav2lip.pth
```

### Permission Denied

**Error:** `Permission denied: wav2lip.pth`

**Solution:**
```bash
chmod 644 livetalking-data/models/wav2lip.pth
```

## 🌐 All Download Sources

| Source | Speed | Reliability | Notes |
|--------|-------|-------------|-------|
| **Official OneDrive** | Medium | High | Recommended |
| **Google Drive** | Fast | High | Recommended |
| **Quark Cloud** | Varies | Medium | Chinese mirror |

## 📝 Next Steps

After downloading the model:

1. **Verify location:**
   ```bash
   ls -lh livetalking-data/models/wav2lip.pth
   ```

2. **Add avatar image:**
   ```bash
   mkdir -p livetalking-data/avatars/default
   # Copy your photo to: livetalking-data/avatars/default/avatar.jpg
   ```

3. **Start service:**
   ```bash
   docker compose --profile avatar up livetalking -d
   ```

4. **Generate video:**
   ```bash
   python livetalking/examples/generate-avatar-video.py "Hello world!"
   ```

## 🆘 Still Having Issues?

1. **Use the automated script:** `./download-model-simple.sh`
2. **Check the FAQ:** `AVATAR_SETUP.md`
3. **Open an issue:** Include error messages and file size

---

**Recommended:** Use Google Drive or the official OneDrive link. 🚀
