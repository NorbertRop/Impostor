# 🔥 Firebase Cloud Functions for Impostor

Cloud Functions handle **all game logic** for the Impostor game, eliminating the need for a backend server!

Written in **Python 3.12** - same language as the Discord bot for code consistency.

## ✨ Key Features

- **Automatic game start** - Firestore trigger handles word selection and impostor assignment
- **5000+ Polish words** - Loaded from `words.txt` (43KB, included in deployment)
- **Automatic cleanup** - Removes old rooms and anonymous users daily
- **Serverless** - No server to maintain, scales automatically
- **Python** - Consistent with Discord bot, type-safe

## 📦 Functions

### `on_game_start` (Firestore Trigger) ⭐
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

### `cleanup_old_rooms` (Scheduled)
- **Trigger**: Every 24 hours
- **Purpose**: Automatically deletes rooms and their subcollections older than 24 hours
- **Keeps**: Firestore clean and costs low

### `cleanup_anonymous_users` (Scheduled) ⭐ **NEW**
- **Trigger**: Every 24 hours
- **Purpose**: Automatically deletes anonymous Firebase Auth users who haven't signed in for 30 days
- **Why**: Prevents accumulation of unused anonymous user accounts
- **Keeps**: Authentication costs low and user list manageable

### `manual_cleanup` (HTTP)
- **Trigger**: HTTP request
- **Purpose**: Manual cleanup for testing
- **Parameters**: `?hours=X` - cleanup rooms older than X hours (default: 24)
- **Example**: `https://YOUR_PROJECT.cloudfunctions.net/manual_cleanup?hours=12`

### `manual_user_cleanup` (HTTP) ⭐ **NEW**
- **Trigger**: HTTP request
- **Purpose**: Manual anonymous user cleanup for testing
- **Parameters**: `?days=X` - cleanup anonymous users inactive for X days (default: 30)
- **Example**: `https://YOUR_PROJECT.cloudfunctions.net/manual_user_cleanup?days=7`

## 🏗️ Architecture

```
Frontend/Discord Bot
        ↓
    Firestore (set status="started")
        ↓ (triggers on_game_start)
 Cloud Function (Python)
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

### Prerequisites:
- Python 3.12+
- Firebase CLI: `npm install -g firebase-tools`
- Firebase project with Blaze plan (required for Cloud Functions)

### First time setup:
```bash
cd functions
# Python dependencies are automatically installed during deployment
```

### Deploy all functions:
```bash
firebase deploy --only functions
```

### Deploy specific function:
```bash
firebase deploy --only functions:on_game_start
firebase deploy --only functions:cleanup_old_rooms
firebase deploy --only functions:manual_cleanup
```

## 📝 Words File

The `words.txt` file contains 5000+ Polish words:
- **Size**: 43KB (tiny!)
- **Loaded**: On function initialization (cached)
- **Performance**: Lightning fast, in-memory access
- **Cost**: Free tier easily covers this

## 🧪 Local Testing

```bash
# Install Python dependencies locally
pip install -r requirements.txt

# Start Firebase emulators
firebase emulators:start --only functions
```

Then test with Firebase Emulator UI at http://localhost:4000

## 📊 Monitoring

View logs:
```bash
firebase functions:log
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

| Aspect            | Backend API        | Cloud Functions      |
| ----------------- | ------------------ | -------------------- |
| **Maintenance**   | Server to manage   | Zero maintenance     |
| **Scaling**       | Manual/Complex     | Automatic            |
| **Cost**          | $7-15/month        | $0-2/month           |
| **Words storage** | Need file/database | Included in function |
| **Deployment**    | CI/CD setup        | `firebase deploy`    |
| **Cold starts**   | None               | 1-2s (rarely)        |

## 🔧 How it Works

1. **Frontend/Discord** updates room status to `"started"` in Firestore
2. **Firestore** triggers `on_game_start` Cloud Function automatically
3. **Function** executes (Python):
   - Loads words from memory (cached)
   - Selects random word
   - Picks random impostor
   - Creates secrets collection with roles
4. **Frontend/Discord** receives realtime updates via Firestore listeners
5. **Discord bot** reads secrets and sends DMs to players

## 🆕 Migration from Backend

The Cloud Functions replace:
- ❌ `backend/game_logic.py` → ✅ `functions/main.py` (on_game_start)
- ❌ `backend/api/rooms.py` → ✅ Firestore + triggers
- ❌ `backend/words.txt` → ✅ `functions/words.txt`
- ❌ Backend server ($7-15/mo) → ✅ Serverless ($0-2/mo)

**Result**: Simpler, cheaper, more reliable! 🎉

**Code reuse**: Game logic now shared between Discord bot and Cloud Functions!

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
