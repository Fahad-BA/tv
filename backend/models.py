from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship, Session
from .database import Base
from . import schemas

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class WatchlistItem(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tmdb_id = Column(Integer)
    title = Column(String)
    media_type = Column(String) # 'movie' or 'tv'
    poster_path = Column(String)
    status = Column(String, default="planning") # planning, watching, completed

def add_watchlist_item(db: Session, item: schemas.WatchlistItemCreate, user_id: int):
    db_item = WatchlistItem(
        user_id=user_id,
        tmdb_id=item.tmdb_id,
        title=item.title,
        media_type=item.media_type,
        poster_path=item.poster_path,
        status=item.status,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
