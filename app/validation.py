from pydantic import BaseModel, EmailStr, constr

class PostCreate(BaseModel):
    text: constr(max_length=1024 * 1024)  # Limit text size to 1MB

class PostDelete(BaseModel):
    postID: int

class UserSignup(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str