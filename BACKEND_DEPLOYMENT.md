# Backend Deployment Guide

Complete guide to deploying the FastAPI + Discord bot backend to Render.

## Prerequisites

- GitHub account
- Render account (free tier works)
- Discord bot created (see [DISCORD_SETUP.md](./DISCORD_SETUP.md))
- Firebase service account key

## Step 1: Get Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click ⚙️ (Settings) → **Project settings**
4. Go to **Service accounts** tab
5. Click **Generate new private key**
6. Click **Generate key** → downloads JSON file
7. Open the JSON file and **copy entire contents**
8. Convert to single line (remove newlines):
   ```bash
   # On Mac/Linux:
   cat serviceAccountKey.json | tr -d '\n'
   
   # Or use online tool: jsonformatter.org/json-minifier
   ```
9. Save this single-line JSON - you'll need it for Render

⚠️ **Never commit this file to git!**

## Step 2: Push Code to GitHub

```bash
# Make sure you're in the project root
cd /path/to/impostor

# Add backend files
git add backend/
git add firebase.json
git add .firebaserc
git add firestore.indexes.json

# Commit
git commit -m "Add Discord bot backend with FastAPI"

# Push
git push origin main
```

## Step 3: Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure service:

**Settings:**
- **Name:** `impostor-backend` (or your choice)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Instance Type:** `Free`

5. Click **Advanced** to set environment variables

## Step 4: Set Environment Variables

Add these in Render's Environment Variables section:

### Required Variables

**`DISCORD_TOKEN`**
- Value: Your Discord bot token from Developer Portal
- Example: `YOUR_BOT_TOKEN_HERE`

**`FIREBASE_SERVICE_ACCOUNT`**
- Value: Single-line JSON from Step 1
- Example: `{"type":"service_account","project_id":"your-project",...}`

**`CORS_ORIGINS`**
- Value: Your Firebase Hosting URL + localhost
- Example: `https://your-project.web.app,http://localhost:5173`

**`WEB_BASE_URL`**
- Value: Your Firebase Hosting URL
- Example: `https://your-project.web.app`

**`PORT`**
- Value: `8000`
- (Render auto-sets this, but good to define)

### Example Configuration

```
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
FIREBASE_SERVICE_ACCOUNT={"type":"service_account","project_id":"your-project-id",...}
CORS_ORIGINS=https://your-project.web.app,http://localhost:5173
WEB_BASE_URL=https://your-project.web.app
PORT=8000
```

## Step 5: Deploy

1. Click **Create Web Service**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Start the service
3. Watch the logs for:
   ```
   ✅ Firebase Admin SDK initialized successfully
   ✅ Discord bot logged in as YourBot
   ✅ Synced N command(s)
   ```

## Step 6: Verify Deployment

### Check Health Endpoint

Visit: `https://your-service.onrender.com/health`

Should return:
```json
{
  "status": "ok",
  "service": "impostor-backend",
  "version": "1.0.0"
}
```

### Check API Docs

Visit: `https://your-service.onrender.com/docs`

Should show FastAPI Swagger documentation.

### Check Discord Bot

In your Discord server, type `/` and verify:
- `/impostor` command appears
- Commands work

## Step 7: Update Frontend

Update `frontend/.env` with backend URL:

```env
VITE_BACKEND_URL=https://your-service.onrender.com
```

(Optional - only if frontend needs to call API directly)

## Monitoring

### View Logs

1. Go to Render Dashboard
2. Click your service
3. Click **Logs** tab
4. Monitor for errors

### Common Log Messages

✅ **Success:**
```
✅ Firebase Admin SDK initialized successfully
✅ Loaded 10000 words from /app/words.txt
✅ Discord bot logged in as ImpostorBot
✅ Synced 1 command(s)
```

❌ **Errors:**
```
❌ Failed to initialize Firebase: ...
❌ Configuration error: DISCORD_TOKEN environment variable is required
```

## Troubleshooting

### Service won't start

**Check:**
- All environment variables are set
- Service account JSON is valid single-line
- Build logs for Python errors

**Solution:**
- Review logs in Render dashboard
- Verify env vars don't have extra spaces
- Test locally first

### Bot not connecting

**Symptoms:**
- No "Discord bot logged in" message
- Commands don't appear

**Causes:**
- Invalid `DISCORD_TOKEN`
- Bot not invited to server
- Network issues

**Solution:**
- Regenerate token in Discord Developer Portal
- Re-invite bot with OAuth URL
- Check Render status page

### Firebase errors

**Symptoms:**
```
❌ Failed to initialize Firebase
permission-denied
```

**Causes:**
- Invalid service account JSON
- Wrong project ID
- Firestore rules not deployed

**Solution:**
- Re-download service account key
- Verify project ID matches
- Deploy Firestore rules:
  ```bash
  firebase deploy --only firestore:rules
  ```

### Commands not syncing

**Symptoms:**
- Bot is online but commands don't appear
- `/impostor` not in slash command list

**Causes:**
- Commands take time to sync (up to 1 hour)
- Bot missing `applications.commands` scope

**Solution:**
- Wait 10-15 minutes
- Re-invite bot with correct OAuth URL
- Restart Render service

### Free tier sleeping

**Issue:**
Render free tier sleeps after 15 minutes of inactivity.

**Impact:**
- First request after sleep takes ~30 seconds
- Discord bot goes offline

**Solutions:**
1. **Upgrade to paid plan** ($7/month)
2. **Use cron job** to ping every 10 minutes:
   ```bash
   # In cron-job.org or similar
   */10 * * * * curl https://your-service.onrender.com/health
   ```
3. **Accept the limitation** for hobby projects

## Updating Deployment

### Code Changes

```bash
# Make changes
git add .
git commit -m "Update backend"
git push

# Render auto-deploys on push
```

### Environment Variable Changes

1. Go to Render Dashboard
2. Click your service
3. Go to **Environment** tab
4. Update variables
5. Service auto-restarts

### Manual Redeploy

1. Go to Render Dashboard
2. Click your service
3. Click **Manual Deploy** → **Deploy latest commit**

## Security Best Practices

### Protect Secrets

- ✅ Never commit `.env` to git
- ✅ Never log sensitive values
- ✅ Rotate tokens if exposed
- ✅ Use Render's secret management

### Monitor Access

- Check Render logs regularly
- Monitor Firebase usage
- Watch for unusual activity

### Rate Limiting

Consider adding rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Cost Estimation

### Free Tier

**Render:**
- 750 hours/month
- 512 MB RAM
- Sleeps after 15min inactivity
- **Cost: $0**

**Firebase:**
- 50k reads/day
- 20k writes/day
- 1 GB storage
- **Cost: $0**

**Total: $0/month** for hobby use

### Paid Plans

**Render Starter ($7/month):**
- No sleeping
- 512 MB RAM
- Always online

**Firebase Blaze (pay-as-you-go):**
- Beyond free tier limits
- ~$0.06 per 100k reads
- ~$0.18 per 100k writes

**Estimated for 1000 users:**
- Render: $7/month
- Firebase: ~$5/month
- **Total: ~$12/month**

## Production Checklist

Before going live:

- [ ] Discord bot created and invited
- [ ] Firebase service account downloaded
- [ ] Firestore rules deployed
- [ ] Backend deployed to Render
- [ ] All environment variables set
- [ ] Health endpoint returns 200
- [ ] Discord commands work
- [ ] Frontend deployed to Firebase Hosting
- [ ] DMs are being sent
- [ ] Tested end-to-end
- [ ] Monitoring set up
- [ ] Backup plan for outages

## Next Steps

- ✅ Backend deployed
- ✅ Bot is online
- 📱 Deploy frontend: `cd frontend && npm run deploy`
- 🎮 Test full flow: Discord + Web
- 📊 Monitor logs and usage

See:
- [DISCORD_SETUP.md](./DISCORD_SETUP.md) - Discord bot configuration
- [TESTING.md](./TESTING.md) - Testing guide
- [README.md](./README.md) - Main documentation

