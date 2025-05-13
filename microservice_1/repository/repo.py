from sqlalchemy.orm import Session
from models.model import Film


def create_film(db: Session, film: "FilmCreate"):
    db_film = Film(**film.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

def get_film(db: Session, film_id: int):
    return db.query(Film).filter(Film.id == film_id).first()

def update_film(db: Session, film_id: int, film: "FilmUpdate"):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        return None
    for key, value in film.dict(exclude_none=True).items():
        setattr(db_film, key, value)
    db.commit()
    db.refresh(db_film)
    return db_film

def delete_film(db: Session, film_id: int):
    db_film = db.query(Film).filter(Film.id == film_id).first()
    if db_film is None:
        return None
    db.delete(db_film)
    db.commit()
    return db_film

def get_films(db: Session, filters: dict):
    query = db.query(Film)
    if filters.get("id"):
        query = query.filter(Film.id == filters["id"])
    if filters.get("title"):
        query = query.filter(Film.title.ilike(f"%{filters['title']}%"))
    if filters.get("genre"):
        query = query.filter(Film.genre.ilike(f"%{filters['genre']}%"))
    if filters.get("year"):
        query = query.filter(Film.year == filters["year"])
    if filters.get("rating_min"):
        query = query.filter(Film.rating >= filters["rating_min"])
    if filters.get("description"):
        query = query.filter(Film.description.ilike(f"%{filters['description']}%"))
    return query.all()