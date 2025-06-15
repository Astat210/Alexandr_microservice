from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from connection.postgres import get_db
from repository.postgres_repository import PostgresRepository
import requests
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@router.post("/stock/create")
async def create_stock(product_id: str, product_name: str, quantity: int, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        stock = repo.create_stock(product_id, product_name, quantity)
        return {"message": "Товар добавлен", "data": stock}
    except Exception as e:
        logging.error(f"Error in create_stock: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sales/create")
async def create_sale(product_id: str, quantity_sold: int, revenue: float, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        sale = repo.create_sale(product_id, quantity_sold, revenue)
        return {"message": "Продажа добавлена", "data": sale}
    except Exception as e:
        logging.error(f"Error in create_sale: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/report", response_class=HTMLResponse)
async def get_stock_report(request: Request, start_date: str = None, end_date: str = None, page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        report = repo.get_stock_report(start_date, end_date, page, page_size)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "data": report["data"],
            "total": report["total"],
            "page": report["page"],
            "page_size": report["page_size"],
            "start_date": start_date or "",
            "end_date": end_date or ""
        })
    except Exception as e:
        logging.error(f"Error in get_stock_report: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        repo = PostgresRepository(db)
        result = repo.load_excel_data(file_path)
        os.remove(file_path)
        return result
    except Exception as e:
        logging.error(f"Error uploading Excel: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/external-api")
async def fetch_external_stock():
    try:
        response = requests.get("https://api.example.com/stock", timeout=5)
        response.raise_for_status()
        data = response.json()
        logging.info("Fetched data from external API")
        return {"message": "Данные из внешнего API получены", "data": data}
    except requests.RequestException as e:
        logging.error(f"Error fetching external API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))