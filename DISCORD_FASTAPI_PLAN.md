# Discord Bot + FastAPI Backend Plan (v2)

This document outlines the future implementation of a Discord bot integration and FastAPI backend for the Impostor game.

## Overview

The Discord integration will allow players to:
1. Start a game via Discord slash command
2. Receive their word/role via DM from the bot
3. Still use the web interface to see the lobby and game state
4. Play entirely through Discord or hybrid (Discord + Web)

## Architecture

```
Discord Bot (discord.py)
    ↓
FastAPI Backend (REST API)
    ↓
Firestore (shared with Web)
    ↓
Web Frontend (React)
```

## Components

### 1. FastAPI Backend

**Location**: `backend/` (new directory)

**Endpoints**:
- `POST /api/rooms/create` - Create a new room via Discord
- `POST /api/rooms/{roomId}/join` - Join a room via Discord
- `POST /api/rooms/{roomId}/start` - Start game (Discord host)
- `GET /api/rooms/{roomId}` - Get room status
- `GET /api/rooms/{roomId}/secret/{userId}` - Get player's secret

**Features**:
- Service account authentication to Firestore
- Same data model as web frontend
- CORS enabled for web frontend
- Rate limiting for API protection

**Example Implementation**:
```python
from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore, initialize_app
import random

app = FastAPI()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

@app.post("/api/rooms/create")
async def create_room(discord_user_id: str, discord_username: str):
    room_id = generate_room_id()
    room_ref = db.collection('rooms').document(room_id)
    room_ref.set({
        'hostUid': discord_user_id,
        'hostSource': 'discord',
        'status': 'lobby',
        'createdAt': firestore.SERVER_TIMESTAMP,
        'allowJoin': True
    })
    
    player_ref = room_ref.collection('players').document(discord_user_id)
    player_ref.set({
        'name': discord_username,
        'isHost': True,
        'joinedAt': firestore.SERVER_TIMESTAMP,
        'seen': False,
        'present': True
    })
    
    return {'roomId': room_id}
```

### 2. Discord Bot

**Location**: `backend/bot/` (new directory)

**Commands**:
- `/impostor create` - Create a new game room
- `/impostor join <code>` - Join an existing room
- `/impostor start` - Start the game (host only)
- `/impostor status` - Check room status
- `/impostor reveal` - Show your word again (DM)

**Flow**:
1. User runs `/impostor create` in a Discord channel
2. Bot calls FastAPI to create room
3. Bot replies with room code and join instructions
4. Other players use `/impostor join ABC123`
5. Bot adds them to the room via API
6. Host uses `/impostor start`
7. Bot calls API to start game and get secrets
8. Bot DMs each player their role/word
9. Players can check status in channel or web

**Example Bot Code**:
```python
import discord
from discord import app_commands
import aiohttp

class ImpostorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        
    async def setup_hook(self):
        await self.tree.sync()

@client.tree.command(name="create")
async def create_game(interaction: discord.Interaction):
    """Create a new Impostor game room"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/api/rooms/create",
            json={
                "discord_user_id": str(interaction.user.id),
                "discord_username": interaction.user.display_name
            }
        ) as resp:
            data = await resp.json()
            room_id = data['roomId']
            
    await interaction.response.send_message(
        f"✅ Room created: **{room_id}**\n"
        f"Join link: {WEB_BASE}/r/{room_id}\n"
        f"Others can join with `/impostor join {room_id}`"
    )
```

### 3. Shared Data Model

Both web and Discord use the same Firestore collections:

**Enhanced room document**:
```javascript
{
  hostUid: string,          // Can be Discord user ID or Firebase UID
  hostSource: 'web' | 'discord',
  status: 'lobby' | 'dealt' | 'playing' | 'ended',
  createdAt: Timestamp,
  allowJoin: boolean,
  discordChannelId?: string  // Optional: link to Discord channel
}
```

**Enhanced player document**:
```javascript
{
  name: string,
  isHost: boolean,
  joinedAt: Timestamp,
  seen: boolean,
  present: boolean,
  source: 'web' | 'discord',     // New field
  discordUserId?: string          // Optional
}
```

### 4. Deployment

**FastAPI Backend**:
- Deploy to: Render, Fly.io, Railway, or Cloud Run
- Environment variables:
  - `FIREBASE_SERVICE_ACCOUNT` - Service account JSON
  - `CORS_ORIGINS` - Allowed frontend origins
  - `API_KEY` - Optional API key for Discord bot

**Discord Bot**:
- Deploy to: Same as backend or separate service
- Environment variables:
  - `DISCORD_TOKEN` - Bot token from Discord Developer Portal
  - `API_BASE_URL` - FastAPI backend URL
  - `WEB_BASE_URL` - Frontend URL

**Cost Estimate**:
- Firestore: Free tier (50k reads/day)
- FastAPI + Bot: ~$5-7/month (Render/Fly free tier may suffice)
- Total: Likely free for moderate usage

### 5. Security Considerations

1. **Service Account**: Store Firebase service account key securely
2. **Discord Token**: Never commit to git, use environment variables
3. **API Authentication**: Consider API keys or OAuth for FastAPI
4. **Rate Limiting**: Prevent abuse of Discord commands
5. **Firestore Rules**: Already secured, no changes needed

### 6. Implementation Steps

1. **Setup Backend**:
   - Create `backend/` directory
   - Initialize FastAPI project
   - Add Firebase Admin SDK
   - Implement room management endpoints
   - Add CORS middleware
   - Test with curl/Postman

2. **Setup Bot**:
   - Create Discord application at discord.com/developers
   - Install discord.py
   - Implement slash commands
   - Connect to FastAPI backend
   - Test in private Discord server

3. **Integration Testing**:
   - Create room via Discord
   - Join via web
   - Start game via Discord
   - Verify DMs are sent
   - Check web interface updates in real-time

4. **Deploy**:
   - Deploy FastAPI to Render/Fly
   - Deploy bot to same or separate service
   - Update environment variables
   - Test production deployment

5. **Documentation**:
   - Update main README
   - Add bot command documentation
   - Create deployment guide

## Future Enhancements

- **Game Management**: `/impostor end`, `/impostor kick @user`
- **Statistics**: Track games played, win rates
- **Leaderboards**: Discord server leaderboards
- **Custom Word Lists**: Per-server word lists
- **Voting System**: Vote for impostor in Discord
- **Voice Integration**: Mute/unmute players during discussion
- **Multi-language**: Support different languages per server

## Notes

- The Discord integration is **optional** - web-only mode will continue to work
- Hybrid mode allows mixing Discord and web players in the same game
- All game logic remains client-side for simplicity
- Backend is stateless; Firestore is the single source of truth

