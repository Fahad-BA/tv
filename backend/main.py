from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import os

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

@app.get("/api/search")
def search_media(query: str, current_user: models.User = Depends(auth.get_current_user)):
    return tmdb.search(query)

@app.post("/api/watchlist")
def add_to_watchlist(item: schemas.WatchlistItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return models.add_watchlist_item(db, item, current_user.id)

# --- Static File Serving ---

# Ensure frontend directory path is absolute
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

# Mount the frontend directory for static assets (CSS/JS/images)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Serve the main index.html for the root path
@app.get("/")
@app.get("/{path_name:path}")
async def serve_frontend(path_name: str = None):
    # This serves index.html for all non-API routes to support SPA behavior
    file_path = os.path.join(frontend_path, "index.html")
    return FileResponse(file_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
