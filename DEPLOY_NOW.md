# Quick Deployment Guide

Your code is now on GitHub! Follow these steps to deploy.

## ✅ What's Already Done

- ✅ Code pushed to GitHub
- ✅ Firebase service account excluded from repo
- ✅ All backend code ready
- ✅ All documentation complete

## 🚀 Next Steps

### Step 1: Deploy Backend to Render (10 minutes)

1. **Go to Render**: https://dashboard.render.com/

2. **Create New Web Service**:
   - Click **New +** → **Web Service**
   - Connect your GitHub account (if not already)
   - Select repository: `NorbertRop/Impostor`
   - Click **Connect**

3. **Configure Service**:
   - **Name**: `impostor-backend` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

4. **Set Environment Variables** (click "Advanced"):
   
   **DISCORD_TOKEN**
   ```
   YOUR_DISCORD_BOT_TOKEN_FROM_DEVELOPER_PORTAL
   ```
   
   **FIREBASE_SERVICE_ACCOUNT**
   ```
   {"type":"service_account","project_id":"impostor-6320a","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
   ```
   ⚠️ **Copy from your `backend/impostor-6320a-firebase-adminsdk-*.json` file as SINGLE LINE**
   
   **CORS_ORIGINS**
   ```
   https://impostor-6320a.web.app,http://localhost:5173
   ```
   
   **WEB_BASE_URL**
   ```
   https://impostor-6320a.web.app
   ```

5. **Click "Create Web Service"**

6. **Wait for deployment** (2-3 minutes)
   - Watch logs for:
     ```
     ✅ Firebase Admin SDK initialized successfully
     ✅ Discord bot logged in as YourBot
     ✅ Synced 1 command(s)
     ```

7. **Note your Render URL**: `https://impostor-backend-xxxx.onrender.com`

### Step 2: Test Discord Bot (2 minutes)

1. **In your Discord server**, type `/`

2. **Look for `/impostor` command** in the list

3. **Test it**:
   ```
   /impostor create
   ```

4. **You should get a response** with a room code!

### Step 3: Deploy Frontend to Firebase Hosting (5 minutes)

1. **Install Firebase CLI** (if not already):
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

4. **Note your hosting URL**: `https://impostor-6320a.web.app`

### Step 4: Test End-to-End (5 minutes)

**Test 1: Discord Create + Web Join**
1. Discord: `/impostor create`
2. Copy the room code
3. Web: Open `https://impostor-6320a.web.app`
4. Enter name and join with code
5. Discord: `/impostor start code:ABC123`
6. Check DM for your word!

**Test 2: Web Create + Discord Join**
1. Web: Create room
2. Copy code
3. Discord: `/impostor join code:ABC123`
4. Web: Start game
5. Discord: `/impostor reveal code:ABC123`

## 🐛 Troubleshooting

### Backend won't start
- Check environment variables are set correctly
- View Render logs for errors
- Verify Firebase service account JSON is valid single line

### Bot not responding
- Wait 5-10 minutes for commands to sync
- Check bot is online in Discord
- Verify DISCORD_TOKEN is correct
- Check Render logs

### DMs not working
- Enable "Allow direct messages from server members" in Discord
- Check Message Content Intent is enabled in Developer Portal

## 📋 Checklist

- [ ] Backend deployed to Render
- [ ] Environment variables set
- [ ] Backend logs show bot connected
- [ ] Discord commands appear
- [ ] `/impostor create` works
- [ ] Frontend deployed to Firebase
- [ ] Web interface loads
- [ ] Can create room on web
- [ ] Discord + Web hybrid works
- [ ] DMs are received

## 🎮 You're Done!

Once all checkboxes are complete, you can:
- Share your Discord server invite
- Share web link: `https://impostor-6320a.web.app`
- Play with friends!

## 📞 Need Help?

Check these files:
- `DISCORD_SETUP.md` - Discord bot configuration
- `BACKEND_DEPLOYMENT.md` - Detailed Render guide
- `backend/README.md` - Local testing guide
- `IMPLEMENTATION_COMPLETE.md` - Full summary

---

**Current Status:**
- ✅ Code on GitHub: https://github.com/NorbertRop/Impostor
- ⏳ Backend: Deploy to Render now
- ⏳ Frontend: Deploy to Firebase after backend
- ⏳ Testing: After both are deployed

Good luck! 🚀

