# Impostor Backend API

FastAPI REST API for the Impostor web game.

## ℹ️ Note

**The Discord bot has been moved to the `discord_bot/` directory for independent deployment.**

This backend now serves **only the web API** for the web frontend.

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials
   ```

3. **Run the server**:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

## 📋 Environment Variables

- `FIREBASE_SERVICE_ACCOUNT` - Firebase service account JSON (required)
- `CORS_ORIGINS` - Comma-separated list of allowed origins (default: `http://localhost:5173`)
- `PORT` - Server port (default: `8000`)
- `WEB_BASE_URL` - Web frontend URL (default: `http://localhost:5173`)

## 📦 Deployment

### Render (Free Tier)

1. Create new Web Service on Render
2. Connect your repository
3. Set root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python main.py`
6. Add environment variables
7. Deploy

**Note**: Render free tier sleeps after 15 min of inactivity. This is OK for a web API that's only called from the frontend.

### Optional: Keep Awake with UptimeRobot

To prevent sleep on Render free tier:
1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Create monitor for: `https://your-app.onrender.com/health`
3. Set interval to 5 minutes

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns API status.

### Root
```
GET /
```
Returns API information.

### Rooms API
```
GET /api/rooms/{room_id}
```
Get room details (requires proper authentication).

See `api/rooms.py` for full API documentation.

## 🛠️ Architecture

```
backend/
├── api/
│   ├── __init__.py
│   ├── models.py        # Pydantic models
│   └── rooms.py         # Room endpoints
├── config.py            # Configuration
├── firestore_client.py  # Firebase Admin SDK
├── game_logic.py        # Game logic
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── render.yaml          # Render config
└── words.txt            # Polish word list
```

## 🤖 Discord Bot

The Discord bot is now in a **separate directory**: `../discord_bot/`

See `../discord_bot/README.md` for bot deployment instructions.

## 📄 License

MIT
