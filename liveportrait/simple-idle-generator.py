#!/usr/bin/env python3
"""
Idle Animation Generator — optimised for MuseTalk base video production.

Generates a natural-looking idle animation from a portrait image using
LivePortrait, ready to feed into MuseTalk for lip-sync.
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path
from flask import Flask, request, send_file, render_template_string, jsonify
import uuid

# Add LivePortrait to path
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/src")

app = Flask(__name__)

# Directories
OUTPUT_DIR = Path("/app/output")
DRIVING_DIR = Path("/app/data/driving")
ASSETS_DIR = Path("/app/assets/examples/driving")

OUTPUT_DIR.mkdir(exist_ok=True)
DRIVING_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Presets — tuned for MuseTalk base video production
#
# Key decisions:
#   animation_region = "pose"   → head sway only; MuseTalk handles expressions
#   flag_normalize_lip          → forces mouth closed so MuseTalk starts neutral
#   driving_multiplier          → scales motion magnitude (lower = more subtle)
#   driving_smooth_obs_variance → temporal smoothing (higher = smoother/floatier)
#   driving video               → d9.mp4 / d3.mp4 are natural talking-head clips;
#                                  d0.mp4 is longer but has bigger expressions
# ---------------------------------------------------------------------------
PRESETS = {
    "musetalk_ready": {
        "label": "MuseTalk Ready",
        "description": "Subtle head sway, mouth closed. Best starting point for lip-sync.",
        "driving": "d9.mp4",
        "animation_region": "pose",
        "driving_multiplier": 0.4,
        "driving_smooth_observation_variance": 1e-5,
        "flag_normalize_lip": True,
    },
    "natural_idle": {
        "label": "Natural Idle",
        "description": "Gentle full-face motion — blinks, micro-expressions, head sway.",
        "driving": "d9.mp4",
        "animation_region": "all",
        "driving_multiplier": 0.35,
        "driving_smooth_observation_variance": 1e-5,
        "flag_normalize_lip": True,
    },
    "head_sway": {
        "label": "Head Sway",
        "description": "Slightly more pronounced head movement for a lively feel.",
        "driving": "d3.mp4",
        "animation_region": "pose",
        "driving_multiplier": 0.5,
        "driving_smooth_observation_variance": 5e-6,
        "flag_normalize_lip": True,
    },
    "expressive": {
        "label": "Expressive",
        "description": "More visible facial motion — useful if MuseTalk result looks too static.",
        "driving": "d0.mp4",
        "animation_region": "all",
        "driving_multiplier": 0.45,
        "driving_smooth_observation_variance": 1e-5,
        "flag_normalize_lip": False,
    },
}


def resolve_driving_video(filename: str) -> str | None:
    """Find a driving video by filename in known locations."""
    for base in [DRIVING_DIR, ASSETS_DIR]:
        p = base / filename
        if p.exists():
            return str(p)
    return None


def any_driving_video_available() -> bool:
    for preset in PRESETS.values():
        if resolve_driving_video(preset["driving"]):
            return True
    return False


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Idle Animation Generator</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            max-width: 820px;
            margin: 40px auto;
            padding: 20px;
            background: #f0f2f5;
        }
        .container {
            background: white;
            padding: 32px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }
        h1 { color: #222; text-align: center; margin-bottom: 4px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 24px; font-size: 14px; }

        /* upload */
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 36px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #2563eb;
            background: #eff6ff;
        }
        input[type="file"] { display: none; }
        .preview { margin: 16px 0; text-align: center; }
        .preview img { max-height: 260px; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.15); }

        /* presets */
        .presets { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }
        .preset-card {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .preset-card:hover { border-color: #93c5fd; background: #f0f9ff; }
        .preset-card.selected { border-color: #2563eb; background: #eff6ff; }
        .preset-card input[type="radio"] { position: absolute; opacity: 0; }
        .preset-card .preset-name { font-weight: bold; font-size: 15px; color: #1e3a5f; }
        .preset-card .preset-desc { font-size: 12px; color: #6b7280; margin-top: 4px; line-height: 1.4; }

        /* intensity slider */
        .slider-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 16px 0 8px;
        }
        .slider-row label { font-size: 13px; color: #374151; white-space: nowrap; }
        .slider-row input[type="range"] { flex: 1; }
        .slider-row .slider-val {
            font-size: 13px;
            font-weight: bold;
            color: #2563eb;
            width: 40px;
            text-align: right;
        }
        .slider-hint { font-size: 11px; color: #9ca3af; margin-bottom: 4px; }

        /* button */
        button#generateBtn {
            background: #2563eb;
            color: white;
            border: none;
            padding: 14px 28px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            transition: background 0.2s;
        }
        button#generateBtn:hover { background: #1d4ed8; }
        button#generateBtn:disabled { background: #9ca3af; cursor: not-allowed; }

        /* status / progress */
        .status {
            margin: 16px 0;
            padding: 12px 16px;
            border-radius: 6px;
            display: none;
            font-size: 14px;
        }
        .status.info    { background: #eff6ff; border: 1px solid #93c5fd; color: #1e40af; }
        .status.success { background: #f0fdf4; border: 1px solid #86efac; color: #166534; }
        .status.error   { background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; }
        .status.warning { background: #fffbeb; border: 1px solid #fcd34d; color: #92400e; }
        .progress {
            width: 100%; height: 28px; background: #f3f4f6;
            border-radius: 14px; overflow: hidden; margin: 16px 0; display: none;
        }
        .progress-bar {
            height: 100%; background: #2563eb; width: 0%;
            transition: width 0.4s; text-align: center;
            line-height: 28px; color: white; font-size: 13px;
        }

        /* result */
        .result { margin: 20px 0; display: none; }
        .result video { width: 100%; border-radius: 8px; }
        .dl-btn {
            display: inline-block; margin-top: 12px;
            padding: 10px 22px; background: #16a34a;
            color: white; text-decoration: none;
            border-radius: 6px; font-size: 14px;
        }

        /* info / error box */
        .info-box  { background: #fffbeb; border: 1px solid #fcd34d; padding: 14px; border-radius: 6px; margin: 16px 0; }
        .error-box { background: #fef2f2; border: 1px solid #fca5a5; padding: 14px; border-radius: 6px; margin: 16px 0; }
    </style>
</head>
<body>
<div class="container">
    <h1>🎭 Idle Animation Generator</h1>
    <p class="subtitle">Portrait image → natural idle animation → ready for MuseTalk lip-sync</p>

    {% if not has_driving %}
    <div class="error-box">
        <strong>⚠️ No driving videos found.</strong><br>
        Run inside the container: <code>bash /app/download-driving-videos.sh</code>
    </div>
    {% else %}
    <div class="info-box">
        <strong>💡 MuseTalk tip:</strong> Use <em>MuseTalk Ready</em> or <em>Natural Idle</em> — they animate only the
        head pose with the mouth closed, giving MuseTalk a clean neutral base to add lip sync onto.
    </div>
    {% endif %}

    <!-- Upload -->
    <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
        <p style="font-size:40px;margin:0">📸</p>
        <p>Click to upload or drag &amp; drop your portrait image</p>
        <p style="color:#9ca3af;font-size:13px">JPG or PNG — square crop with a clear face works best</p>
        <input type="file" id="fileInput" accept="image/*">
    </div>
    <div class="preview" id="preview"></div>

    {% if has_driving %}
    <!-- Preset picker -->
    <h3 style="margin-bottom:8px">Motion preset:</h3>
    <div class="presets">
        {% for key, p in presets.items() %}
        <label class="preset-card {% if loop.first %}selected{% endif %}">
            <input type="radio" name="preset" value="{{ key }}" {% if loop.first %}checked{% endif %}>
            <div class="preset-name">{{ p.label }}</div>
            <div class="preset-desc">{{ p.description }}</div>
        </label>
        {% endfor %}
    </div>

    <!-- Motion intensity slider -->
    <div class="slider-row">
        <label>Motion intensity:</label>
        <input type="range" id="intensitySlider" min="10" max="100" value="40" step="5"
               oninput="document.getElementById('intensityVal').textContent = this.value + '%'">
        <span class="slider-val" id="intensityVal">40%</span>
    </div>
    <p class="slider-hint">Lower = more subtle (better for MuseTalk). Higher = more visible movement.</p>

    <button id="generateBtn" onclick="generateIdle()" disabled>
        Generate Idle Animation
    </button>
    {% endif %}

    <div class="progress" id="progress"><div class="progress-bar" id="progressBar">0%</div></div>
    <div class="status" id="status"></div>
    <div class="result" id="result"></div>
</div>

<script>
    let selectedFile = null;
    const hasMotions = {{ 'true' if has_driving else 'false' }};

    document.getElementById('fileInput').addEventListener('change', e => handleFile(e.target.files[0]));

    const uploadArea = document.getElementById('uploadArea');
    uploadArea.addEventListener('dragover',  e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', e => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', e => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFile(e.dataTransfer.files[0]);
    });

    document.querySelectorAll('.preset-card').forEach(card => {
        card.addEventListener('click', function() {
            document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            this.querySelector('input').checked = true;
        });
    });

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            showStatus('Please select an image file.', 'error');
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = e => {
            document.getElementById('preview').innerHTML =
                '<img src="' + e.target.result + '" alt="Preview">';
        };
        reader.readAsDataURL(file);
        if (hasMotions) {
            document.getElementById('generateBtn').disabled = false;
            showStatus('Image loaded — choose a preset and click Generate.', 'info');
        }
    }

    async function generateIdle() {
        if (!selectedFile) { showStatus('Please select an image first.', 'error'); return; }

        const preset   = document.querySelector('input[name="preset"]:checked').value;
        const intensity = parseInt(document.getElementById('intensitySlider').value);

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('preset', preset);
        formData.append('intensity', intensity);

        document.getElementById('progress').style.display = 'block';
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('result').style.display = 'none';
        showStatus('Processing… this takes ~30–60 s on GPU.', 'info');

        let pct = 0;
        const ticker = setInterval(() => {
            pct = Math.min(pct + 3, 88);
            updateProgress(pct);
        }, 1000);

        try {
            const resp = await fetch('/generate', { method: 'POST', body: formData });
            clearInterval(ticker);
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || 'Generation failed');
            }
            const blob = await resp.blob();
            const url  = URL.createObjectURL(blob);
            updateProgress(100);
            document.getElementById('result').innerHTML =
                '<h3>✅ Idle Animation Ready!</h3>' +
                '<video controls autoplay loop><source src="' + url + '" type="video/mp4"></video><br>' +
                '<a class="dl-btn" href="' + url + '" download="idle_animation.mp4">⬇ Download MP4</a>';
            document.getElementById('result').style.display = 'block';
            showStatus('Done! Download the video and feed it into MuseTalk.', 'success');
            setTimeout(() => document.getElementById('progress').style.display = 'none', 1200);
        } catch (err) {
            clearInterval(ticker);
            showStatus('Error: ' + err.message, 'error');
            document.getElementById('progress').style.display = 'none';
        } finally {
            document.getElementById('generateBtn').disabled = false;
        }
    }

    function updateProgress(p) {
        const bar = document.getElementById('progressBar');
        bar.style.width = p + '%';
        bar.textContent = p + '%';
    }
    function showStatus(msg, type) {
        const el = document.getElementById('status');
        el.textContent = msg;
        el.className = 'status ' + type;
        el.style.display = 'block';
    }
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        has_driving=any_driving_video_available(),
        presets=PRESETS,
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "driving_available": any_driving_video_available(),
            "presets": list(PRESETS.keys()),
        }
    )


@app.route("/generate", methods=["POST"])
def generate():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image = request.files["image"]
        preset_key = request.form.get("preset", "musetalk_ready")
        intensity = int(request.form.get("intensity", 40))  # 10–100

        if preset_key not in PRESETS:
            preset_key = "musetalk_ready"
        preset = PRESETS[preset_key]

        # Resolve driving video
        driving_video = resolve_driving_video(preset["driving"])
        if not driving_video:
            # fallback: any available mp4
            for base in [DRIVING_DIR, ASSETS_DIR]:
                mp4s = list(base.glob("*.mp4"))
                if mp4s:
                    driving_video = str(mp4s[0])
                    break
        if not driving_video:
            return jsonify(
                {"error": "No driving video found. Run download-driving-videos.sh"}
            ), 500

        # Scale the preset's base multiplier by the UI intensity slider (10–100 → 0.25–1.0 range)
        # We keep a ceiling so even 100% doesn't look ridiculous
        base_multiplier = preset["driving_multiplier"]
        scaled_multiplier = base_multiplier * (
            intensity / 40.0
        )  # 40% = 1× preset default
        scaled_multiplier = round(max(0.1, min(scaled_multiplier, 1.2)), 3)

        job_id = str(uuid.uuid4())[:8]
        image_path = OUTPUT_DIR / f"source_{job_id}.jpg"
        image.save(image_path)

        output_dir = OUTPUT_DIR / f"job_{job_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "python",
            "/app/inference.py",
            "-s",
            str(image_path),
            "-d",
            driving_video,
            "-o",
            str(output_dir),
            "--flag-relative-motion",
            "--flag-do-crop",
            "--flag-pasteback",
            "--flag-stitching",
            "--animation-region",
            preset["animation_region"],
            "--driving-multiplier",
            str(scaled_multiplier),
            "--driving-smooth-observation-variance",
            str(preset["driving_smooth_observation_variance"]),
        ]

        # Normalize lip (force mouth closed) — critical for MuseTalk presets
        if preset["flag_normalize_lip"]:
            cmd.append("--flag-normalize-lip")

        print(
            f"[{job_id}] preset={preset_key}  intensity={intensity}%  multiplier={scaled_multiplier}"
        )
        print(f"[{job_id}] driving={driving_video}")
        print(f"[{job_id}] cmd: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            raise Exception(f"LivePortrait inference failed:\n{result.stderr[-2000:]}")

        # Pick the final pasted-back result (not the _concat side-by-side)
        mp4s = [
            f for f in output_dir.glob("*.mp4") if not f.name.endswith("_concat.mp4")
        ]
        if not mp4s:
            mp4s = list(output_dir.glob("*.mp4"))
        if not mp4s:
            raise Exception(
                f"No output video in {output_dir}.\nstdout: {result.stdout[-1000:]}"
            )

        output_path = mp4s[0]
        print(f"[{job_id}] ✅ Done: {output_path}")

        return send_file(
            output_path,
            mimetype="video/mp4",
            as_attachment=True,
            download_name=f"idle_{preset_key}.mp4",
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🎭 Idle Animation Generator — MuseTalk optimised")
    print(f"   Driving dir : {DRIVING_DIR}")
    print(f"   Assets dir  : {ASSETS_DIR}")
    print(f"   Output dir  : {OUTPUT_DIR}")
    print(f"   Presets     : {', '.join(PRESETS.keys())}")
    print(f"   Driving OK  : {any_driving_video_available()}")
    print()
    app.run(host="0.0.0.0", port=8012, debug=False)
