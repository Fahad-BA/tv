from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from . import models, schemas, auth, tmdb, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="TV Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/token")
def login(form_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/search")
def search_media(query: str, current_user: models.User = Depends(auth.get_current_user)):
    return tmdb.search(query)

@app.post("/watchlist")
def add_to_watchlist(item: schemas.WatchlistItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return models.add_watchlist_item(db, item, current_user.id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
