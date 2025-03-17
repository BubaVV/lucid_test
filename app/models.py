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
    text: str
    author_id: str

def init_db():
    SQLModel.metadata.create_all(engine)
