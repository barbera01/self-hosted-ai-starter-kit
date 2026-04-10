#!/usr/bin/env python3
"""
Simple Idle Animation Generator
Upload an image, get an idle animation video - that's it!
"""

import os
import sys
import subprocess
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

OUTPUT_DIR.mkdir(exist_ok=True)
SHARED_DIR.mkdir(exist_ok=True)
DRIVING_DIR.mkdir(exist_ok=True)

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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Idle Animation Generator</h1>
        <p style="text-align: center; color: #666;">
            Upload an image → Select motion → Get loopable idle video
        </p>
        
        <div class="info-box">
            <strong>💡 Perfect for MuseTalk!</strong><br>
            Create natural idle animations (blinking, breathing, head nods) to use as base videos for MuseTalk lip-sync.
        </div>
        
        <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
            <p style="font-size: 48px; margin: 0;">📸</p>
            <p>Click to upload or drag & drop your image here</p>
            <p style="color: #999; font-size: 14px;">Supports JPG, PNG (512x512 or higher recommended)</p>
            <input type="file" id="fileInput" accept="image/*">
        </div>
        
        <div class="preview" id="preview"></div>
        
        <div class="motion-selector">
            <h3>Select Idle Motion:</h3>
            <label class="motion-option selected">
                <input type="radio" name="motion" value="idle_combined" checked>
                <div>
                    <strong>🎬 Combined Idle</strong><br>
                    <small>Blink + breathing + subtle movement (recommended)</small>
                </div>
            </label>
            <label class="motion-option">
                <input type="radio" name="motion" value="blink">
                <div>
                    <strong>👁️ Blink Only</strong><br>
                    <small>Natural eye blinking</small>
                </div>
            </label>
            <label class="motion-option">
                <input type="radio" name="motion" value="breathing">
                <div>
                    <strong>💨 Breathing</strong><br>
                    <small>Subtle chest/shoulder movement</small>
                </div>
            </label>
            <label class="motion-option">
                <input type="radio" name="motion" value="head_nod">
                <div>
                    <strong>👤 Head Nod</strong><br>
                    <small>Gentle affirmative nod</small>
                </div>
            </label>
        </div>
        
        <button id="generateBtn" onclick="generateIdle()" disabled>
            Generate Idle Animation
        </button>
        
        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar">0%</div>
        </div>
        
        <div class="status" id="status"></div>
        
        <div class="result" id="result"></div>
    </div>
    
    <script>
        let selectedFile = null;
        
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
            document.getElementById('generateBtn').disabled = false;
            showStatus('Image loaded! Select a motion type and click Generate.', 'info');
        }
        
        async function generateIdle() {
            if (!selectedFile) {
                showStatus('Please select an image first', 'error');
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
                    throw new Error('Generation failed');
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
    return render_template_string(HTML_TEMPLATE)


@app.route("/generate", methods=["POST"])
def generate():
    """Generate idle animation from uploaded image"""
    try:
        # Get uploaded image
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image = request.files["image"]
        motion_type = request.form.get("motion_type", "idle_combined")

        # Save uploaded image
        job_id = str(uuid.uuid4())[:8]
        image_path = OUTPUT_DIR / f"source_{job_id}.jpg"
        image.save(image_path)

        # For now, use a simple approach - just call LivePortrait inference
        # In production, you'd have actual driving videos
        output_path = OUTPUT_DIR / f"idle_{job_id}.mp4"

        # Import LivePortrait inference
        from inference import main as liveportrait_inference

        # Create args object
        class Args:
            def __init__(self):
                self.source = str(image_path)
                self.driving = f"/app/data/driving/{motion_type}.mp4"
                self.output = str(output_path)
                self.flag_relative = True
                self.flag_do_crop = True
                self.flag_pasteback = True
                self.flag_stitching = True
                self.driving_multiplier = 0.8
                self.flag_crop_driving_video = False

        args = Args()

        # Run inference
        liveportrait_inference(args)

        # Return the video file
        return send_file(
            output_path,
            mimetype="video/mp4",
            as_attachment=True,
            download_name=f"idle_{motion_type}.mp4",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check"""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    print("🎭 Starting Simple Idle Animation Generator...")
    print("📍 Open http://localhost:8012 in your browser")
    print("💡 Upload an image, select motion, get idle video!")
    app.run(host="0.0.0.0", port=8012, debug=False)
