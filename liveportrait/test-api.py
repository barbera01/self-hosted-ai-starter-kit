#!/usr/bin/env python3
"""
Simple test script for LivePortrait API
"""

import requests
import time
import sys
import json
from pathlib import Path

API_URL = "http://localhost:8012"


def check_health():
    """Check if service is healthy"""
    print("🔍 Checking service health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()

        print(f"✅ Service is {health['status']}")
        print(f"   Models downloaded: {health['models_downloaded']}")
        print(f"   GPU available: {health['gpu_available']}")

        return health["status"] == "healthy"
    except requests.exceptions.RequestException as e:
        print(f"❌ Service is not available: {e}")
        return False


def upload_file(file_path, endpoint):
    """Upload a file to the API"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    print(f"📤 Uploading {file_path.name}...")

    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            response = requests.post(f"{API_URL}{endpoint}", files=files)
            response.raise_for_status()

        result = response.json()
        print(f"✅ Uploaded: {result['file_id']}")
        return result["path"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")
        return None


def create_animation(source_path, driving_path, **kwargs):
    """Create an animation job"""
    print("🎬 Creating animation job...")

    payload = {
        "source_image": source_path,
        "driving_video": driving_path,
        "flag_relative": kwargs.get("flag_relative", True),
        "flag_do_crop": kwargs.get("flag_do_crop", True),
        "flag_pasteback": kwargs.get("flag_pasteback", True),
        "flag_stitching": kwargs.get("flag_stitching", True),
        "driving_multiplier": kwargs.get("driving_multiplier", 1.0),
        "flag_crop_driving_video": kwargs.get("flag_crop_driving_video", False),
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/animate",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()
        job_id = result["job_id"]
        print(f"✅ Job created: {job_id}")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Job creation failed: {e}")
        if hasattr(e.response, "text"):
            print(f"   Response: {e.response.text}")
        return None


def check_job_status(job_id):
    """Check job status"""
    try:
        response = requests.get(f"{API_URL}/api/v1/job/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Status check failed: {e}")
        return None


def wait_for_completion(job_id, timeout=300):
    """Wait for job to complete"""
    print(f"⏳ Waiting for job {job_id} to complete...")

    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(f"⏰ Timeout after {timeout} seconds")
            return False

        status = check_job_status(job_id)
        if not status:
            return False

        current_status = status["status"]
        print(f"   Status: {current_status}")

        if current_status == "completed":
            print("✅ Job completed successfully!")
            return True
        elif current_status == "failed":
            error = status.get("error", "Unknown error")
            print(f"❌ Job failed: {error}")
            return False

        time.sleep(3)


def download_result(job_id, output_path=None):
    """Download animation result"""
    if output_path is None:
        output_path = f"{job_id}_output.mp4"

    print(f"📥 Downloading result to {output_path}...")

    try:
        response = requests.get(f"{API_URL}/api/v1/download/{job_id}", stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = Path(output_path).stat().st_size
        print(f"✅ Downloaded: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return None


def list_jobs():
    """List all jobs"""
    print("📋 Listing all jobs...")

    try:
        response = requests.get(f"{API_URL}/api/v1/jobs")
        response.raise_for_status()

        result = response.json()
        jobs = result["jobs"]
        total = result["total"]

        print(f"   Total jobs: {total}")
        for job in jobs:
            print(f"   - {job['job_id']}: {job['status']}")

        return jobs
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to list jobs: {e}")
        return []


def main():
    """Main test function"""
    print("🎭 LivePortrait API Test Script")
    print("=" * 50)

    # Check health
    if not check_health():
        print("\n⚠️  Service is not healthy. Please check the service status.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Test Options:")
    print("1. Upload and animate (requires source and driving files)")
    print("2. List all jobs")
    print("3. Check specific job status")
    print("4. Download specific job result")
    print("=" * 50)

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        source_file = input("Enter source image/video path: ").strip()
        driving_file = input("Enter driving video/template path: ").strip()

        # Upload files
        source_path = upload_file(source_file, "/api/v1/upload/source")
        if not source_path:
            sys.exit(1)

        driving_path = upload_file(driving_file, "/api/v1/upload/driving")
        if not driving_path:
            sys.exit(1)

        # Create job
        job_id = create_animation(source_path, driving_path)
        if not job_id:
            sys.exit(1)

        # Wait for completion
        if wait_for_completion(job_id):
            # Download result
            download_result(job_id)

    elif choice == "2":
        list_jobs()

    elif choice == "3":
        job_id = input("Enter job ID: ").strip()
        status = check_job_status(job_id)
        if status:
            print(json.dumps(status, indent=2))

    elif choice == "4":
        job_id = input("Enter job ID: ").strip()
        output_path = input("Enter output path (or press Enter for default): ").strip()
        download_result(job_id, output_path if output_path else None)

    else:
        print("❌ Invalid choice")
        sys.exit(1)

    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()
