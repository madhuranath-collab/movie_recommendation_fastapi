from app.models.watchlist import Watchlist
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.repositories.watchlist_repository import WatchlistRepository
from app.exceptions.custom_exceptions import (
    MovieAlreadyInWatchlistException,
    MovieNotFoundException,
    MovieNotInWatchlistException
)

class WatchlistService:

    ''' Service layer handling all watchlist-related operations such as
      fetching creation, update, and deletion.'''

    def __init__(self, db: Session):
        self.db = db
        self.repo = WatchlistRepository(db)


    def add_to_watchlist(self, user_id: int, movie_ids: List[int], status_value: str = "To Watch"):
        added_items = []
        for movie_id in movie_ids:
            if self.repo.get_by_user_and_movie(user_id, movie_id):
                raise MovieAlreadyInWatchlistException(movie_id)

            movie = self.repo.get_movie(movie_id)
            if not movie:
                raise MovieNotFoundException(movie_id)

            new_entry = Watchlist(user_id=user_id, movie_id=movie_id, status=status_value)
            added_items.append(self.repo.add(new_entry))
        return added_items

    def update_watchlist_status(self, user_id: int, movie_id: int, status_value: str):
        entry = self.repo.update_status(user_id, movie_id, status_value)
        if not entry:
            raise MovieNotInWatchlistException(movie_id)
        return entry

    def delete_from_watchlist(self, user_id: int, movie_id: int):
        success = self.repo.delete(user_id, movie_id)
        if not success:
            raise MovieNotInWatchlistException(movie_id)
        return {"message": f"Movie with id {movie_id} deleted successfully"}

    def get_user_watchlist(self,user_id: int, status: str = None, sort: str = "created_at", desc: bool = True, page: int = 1, size: int = 10):
            query = self.repo.get_user_watchlist_query(user_id, status, sort, desc)

            total = query.count()
            results = query.offset((page - 1) * size).limit(size).all()

            items = [
                {
                    "id": w.id,
                    "movie_id": w.movie_id,
                    "movie_title": title,
                    "status": w.status,
                    "created_at": w.created_at,
                }
                for w, title in results
            ]

            return {"total": total, "items": items}

    # def delete_from_watchlist(self,user_id: int, movie_id: int):
    #     """Delete a specific movie from a user's watchlist."""
    #     success = self.repo.delete(user_id, movie_id)
    #     if not success:
    #         raise HTTPException(status_code=404, detail="Movie not in watchlist")
    #     return {f"movie with id {movie_id} was deleted successfully"}

    def delete_bulk_watchlist(self,user_id: int, movie_ids: List[int]):
        """Delete multiple movies from a user's watchlist."""
        self.db.query(Watchlist).filter(
            Watchlist.user_id == user_id,
            Watchlist.movie_id.in_(movie_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return {f"movies with id's {movie_ids} were deleted successfully"}


    def check_watchlist(self,user_id: int, movie_id: int):
        """Check if a movie exists in a user's watchlist."""
        entry = self.repo.get_by_user_and_movie(user_id, movie_id)
        if not entry:
            return {"inWatchlist": False}
        return {"inWatchlist": True, "status": entry.status}


    def get_summary(self,user_id: int):
        """Get a summary of total, watched, and to-watch movies using repository."""
        return self.repo.summary(user_id)