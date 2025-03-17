from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from auth import JWTBearer
from models import engine, Post
from models import User
from passlib.context import CryptContext
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from validation import PostCreate, PostDelete, UserSignup, UserLogin

posts = APIRouter()
auth = APIRouter()

@posts.post('/AddPost')
async def create_post(request: Request, auth=Depends(JWTBearer())):
    # Validate payload size
    if request.headers.get('content-length') and int(request.headers.get('content-length')) > 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload too large")

    post_data = await request.json()

    # Validate post data using Pydantic model
    try:
        post = PostCreate(**post_data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Check for valid token and get user email
    if 'email' not in auth:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    user_email = auth['email']

    # Get author_id from Users table based on email
    with Session(engine) as session:
        statement = select(User).where(User.username == user_email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        post_data['author_id'] = user.id

        # Save the post in memory
        new_post = Post(**post_data)
        session.add(new_post)
        session.commit()
        session.refresh(new_post)

    return {"postID": new_post.id}

@posts.get('/GetPosts')
@cache(expire=300)
async def get_user_posts(request: Request, auth=Depends(JWTBearer())):
    # Check for valid token and get user email
    if 'email' not in auth:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    user_email = auth['email']

    # Get author_id from Users table based on email
    with Session(engine) as session:
        statement = select(User).where(User.username == user_email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        author_id = user.id

        # Get all posts by the user
        statement = select(Post).where(Post.author_id == author_id)
        user_posts = session.exec(statement).all()

    return user_posts

@posts.delete('/DeletePost')
async def delete_post(request: Request, auth=Depends(JWTBearer())):
    # Validate payload size
    if request.headers.get('content-length') and int(request.headers.get('content-length')) > 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload too large")

    post_data = await request.json()
    # Validate post data using Pydantic model
    try:
        post_delete = PostDelete(**post_data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    postID = post_data.get('postID')

    if not postID:
        raise HTTPException(status_code=400, detail="Post ID is required")

    # Check for valid token and get user email
    if 'email' not in auth:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    user_email = auth['email']

    with Session(engine) as session:
        # Get author_id from Users table based on email
        statement = select(User).where(User.username == user_email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        author_id = user.id

        # Get the post to delete
        statement = select(Post).where(Post.id == postID, Post.author_id == author_id)
        post = session.exec(statement).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found or you do not have permission to delete this post")

        # Delete the post
        session.delete(post)
        session.commit()

    return {"detail": "Post deleted successfully"}

# Initialize cache
FastAPICache.init(InMemoryBackend())

@auth.post('/Signup')
async def signup(request: Request):
    data = await request.json()
    # Validate user signup data using Pydantic model
    try:
        user_signup = UserSignup(**data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
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
    # Validate user login data using Pydantic model
    try:
        user_login = UserLogin(**data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
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

