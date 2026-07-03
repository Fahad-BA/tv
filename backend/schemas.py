from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class WatchlistItemCreate(BaseModel):
    tmdb_id: int
    title: str
    media_type: str
    poster_path: str | None = None
    status: str = "planning"
