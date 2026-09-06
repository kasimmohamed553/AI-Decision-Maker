# AI Decision Maker

A full-stack app that analyzes sales data (CSV/Excel) and produces a business
decision — **EXPAND / MAINTAIN / REDUCE** — using a self-contained, rule-based
decision engine. No external AI API, no API keys to manage, no rate limits.

- **Frontend:** plain HTML, CSS, JS (no build step)
- **Backend:** Flask, with JWT-based login/register
- **Decision engine:** your own scoring rules in `backend/decision_engine.py`

## How the decision engine works

It's transparent by design — see `backend/decision_engine.py`. Four signals
are scored and summed into a single number from -100 to +100:

| Signal | What it checks |
|---|---|
| Growth | Sales trend between first and second half of the dataset |
| Order value | Average order size |
| Volume | Total number of orders (confidence signal) |
| Concentration | How reliant sales are on one product (risk signal) |

The final score maps to a verdict:
- `score >= 30` → **EXPAND**
- `-10 <= score < 30` → **MAINTAIN**
- `score < -10` → **REDUCE**

Every reason behind the score is returned in the API response and shown in
the UI — nothing is a black box. You can freely tune the thresholds/weights
in `decision_engine.py` to fit your own business logic.

## Project structure

```
ai_decision_maker/
├── backend/
│   ├── app.py                   # Flask app & routes
│   ├── config.py                # Settings (reads .env)
│   ├── models.py                # User DB model
│   ├── auth.py                  # /register, /login, /me
│   ├── analyzer.py              # Parses CSV/XLSX into summary stats
│   ├── decision_engine.py       # <-- the "AI" (your own rules)
│   ├── recommendation_engine.py # Extra tips based on summary
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── css/style.css
    └── js/
        ├── config.js             # Set your backend URL here
        └── script.js
```

## Setup (local)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set a real secret:
```
JWT_SECRET_KEY=some_long_random_string
```

Run it:
```bash
python app.py
```
Server starts at `http://127.0.0.1:5000`.

### 2. Frontend

No build step needed. Just open `frontend/login.html` directly in your
browser, or serve the folder with any static server, e.g.:
```bash
cd frontend
python -m http.server 5500
```
Then visit `http://127.0.0.1:5500/login.html`.

`frontend/js/config.js` controls which backend URL the frontend talks to —
update it if your backend isn't on `127.0.0.1:5000`.

## Required CSV/Excel columns

Only **`Order_Amount`** is strictly required. These are optional but unlock
deeper analysis:
```
Product, Category, Region, Order_Date, No_of_Items
```

## Deploying live

- **Backend** → any Python host (Render, Railway, Fly.io). Set `JWT_SECRET_KEY`
  as an environment variable there — never commit `.env`. Use
  `gunicorn app:app` as the start command instead of `python app.py`.
- **Frontend** → any static host (Netlify, GitHub Pages, Vercel). Update
  `API_BASE` in `js/config.js` to your live backend URL before deploying.

## Security notes

- Passwords are hashed with bcrypt, never stored in plain text.
- Auth uses JWT tokens (stored in `localStorage` on the frontend), sent via
  `Authorization: Bearer <token>` — works cleanly across different domains
  for frontend/backend.
- `.gitignore` already excludes `.env`, `users.db`, and uploaded files.
