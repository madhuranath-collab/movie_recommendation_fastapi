'''This module defines the Pydantic schema models for the User of the application.
    These models are primarily imported and used in FastAPI endpoints,
    service layers, and database repositories for input validation and
    response formatting.'''

from pydantic import BaseModel,EmailStr
from typing import Optional

class UserCreate(BaseModel):
    '''schema for creating a new user'''
    username: str
    email: str
    role: Optional[str] ="user"
    password: str

class UserLogin(BaseModel):
    '''schema for input of login endpoint'''
    email:EmailStr
    password:str

class create_platform(BaseModel):
    movie_id:int
    platform:str


