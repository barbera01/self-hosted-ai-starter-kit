# Fix Stuck Model Download

The container is stuck downloading models. Here's how to fix it:

## Quick Fix - Start Without Models

**Stop the stuck container and rebuild:**

```bash
# Stop it
docker compose stop liveportrait

# Rebuild with new startup script (doesn't wait for models)
docker compose build liveportrait

# Start it
docker compose up liveportrait -d

# Check logs - should start immediately now
docker compose logs -f liveportrait
```

The service will now **start immediately** without waiting for models!

## Download Models After Startup

Once the service is running, download models in the background:

```bash
# Option 1: Download in background
docker compose exec liveportrait nohup /app/download-models.sh > /app/output/download.log 2>&1 &

# Monitor progress
docker compose exec liveportrait tail -f /app/output/download.log

# Option 2: Download in foreground (see progress)
docker compose exec liveportrait /app/download-models.sh
```

## Alternative - Manual Download

If HuggingFace download is too slow, download manually:

```bash
# 1. Download from Google Drive (faster)
# Visit: https://drive.google.com/drive/folders/1UtKgzKjFAOmZkhNK-OYT0caJ_w2XAnib
# Download all files

# 2. Copy to the container
docker cp ./pretrained_weights/. liveportrait:/app/pretrained_weights/

# 3. Mark as downloaded
docker compose exec liveportrait touch /app/pretrained_weights/.downloaded
```

## Why It Got Stuck

HuggingFace downloads can be slow/unreliable. The new startup script:
- ✅ Starts the web service immediately
- ✅ Downloads models on-demand or in background
- ✅ Doesn't block startup

## Verify It's Working

```bash
# Service should be running now
curl http://localhost:8012/health

# Should show:
# {"status": "healthy", "motions_available": X, ...}

# Open web interface
open http://localhost:8012
```

The first time you generate an animation, it will trigger the model download if needed.
