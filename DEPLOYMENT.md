# Deployment Guide - Gra w Impostora

This app is now a **Progressive Web App (PWA)** that works 100% offline on iPhone after installation.

## 🚀 Quick Deploy Options

### Option 1: GitHub Pages (Recommended - Free & Easy)

1. **Push to GitHub:**
```bash
cd /Users/norbert/git/impostor
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/impostor.git
git push -u origin main
```

2. **Build the app:**
```bash
cd frontend
npm run build
```

3. **Deploy to GitHub Pages:**
```bash
# Install gh-pages
npm install -D gh-pages

# Add to package.json scripts:
# "deploy": "npm run build && gh-pages -d dist"

# Deploy
npm run deploy
```

4. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: gh-pages branch
   - Your app will be at: `https://YOUR_USERNAME.github.io/impostor/`

### Option 2: Vercel (Free & Instant)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel
```

3. Follow prompts and get instant URL

### Option 3: Netlify Drop (Easiest)

1. Build the app:
```bash
cd frontend
npm run build
```

2. Visit https://app.netlify.com/drop
3. Drag and drop the `dist` folder
4. Get instant URL

## 📱 Install on iPhone

Once deployed to any hosting:

1. **Open the URL in Safari** on your iPhone
2. **Tap the Share button** (square with arrow)
3. **Scroll down and tap "Add to Home Screen"**
4. **Tap "Add"**
5. **Done!** The app icon appears on your home screen

### After Installation:
- ✅ Works completely offline
- ✅ No backend needed
- ✅ Full screen experience
- ✅ 10,000 Polish words included
- ✅ Like a native app

## 🔧 Local Testing

To test locally before deployment:

```bash
cd frontend
npm run build
npm run preview
```

Then test on your iPhone by:
1. Finding your computer's local IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. Opening `http://YOUR_IP:4173` in iPhone Safari (both devices on same WiFi)

## 📦 What's Included in the Build

- All React app code (minified)
- 10,000 Polish words (optimized dictionary)
- PWA manifest for iOS installation
- Service worker for offline functionality
- App icons (192x192 and 512x512)

## 🌐 Free Hosting Options Summary

| Service | Pros | Cons |
|---------|------|------|
| **GitHub Pages** | Free, reliable, version control | Requires GitHub account |
| **Vercel** | Instant, CI/CD, custom domains | Requires account |
| **Netlify** | Drag-and-drop, easy | Manual updates |
| **Cloudflare Pages** | Fast, free SSL | Requires account |

All options are **100% free** for this use case!

## ✅ Current Status

- ✅ App is client-side only
- ✅ No backend required
- ✅ PWA configured
- ✅ Offline support ready
- ✅ iPhone optimized
- ✅ Ready to deploy

Choose any hosting option above and your app will work perfectly on iPhone!

