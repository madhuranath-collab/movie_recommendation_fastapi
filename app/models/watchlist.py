from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Float, Boolean, Enum, TIMESTAMP, Date,
    ForeignKey, text
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Watchlist(Base):
    __tablename__ = "Watchlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(BigInteger, ForeignKey("Movies.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    status = Column(Enum('To Watch', 'Watched'), server_default='To Watch')

    user = relationship("User", back_populates="watchlist", passive_deletes=True)
    movie = relationship("Movies", back_populates="watchlist", passive_deletes=True)