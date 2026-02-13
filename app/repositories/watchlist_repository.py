'''This module contains the repository classes and functions responsible for
interacting with the alchemy models.'''

from sqlalchemy.orm import Session
from app.models.user import Movies
from app.models.watchlist import Watchlist  

class WatchlistRepository:
    ''' Repository class for performing CRUD operations on Watchlist,Movies entities'''

    def __init__(self, db: Session):
        self.db = db
    
    def get_movie(self,movie_id:int):
        ''' fetch movies with the help of movie_id'''
        return self.db.query(Movies).filter_by(id=movie_id).first()
    
    def get_user_watchlist_query(self, user_id: int, status: str = None, sort: str = "created_at", desc_order: bool = True):
        '''fetch a query object  with the help of user_id and movie_id'''
        query = (
            self.db.query(Watchlist, Movies.title.label("movie_title"))
            .join(Movies, Watchlist.movie_id == Movies.id)
            .filter(Watchlist.user_id == user_id)
        )

        if status:
            query = query.filter(Watchlist.status == status)

      
        sort_attr = getattr(Watchlist, sort)
        query = query.order_by(sort_attr.desc() if desc_order else sort_attr)

        return query
    
    def get_by_user_and_movie(self, user_id: int, movie_id: int):
        """Fetch a specific watchlist entry for a given user and movie."""
        return (
            self.db.query(Watchlist)
            .filter_by(user_id=user_id, movie_id=movie_id)
            .first()
        )

    def get_all_by_user(self, user_id: int):
        """Fetch all watchlist entries for a given user."""
        return self.db.query(Watchlist).filter_by(user_id=user_id).all()

    def add(self, watchlist_item: Watchlist):
        """Add a new watchlist item."""
        self.db.add(watchlist_item)
        self.db.commit()
        self.db.refresh(watchlist_item)
        return watchlist_item

    def delete(self, user_id: int, movie_id: int):
        """Delete a watchlist item for a user and movie."""
        item = self.get_by_user_and_movie(user_id, movie_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False

    def update_status(self, user_id: int, movie_id: int, status: str):
        """Update the status of a watchlist item (e.g., 'To Watch' → 'Watched')."""
        item = self.get_by_user_and_movie(user_id, movie_id)
        if item:
            item.status = status
            self.db.commit()
            self.db.refresh(item)
            return item
        return None
    
    def summary(self, user_id: int):
        """Return counts of total, 'To Watch', and 'Watched' movies."""
        total = self.db.query(Watchlist).filter_by(user_id=user_id).count()
        to_watch = self.db.query(Watchlist).filter_by(user_id=user_id, status="To Watch").count()
        watched = self.db.query(Watchlist).filter_by(user_id=user_id, status="Watched").count()

        return {"total_movies": total, "to_watch": to_watch, "watched": watched}
