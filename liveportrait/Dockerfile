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
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

WORKDIR /app

# Clone LivePortrait repository
RUN git clone https://github.com/KlingAIResearch/LivePortrait.git . && \
    git checkout main

# Install PyTorch with CUDA 12.4 support
RUN pip install --no-cache-dir \
    torch==2.5.0 \
    torchvision==0.20.0 \
    torchaudio==2.5.0 \
    --index-url https://download.pytorch.org/whl/cu124

# Install LivePortrait dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for our simple web UI
RUN pip install --no-cache-dir \
    flask \
    python-multipart

# Create necessary directories
RUN mkdir -p /app/pretrained_weights \
    /app/data/source \
    /app/data/driving \
    /app/output \
    /app/input \
    /app/shared

# Copy our simple web UI
COPY simple-idle-generator.py /app/
COPY download-models.sh /app/

# Make scripts executable
RUN chmod +x /app/download-models.sh

# Expose API port
EXPOSE 8012

# Default command - run our simple web UI
CMD ["python", "/app/simple-idle-generator.py"]
