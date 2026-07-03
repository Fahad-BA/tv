from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    backdrop_url: Optional[str] = None

class User(UserBase):
    id: int
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class WatchlistItemCreate(BaseModel):
    tmdb_id: int
    title: str
    media_type: str
    poster_path: Optional[str] = None
    status: str = "planning"

class WatchlistItemUpdate(BaseModel):
    status: Optional[str] = None
    episodes_watched: Optional[int] = None
    total_episodes: Optional[int] = None
    user_rating: Optional[float] = None
    is_favorite: Optional[bool] = None
