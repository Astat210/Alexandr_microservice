from sqlalchemy.orm import Session
from models.models import Stock, Sales
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostgresRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_stock(self, product_id: str, product_name: str, quantity: int):
        try:
            stock = Stock(product_id=product_id, product_name=product_name, quantity=quantity)
            self.db.add(stock)
            self.db.commit()
            self.db.refresh(stock)
            logging.info(f"Created stock item: {product_id}")
            return stock
        except SQLAlchemyError as e:
            logging.error(f"Error creating stock: {str(e)}")
            self.db.rollback()
            raise

    def create_sale(self, product_id: str, quantity_sold: int, revenue: float):
        try:
            sale = Sales(product_id=product_id, quantity_sold=quantity_sold, revenue=revenue)
            self.db.add(sale)
            self.db.commit()
            self.db.refresh(sale)
            logging.info(f"Created sale for product: {product_id}")
            return sale
        except SQLAlchemyError as e:
            logging.error(f"Error creating sale: {str(e)}")
            self.db.rollback()
            raise

    def get_stock_report(self, start_date: str = None, end_date: str = None):
        try:
            query = self.db.query(Stock.product_id, Stock.product_name, Stock.quantity,
                                 Sales.quantity_sold, Sales.revenue, Sales.sale_date)\
                .join(Sales, Stock.product_id == Sales.product_id)
            if start_date:
                query = query.filter(Sales.sale_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(Sales.sale_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            results = query.all()
            df = pd.DataFrame(results, columns=['product_id', 'product_name', 'quantity', 'quantity_sold', 'revenue', 'sale_date'])
            df.to_excel('stock_report.xlsx', index=False, encoding='utf-8')
            logging.info("Generated stock report")
            return df.to_dict(orient='records')
        except Exception as e:
            logging.error(f"Error generating stock report: {str(e)}")
            raise

    def get_stock_by_id(self, product_id: str):
        try:
            stock = self.db.query(Stock).filter(Stock.product_id == product_id).first()
            if not stock:
                logging.warning(f"Stock not found: {product_id}")
                return None
            return stock
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving stock: {str(e)}")
            raise