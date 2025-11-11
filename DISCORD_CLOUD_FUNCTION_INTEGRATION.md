# Discord Bot + Cloud Functions Integration

## Overview

The Discord bot now integrates seamlessly with Firebase Cloud Functions for hybrid games (Discord + Web players).

## How It Works

### 1. Game Creation Flow

```
Discord User → /impostor create
      ↓
Discord Bot → Creates room in Firestore
      ↓
Discord Bot → Starts Firestore listener for this room
      ↓
Room is ready for Discord + Web players
```

### 2. Joining Flow

**Discord Players:**
```
User → /impostor join code:ABC123
  ↓
Bot → Adds player to Firestore (with discord_id field)
  ↓
Bot → Starts listener (if not already listening)
```

**Web Players:**
```
User → Joins via frontend
  ↓
Frontend → Adds player to Firestore (no discord_id)
```

### 3. Game Start Flow (Hybrid Support!)

**When Discord host starts:**
```
Discord User → /impostor start code:ABC123
      ↓
Discord Bot → Updates Firestore: status="started"
      ↓
Cloud Function (Python) → Triggered automatically
      ↓
Cloud Function → Creates secrets for ALL players
      ↓
Firestore → Secrets collection updated
      ↓
Discord Bot Listener → Detects new secrets
      ↓
Discord Bot → Sends DMs to Discord players (checks discord_id field)
      ↓
Web Frontend → Displays secrets to web players
```

**When Web host starts:**
```
Web User → Clicks "Start Game"
      ↓
Frontend → Updates Firestore: status="started"
      ↓
Cloud Function (Python) → Triggered automatically
      ↓
Cloud Function → Creates secrets for ALL players
      ↓
Firestore → Secrets collection updated
      ↓
Discord Bot Listener → Detects new secrets
      ↓
Discord Bot → Sends DMs to Discord players
      ↓
Web Frontend → Displays secrets to web players
```

## Key Components

### 1. Cloud Function (`functions/main.py`)

```python
@firestore_fn.on_document_updated(document="rooms/{room_id}")
def on_game_start(event):
    # Triggered when status changes to "started"
    # Creates secrets for ALL players (Discord + Web)
    # Updates room status to "dealt"
```

### 2. Discord Bot Listener (`discord_bot/firestore_listener.py`)

```python
class FirestoreListener:
    def start_room_listener(self, room_id):
        # Watches rooms/{room_id}/secrets collection
        # When secrets are added:
        #   - Checks for discord_id field
        #   - Sends DM to Discord user
```

### 3. Player Data Structure

```python
# Firestore: rooms/{roomId}/players/{playerId}
{
    "name": "PlayerName",
    "isHost": true/false,
    "source": "discord" | "web",
    "discord_id": "123456789"  # Only for Discord players
}
```

```python
# Firestore: rooms/{roomId}/secrets/{playerId}
{
    "name": "PlayerName",
    "role": "impostor" | "player",
    "word": "kot" | null,
    "discord_id": "123456789"  # Only for Discord players
}
```

## Benefits

✅ **Unified Game Logic**: Cloud Function handles word selection for all players
✅ **Hybrid Games**: Discord and Web players in the same game
✅ **Real-time Updates**: Firestore listeners provide instant notifications
✅ **Separation of Concerns**: Cloud Function = game logic, Bot = Discord interface
✅ **Automatic DMs**: Bot automatically sends DMs when secrets are created
✅ **Language Consistency**: Both Cloud Function and Bot are Python

## Message Flow Example

### Hybrid Game Scenario

1. **Discord User A** creates room: `ABC123`
2. **Web User B** joins via frontend
3. **Discord User C** joins via `/impostor join code:ABC123`
4. **Web User D** (host) starts game from browser
5. **Cloud Function** creates secrets for all 4 players
6. **Discord Bot** automatically sends DMs to Users A and C
7. **Web Frontend** displays secrets to Users B and D

All handled automatically! 🎉

## Configuration

### Discord Bot

```python
# discord_bot/main.py
listener = FirestoreListener(bot, config.WEB_URL)
bot.firestore_listener = listener
```

### Cloud Function

```python
# functions/main.py
@firestore_fn.on_document_updated(document="rooms/{room_id}")
def on_game_start(event):
    # Automatically triggered on status change
```

## Testing

### Test Hybrid Game

1. Deploy Cloud Functions:
   ```bash
   firebase deploy --only functions
   ```

2. Start Discord Bot:
   ```bash
   cd discord_bot
   python main.py
   ```

3. Create room via Discord:
   ```
   /impostor create
   ```

4. Join with web player:
   - Open browser: `https://your-app.web.app/r/ABC123`

5. Start game (from Discord or Web)

6. Verify:
   - Discord players get DMs
   - Web players see secrets in browser

## Troubleshooting

### Discord players not receiving DMs

**Check:**
1. Is `discord_id` field set when joining? (Should be Discord user ID)
2. Is bot listening? (Check logs for "Started listener for room...")
3. Are DM permissions enabled? (Users must allow DMs from server members)

**Debug:**
```bash
# Check bot logs
tail -f discord_bot.log

# Check Cloud Function logs
firebase functions:log
```

### Cloud Function not triggering

**Check:**
1. Is function deployed? `firebase functions:list`
2. Is status changing to "started"?
3. Check function logs: `firebase functions:log --only on_game_start`

## Architecture Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   Discord Bot   │         │   Web Frontend  │
│                 │         │                 │
│  - Commands     │         │  - React App    │
│  - Listener     │         │  - Firestore    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           │
         └────────┬──────────────────┘
                  │
         ┌────────▼────────┐
         │   Firestore     │
         │                 │
         │  rooms/         │
         │    {id}/        │
         │      players/   │
         │      secrets/   │
         └────────┬────────┘
                  │
                  │ (triggers)
                  │
         ┌────────▼────────┐
         │ Cloud Function  │
         │   (Python)      │
         │                 │
         │ - on_game_start │
         │ - Word selection│
         │ - Impostor pick │
         └─────────────────┘
```

## Next Steps

1. Deploy the updated bot
2. Test hybrid games
3. Monitor logs for any issues
4. Enjoy seamless Discord + Web games! 🎮

