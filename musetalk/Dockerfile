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

# PyTorch 2.5.0 + CUDA 12.4 (matches rest of stack)
RUN pip install --no-cache-dir \
    torch==2.5.0 \
    torchvision==0.20.0 \
    torchaudio==2.5.0 \
    --index-url https://download.pytorch.org/whl/cu124

# MMLab stack required by MuseTalk pose estimation
RUN pip install --no-cache-dir openmim && \
    mim install mmengine && \
    mim install "mmcv==2.0.1" && \
    mim install "mmdet==3.1.0" && \
    mim install "mmpose==1.1.0"

# MuseTalk Python deps (skip tensorflow — not needed for inference)
RUN pip install --no-cache-dir \
    diffusers==0.27.2 \
    accelerate \
    transformers \
    omegaconf \
    einops \
    huggingface_hub \
    gdown \
    imageio[ffmpeg] \
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
    Pillow

# Install remaining MuseTalk requirements (may partially overlap above)
RUN pip install --no-cache-dir -r requirements.txt || true

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
