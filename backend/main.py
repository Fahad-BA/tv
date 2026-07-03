from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import json
import csv
import io
import zipfile
import uuid
import requests

from . import models, schemas, auth, tmdb, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TV Tracker API")

# Ensure upload directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth ---
@app.post("/api/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user: raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/api/token")
def login(form_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user: raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": auth.create_access_token(data={"sub": user.email}), "token_type": "bearer"}

# --- User & Stats ---
@app.get("/api/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.patch("/api/me", response_model=schemas.User)
def update_me(data: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/api/me/avatar")
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    avatar_url = f"/api/static/uploads/{unique_filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    return {"avatar_url": avatar_url}

@app.get("/api/me/followed-shows-backdrops")
def get_followed_backdrops(show_id: int, current_user: models.User = Depends(auth.get_current_user)):
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/tv/{show_id}/images?api_key={TMDB_API_KEY}"
    res = requests.get(url).json()
    backdrops = res.get('backdrops', [])[:4]
    return [{"url": f"https://image.tmdb.org/t/p/original{b['file_path']}"} for b in backdrops]

@app.get("/api/stats")
def get_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    watches = db.query(models.EpisodeWatch).filter(models.EpisodeWatch.user_id == current_user.id).count()
    total_minutes = watches * 40
    return {
        "total_episodes": watches,
        "time_spent": {"months": total_minutes // 43200, "days": (total_minutes % 43200) // 1440, "hours": (total_minutes % 1440) // 60, "mins": total_minutes % 60}
    }

# --- Media Tracking ---
@app.get("/api/trending")
def get_trending(current_user: models.User = Depends(auth.get_current_user)):
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={TMDB_API_KEY}"
    return requests.get(url).json().get("results", [])

@app.get("/api/search")
def search_media(query: str, current_user: models.User = Depends(auth.get_current_user)):
    return tmdb.search(query)

@app.get("/api/watchlist")
def get_watchlist(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    items = db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == current_user.id).all()
    results = []
    for item in items:
        watched_count = db.query(models.EpisodeWatch).filter(models.EpisodeWatch.user_id == current_user.id, models.EpisodeWatch.show_id == item.tmdb_id).count()
        d = item.__dict__.copy()
        d['episodes_watched'] = watched_count
        results.append(d)
    return results

@app.post("/api/watchlist")
def add_to_watchlist(item: schemas.WatchlistItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return models.add_watchlist_item(db, item, current_user.id)

@app.get("/api/shows/{show_id}/seasons")
def get_show_seasons(show_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    details = tmdb.get_show_details(show_id)
    seasons = []
    for s in details.get('seasons', []):
        s_num = s['season_number']
        s_details = tmdb.get_season_details(show_id, s_num)
        episodes = []
        for ep in s_details.get('episodes', []):
            ep_num = ep['episode_number']
            watch = db.query(models.EpisodeWatch).filter(
                models.EpisodeWatch.user_id == current_user.id,
                models.EpisodeWatch.show_id == show_id,
                models.EpisodeWatch.season_number == s_num,
                models.EpisodeWatch.episode_number == ep_num
            ).first()
            ep['watched'] = watch is not None
            ep['user_rating'] = watch.rating if watch else None
            episodes.append(ep)
        s['episodes'] = episodes
        seasons.append(s)
    return seasons

@app.post("/api/episodes/{show_id}/{season}/{episode}/toggle")
def toggle_episode(show_id: int, season: int, episode: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    watch = db.query(models.EpisodeWatch).filter(
        models.EpisodeWatch.user_id == current_user.id,
        models.EpisodeWatch.show_id == show_id,
        models.EpisodeWatch.season_number == season,
        models.EpisodeWatch.episode_number == episode
    ).first()
    if watch:
        db.delete(watch)
        status = False
    else:
        db.add(models.EpisodeWatch(user_id=current_user.id, show_id=show_id, season_number=season, episode_number=episode))
        status = True
    db.commit()
    return {"watched": status}

@app.post("/api/shows/{show_id}/seasons/toggle")
def toggle_season(show_id: int, data: schemas.SeasonToggle, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    for ep_num in data.episodes:
        existing = db.query(models.EpisodeWatch).filter(
            models.EpisodeWatch.user_id == current_user.id,
            models.EpisodeWatch.show_id == show_id,
            models.EpisodeWatch.season_number == data.season_number,
            models.EpisodeWatch.episode_number == ep_num
        ).first()
        if not existing:
            db.add(models.EpisodeWatch(user_id=current_user.id, show_id=show_id, season_number=data.season_number, episode_number=ep_num))
    db.commit()
    return {"message": "Season marked as watched"}

# --- Import ---
@app.post("/api/import")
async def import_tv_time(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    content = await file.read()
    filename = file.filename.lower()
    items_added = 0
    
    def process_import(data_stream, fname):
        nonlocal items_added
        if fname.endswith('.csv'):
            decoded = data_stream.decode('utf-8', errors='ignore')
            reader = csv.DictReader(io.StringIO(decoded))
            for row in reader:
                show_name = row.get('tv_show_name') or row.get('show_name') or row.get('Show Name')
                if show_name:
                    # Map to watchlist
                    models.add_watchlist_item(db, schemas.WatchlistItemCreate(tmdb_id=0, title=show_name, media_type='tv'), current_user.id)
                    
                    # Map episode watch
                    try:
                        s_num = int(row.get('season_number', row.get('Season', 0)))
                        e_num = int(row.get('episode_number', row.get('Episode', 0)))
                        if s_num and e_num:
                            existing_watch = db.query(models.EpisodeWatch).filter(
                                models.EpisodeWatch.user_id == current_user.id,
                                models.EpisodeWatch.show_id == 0, # Imported shows without TMDB ID yet
                                models.EpisodeWatch.season_number == s_num,
                                models.EpisodeWatch.episode_number == e_num
                            ).first()
                            if not existing_watch:
                                db.add(models.EpisodeWatch(user_id=current_user.id, show_id=0, season_number=s_num, episode_number=e_num))
                                items_added += 1
                    except:
                        pass # Ignore row if episode data malformed

    if filename.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            for n in z.namelist():
                if n.endswith('.csv'): 
                    process_import(z.read(n), n)
    else: 
        process_import(content, filename)
    
    db.commit()
    return {"message": f"Successfully imported data across all records.", "count": items_added}

# --- Static ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/api/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

frontend_path = os.path.join(backend_dir, "..", "frontend")
@app.get("/")
@app.get("/watchlist")
@app.get("/import")
@app.get("/profile")
async def serve_frontend(): return FileResponse(os.path.join(frontend_path, "index.html"))
app.mount("/", StaticFiles(directory=frontend_path), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
