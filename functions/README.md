# Firebase Cloud Functions

Scheduled cleanup functions for the Impostor game.

## Functions

### `cleanupOldRooms` (Scheduled)

Automatically runs **once every 24 hours** and removes rooms older than 24 hours, including all subcollections (players and secrets).

**Schedule:** `every 24 hours`

This function runs independently of the backend app, so it continues working even when the Render app is asleep.

### `manualCleanup` (HTTP)

Manually trigger cleanup for testing or immediate cleanup needs.

**Endpoint:** `https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/manualCleanup`

**Query Parameters:**
- `hours` (optional): Number of hours threshold (default: 24)

**Example:**
```bash
# Clean rooms older than 24 hours (default)
curl https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/manualCleanup

# Clean rooms older than 12 hours
curl https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/manualCleanup?hours=12
```

## Setup

### 1. Install Dependencies

```bash
cd functions
npm install
```

### 2. Test Locally (Optional)

```bash
npm run serve
```

This starts the Firebase emulators locally.

### 3. Deploy to Firebase

```bash
# From the project root
firebase deploy --only functions

# Or from the functions directory
npm run deploy
```

### 4. View Logs

```bash
firebase functions:log
```

Or view in Firebase Console: Functions → Logs

## Configuration

The cleanup function is configured to:
- Run every 24 hours
- Delete rooms older than 24 hours
- Clean up all subcollections (players, secrets)

To change the schedule, edit `index.js`:

```javascript
exports.cleanupOldRooms = onSchedule("every 24 hours", async (event) => {
  // Change "every 24 hours" to your desired schedule
  // Examples:
  // - "every 12 hours"
  // - "every day 00:00"
  // - "0 2 * * *" (cron format - 2 AM daily)
});
```

## Cost Considerations

- **Scheduled function:** Runs once per day (every 24 hours)
- **Function invocations:** Part of Firebase free tier (2M invocations/month)
- **Firestore reads/writes:** Depends on number of old rooms

The cleanup function is very lightweight and should stay well within Firebase's free tier for typical usage.

## Monitoring

Check function execution in Firebase Console:
1. Go to Firebase Console → Functions
2. Click on `cleanupOldRooms`
3. View execution history and logs

## Troubleshooting

### Functions not deploying
- Ensure you're logged in: `firebase login`
- Check you have the correct project: `firebase use --add`
- Verify billing is enabled (required for Cloud Functions)

### Scheduled function not running
- Check Cloud Scheduler is enabled in Google Cloud Console
- View scheduler jobs: Google Cloud Console → Cloud Scheduler
- Verify function is deployed: `firebase functions:list`

### Manual cleanup not working
- Check function URL in Firebase Console → Functions
- Verify function has public access (or use authentication)
- Check function logs for errors

