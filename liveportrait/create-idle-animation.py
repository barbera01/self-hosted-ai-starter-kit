#!/usr/bin/env python3
"""
Create Idle Animations for LivePortrait
Generates loopable idle animations (blinking, breathing, head nods) from a source image
Perfect for creating base animations to use with MuseTalk
"""

import requests
import time
import sys
import json
from pathlib import Path
from typing import Optional

API_URL = "http://localhost:8012"

# Pre-defined idle motion templates
IDLE_MOTIONS = {
    "blink": {
        "description": "Natural blinking animation",
        "template": "blink.pkl",
        "duration": "2-3 seconds",
        "loop_friendly": True,
        "multiplier": 1.0,
    },
    "breathing": {
        "description": "Subtle breathing motion",
        "template": "breathing.pkl",
        "duration": "4-5 seconds",
        "loop_friendly": True,
        "multiplier": 0.8,
    },
    "head_nod": {
        "description": "Gentle head nod",
        "template": "head_nod.pkl",
        "duration": "3-4 seconds",
        "loop_friendly": True,
        "multiplier": 0.7,
    },
    "idle_combined": {
        "description": "Combined idle motions (blink + breathing + subtle movement)",
        "template": "idle_combined.pkl",
        "duration": "5-6 seconds",
        "loop_friendly": True,
        "multiplier": 0.9,
    },
    "wink": {
        "description": "Playful wink",
        "template": "wink.pkl",
        "duration": "2 seconds",
        "loop_friendly": False,
        "multiplier": 1.0,
    },
}


class IdleAnimationCreator:
    """Helper class for creating idle animations"""

    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url

    def check_health(self) -> bool:
        """Check if service is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            health = response.json()
            return health["status"] == "healthy"
        except:
            return False

    def upload_source(self, file_path: str) -> Optional[str]:
        """Upload source image or video"""
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None

        print(f"📤 Uploading source: {file_path.name}...")

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                response = requests.post(
                    f"{self.api_url}/api/v1/upload/source", files=files
                )
                response.raise_for_status()

            result = response.json()
            print(f"✅ Uploaded: {result['file_id']}")
            return result["path"]
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def create_idle_animation(
        self,
        source_path: str,
        motion_type: str,
        output_name: Optional[str] = None,
        custom_multiplier: Optional[float] = None,
    ) -> Optional[str]:
        """Create an idle animation"""

        if motion_type not in IDLE_MOTIONS:
            print(f"❌ Unknown motion type: {motion_type}")
            print(f"Available types: {', '.join(IDLE_MOTIONS.keys())}")
            return None

        motion = IDLE_MOTIONS[motion_type]
        multiplier = custom_multiplier if custom_multiplier else motion["multiplier"]

        print(f"\n🎬 Creating {motion_type} animation...")
        print(f"   Description: {motion['description']}")
        print(f"   Duration: {motion['duration']}")
        print(f"   Loop friendly: {motion['loop_friendly']}")
        print(f"   Multiplier: {multiplier}")

        # For now, we'll use the source path directly
        # In production, you'd have actual .pkl templates
        payload = {
            "source_image": source_path,
            "driving_video": f"/app/data/driving/{motion['template']}",
            "flag_relative": True,
            "flag_do_crop": True,
            "flag_pasteback": True,
            "flag_stitching": True,
            "driving_multiplier": multiplier,
            "flag_crop_driving_video": False,
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/animate",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            result = response.json()
            job_id = result["job_id"]
            print(f"✅ Job created: {job_id}")

            # Wait for completion
            if self.wait_for_completion(job_id):
                output_path = self.download_result(job_id, output_name)
                return output_path

            return None

        except Exception as e:
            print(f"❌ Failed to create animation: {e}")
            if hasattr(e, "response") and hasattr(e.response, "text"):
                print(f"   Response: {e.response.text}")
            return None

    def wait_for_completion(self, job_id: str, timeout: int = 300) -> bool:
        """Wait for job to complete"""
        print(f"⏳ Processing animation...")

        start_time = time.time()
        last_status = None

        while True:
            if time.time() - start_time > timeout:
                print(f"⏰ Timeout after {timeout} seconds")
                return False

            try:
                response = requests.get(f"{self.api_url}/api/v1/job/{job_id}")
                response.raise_for_status()
                status_data = response.json()
                current_status = status_data["status"]

                if current_status != last_status:
                    print(f"   Status: {current_status}")
                    last_status = current_status

                if current_status == "completed":
                    print("✅ Animation completed!")
                    return True
                elif current_status == "failed":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ Animation failed: {error}")
                    return False

            except Exception as e:
                print(f"⚠️  Status check error: {e}")

            time.sleep(2)

    def download_result(
        self, job_id: str, output_name: Optional[str] = None
    ) -> Optional[str]:
        """Download animation result"""
        if output_name is None:
            output_name = f"idle_{job_id}.mp4"

        output_path = Path(output_name)

        print(f"📥 Downloading result to {output_path}...")

        try:
            response = requests.get(
                f"{self.api_url}/api/v1/download/{job_id}", stream=True
            )
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = output_path.stat().st_size
            print(f"✅ Downloaded: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
            return str(output_path)

        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def create_batch_idle_animations(
        self, source_path: str, motion_types: list, output_dir: Optional[str] = None
    ):
        """Create multiple idle animations from one source"""

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        for motion_type in motion_types:
            if motion_type not in IDLE_MOTIONS:
                print(f"⚠️  Skipping unknown motion type: {motion_type}")
                continue

            output_name = f"idle_{motion_type}.mp4"
            if output_dir:
                output_name = str(output_dir / output_name)

            result = self.create_idle_animation(source_path, motion_type, output_name)

            results[motion_type] = result

            if result:
                print(f"\n✅ {motion_type}: {result}")
            else:
                print(f"\n❌ {motion_type}: Failed")

            # Small delay between jobs
            time.sleep(1)

        return results


def main():
    """Main function"""
    print("🎭 LivePortrait Idle Animation Creator")
    print("=" * 60)
    print("Create loopable idle animations for use with MuseTalk")
    print("=" * 60)

    creator = IdleAnimationCreator()

    # Check service health
    print("\n🔍 Checking LivePortrait service...")
    if not creator.check_health():
        print("❌ LivePortrait service is not available!")
        print(
            "   Please start it with: docker compose --profile avatar up liveportrait -d"
        )
        sys.exit(1)
    print("✅ Service is healthy")

    # Show available motion types
    print("\n📋 Available Idle Motion Types:")
    print("-" * 60)
    for motion_type, info in IDLE_MOTIONS.items():
        loop_icon = "🔄" if info["loop_friendly"] else "➡️"
        print(f"{loop_icon} {motion_type:20} - {info['description']}")
        print(f"   Duration: {info['duration']}, Multiplier: {info['multiplier']}")
    print("-" * 60)

    # Get user input
    print("\n📝 Configuration:")
    source_file = input("Enter source image/video path: ").strip()

    if not Path(source_file).exists():
        print(f"❌ File not found: {source_file}")
        sys.exit(1)

    print("\nOptions:")
    print("1. Create single idle animation")
    print("2. Create all loop-friendly animations")
    print("3. Create all animations")

    choice = input("\nEnter your choice (1-3): ").strip()

    # Upload source
    source_path = creator.upload_source(source_file)
    if not source_path:
        sys.exit(1)

    if choice == "1":
        # Single animation
        print("\nAvailable types:", ", ".join(IDLE_MOTIONS.keys()))
        motion_type = input("Enter motion type: ").strip()

        multiplier_input = input(
            "Enter multiplier (or press Enter for default): "
        ).strip()
        multiplier = float(multiplier_input) if multiplier_input else None

        output_name = input(
            "Enter output filename (or press Enter for default): "
        ).strip()
        output_name = output_name if output_name else None

        result = creator.create_idle_animation(
            source_path, motion_type, output_name, multiplier
        )

        if result:
            print(f"\n✅ Success! Animation saved to: {result}")
            print(f"\n💡 Next steps:")
            print(f"   1. Review the animation: {result}")
            print(f"   2. Use with MuseTalk for talking avatar")
            print(f"   3. Loop the video for continuous idle animation")
        else:
            print("\n❌ Failed to create animation")

    elif choice == "2":
        # All loop-friendly animations
        loop_friendly = [k for k, v in IDLE_MOTIONS.items() if v["loop_friendly"]]

        output_dir = input(
            "Enter output directory (or press Enter for current): "
        ).strip()
        output_dir = output_dir if output_dir else None

        print(f"\n🎬 Creating {len(loop_friendly)} loop-friendly animations...")
        results = creator.create_batch_idle_animations(
            source_path, loop_friendly, output_dir
        )

        print("\n" + "=" * 60)
        print("📊 Results Summary:")
        for motion_type, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {motion_type}: {result or 'Failed'}")

        successful = [r for r in results.values() if r]
        print(f"\n✅ Successfully created {len(successful)}/{len(results)} animations")

    elif choice == "3":
        # All animations
        output_dir = input(
            "Enter output directory (or press Enter for current): "
        ).strip()
        output_dir = output_dir if output_dir else None

        print(f"\n🎬 Creating {len(IDLE_MOTIONS)} animations...")
        results = creator.create_batch_idle_animations(
            source_path, list(IDLE_MOTIONS.keys()), output_dir
        )

        print("\n" + "=" * 60)
        print("📊 Results Summary:")
        for motion_type, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {motion_type}: {result or 'Failed'}")

        successful = [r for r in results.values() if r]
        print(f"\n✅ Successfully created {len(successful)}/{len(results)} animations")

    else:
        print("❌ Invalid choice")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 Done!")
    print("\n💡 Tips for using with MuseTalk:")
    print("   1. Use loop-friendly animations for continuous idle state")
    print("   2. Combine idle animation with MuseTalk audio-driven animation")
    print("   3. Adjust multiplier to control motion intensity")
    print("   4. Test different motion types to find the best fit")
    print("=" * 60)


if __name__ == "__main__":
    main()
