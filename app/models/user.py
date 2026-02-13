from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Float, Boolean, Enum, TIMESTAMP, Date,
    ForeignKey, text
)
from sqlalchemy.orm import relationship
from app.db.session import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ----------------- User -----------------
class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum('admin', 'user'), server_default='user')
    password = Column(String(100), nullable=False)
    status = Column(Enum('active', 'suspended'), server_default='active')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'),
                        onupdate=text('CURRENT_TIMESTAMP'))

    movies_created = relationship(
        "Movies", back_populates="creator",
        cascade="all, delete-orphan", passive_deletes=True
    )
    reviews = relationship(
        "Reviews", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True
    )
    watchlist = relationship(
        "Watchlist", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True
    )
    activities = relationship(
        "UserActivityLogs", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True
    )
    recommendations = relationship(
        "Recommendation", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True
    )
    logins = relationship(
        "UserLogins", back_populates="user",
        cascade="all, delete-orphan", passive_deletes=True
    )

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

# ----------------- UserLogins -----------------
class UserLogins(Base):
    __tablename__ = "User_Logins"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    status = Column(Enum('active', 'suspended'), server_default='active')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    expiration_date = Column(TIMESTAMP)

    user = relationship("User", back_populates="logins", passive_deletes=True)

# ----------------- Movies -----------------
class Movies(Base):
    __tablename__ = "Movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    language = Column(String(50))
    director = Column(String(100))
    cast = Column(Text)
    release_year = Column(Integer)
    poster_url = Column(Text)
    rating = Column(Float, default=0.0)
    approved = Column(Boolean, default=False)
    created_by = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'),
                        onupdate=text('CURRENT_TIMESTAMP'))
    platform=Column(String(100))

    creator = relationship("User", back_populates="movies_created", passive_deletes=True)
    reviews = relationship("Reviews", back_populates="movie",
                           cascade="all, delete-orphan", passive_deletes=True)
    watchlist = relationship("Watchlist", back_populates="movie",
                             cascade="all, delete-orphan", passive_deletes=True)
    availability = relationship("MovieAvailability", back_populates="movie",
                                cascade="all, delete-orphan", passive_deletes=True)
    recommendations = relationship("Recommendation", back_populates="recommended_movie",
                                   cascade="all, delete-orphan", passive_deletes=True)

# ----------------- Reviews -----------------
class Reviews(Base):
    __tablename__ = "Reviews"

    id = Column(Integer, primary_key=True)
    movie_id = Column(BigInteger, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'),
                        onupdate=text('CURRENT_TIMESTAMP'))

    movie = relationship("Movies", back_populates="reviews", passive_deletes=True)
    user = relationship("User", back_populates="reviews", passive_deletes=True)

# # ----------------- Watchlist -----------------
# class Watchlist(Base):
#     __tablename__ = "Watchlist"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
#     movie_id = Column(BigInteger, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
#     created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
#     status = Column(Enum('To Watch', 'Watched'), server_default='To Watch')

#     user = relationship("User", back_populates="watchlist", passive_deletes=True)
#     movie = relationship("Movies", back_populates="watchlist", passive_deletes=True)

# ----------------- Platforms -----------------
class Platforms(Base):
    __tablename__ = "Platforms"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    website = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    availability = relationship(
        "MovieAvailability", back_populates="platform",
        cascade="all, delete-orphan", passive_deletes=True
    )

# ----------------- Regions -----------------
class Regions(Base):
    __tablename__ = "Regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    availability = relationship(
        "MovieAvailability", back_populates="region",
        cascade="all, delete-orphan", passive_deletes=True
    )

# ----------------- Movie_Availability -----------------
class MovieAvailability(Base):
    __tablename__ = "Movie_Availability"

    id = Column(Integer, primary_key=True)
    movie_id = Column(BigInteger, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    platform_id = Column(BigInteger, ForeignKey("Platforms.id", ondelete="CASCADE"), nullable=False)
    region_id = Column(BigInteger, ForeignKey("Regions.id", ondelete="CASCADE"), nullable=False)
    availability_type = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    url = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'),
                        onupdate=text('CURRENT_TIMESTAMP'))

    movie = relationship("Movies", back_populates="availability", passive_deletes=True)
    platform = relationship("Platforms", back_populates="availability", passive_deletes=True)
    region = relationship("Regions", back_populates="availability", passive_deletes=True)

# ----------------- User_Activity_Logs -----------------
class UserActivityLogs(Base):
    __tablename__ = "User_Activity_Logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    user = relationship("User", back_populates="activities", passive_deletes=True)

# ----------------- Recommendation -----------------
class Recommendation(Base):
    __tablename__ = "Recommendation"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    recommended_movie_id = Column(BigInteger, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    user = relationship("User", back_populates="recommendations", passive_deletes=True)
    recommended_movie = relationship("Movies", back_populates="recommendations", passive_deletes=True)
