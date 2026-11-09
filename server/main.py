import secrets
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import uvicorn

app = FastAPI ()

# Define complex object models
class Author (BaseModel):
    name: str 
    email: Optional [str] = None

class Book (BaseModel):
    id: int
    title: str
    author: Author
    year: int
    genre: str

class AuthorUpdate (BaseModel):
    name: Optional [str] = None
    email: Optional [str] = None

class BookUpdate (BaseModel):
    title: Optional [str] = None
    author: Optional [AuthorUpdate] = None # Enables nested updates
    year: Optional [int] = None
    genre: Optional [str] = None

# In-memory dataset
books = [
    Book (
        id = 1,
        title = "The Great Gatsby",
        author = Author (name = "F. Scott Fitzgerald", email = "fscott@example.com"),
        year = 1925,
        genre = "Fiction"
    ),
    Book (
        id = 2,
        title = "1984",
        author = Author (name = "George Orwell", email = "gorwell@example.edu"),
        year = 1949,
        genre = "Dystopian"
    )
]

security = HTTPBasic ()

USERNAME = "admin"
PASSWORD = "password"

def authenticate (credentials: HTTPBasicCredentials = Depends (security)):
    valid_username = secrets.compare_digest (
        credentials.username.encode ("utf-8"),
        USERNAME.encode ("utf-8"))
    
    valid_password = secrets.compare_digest (
        credentials.password.encode ("utf-8"),
        PASSWORD.encode ("utf-8"))

    if not (valid_username and valid_password):
        raise HTTPException (
            status_code = 401, 
            detail = "Invalid credentials", 
            headers = {"WWW-Authenticate": "Basic"})

    return credentials.username

# GET all books
@app.get ("/books", response_model = List [Book], dependencies = [Depends (authenticate)])
async def get_all_books ():
    return books

# GET book count
@app.get ("/books/count", dependencies = [Depends (authenticate)])
async def count_books ():
    return {"count": len (books)}

# GET select genre
@app.get ("/books/genre/{genre}", response_model = List [Book], dependencies = [Depends (authenticate)])
async def search_by_genre (genre: str):
    genre_matches = [book for book in books if book.genre.lower () == genre.lower ()]
    return genre_matches

# GET a book by ID
@app.get ("/books/{book_id}", response_model = Book, dependencies = [Depends (authenticate)])
async def get_book (book_id: int):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException (status_code = 404, detail = "Book not found. ")

# POST a new book
@app.post ("/books", response_model = Book, dependencies = [Depends (authenticate)])
async def create_book (book: Book):
    if any (b.id == book.id for b in books):
        raise HTTPException (status_code = 400, detail = "Book ID already exists. ")
    books.append (book)
    return book

# PUT updates a book
@app.put ("/books/{book_id}", response_model = Book, dependencies = [Depends (authenticate)])
async def update_book (book_id: int, updated_book: Book):
    for i, book in enumerate (books):
        if book.id == book_id:
            books [i] = updated_book
            return updated_book
    raise HTTPException (status_code = 404, detail = "Book not found. ")

# PATCH selected fields
@app.patch ("/books/{book_id}", response_model = Book, dependencies = [Depends (authenticate)])
async def patch_book (book_id: int, updates: BookUpdate):
    for i, book in enumerate (books):
        if book.id == book_id:
            book_data = book.model_dump ()
            update_data = updates.model_dump (exclude_unset = True) # Extracts only fields explicitly provided by the client

            # Handles nested author updates
            if "author" in update_data:
                author_updates = update_data.pop ("author")

                if author_updates is None:
                    raise HTTPException (status_code = 422, detail = "Author cannot be null. ")

                book_data ["author"].update (author_updates) # Merges nested author changes, preserves existing data

            # Updates simple Book attributes
            book_data.update (update_data)

            # Updated Book validation
            try:
                updated_book = Book.model_validate (book_data)
            except ValueError:
                raise HTTPException (status_code = 422, detail = "Invalid book update. ")

            books [i] = updated_book
            return updated_book
        
    raise HTTPException (status_code = 404, detail = "Book not found. ")

# DELETE a book
@app.delete ("/books/{book_id}", dependencies = [Depends (authenticate)])
async def delete_book (book_id: int):
    for i, book in enumerate (books):
        if book.id == book_id:
            books.pop (i)
            return {"message": "Book deleted. "}
    raise HTTPException (status_code = 404, detail = "Book not found. ")

if __name__ == '__main__':
    uvicorn.run (app, host = "0.0.0.0", port = 8000)