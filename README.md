# TV Tracker - Self-Hosted Application

A beautifully designed self-hosted TV show and movie tracking application built with Python (FastAPI) and SQLite.

## Features
- TMDB Integration for metadata
- Watchlist and progress tracking
- TV Time data import
- Modern, responsive Tailwind UI
- Simple Linux bare-metal deployment

## Manual Installation (Linux)

### 1. Prerequisites
- Python 3.9+
- Nginx
- TMDB API Key

### 2. Backend Setup
```bash
git clone https://github.com/Fahad-BA/tv.git
cd tv/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TMDB_API_KEY="your_api_key"
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Nginx Configuration (Subpath Setup)
To serve the app under `yourdomain.com/tv`, add this to your Nginx config:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend serving from /tv
    location /tv/ {
        alias /var/www/tv/frontend/;
        index index.html;
        try_files $uri $uri/ /tv/index.html;
    }

    # API Proxying from /tv/api/
    location /tv/api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Systemd Service
Create `/etc/systemd/system/tv-backend.service`:
```ini
[Unit]
Description=TV Tracker Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tv/backend
Environment="PATH=/var/www/tv/backend/venv/bin"
Environment="TMDB_API_KEY=your_api_key"
ExecStart=/var/www/tv/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
```

## Import from TV Time
Navigate to `yourdomain.com/tv` and use the Import section to upload your TV Time data.
