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

    def get_stock_report(self, start_date: str = None, end_date: str = None, page: int = 1, page_size: int = 10):
        try:
            query = self.db.query(Stock.product_id, Stock.product_name, Stock.quantity,
                                 Sales.quantity_sold, Sales.revenue, Sales.sale_date)\
                .join(Sales, Stock.product_id == Sales.product_id)
            if start_date:
                query = query.filter(Sales.sale_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(Sales.sale_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            total = query.count()
            results = query.offset((page - 1) * page_size).limit(page_size).all()
            df = pd.DataFrame(results, columns=['product_id', 'product_name', 'quantity', 'quantity_sold', 'revenue', 'sale_date'])
            df.to_excel('stock_report.xlsx', index=False, encoding='utf-8')
            logging.info(f"Generated paginated stock report, page {page}, size {page_size}")
            return {"data": df.to_dict(orient='records'), "total": total, "page": page, "page_size": page_size}
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

    def load_excel_data(self, file_path: str):
        try:
            # Чтение Excel-файла
            stock_df = pd.read_excel(file_path, sheet_name='Stock')
            sales_df = pd.read_excel(file_path, sheet_name='Sales')

            # Загрузка данных в таблицу stock
            for _, row in stock_df.iterrows():
                stock = Stock(
                    product_id=str(row['product_id']),
                    product_name=str(row['product_name']),
                    quantity=int(row['quantity']),
                    last_updated=pd.to_datetime(row['last_updated'])
                )
                self.db.add(stock)

            # Загрузка данных в таблицу sales
            for _, row in sales_df.iterrows():
                sale = Sales(
                    product_id=str(row['product_id']),
                    quantity_sold=int(row['quantity_sold']),
                    sale_date=pd.to_datetime(row['sale_date']),
                    revenue=float(row['revenue'])
                )
                self.db.add(sale)

            self.db.commit()
            logging.info(f"Loaded data from {file_path} into database")
            return {"message": "Excel data loaded successfully"}
        except Exception as e:
            logging.error(f"Error loading Excel data: {str(e)}")
            self.db.rollback()
            raise