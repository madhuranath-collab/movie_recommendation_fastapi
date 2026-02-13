'''This module defines the authentication and user management API endpoints
for the FastAPI application. It provides routes for user registration,
login, logout, authentication checks, and administrative user management
operations.'''

from fastapi import APIRouter, Depends, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime,timezone
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserLogin
from app.services.user import UserService
from app.utils.decorators import admin_required,login_required
from app.core.logger import *
from app.db.session import get_db
from app.models.user import Movies

router = APIRouter(prefix="/auth")
security = HTTPBearer()


# ----------------- Register -----------------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    '''Register a new user in the system.'''
    service = UserService(db)
    created_user = service.create_user(user.username, user.email, user.role, user.password)
    logger.info(
        {
        "event": "User Registered",
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )
    return created_user

# ------------------------- Login ---------------------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    '''Authenticate a user and generate a JWT access token.'''
    service = UserService(db)
    logger.info(
        {
            "event": "User Logged In",
            "email": user.email,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )
    return service.login_service(user.email, user.password)


#-------------------authentication(for me)----------------
@router.get("/me",dependencies=[Depends(security)])
@login_required
async def me(request: Request,db: Session = Depends(get_db)):
    '''Retrieve details of the currently authenticated user.'''
    user=request.state.user
    if not user:
        logger.warning(
            {
                "event": "User Retrieval Failed",
                "reason": "Authenticated user not found in request state",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        )
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(
        {
            "event": "User Profile Retrieved",
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )

    return [
        {
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "role":user.role,
            "status":user.status,
            "created_at":user.created_at
        }
    ]


#-------------------authentication(only for admins)----------------
@router.get("/admins",summary="get all users (admin only)",dependencies=[Depends(security)])
@admin_required
async def get_all_users(request: Request,db: Session = Depends(get_db)):
    '''Retrieve a list of all registered users. Accessible only by admin users.'''
    service=UserService(db)
    users=service.list_users()
    logger.info(
        {
            "event": "Admin Access - User List Retrieved",
            "admin_user": getattr(request.state, "user", None),
            "total_users": len(users),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )
    return [
        {"id":u.id,
            "username":u.username,
            "email":u.email,
            "role":u.role,
            "status":u.status,
            "created_at":u.created_at}
        for u in users
    ]


#------------------------update user-------------------

@router.put("/users/{user_id}", dependencies=[Depends(security)])
@admin_required
async def update_users(user_id: int, request: Request, user: UserCreate, db: Session = Depends(get_db)):
    '''Update user details (admin only).'''
    service = UserService(db)
    return service.update_user(user_id, user)

#-----------------delete user--------------------------

@router.delete("/{user_id}",summary="access for admin only",dependencies=[Depends(security)])
@admin_required
async def delete_users(user_id : int, request:Request, db: Session = Depends(get_db)):
    '''Delete a user by ID (admin only).'''
    service=UserService(db)
    deleted=service.delete_user_service(user_id)
    if not deleted:
        logger.warning(
            {
                "event": "User Deletion Failed",
                "admin_user": getattr(request.state, "user", None),
                "user_id": user_id,
                "reason": "User not found",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        )
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(
        {
            "event": "User Deleted Successfully",
            "admin_user": getattr(request.state, "user", None),
            "deleted_user": deleted.username,
            "deleted_user_id": deleted.id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )
    return {"message":f"user '{deleted.username}' deleted successfully"}
     

#-------------------logout--------------------------


@router.post("/logout", dependencies=[Depends(security)])
@login_required
async def logout(request: Request,credentials: HTTPAuthorizationCredentials = Depends(security),db: Session = Depends(get_db)):
    '''Logout the currently authenticated user by invalidating their JWT token.'''
    token = credentials.credentials
    #credentials.schema will be bearer and creadentials.credentials will be the token if authorization header is present 
    service = UserService(db)
    user_info = getattr(request.state, "user", None)
    return service.logout_service(token, user_info)

