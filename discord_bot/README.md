# Impostor Discord Bot

Discord bot dla gry Impostor - standalone deployment.

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the bot**:
   ```bash
   python main.py
   ```

## 📦 Deployment Options

### Option 1: Railway (Recommended - $5/month)

1. Sign up at [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select this repository
4. Set root directory to `discord_bot`
5. Add environment variables:
   - `DISCORD_TOKEN`
   - `FIREBASE_SERVICE_ACCOUNT`
   - `WEB_BASE_URL`
6. Deploy!

Railway will auto-detect the configuration from `railway.json`.

### Option 2: Oracle Cloud (Free Forever)

See `DEPLOYMENT.md` for detailed Oracle Cloud setup instructions.

### Option 3: Fly.io (~$3-5/month)

```bash
cd discord_bot
flyctl launch
flyctl secrets set DISCORD_TOKEN="your_token"
flyctl secrets set FIREBASE_SERVICE_ACCOUNT="$(cat *.json)"
flyctl secrets set WEB_BASE_URL="https://your-app.web.app"
flyctl deploy
```

### Option 4: Render Worker ($7/month)

1. Create new Worker on Render
2. Connect repository
3. Set root directory: `discord_bot`
4. Start command: `python main.py`
5. Add environment variables
6. Deploy

### Option 5: DigitalOcean App Platform ($5/month)

1. Create new App
2. Connect repository
3. Select Worker type
4. Source directory: `discord_bot`
5. Run command: `python main.py`
6. Add environment variables
7. Deploy

## 🔧 Environment Variables

- `DISCORD_TOKEN` - Your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
- `FIREBASE_SERVICE_ACCOUNT` - Firebase service account JSON (as string or file)
- `WEB_BASE_URL` - URL of your web frontend (e.g., `https://impostor.web.app`)

## 📝 Commands

The bot provides the `/impostor` slash command with the following actions:

- **create** - Create a new game room
- **join** - Join an existing room
- **start** - Start the game (host only)
- **status** - Check room status
- **reveal** - Show your word again

## 🛠️ Architecture

```
discord_bot/
├── bot/
│   ├── __init__.py
│   ├── bot.py          # Bot initialization & connection handling
│   ├── commands.py     # Discord slash commands
│   └── utils.py        # Helper functions
├── config.py           # Configuration
├── firestore_client.py # Firebase connection
├── game_logic.py       # Game logic
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── words.txt           # Polish word list
└── Dockerfile          # Docker configuration
```

## 🔥 Features

- ✅ Automatic reconnection on disconnect
- ✅ Error handling and retry logic
- ✅ Health monitoring
- ✅ DM word distribution
- ✅ Integration with Firebase Firestore
- ✅ Polish language support

## 🤝 Contributing

This bot is part of the Impostor game project. For the full project, see the parent directory.

## 📄 License

MIT

