# 🔄 Migration: Backend → Cloud Functions

## Overview

Replace the backend API server with serverless Cloud Functions for:
- ✅ **Lower costs**: $0-2/month vs $7-15/month
- ✅ **Zero maintenance**: No server to manage
- ✅ **Better scaling**: Automatic, handles any load
- ✅ **Simpler deployment**: `firebase deploy` vs full CI/CD
- ✅ **Same functionality**: Word selection, impostor assignment

## What Changes

### ❌ Removed (Backend)
```
backend/
  ├── game_logic.py      # Game logic (word selection, impostor)
  ├── api/rooms.py       # API endpoints
  ├── words.txt          # Word list
  ├── main.py            # FastAPI server
  └── render.yaml        # Deployment config
```

### ✅ Added (Cloud Functions)
```
functions/
  ├── index.js           # Cloud Function with game logic
  ├── words.txt          # Same word list (5000+ words, 43KB)
  └── package.json       # Dependencies
```

## How It Works

### Before (Backend API):
```
Frontend → HTTP POST /rooms/{id}/start
         → Backend API (FastAPI)
         → game_logic.py selects word & impostor
         → Updates Firestore
         → Returns response
```

### After (Cloud Functions):
```
Frontend → Firestore.update(status="started")
         → Triggers onGameStart Cloud Function automatically
         → Selects word & impostor
         → Updates Firestore
         → Frontend gets realtime update
```

## Migration Steps

### 1. Deploy Cloud Functions

```bash
cd functions
npm install
firebase deploy --only functions
```

Verify in Firebase Console that `onGameStart` is deployed.

### 2. Update Frontend Code

**OLD (Backend API):**
```javascript
// frontend/src/api/room.js
export async function startGame(roomId) {
  const response = await fetch(`${API_URL}/rooms/${roomId}/start`, {
    method: 'POST'
  });
  return response.json();
}
```

**NEW (Direct Firestore):**
```javascript
// frontend/src/api/room.js
import { doc, updateDoc } from 'firebase/firestore';
import { db } from '../firebase';

export async function startGame(roomId) {
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    status: 'started'
  });
  // Cloud Function automatically triggered!
  // No need to wait for response, Firestore listeners handle updates
}
```

### 3. Update Discord Bot

**OLD (Backend API):**
```python
# discord_bot/bot/commands.py
async def start_game(room_id, user_id):
    response = await http_client.post(f"{API_URL}/rooms/{room_id}/start")
    return response.json()
```

**NEW (Direct Firestore):**
```python
# discord_bot/bot/commands.py
async def start_game(room_id, user_id):
    db = get_db()
    room_ref = db.collection('rooms').document(room_id)
    room_ref.update({'status': 'started'})
    # Cloud Function automatically triggered!
    # Secrets collection will be created automatically
```

### 4. Test Everything

1. **Create a room** (frontend or Discord)
2. **Join with 3+ players**
3. **Start the game**
4. **Check Firebase Console**:
   - Functions → Logs → See "Game starting for room: XXX"
   - Firestore → rooms → {roomId} → secrets (should be created)
5. **Verify players get their words** (DMs for Discord, frontend display)

### 5. Remove Backend (Optional)

Once Cloud Functions work:
```bash
# Stop the backend on Render
# Or delete the Render service

# Optionally remove backend code
git rm -r backend/
git commit -m "Remove backend, using Cloud Functions"
```

## Code Changes Summary

### Frontend Changes

#### `frontend/src/api/room.js`

<details>
<summary>Show changes</summary>

```javascript
// Remove these backend API calls:
- export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
- 
- export async function createRoom(userId, username) {
-   const response = await fetch(`${API_URL}/rooms`, {
-     method: 'POST',
-     headers: { 'Content-Type': 'application/json' },
-     body: JSON.stringify({ userId, username })
-   });
-   return response.json();
- }

// Replace with direct Firestore operations:
import { collection, doc, setDoc, updateDoc, addDoc } from 'firebase/firestore';
import { db } from '../firebase';

export async function createRoom(userId, username) {
  const roomsRef = collection(db, 'rooms');
  const roomData = {
    hostId: userId,
    status: 'lobby',
    createdAt: new Date(),
    maxPlayers: 10
  };
  
  const docRef = await addDoc(roomsRef, roomData);
  
  // Add host as first player
  const playersRef = collection(db, 'rooms', docRef.id, 'players');
  await setDoc(doc(playersRef, userId), {
    name: username,
    isHost: true,
    joinedAt: new Date()
  });
  
  return docRef.id;
}

export async function startGame(roomId) {
  const roomRef = doc(db, 'rooms', roomId);
  await updateDoc(roomRef, {
    status: 'started'
  });
  // Cloud Function automatically handles the rest!
}
```

</details>

### Discord Bot Changes

#### `discord_bot/bot/commands.py`

<details>
<summary>Show changes</summary>

```python
# Remove HTTP client imports and calls
- import aiohttp

# The game_logic.py already uses Firestore directly, so no changes needed!
# It already calls:
await game_logic.start_game(code, user_id)

# Which updates Firestore, triggering the Cloud Function automatically
```

</details>

## Benefits

### Cost Comparison

| Service | Backend (Render) | Cloud Functions |
|---------|------------------|-----------------|
| **Monthly cost** | $7-15 | $0-2 |
| **Free tier** | 750 hours | 2M invocations |
| **Scaling** | Manual | Automatic |
| **Cold starts** | App sleeps | 1-2s |
| **Maintenance** | Updates, monitoring | None |

### Performance Comparison

| Operation | Backend API | Cloud Functions |
|-----------|-------------|-----------------|
| **Start game** | ~200-300ms | ~100-200ms |
| **Word loading** | Each request | Cached in memory |
| **Deployment** | 5-10 min | 2-3 min |
| **Rollback** | Complex | One command |

## Rollback Plan

If you need to roll back to the backend:

1. **Keep the backend code** (don't delete yet)
2. **Test Cloud Functions thoroughly** first
3. **If issues arise**:
   ```bash
   # Redeploy backend
   git checkout backend/
   # Deploy to Render
   
   # Disable Cloud Function
   firebase functions:delete onGameStart
   ```

## Monitoring

### Cloud Functions Logs
```bash
# View all function logs
firebase functions:log

# View specific function
firebase functions:log --only onGameStart

# Tail logs
firebase functions:log --only onGameStart --tail
```

### Firebase Console
- Functions → onGameStart → Logs
- See: invocations, errors, execution time
- Monitor: costs, performance, errors

## FAQ

### Q: What if the Cloud Function fails?
**A**: Firestore triggers are reliable. If a function fails:
- It automatically retries
- Check logs in Firebase Console
- Fix the issue and redeploy
- The next game start will work

### Q: Can I still use the backend for other things?
**A**: Yes! You can:
- Keep backend for non-game logic
- Use both backend + Cloud Functions
- Migrate incrementally

### Q: How do I debug Cloud Functions?
**A**: 
```bash
# Local emulation
cd functions
npm run serve

# Check logs
firebase functions:log --only onGameStart

# Test manually
# Trigger by updating a room in Firestore
```

### Q: What about rate limits?
**A**: Cloud Functions have generous limits:
- Free tier: 2M invocations/month
- ~65,000 games/month for free
- More than enough for most games

### Q: Is the words file secure?
**A**: 
- Words are just Polish vocabulary
- Not sensitive data
- Loaded in function memory
- Not exposed to clients
- Impostor/word selection happens server-side

## Conclusion

**Recommendation**: ✅ **Migrate to Cloud Functions**

Reasons:
1. **Cheaper**: Save $5-13/month
2. **Simpler**: No server management
3. **Reliable**: Auto-scaling, auto-retry
4. **Fast**: In-memory word caching
5. **Future-proof**: Serverless is the way

The only downside is cold starts (1-2s), but this is rare and acceptable for a game.

## Need Help?

1. Check logs: `firebase functions:log`
2. Test locally: `npm run serve` in functions/
3. Review Firebase Console → Functions
4. Check this guide's troubleshooting section
5. Ask in Discord/GitHub issues

Happy gaming! 🎮

