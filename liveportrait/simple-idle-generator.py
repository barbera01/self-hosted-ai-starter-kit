#!/usr/bin/env python3
"""
Simple Idle Animation Generator
Upload an image, get an idle animation video - that's it!
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path
from flask import Flask, request, send_file, render_template_string, jsonify
import tempfile
import uuid

# Add LivePortrait to path
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/src")

app = Flask(__name__)

# Directories
OUTPUT_DIR = Path("/app/output")
SHARED_DIR = Path("/app/shared")
DRIVING_DIR = Path("/app/data/driving")
ASSETS_DIR = Path("/app/assets/examples/driving")

OUTPUT_DIR.mkdir(exist_ok=True)
SHARED_DIR.mkdir(exist_ok=True)
DRIVING_DIR.mkdir(exist_ok=True)


# Check for available driving videos
def get_available_motions():
    """Check which motion templates are available"""
    motions = {}

    # Check standard locations
    for motion_name in ["idle_combined", "blink", "breathing", "head_nod"]:
        # Check in driving dir
        if (DRIVING_DIR / f"{motion_name}.mp4").exists():
            motions[motion_name] = str(DRIVING_DIR / f"{motion_name}.mp4")
        # Check in assets dir
        elif (ASSETS_DIR / f"{motion_name}.mp4").exists():
            motions[motion_name] = str(ASSETS_DIR / f"{motion_name}.mp4")

    # If no standard names, use any available videos from assets
    if not motions and ASSETS_DIR.exists():
        for video in ASSETS_DIR.glob("*.mp4"):
            name = video.stem
            motions[name] = str(video)

    # If still nothing, check driving dir for any videos
    if not motions:
        for video in DRIVING_DIR.glob("*.mp4"):
            name = video.stem
            motions[name] = str(video)

    return motions


# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Idle Animation Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            border-color: #4CAF50;
            background: #f9f9f9;
        }
        .upload-area.dragover {
            border-color: #4CAF50;
            background: #e8f5e9;
        }
        input[type="file"] {
            display: none;
        }
        .motion-selector {
            margin: 20px 0;
        }
        .motion-option {
            display: inline-block;
            margin: 10px;
            padding: 15px 25px;
            border: 2px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .motion-option:hover {
            border-color: #4CAF50;
            background: #f9f9f9;
        }
        .motion-option.selected {
            border-color: #4CAF50;
            background: #e8f5e9;
        }
        .motion-option input[type="radio"] {
            display: none;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .preview {
            margin: 20px 0;
            text-align: center;
        }
        .preview img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 5px;
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .status.info {
            background: #e3f2fd;
            border: 1px solid #2196F3;
            color: #1976D2;
        }
        .status.success {
            background: #e8f5e9;
            border: 1px solid #4CAF50;
            color: #2e7d32;
        }
        .status.error {
            background: #ffebee;
            border: 1px solid #f44336;
            color: #c62828;
        }
        .status.warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
        }
        .progress {
            width: 100%;
            height: 30px;
            background: #f0f0f0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
            display: none;
        }
        .progress-bar {
            height: 100%;
            background: #4CAF50;
            width: 0%;
            transition: width 0.3s;
            text-align: center;
            line-height: 30px;
            color: white;
        }
        .result {
            margin: 20px 0;
            display: none;
        }
        .result video {
            width: 100%;
            border-radius: 5px;
        }
        .info-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .error-box {
            background: #ffebee;
            border: 1px solid #f44336;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Idle Animation Generator</h1>
        <p style="text-align: center; color: #666;">
            Upload an image → Select motion → Get loopable idle video
        </p>
        
        {% if not has_motions %}
        <div class="error-box">
            <strong>⚠️ No driving videos found!</strong><br>
            Please set up driving videos first. See the instructions below.
        </div>
        {% else %}
        <div class="info-box">
            <strong>💡 Perfect for MuseTalk!</strong><br>
            Create natural idle animations (blinking, breathing, head nods) to use as base videos for MuseTalk lip-sync.
        </div>
        {% endif %}
        
        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <p style="font-size: 48px; margin: 0;">📸</p>
            <p>Click to upload or drag & drop your image here</p>
            <p style="color: #999; font-size: 14px;">Supports JPG, PNG (512x512 or higher recommended)</p>
            <input type="file" id="fileInput" accept="image/*">
        </div>
        
        <div class="preview" id="preview"></div>
        
        {% if has_motions %}
        <div class="motion-selector">
            <h3>Select Idle Motion:</h3>
            {% for motion, path in motions.items() %}
            <label class="motion-option {% if loop.first %}selected{% endif %}">
                <input type="radio" name="motion" value="{{ motion }}" {% if loop.first %}checked{% endif %}>
                <div>
                    <strong>{{ motion.replace('_', ' ').title() }}</strong>
                </div>
            </label>
            {% endfor %}
        </div>
        
        <button id="generateBtn" onclick="generateIdle()" disabled>
            Generate Idle Animation
        </button>
        {% else %}
        <div class="info-box">
            <h3>📋 Setup Instructions:</h3>
            <p>To use this service, you need driving videos (motion templates).</p>
            <ol>
                <li>Download example videos from <a href="https://github.com/KlingAIResearch/LivePortrait/tree/main/assets/examples/driving" target="_blank">LivePortrait GitHub</a></li>
                <li>Place them in the shared directory or rebuild the container</li>
                <li>Or run: <code>docker compose exec liveportrait /app/download-driving-videos.sh</code></li>
            </ol>
        </div>
        {% endif %}
        
        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar">0%</div>
        </div>
        
        <div class="status" id="status"></div>
        
        <div class="result" id="result"></div>
    </div>
    
    <script>
        let selectedFile = null;
        const hasMotions = {{ 'true' if has_motions else 'false' }};
        
        // File input handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            handleFile(e.target.files[0]);
        });
        
        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', function(e) {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFile(e.dataTransfer.files[0]);
        });
        
        // Motion selector
        document.querySelectorAll('.motion-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.motion-option').forEach(o => o.classList.remove('selected'));
                this.classList.add('selected');
                this.querySelector('input').checked = true;
            });
        });
        
        function handleFile(file) {
            if (!file || !file.type.startsWith('image/')) {
                showStatus('Please select an image file', 'error');
                return;
            }
            
            selectedFile = file;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('preview').innerHTML = 
                    '<img src="' + e.target.result + '" alt="Preview">';
            };
            reader.readAsDataURL(file);
            
            // Enable generate button
            if (hasMotions) {
                document.getElementById('generateBtn').disabled = false;
                showStatus('Image loaded! Select a motion type and click Generate.', 'info');
            } else {
                showStatus('Image loaded, but no driving videos available. Please set up driving videos first.', 'warning');
            }
        }
        
        async function generateIdle() {
            if (!selectedFile) {
                showStatus('Please select an image first', 'error');
                return;
            }
            
            if (!hasMotions) {
                showStatus('No driving videos available. Please set up driving videos first.', 'error');
                return;
            }
            
            const motion = document.querySelector('input[name="motion"]:checked').value;
            const formData = new FormData();
            formData.append('image', selectedFile);
            formData.append('motion_type', motion);
            
            // Show progress
            document.getElementById('progress').style.display = 'block';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('result').style.display = 'none';
            showStatus('Uploading and processing... This may take 30-60 seconds.', 'info');
            
            try {
                // Simulate progress
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += 5;
                    if (progress <= 90) {
                        updateProgress(progress);
                    }
                }, 1000);
                
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(progressInterval);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Generation failed');
                }
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                updateProgress(100);
                
                // Show result
                document.getElementById('result').innerHTML = 
                    '<h3>✅ Idle Animation Ready!</h3>' +
                    '<video controls autoplay loop><source src="' + url + '" type="video/mp4"></video>' +
                    '<br><br>' +
                    '<a href="' + url + '" download="idle_animation.mp4" style="display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Download Video</a>';
                document.getElementById('result').style.display = 'block';
                
                showStatus('Success! Your idle animation is ready. Perfect for MuseTalk!', 'success');
                
                setTimeout(() => {
                    document.getElementById('progress').style.display = 'none';
                }, 1000);
                
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                document.getElementById('progress').style.display = 'none';
            } finally {
                document.getElementById('generateBtn').disabled = false;
            }
        }
        
        function updateProgress(percent) {
            const bar = document.getElementById('progressBar');
            bar.style.width = percent + '%';
            bar.textContent = percent + '%';
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve the simple web UI"""
    motions = get_available_motions()
    return render_template_string(
        HTML_TEMPLATE, has_motions=len(motions) > 0, motions=motions
    )


@app.route("/health")
def health():
    """Health check"""
    motions = get_available_motions()
    return jsonify(
        {
            "status": "healthy",
            "motions_available": len(motions),
            "motions": list(motions.keys()),
        }
    )


@app.route("/generate", methods=["POST"])
def generate():
    """Generate idle animation from uploaded image"""
    try:
        # Get uploaded image
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image = request.files["image"]
        motion_type = request.form.get("motion_type", "idle_combined")

        # Check if motion template exists
        motions = get_available_motions()
        if not motions:
            return jsonify(
                {
                    "error": "No driving videos available. Please set up driving videos first."
                }
            ), 500

        if motion_type not in motions:
            # Use first available motion as fallback
            motion_type = list(motions.keys())[0]
            print(f"⚠️  Requested motion not found, using: {motion_type}")

        driving_video = motions[motion_type]
        print(f"Using driving video: {driving_video}")

        # Save uploaded image
        job_id = str(uuid.uuid4())[:8]
        image_path = OUTPUT_DIR / f"source_{job_id}.jpg"
        image.save(image_path)
        print(f"Saved source image: {image_path}")

        # Output path
        output_path = OUTPUT_DIR / f"idle_{job_id}.mp4"

        # Import and run LivePortrait inference
        print("Loading LivePortrait inference...")

        # Use subprocess to call inference.py directly
        import subprocess

        cmd = [
            "python",
            "/app/inference.py",
            "-s",
            str(image_path),
            "-d",
            driving_video,
            "-o",
            str(output_path),
            "--flag_relative",
            "--flag_do_crop",
            "--flag_pasteback",
            "--flag_stitching",
            "--driving_multiplier",
            "0.8",
        ]

        print(f"Running LivePortrait inference...")
        print(f"  Source: {image_path}")
        print(f"  Driving: {driving_video}")
        print(f"  Output: {output_path}")
        print(f"  Command: {' '.join(cmd)}")

        # Run inference
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            raise Exception(f"LivePortrait inference failed: {result.stderr}")

        # Check if output was created
        if not output_path.exists():
            raise Exception("Output video was not created")

        print(f"✅ Generated: {output_path}")

        # Return the video file
        return send_file(
            output_path,
            mimetype="video/mp4",
            as_attachment=True,
            download_name=f"idle_{motion_type}.mp4",
        )

    except Exception as e:
        print(f"❌ Error generating animation: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🎭 Starting Simple Idle Animation Generator...")

    # Check for driving videos
    motions = get_available_motions()
    if motions:
        print(f"✅ Found {len(motions)} motion templates:")
        for name, path in motions.items():
            print(f"   - {name}: {path}")
    else:
        print("⚠️  Warning: No driving videos found!")
        print("   The web interface will show setup instructions.")
        print("   Run: /app/download-driving-videos.sh to set up driving videos")

    print("")
    print("📍 Open http://localhost:8012 in your browser")
    print("💡 Upload an image, select motion, get idle video!")

    app.run(host="0.0.0.0", port=8012, debug=False)
