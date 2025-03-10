from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    TIMESTAMP
)
import uuid

from src.db.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    borrowed_by = Column(Integer, nullable=True)
    borrowed_at = Column(TIMESTAMP(timezone=True), nullable=True)