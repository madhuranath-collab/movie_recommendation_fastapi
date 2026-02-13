'''This module defines the API routes for managing a user's movie watchlist in the FastAPI application.

It provides endpoints for creating, updating, retrieving, and deleting watchlist entries.
Each operation is authenticated using JWT tokens and protected by the `login_required`
decorator. The routes rely on the `WatchlistService` for all underlying database and
business logic operations.'''

from fastapi import APIRouter, Depends,Request,Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate, WatchlistOut
from app.services.watchlist import WatchlistService
from app.utils.decorators import login_required 
from app.core import logger  

router = APIRouter(prefix="/watchlist")
security=HTTPBearer()

#-----------------------------add new movies to watchlist------------------------

@router.post("/{movie_id}", dependencies=[Depends(security)], response_model=List[WatchlistOut])
@login_required
async def add_movie_to_watchlist(movie_id: int, payload: WatchlistCreate, request:Request, db: Session = Depends(get_db)):
    '''Add a new movie to the authenticated user's watchlist.'''
    movie_ids = [movie_id]
    user = request.state.user
    service=WatchlistService(db)  
    added = service.add_to_watchlist(user.id, movie_ids, payload.status)
    return added

#------------------------------update user watchlist-----------------------------

@router.put("/{movie_id}", dependencies=[Depends(security)], response_model=WatchlistOut)
@login_required
async def update_watchlist(movie_id: int, payload: WatchlistUpdate, request:Request, db: Session = Depends(get_db)):
    '''Update the status of a specific movie in the user's watchlist.'''
    user = request.state.user
    service=WatchlistService(db)   
    return service.update_watchlist_status(user.id, movie_id, payload.status)


#-----------------------------get user watchlist---------------------------------

@router.get("/", dependencies=[Depends(security)])
@login_required
async def get_all_watchlist(
    request:Request,
    db: Session = Depends(get_db),
    page: int = Query(1),
    size: int = Query(10),
    sort: str = Query("created_at"),
    desc: bool = Query(True),
    status_filter: Optional[str] = Query(None)
):
    '''Retrieve all movies in the user's watchlist with optional pagination and filters.'''
    user = request.state.user
    service=WatchlistService(db)   
    result = service.get_user_watchlist(user.id, status_filter, sort, desc, page, size)
    return result["items"]


#-----------------------------delete user watchlist---------------------------------

@router.delete("/{movie_id}", dependencies=[Depends(security)])
@login_required
async def remove_from_watchlist(movie_id: int, request:Request,db: Session = Depends(get_db)):
    '''Remove a single movie from the authenticated user's watchlist.'''
    user=request.state.user
    service=WatchlistService(db) 
    return service.delete_from_watchlist(user.id, movie_id)

#-----------------------------delete bulk watchlist--------------------------------

@router.delete("/", dependencies=[Depends(security)])
@login_required
async def remove_bulk_from_watchlist(movie_ids: List[int],request:Request, db: Session = Depends(get_db)):
    '''Remove multiple movies from the authenticated user's watchlist in one operation.'''
    user=request.state.user
    service=WatchlistService(db) 
    return service.delete_bulk_watchlist(user.id, movie_ids)

#-----------------------------check whether movie is in watchlist-------------------

@router.get("/{movie_id}",dependencies=[Depends(security)])
@login_required
async def check_movie_in_watchlist(movie_id: int, request:Request, db: Session = Depends(get_db)):
    '''Check whether a specific movie is already present in the user's watchlist.'''
    user=request.state.user
    service=WatchlistService(db) 
    return service.check_watchlist(user.id, movie_id)


#-----------------------------get summary of watchlist----------------------------

@router.get("/summary/all",dependencies=[Depends(security)])
@login_required
async def get_watchlist_summary(request:Request,db: Session = Depends(get_db)):
    '''Retrieve a summary of the user's watchlist, including counts of total movies,
    watched movies, and movies yet to watch'''
    user=request.state.user
    service=WatchlistService(db) 
    return service.get_summary(user.id)

