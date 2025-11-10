#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to discord_bot directory
cd ~/impostor/discord_bot

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker-compose down 2>/dev/null || docker stop impostor-discord-bot 2>/dev/null || true

# Build new image
echo "🔨 Building Docker image..."
docker build -t impostor-discord-bot .

# Start container
echo "▶️ Starting container..."
docker run -d \
  --name impostor-discord-bot \
  --restart unless-stopped \
  --env-file .env \
  impostor-discord-bot

echo "✅ Deployment complete!"
echo "📊 Check logs with: docker logs -f impostor-discord-bot"

