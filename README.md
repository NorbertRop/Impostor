# Gra w Impostora 📱

Progressive Web App (PWA) - gra towarzyska w impostora z polskim słownikiem. Działa całkowicie offline na iPhone!

## 🎮 Jak działa gra

Wszyscy gracze oprócz jednego widzą to samo słowo. Impostor musi udawać, że je zna!

1. Wybierz liczbę graczy (minimum 3)
2. Wpisz imiona wszystkich graczy
3. Każdy gracz po kolei podchodzi i widzi swoją informację
4. Jeden losowy gracz jest impostorem
5. Znajdźcie impostora pytając o szczegóły słowa!

## 🚀 Wersja Standalone (bez komputera)

**Aplikacja działa teraz 100% offline na telefonie!**

### Instalacja na iPhone:

1. **Wejdź na link:** [Zobacz DEPLOYMENT.md](./DEPLOYMENT.md) jak wdrożyć na hosting
2. **Otwórz w Safari** na iPhone
3. **Kliknij przycisk "Udostępnij"** (kwadrat ze strzałką)
4. **Wybierz "Dodaj do ekranu głównego"**
5. **Gotowe!** Aplikacja działa offline

### Opcje hostingu (darmowe):

- **GitHub Pages** - https://pages.github.com/
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
├── frontend/              # PWA React app
│   ├── public/
│   │   ├── words.txt     # 10,000 polskich słów
│   │   ├── manifest.json # PWA manifest
│   │   ├── sw.js         # Service worker
│   │   └── icon-*.png    # Ikony aplikacji
│   ├── src/
│   │   ├── utils/
│   │   │   └── game.js   # Logika gry (client-side)
│   │   └── components/   # Komponenty React
│   └── package.json
├── backend/              # [DEPRECATED] Nie jest już potrzebny!
├── DEPLOYMENT.md         # Szczegółowy przewodnik wdrożenia
└── README.md            # Ten plik
```

## 🎯 Funkcje

✅ **Całkowicie offline** - działa bez internetu po instalacji
✅ **10,000+ polskich słów** - zoptymalizowany słownik
✅ **PWA** - instalacja jak natywna aplikacja
✅ **Responsywne UI** - piękny gradient, nowoczesny design
✅ **Zero backendu** - wszystko działa w przeglądarce
✅ **Optymalizacja iOS** - idealne na iPhone

## 📱 Kompatybilność

- ✅ iPhone (Safari) - PWA support
- ✅ Android (Chrome) - PWA support
- ✅ Desktop (wszystkie przeglądarki)

## 🛠️ Technologie

- **React 19** - UI framework
- **Vite** - Build tool
- **PWA** - Progressive Web App
- **Service Worker** - Offline functionality
- **Słownik**: SJP.pl (GPL 2, LGPL 2.1, CC BY 4.0)

## 📝 Licencja

Aplikacja: MIT
Słownik polski: SJP.pl (GPL 2, LGPL 2.1, CC BY 4.0, MPL 1.1, Apache 2.0)

---

**Uwaga:** Stara wersja z backendem (FastAPI) znajduje się w folderze `backend/` ale **nie jest już potrzebna**. Nowa wersja działa w 100% po stronie klienta!
