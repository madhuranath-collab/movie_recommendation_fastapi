from fastapi import HTTPException, status


class WatchlistBaseException(HTTPException):
    """Base class for all watchlist-related exceptions."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class MovieAlreadyInWatchlistException(WatchlistBaseException):
    def __init__(self, movie_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Movie with ID {movie_id} is already in your watchlist."
        )


class MovieNotFoundException(WatchlistBaseException):
    def __init__(self, movie_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} does not exist."
        )


class MovieNotInWatchlistException(WatchlistBaseException):
    def __init__(self, movie_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with ID {movie_id} is not in your watchlist."
        )


class WatchlistOperationFailedException(WatchlistBaseException):
    def __init__(self, operation: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform operation: {operation}"
        )
