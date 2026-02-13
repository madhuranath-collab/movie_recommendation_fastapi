from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.custom_exceptions import WatchlistBaseException
from app.core.logger import logger


async def watchlist_exception_handler(request: Request, exc: WatchlistBaseException):
    """Handle all WatchlistBaseException subclasses uniformly."""
    logger.warning(f"Watchlist error: {exc.detail} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url.path),
        }
    )
