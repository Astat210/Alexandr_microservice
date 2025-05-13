from sqlalchemy import Column, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    genre = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

class FilmCreate(BaseModel):
    title: str
    genre: str
    year: int
    rating: float
    description: str | None = None

class FilmUpdate(BaseModel):
    title: str | None = None
    genre: str | None = None
    year: int | None = None
    rating: float | None = None
    description: str | None = None

class FilmFilter(BaseModel):
    id: int | None = None
    title: str | None = None
    genre: str | None = None
    year: int | None = None
    rating_min: float | None = None
    description: str | None = None