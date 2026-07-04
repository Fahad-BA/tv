<div align="center">

# 🎬 TV Tracker

**A self-hosted TV show & movie tracking application with TMDB integration**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![TMDB](https://img.shields.io/badge/TMDB-API-01B4E4?style=flat-square)](https://www.themoviedb.org/)

</div>

---

## ✨ Features

- **🔍 TMDB Integration** — Rich metadata, posters, and backdrops from The Movie Database
- **📺 Episode Tracking** — Mark episodes as watched, track progress per season, toggle entire seasons at once
- **📋 Watchlist** — Add shows to your watchlist, search TMDB, and manage your library
- **🔥 Trending** — Discover trending shows each week from TMDB
- **📥 TV Time Import** — Migrate your existing watch history from TV Time via CSV or ZIP export
- **👤 User Accounts** — JWT auth with custom avatars, profile backdrops, and bio
- **📊 Profile Stats** — Track total episodes watched and time spent across all shows
- **📱 Mobile-First Design** — Native app-like UI with bottom navigation, optimized for touch
- **🏗️ Self-Hosted** — Runs on a single port, no Nginx required. Perfect behind Cloudflare Tunnels
- **🎨 Gold & Dark Theme** — Sleek cinema-inspired aesthetic

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn |
| **Frontend** | HTML, Tailwind CSS (CDN), Font Awesome, Vanilla JS |
| **Database** | SQLite via SQLAlchemy ORM |
| **Auth** | JWT (python-jose) + bcrypt password hashing |
| **API** | TMDB API v3 |
| **Deployment** | Systemd, Cloudflare Tunnels |

---

## 📦 Installation

### Prerequisites

- Python 3.9+
- A free [TMDB API Key](https://www.themoviedb.org/settings/api)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/Fahad-BA/tv.git
cd tv/backend

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your TMDB_API_KEY and SECRET_KEY

# Run 🚀
python main.py
```

The app will be available at `http://localhost:8000`.

### Production Deployment (Systemd)

Create `/etc/systemd/system/tv.service`:

```ini
[Unit]
Description=TV Tracker Service
After=network.target

[Service]
User=your-user
Group=your-user
WorkingDirectory=/path/to/tv/backend
Environment="PATH=/path/to/tv/backend/venv/bin"
Environment="TMDB_API_KEY=your_tmdb_api_key"
Environment="SECRET_KEY=your_secret_key"
ExecStart=/path/to/tv/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tv
```

### Cloudflare Tunnel

Point your Cloudflare Tunnel (`cloudflared`) directly to `http://localhost:8000` — no reverse proxy needed.

---

## 📥 Import from TV Time

1. Export your data from the TV Time app (Settings → Export) — both **CSV** and **ZIP** formats are supported
2. Open TV Tracker and navigate to **Import**
3. Upload your TV Time export file
4. Your shows and watch history will be matched via TMDB and imported automatically (multi-show imports supported)

---

## 📁 Project Structure

```
tv/
├── backend/
│   ├── main.py          # FastAPI app, all API routes
│   ├── models.py        # SQLAlchemy models (User, WatchlistItem, EpisodeWatch)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # JWT auth, password hashing
│   ├── tmdb.py          # TMDB API client wrapper
│   ├── database.py      # SQLAlchemy engine & session
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Template for environment variables
│   └── static/          # Uploaded avatars & assets
├── frontend/
│   └── index.html       # Single-page app (Tailwind + vanilla JS)
├── tv_tracker.db        # SQLite database (auto-created)
└── README.md
```

---

## 📸 Screenshots

> _Add screenshots here after deployment_

<!-- ![Dashboard](screenshots/dashboard.png)
 ![Show Detail](screenshots/show-detail.png)
 ![Import](screenshots/import.png) -->

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TMDB_API_KEY` | ✅ | Your TMDB v3 API key |
| `SECRET_KEY` | ✅ | JWT signing secret (use a strong random string) |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register` | Create a new account |
| `POST` | `/api/token` | Login and receive JWT |
| `GET` | `/api/me` | Get current user profile |
| `PATCH` | `/api/me` | Update username, bio, backdrop |
| `POST` | `/api/me/avatar` | Upload profile avatar |
| `GET` | `/api/me/followed-shows-backdrops` | Get backdrop images for a followed show |
| `GET` | `/api/stats` | Get episode count and time spent |
| `GET` | `/api/trending` | Get weekly trending TV shows |
| `GET` | `/api/search` | Search TMDB for shows and movies |
| `GET` | `/api/watchlist` | List current user's watchlist |
| `POST` | `/api/watchlist` | Add a show to watchlist |
| `DELETE` | `/api/watchlist/{tmdb_id}` | Remove show and all watch history |
| `GET` | `/api/shows/{id}/seasons` | Get seasons with episode watch state |
| `POST` | `/api/episodes/{id}/{s}/{e}/toggle` | Toggle watched state of an episode |
| `POST` | `/api/shows/{id}/seasons/toggle` | Mark all episodes in a season as watched |
| `POST` | `/api/import` | Import TV Time CSV or ZIP export |

---

## 📝 License

This project is open-source under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Fahad Alhuqaili](https://github.com/Fahad-BA)**

⭐ If this project helped you, consider giving it a star!

</div>
