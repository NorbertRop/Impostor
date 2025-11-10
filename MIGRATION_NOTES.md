# Bot Migration to Separate Directory

## ✅ Changes Made

The Discord bot has been moved from `backend/bot/` to a standalone `discord_bot/` directory for independent deployment.

## 📁 New Structure

```
discord_bot/
├── bot/                    # Bot modules
│   ├── __init__.py
│   ├── bot.py             # Bot initialization
│   ├── commands.py        # Slash commands
│   └── utils.py           # Helper functions
├── main.py                # Entry point
├── config.py              # Configuration
├── firestore_client.py    # Firebase connection
├── game_logic.py          # Game logic (shared)
├── words.txt              # Polish word list
├── requirements.txt       # Dependencies
├── Dockerfile             # Docker config
├── Procfile               # Heroku/Railway config
├── railway.json           # Railway config
├── runtime.txt            # Python version
├── .gitignore             # Git ignore rules
└── README.md              # Deployment guide
```

## 🎯 Benefits

1. **Separate Deployment**: Bot can now be deployed independently from the API
2. **No Sleep Issues**: Deploy bot on always-on service (Railway, Oracle Cloud, etc.)
3. **Cleaner Architecture**: Clear separation of concerns
4. **Easier Scaling**: Scale bot and API independently
5. **Flexible Hosting**: Choose different platforms for each service

## 🚀 Deployment Options

### Discord Bot (`discord_bot/`)
- **Railway**: $5/month - No sleep, easy deployment
- **Oracle Cloud**: FREE - Forever free tier, requires VPS skills
- **Fly.io**: ~$3-5/month - Pay as you go
- **Render Worker**: $7/month - Simple deployment
- **DigitalOcean**: $5/month - Reliable hosting

### API Backend (`backend/`)
- **Render**: FREE - Can sleep (OK for web API)
- Add UptimeRobot to keep it awake if needed

## 📋 Migration Checklist

- [x] Create `discord_bot/` directory
- [x] Copy bot modules to `discord_bot/bot/`
- [x] Copy shared dependencies (config, firestore, game_logic, words)
- [x] Create standalone entry point (`main.py`)
- [x] Create bot-specific `requirements.txt`
- [x] Create deployment configs (Dockerfile, Procfile, etc.)
- [x] Update main README
- [x] Create bot README with deployment instructions
- [ ] Deploy bot to chosen platform
- [ ] Update backend to remove bot code (optional cleanup)
- [ ] Test bot independently

## 🔧 Backend Changes (Optional)

The `backend/` directory can now be simplified:
- Remove `backend/bot/` directory (if desired)
- Remove `backend/bot_main.py` (if desired)
- Remove bot-related configs (`Dockerfile.bot`, `fly.bot.toml`, etc.)
- Update `backend/requirements.txt` to remove `discord.py`

The backend API will continue to work for web clients without the bot.

## 📝 Environment Variables

Both services need:
- `DISCORD_TOKEN` - Bot only
- `FIREBASE_SERVICE_ACCOUNT` - Both
- `WEB_BASE_URL` - Both
- `PORT` - Backend API only

## 🧪 Testing

1. **Test bot locally**:
   ```bash
   cd discord_bot
   pip install -r requirements.txt
   python main.py
   ```

2. **Test backend locally**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Test integration**:
   - Create room via `/impostor create` in Discord
   - Join from web frontend
   - Start game and verify both receive updates

## 🆘 Troubleshooting

### Bot not connecting
- Check `DISCORD_TOKEN` environment variable
- Verify Firebase credentials are correct
- Check bot has necessary Discord permissions

### Commands not showing
- Bot may need to re-sync commands: wait 1-2 minutes
- Check bot has `applications.commands` scope
- Try kicking and re-inviting bot to server

### Firebase errors
- Ensure `FIREBASE_SERVICE_ACCOUNT` is valid JSON
- Check Firestore rules allow bot access
- Verify Firebase project ID matches

## 📚 Related Documentation

- `discord_bot/README.md` - Bot deployment guide
- `backend/README.md` - API deployment guide  
- `DISCORD_SETUP.md` - Discord bot setup
- `FIREBASE_SETUP.md` - Firebase configuration

---

**Date**: November 2024
**Status**: Complete ✅

