'''These decorators work in conjunction with the authentication middleware,
which attaches the authenticated `user` object to `request.state.user`.
They ensure that only authorized users can access certain endpoints.'''

from fastapi import Request, HTTPException
from functools import wraps


def login_required(func):
    """Ensure the user is authenticated"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or args[0]
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await func(*args, **kwargs)
    return wrapper

def admin_required(func):
    """Ensure the user is an admin"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request :Request= kwargs.get("request")
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if getattr(user, "role", None) != "admin":
            raise HTTPException(status_code=403, detail="Admins only can access")
       
        return await func(*args,**kwargs)
    return wrapper