# Quick Fix for "Generation Failed" Error

The error happens because there are no driving videos (motion templates) yet.

## Fix It Now (2 options)

### Option 1: Rebuild Container (Recommended)

This will automatically copy driving videos from the LivePortrait repo:

```bash
# Rebuild the container
docker compose build liveportrait

# Restart it
docker compose up liveportrait -d

# Check logs
docker compose logs -f liveportrait
```

### Option 2: Manual Setup (Faster)

Copy driving videos from the LivePortrait repo that's already in the container:

```bash
# Run the setup script inside the container
docker compose exec liveportrait /app/download-driving-videos.sh

# Restart the service
docker compose restart liveportrait
```

## Verify It Works

```bash
# Check health endpoint
curl http://localhost:8012/health

# Should show:
# {
#   "status": "healthy",
#   "motions_available": 4,
#   "motions": ["idle_combined", "blink", "breathing", "head_nod"]
# }
```

## Then Try Again

1. Open http://localhost:8012
2. Upload an image
3. Select a motion
4. Click Generate
5. Wait 30-60 seconds
6. Download your idle video!

## What the Fix Does

The LivePortrait repository includes example driving videos in `/app/assets/examples/driving/`. The fix script copies these to `/app/data/driving/` and creates standard named symlinks:

- `idle_combined.mp4` - Combined idle motions
- `blink.mp4` - Blinking
- `breathing.mp4` - Breathing
- `head_nod.mp4` - Head nodding

These are the motion templates that drive the idle animations!
