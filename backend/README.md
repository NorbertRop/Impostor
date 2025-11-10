# Impostor Game Backend

FastAPI backend with Discord bot integration for the Impostor multiplayer game.

## Features

- 🤖 Discord bot with slash commands
- 🔥 Firebase Firestore integration
- 🌐 REST API endpoints
- 💬 DM-based word distribution
- 🎮 Hybrid Discord + Web gameplay

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
DISCORD_TOKEN=your_discord_bot_token
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
CORS_ORIGINS=https://your-project.web.app,http://localhost:5173
WEB_BASE_URL=https://your-project.web.app
PORT=8000
```

**Getting Discord Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Bot tab → Add Bot
4. Copy token

**Getting Firebase Service Account:**
1. Firebase Console → Project Settings
2. Service Accounts tab
3. Generate New Private Key
4. Copy entire JSON as single-line string

### 3. Run Locally

```bash
python main.py
```

The backend will start:
- 📡 API on `http://localhost:8000`
- 📚 Docs on `http://localhost:8000/docs`
- 🤖 Discord bot will connect

## Discord Commands

### `/impostor create`
Creates a new game room.

### `/impostor join code:ABC123`
Joins an existing room.

### `/impostor start code:ABC123`
Starts the game (host only). Sends DMs to all players.

### `/impostor status code:ABC123`
Shows room status and player list.

### `/impostor reveal code:ABC123`
Shows your word again (DM).

## API Endpoints

### `POST /api/rooms/create`
Create a new room via API.

### `POST /api/rooms/{room_id}/join`
Join a room via API.

### `GET /api/rooms/{room_id}`
Get room status.

### `POST /api/rooms/{room_id}/start`
Start the game.

### `GET /health`
Health check endpoint.

## Deployment to Render

### 1. Push to GitHub

```bash
git add backend/
git commit -m "Add backend implementation"
git push
```

### 2. Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. New → Web Service
3. Connect your GitHub repo
4. Configure:
   - Name: `impostor-backend`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

### 3. Set Environment Variables

In Render dashboard, add:
- `DISCORD_TOKEN` - Your Discord bot token
- `FIREBASE_SERVICE_ACCOUNT` - Service account JSON (single line)
- `CORS_ORIGINS` - Your frontend URL
- `WEB_BASE_URL` - Your frontend URL

### 4. Deploy

Render will auto-deploy. Check logs for:
```
✅ Firebase Admin SDK initialized successfully
✅ Discord bot logged in as YourBot
✅ Synced N command(s)
```

## Project Structure

```
backend/
├── main.py                 # Entry point
├── config.py               # Configuration
├── firestore_client.py     # Firebase setup
├── game_logic.py           # Game functions
├── words.txt               # Polish word list
├── api/
│   ├── rooms.py           # API endpoints
│   └── models.py          # Pydantic models
└── bot/
    ├── bot.py             # Discord bot setup
    ├── commands.py        # Slash commands
    └── utils.py           # Helper functions
```

## Development

### Run with auto-reload

```bash
uvicorn main:app --reload --port 8000
```

(Note: This only reloads FastAPI, not the Discord bot)

### Test API

```bash
curl http://localhost:8000/health
```

### View API Docs

Open `http://localhost:8000/docs` in browser.

## Troubleshooting

### Bot not connecting
- Check `DISCORD_TOKEN` is correct
- Verify bot has proper permissions
- Check internet connection

### Firebase errors
- Verify service account JSON is valid
- Check Firestore rules are deployed
- Ensure project ID matches

### Commands not appearing
- Wait a few minutes for Discord to sync
- Try in a different server
- Check bot has `applications.commands` scope

### DMs not working
- Users must enable DMs from server members
- Bot needs `SEND_MESSAGES` permission
- Check user privacy settings

## License

MIT

