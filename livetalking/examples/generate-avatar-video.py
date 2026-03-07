#!/usr/bin/env python3
"""
Example: Generate Avatar Video

This script demonstrates how to generate a virtual avatar video
using the LiveTalking service.

Usage:
    python generate-avatar-video.py "Your script text here"
    python generate-avatar-video.py --audio audio.wav
    python generate-avatar-video.py --help
"""

import requests
import time
import sys
import argparse
from pathlib import Path

# Configuration
LIVETALKING_URL = "http://localhost:8010"


def generate_video(
    text: str = None,
    audio_file: str = None,
    avatar_id: str = "default",
    voice: str = "af_heart",
    resolution: str = "1280x720",
    output_file: str = None,
):
    """
    Generate an avatar video

    Args:
        text: Script text (if not using audio_file)
        audio_file: Path to audio file (if not using text)
        avatar_id: Avatar identifier
        voice: TTS voice to use
        resolution: Video resolution
        output_file: Where to save the video
    """

    if not text and not audio_file:
        raise ValueError("Either text or audio_file must be provided")

    # Prepare request
    payload = {
        "avatar_id": avatar_id,
        "model": "wav2lip",
        "voice": voice,
        "resolution": resolution,
        "fps": 25,
    }

    if text:
        payload["text"] = text
    elif audio_file:
        # TODO: Upload audio file or provide URL
        payload["audio_url"] = f"file://{audio_file}"

    # Submit job
    print(f"🎬 Generating video...")
    print(f"   Avatar: {avatar_id}")
    print(f"   Voice: {voice}")
    print(f"   Resolution: {resolution}")
    print()

    try:
        response = requests.post(
            f"{LIVETALKING_URL}/generate", json=payload, timeout=10
        )
        response.raise_for_status()
        job_data = response.json()
        job_id = job_data["job_id"]

        print(f"✓ Job created: {job_id}")
        print()

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create job: {e}")
        print()
        print("Make sure LiveTalking is running:")
        print("  docker compose --profile avatar up livetalking")
        sys.exit(1)

    # Poll for completion
    print("⏳ Processing video...")
    last_progress = 0

    while True:
        try:
            response = requests.get(f"{LIVETALKING_URL}/job/{job_id}", timeout=10)
            response.raise_for_status()
            status_data = response.json()

            status = status_data["status"]
            progress = status_data.get("progress", 0)

            # Show progress
            if progress > last_progress:
                print(f"   Progress: {progress}%")
                last_progress = progress

            if status == "completed":
                print()
                print("✓ Video generation complete!")
                break
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print(f"❌ Generation failed: {error}")
                sys.exit(1)

            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to check status: {e}")
            sys.exit(1)

    # Download video
    if not output_file:
        output_file = f"avatar_video_{job_id}.mp4"

    print(f"📥 Downloading video to: {output_file}")

    try:
        response = requests.get(f"{LIVETALKING_URL}/download/{job_id}", timeout=60)
        response.raise_for_status()

        with open(output_file, "wb") as f:
            f.write(response.content)

        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print(f"✓ Video saved: {output_file} ({file_size:.2f} MB)")
        print()
        print("🎉 Done! You can now:")
        print(f"   - Play the video: open {output_file}")
        print(f"   - Upload to YouTube")
        print(f"   - Share on social media")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download video: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate virtual avatar videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from text
  python generate-avatar-video.py "Hello, welcome to my channel!"
  
  # Use different voice
  python generate-avatar-video.py "Hello!" --voice am_adam
  
  # Use custom avatar
  python generate-avatar-video.py "Hello!" --avatar my-avatar
  
  # High resolution
  python generate-avatar-video.py "Hello!" --resolution 1920x1080
  
  # From audio file
  python generate-avatar-video.py --audio speech.wav

Available voices:
  af_heart, af_bella, af_sarah (Female)
  am_adam, am_michael (Male)
  bf_emma, bm_george (British)
        """,
    )

    parser.add_argument("text", nargs="?", help="Script text for the avatar to speak")
    parser.add_argument("--audio", help="Path to audio file (alternative to text)")
    parser.add_argument(
        "--avatar", default="default", help="Avatar ID (default: default)"
    )
    parser.add_argument(
        "--voice", default="af_heart", help="TTS voice (default: af_heart)"
    )
    parser.add_argument(
        "--resolution",
        default="1280x720",
        choices=["1920x1080", "1280x720", "854x480"],
        help="Video resolution (default: 1280x720)",
    )
    parser.add_argument("--output", help="Output file path (default: auto-generated)")

    args = parser.parse_args()

    # Validate input
    if not args.text and not args.audio:
        parser.print_help()
        sys.exit(1)

    # Generate video
    generate_video(
        text=args.text,
        audio_file=args.audio,
        avatar_id=args.avatar,
        voice=args.voice,
        resolution=args.resolution,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
