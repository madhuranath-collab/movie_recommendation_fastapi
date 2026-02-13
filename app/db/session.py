'''It sets up the database engine using the configured `database_url`, provides a session factory
(`SessionLocal`) for creating transactional database sessions, and defines a dependency function
(`get_db`) that integrates cleanly with FastAPI's dependency injection system.'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import database_url

'''Components:
    - **engine**: SQLAlchemy Engine instance used to interact with the database.
    - **SessionLocal**: Session factory for creating database sessions.
    - **Base**: Declarative base for defining ORM models.
    - **get_db**: Dependency function that provides a scoped database session to API routes.'''

engine=create_engine(database_url)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#base class

'''The SQLAlchemy `Base` class serves as the declarative base for defining ORM models.
All database tables mapped to these models can be created automatically via `Base.metadata.create_all()'''

Base=declarative_base()

Base.metadata.create_all(bind=engine)