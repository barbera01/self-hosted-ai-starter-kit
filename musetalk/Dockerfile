FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Python aliases
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

WORKDIR /app

# Clone MuseTalk v1.5
RUN git clone https://github.com/TMElyralab/MuseTalk.git . && \
    git checkout main

# PyTorch 2.0.1 + CUDA 11.8 wheels.
# Reason: mmcv 2.0.1 only has a pre-built cp310 wheel on the OpenMMLab CDN for
# the cu118/torch2.0 combination.  CUDA is forward-compatible so cu118 wheels
# run without issues on a CUDA 12.4 GPU.
RUN pip install --no-cache-dir \
    torch==2.0.1 \
    torchvision==0.15.2 \
    torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

# MMLab stack — use the OpenMMLab CDN directly so we get the pre-built wheel
# instead of triggering a slow/broken C++17 source compilation.
# Verified: cu118/torch2.0 index contains mmcv-2.0.1-cp310-cp310-manylinux1_x86_64.whl
RUN pip install --no-cache-dir openmim mmengine && \
    pip install --no-cache-dir \
        "mmcv==2.0.1" \
        -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html && \
    pip install --no-cache-dir \
        "mmdet==3.1.0" \
        "mmpose==1.1.0"

# MuseTalk Python deps (tensorflow skipped — not needed for inference)
RUN pip install --no-cache-dir \
    diffusers==0.27.2 \
    accelerate \
    transformers \
    omegaconf \
    einops \
    huggingface_hub \
    gdown \
    "imageio[ffmpeg]" \
    librosa \
    soundfile \
    fastapi \
    uvicorn \
    python-multipart \
    aiofiles \
    aiohttp \
    pydantic \
    tqdm \
    opencv-python-headless \
    Pillow \
    pyyaml

# Install remaining MuseTalk requirements (overlaps fine, tensorflow + torch skipped)
RUN grep -v -E "^(tensorflow|torch)" requirements.txt \
    | pip install --no-cache-dir -r /dev/stdin || true

# Directories
RUN mkdir -p /app/models \
    /app/data/avatars \
    /app/output_jobs \
    /app/input \
    /app/shared

# Copy our service files
COPY batch-inference.py /app/
COPY download-models.sh /app/
RUN chmod +x /app/download-models.sh

EXPOSE 8011

CMD ["python", "/app/batch-inference.py"]
