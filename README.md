# Gra w Impostora

Webowa gra w impostora dla n graczy z polskim słownikiem. Wszyscy gracze oprócz jednego widzą to samo słowo, a impostor musi udawać, że je zna.

## Wymagania

- Python 3.8+
- Node.js 18+
- npm

## Instalacja i uruchomienie

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend będzie działał na `http://localhost:8000`

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend będzie działał na `http://localhost:5173`

## Jak grać

1. Otwórz `http://localhost:5173` w przeglądarce
2. Wybierz liczbę graczy (minimum 3)
3. Wpisz imiona wszystkich graczy
4. Kliknij "Rozpocznij Grę"
5. Każdy gracz po kolei podchodzi do komputera i widzi:
   - Swoje słowo (jeśli jest normalnym graczem)
   - Komunikat "Jesteś IMPOSTOREM!" (jeśli jest impostorem)
6. Po zobaczeniu słowa, gracz klika "Następny Gracz"
7. Po tym jak wszyscy zobaczyli swoje słowa, możecie rozpocząć grę

## Struktura projektu

```
impostor/
├── backend/
│   ├── main.py           # FastAPI endpoints
│   ├── game.py           # Game logic
│   ├── dictionary.py     # Polish dictionary loader
│   ├── requirements.txt  # Python dependencies
│   └── data/
│       └── polish_words.txt  # 340k+ Polish words
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Setup.jsx       # Game setup screen
│   │   │   ├── PlayerView.jsx  # Player turn screen
│   │   │   └── *.css           # Component styles
│   └── package.json
└── README.md
```

## Słownik

Projekt używa oficjalnego słownika polskiego z [sjp.pl](https://sjp.pl/sl/ort/) zawierającego ponad 340,000 polskich słów.

## Technologie

- **Backend**: FastAPI, Python 3
- **Frontend**: React, Vite
- **Słownik**: SJP.pl (licencje: GPL 2, LGPL 2.1, CC BY 4.0, MPL 1.1, Apache 2.0)

