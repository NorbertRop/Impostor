# Discord Bot Setup Guide

Complete guide to setting up the Discord bot for the Impostor game.

## Prerequisites

- Discord account
- Server where you have admin permissions (or create one)
- Backend code ready to deploy

## Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Enter name: "Impostor Game" (or your choice)
4. Click **Create**

## Step 2: Create Bot

1. In your application, go to **Bot** tab (left sidebar)
2. Click **Add Bot** → **Yes, do it!**
3. Under "Privileged Gateway Intents", enable:
   - ✅ **Message Content Intent**
4. Under "Bot Permissions", select:
   - ✅ Send Messages
   - ✅ Use Slash Commands
5. Click **Reset Token** and **Copy** the token
   - ⚠️ **Save this token securely** - you'll need it for deployment

## Step 3: Configure OAuth2

1. Go to **OAuth2** tab
2. In **OAuth2 URL Generator**:
   - Under "Scopes", select:
     - ✅ `bot`
     - ✅ `applications.commands`
   - Under "Bot Permissions", select:
     - ✅ Send Messages
     - ✅ Read Messages/View Channels
     - ✅ Use Slash Commands
3. Copy the generated URL at the bottom

## Step 4: Invite Bot to Server

1. Paste the OAuth2 URL from Step 3 into your browser
2. Select your server from dropdown
3. Click **Authorize**
4. Complete the captcha
5. Bot should now appear in your server!

## Step 5: Test Bot (Local)

Before deploying, test locally:

1. Create `backend/.env`:
```env
DISCORD_TOKEN=your_bot_token_from_step_2
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
CORS_ORIGINS=http://localhost:5173
WEB_BASE_URL=http://localhost:5173
```

2. Run backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

3. In Discord, type `/` and you should see:
   - `/impostor` command appear in the list

4. Test commands:
```
/impostor create
/impostor join code:ABC123
/impostor status code:ABC123
```

## Step 6: Deploy to Render

See [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) for full deployment guide.

Quick version:

1. Push code to GitHub
2. Create Render Web Service
3. Set environment variables:
   - `DISCORD_TOKEN` - Token from Step 2
   - `FIREBASE_SERVICE_ACCOUNT` - Service account JSON
   - `CORS_ORIGINS` - Your Firebase Hosting URL
   - `WEB_BASE_URL` - Your Firebase Hosting URL
4. Deploy

## Commands Reference

### `/impostor create`
Creates a new game room.

**Response:**
- Room code (e.g., ABC123)
- Web link
- Instructions for starting

**Example:**
```
/impostor create
```

### `/impostor join code:ABC123`
Joins an existing room.

**Parameters:**
- `code` - 6-character room code

**Example:**
```
/impostor join code:ABC123
```

### `/impostor start code:ABC123`
Starts the game (host only).

**Parameters:**
- `code` - Your room code

**What happens:**
- Bot assigns impostor
- DMs each player their word/role
- Updates room status

**Example:**
```
/impostor start code:ABC123
```

### `/impostor status code:ABC123`
Shows room status and player list.

**Parameters:**
- `code` - Room code to check

**Shows:**
- Current status
- Player list
- Ready count

**Example:**
```
/impostor status code:ABC123
```

### `/impostor reveal code:ABC123`
Re-sends your word in DM.

**Parameters:**
- `code` - Your room code

**Use when:**
- You closed the DM
- You forgot your word
- You need to check your role

**Example:**
```
/impostor reveal code:ABC123
```

## Troubleshooting

### Bot not responding

**Check:**
- Bot is online (green dot in member list)
- Bot has proper permissions
- Commands are synced (wait 5 minutes after deployment)

**Solution:**
- Restart backend service
- Check Render logs for errors
- Re-invite bot with new OAuth URL

### Commands not appearing

**Reasons:**
- Commands take time to sync (up to 1 hour)
- Missing `applications.commands` scope
- Bot not in server

**Solution:**
- Wait 5-10 minutes
- Re-invite bot with correct permissions
- Check bot is online

### Can't receive DMs

**Reasons:**
- User has DMs disabled from server members
- Privacy settings

**Solution:**
1. Right-click server name
2. Privacy Settings
3. Enable "Allow direct messages from server members"

### "Only host can start game" error

**Cause:**
- You're not the person who created the room

**Solution:**
- Ask the host to run `/impostor start`
- Or create your own room with `/impostor create`

### Bot goes offline

**Causes:**
- Render free tier sleeps after 15min inactivity
- Deployment failed
- Environment variables missing

**Solution:**
- Visit backend URL to wake it up
- Check Render logs
- Verify all env vars are set

## Bot Permissions Explained

### Required Permissions

**Send Messages**
- Needed to respond to commands
- Send room codes and status

**Read Messages/View Channels**
- See when commands are used
- Access channel information

**Use Slash Commands**
- Register and use `/impostor` commands

### Privileged Intents

**Message Content Intent**
- Required for bot to function properly
- Must be enabled in Developer Portal

## Privacy & Security

### What the bot stores:
- Discord user IDs (for game matching)
- Display names (shown in game)
- Room codes (temporary)

### What the bot DOESN'T store:
- Message content
- Personal information
- Anything outside game context

### Data retention:
- Rooms expire after inactivity
- No permanent user data storage
- All data in Firebase (can be deleted)

## Advanced: Multiple Servers

The bot can be used in multiple Discord servers simultaneously:

1. Same bot token works everywhere
2. Each server gets its own room codes
3. Room codes are global (can join from any server)
4. Web players and Discord players can mix

## Support

### Common Issues

**"Room does not exist"**
- Check room code is correct (uppercase)
- Room might have expired
- Ask host to create new room

**"Room is not accepting new players"**
- Host locked the room
- Game already started
- Ask host to unlock or create new room

**"Game has already started"**
- Can't join mid-game
- Wait for next game
- Or create your own room

### Getting Help

1. Check backend logs (Render dashboard)
2. Verify Firebase Firestore rules are deployed
3. Test with web interface to isolate issue
4. Check bot token is valid

## Next Steps

- ✅ Bot is set up
- ✅ Commands work
- ✅ DMs are sent
- 📱 Deploy frontend to Firebase Hosting
- 🎮 Play with friends!

See:
- [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) - Deploy backend
- [README.md](./README.md) - Main documentation
- [TESTING.md](./TESTING.md) - Testing guide

