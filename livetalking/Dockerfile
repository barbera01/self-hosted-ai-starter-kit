FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
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
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

WORKDIR /app

# Clone LiveTalking repository
RUN git clone https://github.com/lipku/LiveTalking.git . && \
    git checkout main

# Install PyTorch with CUDA 12.4 support
RUN pip install --no-cache-dir \
    torch==2.5.0 \
    torchvision==0.20.0 \
    torchaudio==2.5.0 \
    --index-url https://download.pytorch.org/whl/cu124

# Install LiveTalking dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/models \
    /app/data/avatars \
    /app/output \
    /app/input \
    /app/shared

# Download base models (optional - can be done via volume mount)
# Uncomment if you want models baked into the image
# RUN wget -O /app/models/wav2lip.pth https://your-model-source/wav2lip256.pth

# Copy our custom batch inference API
COPY batch-inference.py /app/
COPY wav2lip_batch_infer.py /app/
COPY requirements.txt /app/requirements-custom.txt
COPY download-models.sh /app/

# Install additional dependencies for our API
RUN pip install --no-cache-dir -r /app/requirements-custom.txt

# Make scripts executable
RUN chmod +x /app/download-models.sh

# Expose API port
EXPOSE 8010

# Default command - run our batch inference API
CMD ["python", "/app/batch-inference.py"]
