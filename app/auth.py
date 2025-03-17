import time

import jwt
from config import JWT_ALGORITHM, JWT_SECRET
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer




class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    def decodeJWT(self, token):
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return decoded_token if float(decoded_token["expires"]) >= time.time() else None
        except jwt.exceptions.InvalidTokenError:
            return None

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            decoded_creds = self.decodeJWT(credentials.credentials)
            if not decoded_creds:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return decoded_creds
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        
    def createJWT(self, email: str):
        payload = {
            "email": email,
            "expires": time.time() + 600  # Token expires in 10 minutes
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token