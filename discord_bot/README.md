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
- **join** - Join an existing room (requires code first time)
- **start** - Start the game (host only, code optional after first join)
- **status** - Check room status (code optional after first join)
- **reveal** - Show your word again (code optional after first join)
- **restart** - Restart the game with new roles (code optional after first join)

### 💡 Room Memory Feature

The bot automatically remembers which room you're currently in! After you create or join a room, you don't need to provide the room code in subsequent commands:

```bash
# First time - provide the code
/impostor join code:ABC123

# Later - no code needed!
/impostor status
/impostor reveal
/impostor start

# Want to switch rooms? Just provide a new code
/impostor join code:XYZ789
```

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
├── firestore_listener.py # Firestore change listener
├── game_logic.py       # Game logic
├── user_sessions.py    # User session management
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── words.txt           # Polish word list
└── Dockerfile          # Docker configuration
```

## 🔥 Features

- ✅ Automatic reconnection on disconnect
- ✅ Error handling and retry logic
- ✅ Health monitoring
- ✅ DM word distribution with random speaking order
- ✅ Integration with Firebase Firestore
- ✅ Polish language support
- ✅ Room memory - no need to repeat room codes
- ✅ Persistent user sessions across bot restarts
- ✅ Random speaking order for fair gameplay

## 🤝 Contributing

This bot is part of the Impostor game project. For the full project, see the parent directory.

## 📄 License

MIT

