# Firestore Data Structure

## Overview

This document defines the **canonical data structure** for the Impostor game. All clients (Web, Discord, Cloud Functions) MUST follow these field names exactly.

## Why Separate Collections?

✅ **`players/` and `secrets/` are intentionally separate for security:**

- **Security**: Firestore rules make `secrets/{playerId}` readable ONLY by that player
- **Privacy**: `players/` is public (for lobby view), `secrets/` is private
- **Clean separation**: Lobby state vs game state

## Collections

### `rooms/{roomId}`

Main room document.

```typescript
{
  hostUid: string,              // Player ID of room host
  hostSource: "web" | "discord", // Where host created the room
  status: "lobby" | "started" | "dealt" | "playing",
  createdAt: timestamp,
  allowJoin: boolean,
  
  // Set when game starts (by Cloud Function)
  word?: string,                // The secret word (only after game starts)
  impostorId?: string,          // Player ID of the impostor
  startedAt?: timestamp,
  
  // Optional Discord integration
  discordChannelId?: string     // Discord channel ID (only if created via Discord)
}
```

### `rooms/{roomId}/players/{playerId}`

Public player information (visible to all in room).

```typescript
{
  name: string,                 // Player display name
  isHost: boolean,              // Is this player the host?
  source: "web" | "discord",    // Where player joined from
  joinedAt: timestamp,
  seen: boolean,                // Has player seen their secret?
  present: boolean,             // Is player still in room?
  
  // ONLY for Discord players
  discordId?: string            // Discord user ID (numeric string)
}
```

**Key Points:**
- `playerId` (document ID) is:
  - Firebase Auth UID for web players
  - Discord user ID for Discord players
- `discordId` field is ONLY set for Discord players
- `source` field MUST be set by all clients

### `rooms/{roomId}/secrets/{playerId}`

Private game information (readable only by that player).

```typescript
{
  name: string,                 // Player display name (for convenience)
  role: "impostor" | "player",  // Player's role
  word: string | null,          // The word (null for impostor)
  createdAt: timestamp,
  
  // ONLY for Discord players
  discordId?: string            // Discord user ID (for DM sending)
}
```

**Key Points:**
- Created by Cloud Function when game starts
- `discordId` is copied from `players/` collection
- Discord bot listens for these and sends DMs to Discord players

## Field Name Standards

### ✅ Correct (Use These)

| Field | Type | Usage |
|-------|------|-------|
| `discordId` | `string` | Discord user ID (camelCase) |
| `isHost` | `boolean` | Host flag (camelCase) |
| `source` | `"web" \| "discord"` | Player source (lowercase) |
| `createdAt` | `timestamp` | Creation time (camelCase) |
| `joinedAt` | `timestamp` | Join time (camelCase) |
| `startedAt` | `timestamp` | Start time (camelCase) |
| `allowJoin` | `boolean` | Can join flag (camelCase) |
| `hostUid` | `string` | Host player ID (camelCase) |
| `hostSource` | `string` | Host source (camelCase) |
| `impostorId` | `string` | Impostor player ID (camelCase) |

### ❌ Incorrect (Don't Use)

| Wrong | Correct | Why |
|-------|---------|-----|
| `discord_id` | `discordId` | Use camelCase consistently |
| `discordUserId` | `discordId` | Too verbose |
| `is_host` | `isHost` | Use camelCase |
| `created_at` | `createdAt` | Use camelCase |

## Example Data

### Web Player Creates Room

```javascript
// rooms/ABC123
{
  hostUid: "firebase-uid-123",
  hostSource: "web",
  status: "lobby",
  createdAt: 2025-01-01T12:00:00Z,
  allowJoin: true
}

// rooms/ABC123/players/firebase-uid-123
{
  name: "Alice",
  isHost: true,
  source: "web",
  joinedAt: 2025-01-01T12:00:00Z,
  seen: false,
  present: true
}
```

### Discord Player Joins

```javascript
// rooms/ABC123/players/987654321
{
  name: "Bob",
  isHost: false,
  source: "discord",
  discordId: "987654321",  // Discord user ID
  joinedAt: 2025-01-01T12:01:00Z,
  seen: false,
  present: true
}
```

### Game Starts (Cloud Function Creates Secrets)

```javascript
// rooms/ABC123 (updated by Cloud Function)
{
  ...previousFields,
  status: "dealt",
  word: "kot",
  impostorId: "firebase-uid-123",
  startedAt: 2025-01-01T12:05:00Z
}

// rooms/ABC123/secrets/firebase-uid-123 (Web player - impostor)
{
  name: "Alice",
  role: "impostor",
  word: null,
  createdAt: 2025-01-01T12:05:00Z
}

// rooms/ABC123/secrets/987654321 (Discord player - civilian)
{
  name: "Bob",
  role: "player",
  word: "kot",
  discordId: "987654321",  // Copied from players collection
  createdAt: 2025-01-01T12:05:00Z
}
```

## Client Responsibilities

### Web Frontend
- ✅ MUST set `source: "web"` when creating/joining
- ✅ MUST NOT set `discordId` field
- ✅ Uses Firebase Auth UID as player ID

### Discord Bot
- ✅ MUST set `source: "discord"` when creating/joining
- ✅ MUST set `discordId: user.id` (Discord user ID)
- ✅ Uses Discord user ID as player ID
- ✅ Listens for secrets with `discordId` and sends DMs

### Cloud Function
- ✅ Copies `discordId` from `players/` to `secrets/`
- ✅ Creates secrets for ALL players (web + discord)
- ✅ Sets room `status: "dealt"` after creating secrets

## Migration Notes

### Breaking Changes from Old Structure

| Old Field | New Field | Migration |
|-----------|-----------|-----------|
| `discordUserId` | `discordId` | Update all writes |
| `discord_id` | `discordId` | Update all reads |
| Missing `source` | `source: "web"` | Add to web client |

### How to Migrate Existing Data

If you have existing rooms in Firestore:

```javascript
// Run this once to migrate existing data
const migratePlayers = async () => {
  const rooms = await db.collection('rooms').get();
  
  for (const roomDoc of rooms.docs) {
    const playersRef = roomDoc.ref.collection('players');
    const players = await playersRef.get();
    
    for (const playerDoc of players.docs) {
      const data = playerDoc.data();
      
      // Migrate discordUserId → discordId
      if (data.discordUserId) {
        await playerDoc.ref.update({
          discordId: data.discordUserId,
          discordUserId: firestore.FieldValue.delete()
        });
      }
      
      // Add source if missing
      if (!data.source) {
        await playerDoc.ref.update({
          source: data.discordId ? 'discord' : 'web'
        });
      }
    }
  }
};
```

## Validation

All clients SHOULD validate data structures match this spec. Example:

```typescript
interface Player {
  name: string;
  isHost: boolean;
  source: 'web' | 'discord';
  joinedAt: Timestamp;
  seen: boolean;
  present: boolean;
  discordId?: string; // Required if source === 'discord'
}

function validatePlayer(data: any): Player {
  if (!data.source || !['web', 'discord'].includes(data.source)) {
    throw new Error('Invalid or missing source field');
  }
  
  if (data.source === 'discord' && !data.discordId) {
    throw new Error('Discord players must have discordId field');
  }
  
  return data as Player;
}
```

## Summary

✅ **DO:**
- Use `discordId` (camelCase) for Discord user IDs
- Set `source: "web"` or `source: "discord"` for all players
- Keep `players/` and `secrets/` collections separate
- Copy `discordId` to secrets for Discord players

❌ **DON'T:**
- Use snake_case (`discord_id`, `is_host`)
- Mix old field names with new ones
- Merge players and secrets collections
- Forget to set `source` field

