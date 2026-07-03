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

from . import models, schemas, auth, tmdb, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TV Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routes ---

@app.post("/api/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/api/token")
def login(form_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.patch("/api/me", response_model=schemas.User)
def update_me(data: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    for field, value in data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/api/stats")
def get_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    watchlist = db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == current_user.id).all()
    total_episodes = sum(item.episodes_watched for item in watchlist)
    
    # TV Time style: 1 episode ~ 40 mins avg
    total_minutes = total_episodes * 40
    
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    mins = total_minutes % 60
    months = days // 30
    remaining_days = days % 30

    return {
        "total_shows": len(watchlist),
        "total_episodes": total_episodes,
        "time_spent": {
            "months": int(months),
            "days": int(remaining_days),
            "hours": int(hours),
            "mins": int(mins)
        },
        "favorites": [i for i in watchlist if i.is_favorite]
    }

@app.get("/api/search")
def search_media(query: str, current_user: models.User = Depends(auth.get_current_user)):
    return tmdb.search(query)

@app.post("/api/watchlist")
def add_to_watchlist(item: schemas.WatchlistItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return models.add_watchlist_item(db, item, current_user.id)

@app.get("/api/watchlist")
def get_watchlist(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == current_user.id).all()

@app.post("/api/import")
async def import_tv_time(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    content = await file.read()
    filename = file.filename.lower()
    items_added = 0

    def process_file_content(file_data, fname):
        nonlocal items_added
        if fname.endswith('.json'):
            data = json.loads(file_data)
            shows = data.get('shows', []) or data.get('to_watch', []) or data
            if not isinstance(shows, list): shows = [shows]
            for entry in shows:
                title = entry.get('name') or entry.get('title')
                if title:
                    models.add_watchlist_item(db, schemas.WatchlistItemCreate(
                        tmdb_id=entry.get('id', 0), title=title, media_type='tv', status='watching'
                    ), current_user.id)
                    items_added += 1
        elif fname.endswith('.csv'):
            stream = io.StringIO(file_data.decode("utf-8"))
            reader = csv.DictReader(stream)
            for row in reader:
                title = row.get('name') or row.get('title') or row.get('Show Name') or row.get('show_name')
                if title:
                    models.add_watchlist_item(db, schemas.WatchlistItemCreate(
                        tmdb_id=0, title=title, media_type='tv', status='watching'
                    ), current_user.id)
                    items_added += 1

    if filename.endswith('.zip'):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                for zname in z.namelist():
                    if zname.endswith(('.json', '.csv')):
                        with z.open(zname) as f:
                            process_file_content(f.read(), zname)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process ZIP: {str(e)}")
    else:
        try:
            process_file_content(content, filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    return {"message": f"Successfully imported {items_added} items.", "count": items_added}

# --- Static File Serving ---

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

@app.get("/")
@app.get("/watchlist")
@app.get("/import")
@app.get("/upcoming")
@app.get("/profile")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.mount("/", StaticFiles(directory=frontend_path), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
