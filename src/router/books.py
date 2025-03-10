from typing import List
from fastapi import (
    HTTPException, 
    Depends, 
    status, 
    APIRouter
)
from sqlalchemy.orm import Session
from datetime import datetime

from src.db import models, schemas
from src.db.database import get_db

router = APIRouter(
    prefix="/books",
    tags=["books"]
)

@router.get("/list", response_model=List[schemas.BookSimple])
def list_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books

@router.get('/list_borrowed', response_model=List[schemas.BookBorrowed])
def list_borrowed(db: Session = Depends(get_db)):
    borrowed_books = db.query(models.Book).filter(models.Book.borrowed_by != None).all()
    return borrowed_books

@router.get('/list_available', response_model=List[schemas.BookSimple])
def list_available(db: Session = Depends(get_db)):
    available_books = db.query(models.Book).filter(models.Book.borrowed_by == None).all()
    return available_books

@router.get(
    "/{book_id}", 
    response_model=schemas.BookDetailed
)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.borrowed = book.borrowed_by is not None
    return book

@router.post(
    "/add", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schemas.BookSimple
)
def add_book(book: schemas.BookSimple, db: Session = Depends(get_db)):
    if len(str(book.id)) != 6:
        raise HTTPException(status_code=400, detail="Book id must be six digits long")
    
    existing_book = db.query(models.Book).filter(models.Book.id == book.id).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this id already exists")
    
    new_book = models.Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

@router.post("/delete", response_model=bool)
def delete_book(request: schemas.RequestWithId, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == request.id)
    if not book.first():
        raise HTTPException(status_code=404, detail="Book not found")
    book.delete()
    db.commit()
    return True

@router.post("/borrow", response_model=schemas.BookBorrowed)
def borrow_book(request: schemas.BorrowRequest, db: Session = Depends(get_db)):
    if len(str(request.client)) != 6:
        raise HTTPException(status_code=400, detail="Client codes must be six digits long")
    
    book = db.query(models.Book).filter(models.Book.id == request.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.borrowed_by is not None:
        raise HTTPException(status_code=400, detail="Book already borrowed")
    
    book.borrowed_by = request.client
    book.borrowed_at = request.time if request.time is not None else datetime.now()
    db.commit()
    db.refresh(book)
    return book

@router.post("/return", response_model=schemas.BookSimple)
def return_book(request: schemas.RequestWithId, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == request.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.borrowed_by is None:
        raise HTTPException(status_code=400, detail="Book is not borrowed")
    
    book.borrowed_by = None
    book.borrowed_at = None
    db.commit()
    db.refresh(book)
    return book

@router.post("/clear")
def clear_database(db: Session = Depends(get_db)):
    db.query(models.Book).delete()
    db.commit()