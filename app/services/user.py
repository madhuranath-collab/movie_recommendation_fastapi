'''The repository handles all CRUD(Create, Read, Update, Delete) 
operations and returns data models or schemas to route handlers.'''

from app.models.user import User,UserLogins

from app.core.security import hash_password, is_strong_password
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.core.logger import *
from datetime import datetime,timezone,timedelta
from app.core.security import create_jwt
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
class UserService:

    ''' Service layer handling all user-related operations such as
        creation, update, authentication (login/logout), and deletion.'''
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def create_user(self, username: str, email: str, role: str, password: str):

        ''' Service layer that creates a new user.'''

        if self.repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already exists")

        if not is_strong_password(password):
            raise HTTPException(
                status_code=400,
                detail="Password too weak. Must be 8+ chars, include uppercase, lowercase, number & special char."
            )

        new_user = User(
            username=username,
            email=email,
            role=role,
            password=hash_password(password)
        )
        return self.repo.create(new_user)
    
    def update_user(self, user_id: int, user_data):
        
        '''Update user information including email, password, username, and role.'''

        user_exists = self.repo.get_by_id(user_id)
        if not user_exists:
            logger.warning({
                "event": "User Update Failed",
                "user_id": user_id,
                "reason": "User does not exist",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            raise HTTPException(status_code=400, detail="User does not exist")

        # Check duplicate email
        if user_data.email:
            email_check = self.repo.db.query(User).filter(
                User.email == user_data.email, User.id != user_id
            ).first()
            if email_check:
                logger.warning({
                    "event": "User Update Failed",
                    "user_id": user_id,
                    "email": user_data.email,
                    "reason": "Duplicate email detected",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                })
                raise HTTPException(status_code=400, detail="User already exists with this email")
            user_exists.email = user_data.email

        # Validate and hash password
        if user_data.password:
            if not is_strong_password(user_data.password):
                logger.warning({
                    "event": "User Update Rejected",
                    "user_id": user_id,
                    "reason": "Weak password",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                })
                raise HTTPException(status_code=400, detail="Password is too weak")
            user_exists.password = hash_password(user_data.password)

        # Update other fields
        if user_data.username:
            user_exists.username = user_data.username
        if user_data.role:
            user_exists.role = user_data.role

        updated_user = self.repo.update(user_exists)

        logger.info({
            "event": "User Updated Successfully",
            "user_id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "role": updated_user.role,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        })

        return {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "role": updated_user.role,
            "created_at": updated_user.created_at
        }
    
    def login_service(self, email: str, password: str):

        '''Authenticate user and generate a JWT access token upon successful login.'''

        user = self.repo.get_by_email(email)
        if not user or not user.verify_password(password):
            logger.warning({
                "event": "Login Failed",
                "email": email,
                "reason": "Invalid credentials",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        token = create_jwt({"user_id": user.id, "role": user.role})
        expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Save login record
        login_record = UserLogins(
            user_id=user.id,
            token=token,
            expiration_date=expiry
        )
        self.repo.save_login(login_record)

        logger.info({
            "event": "User Logged In",
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "token_expiry": expiry.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    
    def logout_service(self, token: str, user_info: dict | None = None):

        '''Invalidate a user session by marking the login record as 'suspended'.'''

        login_record = self.repo.get_login_by_token(token)
        if not login_record:
            logger.warning({
                "event": "Logout Failed",
                "user": user_info,
                "reason": "Login record not found or invalid token",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            raise HTTPException(status_code=400, detail="Bad request: login record not found")

        login_record.status = "suspended"
        updated_record = self.repo.update_login(login_record)

        logger.info({
            "event": "User Logged Out Successfully",
            "user": user_info,
            "status": updated_record.status,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        })

        return {"message": "Logged out successfully"}

    def delete_user_service(self,user_id:int):

        '''Permanently delete a user record from the database.'''

        user=self.repo.get_by_id(user_id)
        deleted_user=self.repo.delete(user)
        if not user:
            logger.info({
                "event": "User Deleted Successfully",
                "deleted_user_id": deleted_user.id,
                "deleted_username": deleted_user.username,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            raise HTTPException(status_code=404, detail="user not found")
        return deleted_user
    
    def list_users(self):
        
        '''Retrieve a list of all registered users.'''

        users = self.repo.list()
        logger.info(
            {
                "event": "User List Retrieved",
                "total_users": len(users),
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        )
        return users
    

