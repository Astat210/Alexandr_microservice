from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from models.model import Film, FilmCreate, FilmUpdate, FilmFilter
from repository.repo import create_film, get_film, update_film, delete_film, get_films
from connection.postgres import get_db

router = APIRouter()

@router.post("/films/api", response_model=FilmCreate)
def create_new_film(film: FilmCreate, db: Session = Depends(get_db)):
    return create_film(db, film)

@router.get("/films/list")
def read_films(filters: FilmFilter = Depends(), db: Session = Depends(get_db)):
    return get_films(db, filters.dict(exclude_none=True))

@router.get("/films/{film_id}")
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = get_film(db, film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return film

@router.put("/films/{film_id}")
def update_existing_film(film_id: int, film: FilmUpdate, db: Session = Depends(get_db)):
    updated_film = update_film(db, film_id, film)
    if updated_film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return updated_film

@router.delete("/films/{film_id}")
def delete_existing_film(film_id: int, db: Session = Depends(get_db)):
    film = delete_film(db, film_id)
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return {"message": "Film deleted"}