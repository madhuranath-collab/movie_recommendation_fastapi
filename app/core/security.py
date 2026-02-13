'''This module provides core security utilities for the FastAPI application,
including password validation and hashing, as well as JWT (JSON Web Token)
creation and verification.'''

import re
from passlib.context import CryptContext
from app.core.config import *
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.logger import *

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
 
def is_strong_password(password: str):
    '''Checks whether a given password meets the application's strength requirements.'''
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True
 
def hash_password(password: str):
    ''' Hashes a given password using the Argon2 algorithm.'''
    if not is_strong_password(password):
        logger.error(
            {
                "event": "Password Hashing Failed",
                "reason": "Weak password provided",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        )
        raise ValueError("Password is too weak")
    return pwd_context.hash(password)

# JWT functions
def create_jwt(data: dict, expires_delta: timedelta = None):
    '''Creates a signed JWT access token containing the provided payload.'''
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(token: str):
    '''Verifies and decodes a JWT access token.'''
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(
            {
            "event": "JWT Verified",
            "user_id": payload.get("user_id"),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        )
        return payload
    except JWTError as e:
        logger.warning({
            "event": "JWT Verification Failed",
            "reason": "Invalid or expired token",
            "error": str(e),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        })
        return None
     