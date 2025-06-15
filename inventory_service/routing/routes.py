from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from connection.postgres import get_db
from repository.postgres_repository import PostgresRepository
import requests
import logging

router = APIRouter()
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@router.post("/stock/create")
async def create_stock(product_id: str, product_name: str, quantity: int, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        stock = repo.create_stock(product_id, product_name, quantity)
        return {"message": "Stock created", "data": stock}
    except Exception as e:
        logging.error(f"Error in create_stock: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sales/create")
async def create_sale(product_id: str, quantity_sold: int, revenue: float, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        sale = repo.create_sale(product_id, quantity_sold, revenue)
        return {"message": "Sale created", "data": sale}
    except Exception as e:
        logging.error(f"Error in create_sale: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/report")
async def get_stock_report(start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    try:
        repo = PostgresRepository(db)
        report = repo.get_stock_report(start_date, end_date)
        return {"message": "Report generated", "data": report}
    except Exception as e:
        logging.error(f"Error in get_stock_report: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/external-api")
async def fetch_external_stock():
    try:
        response = requests.get("https://api.example.com/stock", timeout=5)
        response.raise_for_status()
        data = response.json()
        logging.info("Fetched data from external API")
        return {"message": "External stock data fetched", "data": data}
    except requests.RequestException as e:
        logging.error(f"Error fetching external API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))