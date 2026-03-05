#!/bin/bash
echo "=== Generating Secure Keys for .env ==="
echo ""
echo "N8N_ENCRYPTION_KEY=$(openssl rand -base64 24)"
echo "N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -base64 64)"
echo "KOKORO_API_KEY=kokoro-$(openssl rand -hex 16)"
echo ""
echo "Copy these values to your .env file"
