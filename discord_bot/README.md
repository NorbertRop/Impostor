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
## 🔧 Environment Variables

- `DISCORD_TOKEN` - Your Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
- `FIREBASE_SERVICE_ACCOUNT` - Firebase service account JSON (as string or file)

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

