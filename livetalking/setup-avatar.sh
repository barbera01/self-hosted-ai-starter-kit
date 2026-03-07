#!/bin/bash
# Quick setup script for LiveTalking Avatar Video Generator

set -e

echo "=========================================="
echo "LiveTalking Avatar Video Generator Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}Creating directories...${NC}"
mkdir -p livetalking-data/models
mkdir -p livetalking-data/avatars/default
mkdir -p livetalking-data/output
mkdir -p livetalking-data/input

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and configure your settings${NC}"
fi

# Check for models
echo ""
echo -e "${YELLOW}Checking for models...${NC}"
if [ ! -f "livetalking-data/models/wav2lip.pth" ]; then
    echo -e "${RED}Model not found!${NC}"
    echo ""
    echo "Please download the wav2lip model:"
    echo ""
    echo "Option 1 - Quark Cloud Drive:"
    echo "  https://pan.quark.cn/s/83a750323ef0"
    echo "  Download: wav2lip256.pth"
    echo ""
    echo "Option 2 - Google Drive:"
    echo "  https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ"
    echo "  Download: wav2lip256.pth"
    echo ""
    echo "Then copy it to: ./livetalking-data/models/wav2lip.pth"
    echo ""
    read -p "Press Enter when you've downloaded the model, or Ctrl+C to exit..."
    
    # Check again
    if [ ! -f "livetalking-data/models/wav2lip.pth" ]; then
        echo -e "${RED}Model still not found. Please download and try again.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Model found${NC}"

# Check for avatar
echo ""
echo -e "${YELLOW}Checking for avatar...${NC}"
if [ ! -f "livetalking-data/avatars/default/avatar.jpg" ] && \
   [ ! -f "livetalking-data/avatars/default/avatar.png" ] && \
   [ ! -f "livetalking-data/avatars/default/avatar.mp4" ]; then
    echo -e "${YELLOW}No default avatar found${NC}"
    echo ""
    echo "Please add an avatar image:"
    echo "  1. Take a clear headshot photo (face forward, neutral expression)"
    echo "  2. Save as: ./livetalking-data/avatars/default/avatar.jpg"
    echo ""
    echo "Or download sample avatars from:"
    echo "  https://pan.quark.cn/s/83a750323ef0"
    echo "  Extract to: ./livetalking-data/avatars/"
    echo ""
    read -p "Press Enter when you've added an avatar, or Ctrl+C to exit..."
    
    # Check again
    if [ ! -f "livetalking-data/avatars/default/avatar.jpg" ] && \
       [ ! -f "livetalking-data/avatars/default/avatar.png" ] && \
       [ ! -f "livetalking-data/avatars/default/avatar.mp4" ]; then
        echo -e "${YELLOW}No avatar found. You can add one later.${NC}"
    else
        echo -e "${GREEN}✓ Avatar found${NC}"
    fi
else
    echo -e "${GREEN}✓ Avatar found${NC}"
fi

# Build and start service
echo ""
echo -e "${GREEN}Building LiveTalking service...${NC}"
docker compose --profile avatar build livetalking

echo ""
echo -e "${GREEN}Starting LiveTalking service...${NC}"
docker compose --profile avatar up -d livetalking

echo ""
echo -e "${GREEN}Waiting for service to be ready...${NC}"
sleep 10

# Check if service is running
if docker compose ps livetalking | grep -q "Up"; then
    echo -e "${GREEN}✓ LiveTalking is running!${NC}"
else
    echo -e "${RED}✗ LiveTalking failed to start${NC}"
    echo "Check logs with: docker compose logs livetalking"
    exit 1
fi

# Test the service
echo ""
echo -e "${GREEN}Testing service...${NC}"
if curl -s http://localhost:8010/health > /dev/null; then
    echo -e "${GREEN}✓ Service is healthy!${NC}"
else
    echo -e "${YELLOW}Service is starting up, please wait a moment...${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Generate your first video:"
echo "   curl -X POST http://localhost:8010/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"Hello! This is my first video.\", \"avatar_id\": \"default\"}'"
echo ""
echo "2. Check the API documentation:"
echo "   http://localhost:8010/docs"
echo ""
echo "3. View logs:"
echo "   docker compose logs -f livetalking"
echo ""
echo "4. Read the full guide:"
echo "   cat AVATAR_SETUP.md"
echo ""
echo "=========================================="
