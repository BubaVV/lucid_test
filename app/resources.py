from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from auth import JWTBearer
from models import engine, Post
from models import User
from passlib.context import CryptContext

posts = APIRouter()
auth = APIRouter()


@posts.get('/GetPosts')
async def read_posts(request: Request, auth=Depends(JWTBearer())):
    with Session(engine) as session:
        statement = select(Post)
        result = session.exec(statement).all()

    return result


@posts.post('/AddPost')
async def create_post(request: Request, auth=Depends(JWTBearer())):
    post = await request.json()
    post['author_id'] = auth['user']
    with Session(engine) as session:
        session.add(Post(**post))
        session.commit()

@auth.post('/Signup')
async def signup(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(password):
        return pwd_context.hash(password)

    # Hash the password
    hashed_password = get_password_hash(password)

    # Add the user to the database
    with Session(engine) as session:
        user = User(username=email, password=hashed_password)
        session.add(user)
        session.commit()

    # Generate JWT token
    token = JWTBearer().createJWT(email)

    return {"token": token}

@auth.post('/Login')
async def login(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    with Session(engine) as session:
        statement = select(User).where(User.username == email)
        user = session.exec(statement).first()

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=403, detail="Invalid email or password")

    # Generate JWT token
    token = JWTBearer().createJWT(email)

    return {"token": token}
