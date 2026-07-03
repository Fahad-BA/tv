from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from .database import Base
from . import schemas

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    backdrop_url = Column(String, nullable=True)

class WatchlistItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tmdb_id = Column(Integer)
    title = Column(String)
    media_type = Column(String) # 'movie' or 'tv'
    poster_path = Column(String)
    status = Column(String, default="planning") # planning, watching, completed
    user_rating = Column(Float, nullable=True)
    is_favorite = Column(Boolean, default=False)

class EpisodeWatch(Base):
    __tablename__ = "episode_watches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    show_id = Column(Integer) # TMDB Show ID
    season_number = Column(Integer)
    episode_number = Column(Integer)
    watched_at = Column(DateTime, default=datetime.utcnow)
    rating = Column(Integer, nullable=True) # 1-5 or emotional reaction mapping

def add_watchlist_item(db: Session, item: schemas.WatchlistItemCreate, user_id: int):
    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id, 
        WatchlistItem.tmdb_id == item.tmdb_id
    ).first()
    if existing: return existing
    db_item = WatchlistItem(user_id=user_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
