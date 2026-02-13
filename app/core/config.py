'''This module defines the core configuration settings for the FastAPI application.

It centralizes key environment variables and constants used throughout the project,
including database connection details, security parameters, and token expiration settings.'''

import os
database_url='mysql+pymysql://sa:tudip123@localhost:3306/Capstone'
SECRET_KEY=os.getenv("SECRET_KEY","251002")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120