# 🔥 Firebase Cloud Functions for Impostor

Cloud Functions handle **all game logic** for the Impostor game, eliminating the need for a backend server!

## ✨ Key Features

- **Automatic game start** - Firestore trigger handles word selection and impostor assignment
- **5000+ Polish words** - Loaded from `words.txt` (43KB, included in deployment)
- **Automatic cleanup** - Removes old rooms daily
- **Serverless** - No server to maintain, scales automatically

## 📦 Functions

### `onGameStart` (Firestore Trigger) ⭐ **NEW**
- **Trigger**: When a room's `status` changes to `"started"`
- **Purpose**: 
  - Selects random word from 5000+ words
  - Randomly assigns one player as impostor
  - Creates secrets for all players
  - Updates room with game data
- **Benefits**: 
  - No backend API needed
  - Frontend just updates Firestore
  - Automatic, instant response
  - Works for both web and Discord

### `cleanupOldRooms` (Scheduled)
- **Trigger**: Every 24 hours
- **Purpose**: Automatically deletes rooms and their subcollections older than 24 hours
- **Keeps**: Firestore clean and costs low

### `manualCleanup` (HTTP)
- **Trigger**: HTTP request
- **Purpose**: Manual cleanup for testing
- **Parameters**: `?hours=X` - cleanup rooms older than X hours (default: 24)
- **Example**: `https://YOUR_PROJECT.cloudfunctions.net/manualCleanup?hours=12`

## 🏗️ Architecture

```
Frontend/Discord Bot
        ↓
    Firestore (set status="started")
        ↓ (triggers onGameStart)
 Cloud Function
        ↓
   - Load words.txt (5000 words)
   - Select random word
   - Choose random impostor
   - Create secrets
        ↓
    Firestore (updated)
        ↓
Frontend/Discord Bot (realtime updates)
```

## 🚀 Deployment

### First time setup:
```bash
cd functions
npm install
```

### Deploy all functions:
```bash
firebase deploy --only functions
```

### Deploy specific function:
```bash
firebase deploy --only functions:onGameStart
firebase deploy --only functions:cleanupOldRooms
```

## 📝 Words File

The `words.txt` file contains 5000+ Polish words:
- **Size**: 43KB (tiny!)
- **Loaded**: On function initialization (cached)
- **Performance**: Lightning fast, in-memory access
- **Cost**: Free tier easily covers this

## 🧪 Local Testing

```bash
cd functions
npm run serve
```

Then test with Firebase Emulator UI at http://localhost:4000

## 📊 Monitoring

View logs:
```bash
npm run logs
```

Or: Firebase Console → Functions → Logs

## 💰 Cost Estimation

**Free tier includes:**
- 2M invocations/month
- 400,000 GB-seconds
- 200,000 CPU-seconds

**Typical usage:**
- Game start: ~100-200ms per game
- Cleanup: Once per day
- **Expected cost**: $0/month for small-medium usage

## 🎯 Benefits vs Backend

| Aspect | Backend API | Cloud Functions |
|--------|------------|-----------------|
| **Maintenance** | Server to manage | Zero maintenance |
| **Scaling** | Manual/Complex | Automatic |
| **Cost** | $7-15/month | $0-2/month |
| **Words storage** | Need file/database | Included in function |
| **Deployment** | CI/CD setup | `firebase deploy` |
| **Cold starts** | None | 1-2s (rarely) |

## 🔧 How it Works

1. **Frontend/Discord** updates room status to `"started"` in Firestore
2. **Firestore** triggers `onGameStart` Cloud Function automatically
3. **Function** executes:
   - Loads words from memory (cached)
   - Selects random word
   - Picks random impostor
   - Creates secrets collection with roles
4. **Frontend/Discord** receives realtime updates via Firestore listeners
5. **Discord bot** reads secrets and sends DMs to players

## 🆕 Migration from Backend

The Cloud Functions replace:
- ❌ `backend/game_logic.py` → ✅ `functions/index.js` (onGameStart)
- ❌ `backend/api/rooms.py` → ✅ Firestore + triggers
- ❌ `backend/words.txt` → ✅ `functions/words.txt`
- ❌ Backend server ($7-15/mo) → ✅ Serverless ($0-2/mo)

**Result**: Simpler, cheaper, more reliable! 🎉

## 🔧 Troubleshooting

### Functions not deploying
- Ensure you're logged in: `firebase login`
- Check project: `firebase use --add`
- Verify billing enabled (required for Cloud Functions)

### Game not starting
- Check function logs: `firebase functions:log`
- Verify function is deployed: `firebase functions:list`
- Test with manual trigger from Firebase Console

### Words not loading
- Ensure `words.txt` is in `functions/` directory
- Check logs for "Loaded X words" message
- Fallback words will be used if file missing
