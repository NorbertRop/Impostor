#!/bin/bash

# Quick start script for multiplayer mode

echo "🎮 Impostor Game - Multiplayer Mode"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  Firebase configuration not found!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Read FIREBASE_SETUP.md for setup instructions"
    echo "2. Create frontend/.env with your Firebase credentials"
    echo "3. Run this script again"
    echo ""
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Dependencies installed"
    echo ""
fi

echo "🚀 Starting development server..."
echo ""
echo "Open these URLs in different browsers/devices:"
echo "  - Local: http://localhost:5173"
echo "  - Network: Check console for network URL"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
npm run dev -- --host

