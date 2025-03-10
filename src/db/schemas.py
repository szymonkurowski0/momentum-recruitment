from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookSimple(BaseModel):
    id: int
    title: str
    author: str
    
    class Config:
        orm_mode = True

class BookBorrowed(BookSimple):
    borrowed_by: int
    borrowed_at: datetime
    
    class Config:
        orm_mode = True

class BookDetailed(BookSimple):
    borrowed: bool
    borrowed_by: Optional[int]
    borrowed_at: Optional[datetime]
    
    class Config:
        orm_mode = True
        
class RequestWithId(BaseModel):
    id: int

class BorrowRequest(RequestWithId):
    client: int
    time: Optional[datetime]