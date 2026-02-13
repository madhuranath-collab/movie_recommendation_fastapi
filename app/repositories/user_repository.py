'''The repository handles all CRUD(Create, Read, Update, Delete) 
operations and returns data models or schemas to user services.'''

from sqlalchemy.orm import Session
from app.models.user import User,UserLogins

class UserRepository:

    ''' Repository class for performing CRUD operations on User,Userlogins entities'''

    def __init__(self, db: Session):
        self.db = db

    def get_login_by_token(self, token: str):
        '''fetch login record with the help of token'''
        return self.db.query(UserLogins).filter(UserLogins.token == token).first()
    
    def save_login(self, user_login: UserLogins):
        '''save new login record in UserLogins'''
        self.db.add(user_login)
        self.db.commit()
        self.db.refresh(user_login)
        return user_login
    
    def update_login(self, login_record: UserLogins):
        '''update the login status when user loggedout'''
        self.db.commit()
        self.db.refresh(login_record)
        return login_record

    def get_by_email(self, email: str):
        '''fetch the user with a given email'''
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int):
        '''fetch the user with a user_id provided'''
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User):
        '''create a new user'''
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User):
        '''update the existing user'''
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User):
        '''delete an existing user'''
        self.db.delete(user)
        self.db.commit()
        return user

    def list(self):
        '''fetch a list of existing users'''
        return self.db.query(User).all()
