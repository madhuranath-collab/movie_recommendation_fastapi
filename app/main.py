'''This is the entry point of the FastAPI application.

It initializes the FastAPI app instance, sets up the database tables,
attaches middleware for authentication, and includes versioned API routers
for modular route management.'''

from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.v1 import auth
from app.api.v1 import watchlist
from app.middleware.middleware import AuthMiddleware
from app.exceptions.custom_exceptions import WatchlistBaseException
from app.exceptions.handlers import watchlist_exception_handler
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User & Watchlist API")

# add middleware
app.add_middleware(AuthMiddleware)

# Include versioned API routers
app.include_router(auth.router, tags=["Users and Auth"])
app.include_router(watchlist.router, tags=["Users Watchlist"])
app.add_exception_handler(WatchlistBaseException, watchlist_exception_handler)