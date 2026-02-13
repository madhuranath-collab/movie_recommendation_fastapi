'''Middleware for authenticating requests using JWT-based authorization.

   This middleware intercepts all incoming HTTP requests before they reach the route handlers.
   It validates the presence and correctness of a Bearer token in the `Authorization` header,
   verifies the JWT, and attaches the authenticated user to the request state.'''

from fastapi import FastAPI,Request
from app.core.security import verify_jwt
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.session import SessionLocal
from app.models.user import User
from app.core.logger import *

class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        '''Args:
            request (Request): The incoming HTTP request.
            call_next (Callable): The next middleware or route handler in the chain.

        Returns:
            JSONResponse | Response:
                - `401 Unauthorized` if the request lacks valid authentication.
                - The original route response if authentication succeeds.'''

        EXEMPT_PATHS = (
            "/auth/register",
            "/auth/login",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/streaming"
        )

        if any(request.url.path.startswith(path) for path in EXEMPT_PATHS):
            logger.debug({
                "event": "Auth Skipped (Exempt Path)",
                "path": request.url.path,
                "method": request.method,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        request.state.user = None  # default

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning({
                "event": "Authorization Failed",
                "path": request.url.path,
                "reason": "Missing or invalid Authorization header",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
            return JSONResponse(status_code=401, content={"detail": "Invalid authorization"})

        token = auth_header.split(" ")[1]
        payload = verify_jwt(token)
        if not payload:
            logger.warning({
                "event": "Authorization Failed",
                "path": request.url.path,
                "reason": "Invalid or expired token",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == payload.get("user_id")).first()
            request.state.user = user
        finally:
            db.close()

        if not user:
            return JSONResponse(status_code=401, content={"detail": "User not found"})

        return await call_next(request)