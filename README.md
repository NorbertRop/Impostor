# Gra w Impostora 📱

Progressive Web App (PWA) - gra towarzyska w impostora z polskim słownikiem. **Teraz z trybem multiplayer online!**

## 🎮 Jak działa gra

Wszyscy gracze oprócz jednego widzą to samo słowo. Impostor musi udawać, że je zna!

### 🌐 Tryb Multiplayer (NOWE!)

**Web:**
1. **Host tworzy pokój** - otrzymuje 6-znakowy kod
2. **Gracze dołączają** - używając kodu lub linku
3. **Host rozpoczyna grę** - każdy widzi swoją rolę na swoim urządzeniu
4. **Znajdźcie impostora!** - dyskutujcie i głosujcie

**Discord Bot:**
1. Użyj `/impostor create` na serwerze Discord
2. Inni gracze: `/impostor join code:ABC123`
3. Host: `/impostor start code:ABC123`
4. Bot wysyła DM z słowami do każdego gracza!

### 📱 Tryb lokalny (pojedyncze urządzenie)

1. Wybierz liczbę graczy (minimum 3)
2. Wpisz imiona wszystkich graczy
3. Każdy gracz po kolei podchodzi i widzi swoją informację
4. Jeden losowy gracz jest impostorem
5. Znajdźcie impostora pytając o szczegóły słowa!

## 🚀 Szybki Start

### Option 1: Web Multiplayer (Firebase)

**Wymagania**: Firebase project (darmowy)

1. **Setup Firebase** - Zobacz [FIREBASE_SETUP.md](./FIREBASE_SETUP.md)
2. **Configure environment** - Wypełnij `frontend/.env`
3. **Start app**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. **Open** `http://localhost:5173` w przeglądarce
5. **Test** - otwórz w wielu kartach/urządzeniach

### Option 2: Discord Bot (Discord.py)

**Wymagania**: Discord bot + Render account (darmowy)

1. **Setup Discord Bot** - Zobacz [DISCORD_SETUP.md](./DISCORD_SETUP.md)
2. **Use commands**:
   ```
   /impostor create
   /impostor join code:ABC123
   /impostor start code:ABC123
   ```
3. **Receive DM** - Bot wysyła słowa przez wiadomości prywatne!

### Tryb lokalny (bez internetu)

**Nie potrzebujesz Firebase do trybu lokalnego!**

1. **Wejdź na link:** [Zobacz DEPLOYMENT.md](./DEPLOYMENT.md) jak wdrożyć na hosting
2. **Otwórz w Safari** na iPhone
3. **Kliknij przycisk "Udostępnij"** (kwadrat ze strzałką)
4. **Wybierz "Dodaj do ekranu głównego"**
5. **Gotowe!** Aplikacja działa offline

### Opcje hostingu (darmowe):

- **Firebase Hosting** - https://firebase.google.com/docs/hosting
- **Vercel** - https://vercel.com/
- **Netlify** - https://www.netlify.com/
- **Cloudflare Pages** - https://pages.cloudflare.com/

Zobacz [DEPLOYMENT.md](./DEPLOYMENT.md) dla szczegółowych instrukcji.

## 💻 Rozwój lokalny

### Build aplikacji:

```bash
cd frontend
npm install
npm run build
```

### Test lokalny:

```bash
npm run preview
```

Aplikacja będzie dostępna na `http://localhost:4173`

### Test na iPhone (lokalna sieć):

```bash
npm run dev -- --host
```

Znajdź swoje IP i otwórz `http://YOUR_IP:5173` w Safari na iPhone

## 📁 Struktura projektu

```
impostor/
├── frontend/                  # PWA React app
│   ├── public/
│   │   ├── words.txt         # 10,000 polskich słów
│   │   ├── manifest.json     # PWA manifest
│   │   ├── sw.js             # Service worker
│   │   └── icon-*.png        # Ikony aplikacji
│   ├── src/
│   │   ├── api/
│   │   │   └── room.js       # Firestore API functions
│   │   ├── components/
│   │   │   ├── Setup.jsx     # Create/Join room
│   │   │   ├── Room.jsx      # Room orchestrator
│   │   │   ├── Lobby.jsx     # Waiting room
│   │   │   └── Reveal.jsx    # Word reveal screen
│   │   ├── firebase.js       # Firebase config
│   │   └── App.jsx           # Router setup
│   └── package.json
├── discord_bot/               # Discord bot (standalone deployment)
│   ├── bot/
│   │   ├── bot.py            # Discord bot setup
│   │   ├── commands.py       # Slash commands
│   │   └── utils.py          # DM helpers
│   ├── main.py               # Bot entry point
│   ├── game_logic.py         # Game logic
│   ├── config.py             # Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker config
│   └── README.md             # Bot deployment guide
├── functions/                 # Firebase Cloud Functions
│   ├── index.js              # Game logic & scheduled cleanup
│   ├── words.txt             # Polish word list
│   └── package.json          # Node.js dependencies
├── firestore.rules           # Firestore security rules
├── firebase.json             # Firebase Hosting config
├── FIREBASE_SETUP.md         # Firebase setup guide
├── DISCORD_SETUP.md          # Discord bot setup guide
└── README.md                 # Ten plik
```


## 🎯 Funkcje

✅ **Discord Bot** - graj przez Discord z DM-ami
✅ **Multiplayer online** - graj na wielu urządzeniach jednocześnie
✅ **Hybrid mode** - mieszaj graczy Discord i Web
✅ **Real-time sync** - Firestore realtime updates
✅ **Pokoje gry** - krótkie kody dołączania (ABC123)
✅ **Prywatne słowa** - każdy widzi swoją rolę tylko na swoim urządzeniu
✅ **Kolejność wypowiedzi** - losowa kolejność graczy dla sprawiedliwej rozgrywki
✅ **10,000+ polskich słów** - zoptymalizowany słownik
✅ **PWA** - instalacja jak natywna aplikacja
✅ **Responsywne UI** - piękny gradient, nowoczesny design
✅ **Tryb offline** - tryb lokalny działa bez internetu
✅ **Optymalizacja iOS** - idealne na iPhone
✅ **Auto-cleanup** - stare pokoje (24h+) są automatycznie usuwane

## 📱 Kompatybilność

- ✅ iPhone (Safari) - PWA support
- ✅ Android (Chrome) - PWA support
- ✅ Desktop (wszystkie przeglądarki)

## 🛠️ Technologie

**Frontend:**
- **React 19** - UI framework
- **Vite** - Build tool
- **Firebase Firestore** - Real-time database
- **Firebase Auth** - Anonymous authentication
- **Firebase Hosting** - Static hosting
- **React Router** - Client-side routing
- **PWA** - Progressive Web App

**Cloud Functions:**
- **Firebase Functions** - Game logic & scheduled cleanup
- **Cloud Scheduler** - Automatic cleanup

**Discord Bot:**
- **Discord.py** - Discord bot library
- **Firebase Admin SDK** - Server-side Firestore
- **Render** - Deployment platform

**Shared:**
- **Firestore** - Shared database for web + Discord
- **Słownik**: SJP.pl (GPL 2, LGPL 2.1, CC BY 4.0)

## 🔮 Przyszłe funkcje

Potencjalne ulepszenia:
- 📊 Statistics - śledź statystyki gier i ranking graczy
- 🏆 Leaderboards - tabele wyników per serwer Discord
- 🗳️ Voting system - głosowanie na impostora w Discord
- 🎨 Custom word lists - własne listy słów per serwer
- 🌍 Multi-language - wsparcie dla innych języków

## 📝 Licencja

Aplikacja: MIT
Słownik polski: SJP.pl (GPL 2, LGPL 2.1, CC BY 4.0, MPL 1.1, Apache 2.0)
