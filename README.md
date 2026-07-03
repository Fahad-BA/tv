# TV Tracker - Self-Hosted Application

A beautifully designed self-hosted TV show and movie tracking application built with Python (FastAPI) and SQLite.

## Features
- TMDB Integration for metadata
- Watchlist and progress tracking
- TV Time data import
- Modern, responsive Tailwind UI
- Direct port serving (no Nginx required)
- Optimized for Cloudflare Tunnels

## Manual Installation (Linux)

### 1. Prerequisites
- Python 3.9+
- TMDB API Key

### 2. Application Setup
```bash
git clone https://github.com/Fahad-BA/tv.git
cd tv/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TMDB_API_KEY="your_api_key"
# Runs the application on port 8000
python main.py
```

### 3. Systemd Service (Production)
To keep the application running in the background and start on boot, create `/etc/systemd/system/tv.service`:

```ini
[Unit]
Description=TV Tracker Unified Service
After=network.target

[Service]
User=your-user
Group=your-user
WorkingDirectory=/path/to/tv/backend
Environment="PATH=/path/to/tv/backend/venv/bin"
Environment="TMDB_API_KEY=your_tmdb_api_key"
ExecStart=/path/to/tv/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

### 4. Cloudflare Configuration
Since the app runs on a direct port, you can point your Cloudflare Tunnel (cloudflared) or Page Rule directly to `http://localhost:8000`.

## Import from TV Time
Access the application via your domain or direct IP:port and navigate to the Import section to upload your data.
