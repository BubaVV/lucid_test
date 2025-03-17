from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

from config import DB_URI

engine = create_engine(DB_URI)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(primary_key=True, default=None)
    username: str
    password: str

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(primary_key=True, default=None)
    title: str
    content: str
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

def init_db():
    SQLModel.metadata.create_all(engine)
