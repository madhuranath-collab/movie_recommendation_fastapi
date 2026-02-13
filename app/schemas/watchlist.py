'''This module defines the Pydantic schema models for the Watchlist feature of the application.'''

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WatchlistBase(BaseModel):

    '''Base schema for watchlist entries.'''

    movie_id: int
    status: Optional[str] = "To Watch"

class WatchlistCreate(WatchlistBase):
    
    '''Schema for creating a new watchlist entry.'''

    pass

class WatchlistUpdate(BaseModel):

    '''Schema for updating the status of an existing watchlist entry.'''

    status: str

class WatchlistOut(BaseModel):

    ''' Response schema for returning watchlist entry details to the client.'''

    id: int
    user_id:int
    movie_id: int
    status: str
    created_at: datetime

    model_config={"from_attributes":True}

class WatchlistSummary(BaseModel):

    '''Schema representing an aggregated summary of a user's watchlist.'''

    total_movies: int
    to_watch: int
    watched: int

    model_config={"from_attributes":True}
