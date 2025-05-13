from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from connection.postgres import get_db
from routing.routes import router
from models.model import FilmCreate
from repository.repo import create_film

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.templates = Jinja2Templates(directory="templates")

app.include_router(router)

@app.get("/films")
async def get_films_page(request: Request, db: Session = Depends(get_db)):
    from repository.repo import get_films
    filters = {
        "id": request.query_params.get("id", None),
        "title": request.query_params.get("title", None),
        "genre": request.query_params.get("genre", None),
        "year": request.query_params.get("year", None),  # Изменили с year_min на year
        "rating_min": request.query_params.get("rating_min", None),
        "description": request.query_params.get("description", None)
    }
    films = get_films(db, filters)
    return app.templates.TemplateResponse("index.html", {"request": request, "films": films})

@app.post("/films")
async def add_film(
    request: Request,
    title: str = Form(...),
    genre: str = Form(...),
    year: int = Form(...),
    rating: float = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    film = FilmCreate(
        title=title,
        genre=genre,
        year=year,
        rating=rating,
        description=description
    )
    create_film(db, film)
    return RedirectResponse(url="/films", status_code=303)