import logging
from sqlalchemy.orm import Session
from models.models import Category, Product, Customer, Supplier, InventoryItem, Purchase, PurchaseItem, Restock, \
    RestockItem
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from datetime import datetime

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PostgresRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_id: int, name: str, category_id: int, price: float, unit: str):
        try:
            product = Product(product_id=product_id, name=name, category_id=category_id, price=price, unit=unit)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            logging.info(f"Created product: {product_id}")
            return product
        except SQLAlchemyError as e:
            logging.error(f"Error creating product: {str(e)}")
            self.db.rollback()
            raise

    def create_purchase(self, customer_id: int, purchase_date: str, total_amount: float):
        try:
            purchase = Purchase(
                customer_id=customer_id,
                purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d %H:%M:%S'),
                total_amount=total_amount
            )
            self.db.add(purchase)
            self.db.commit()
            self.db.refresh(purchase)
            logging.info(f"Created purchase for customer: {customer_id}")  # Исправлено: self.customer_id -> customer_id
            return purchase
        except SQLAlchemyError as e:
            logging.error(f"Error creating purchase: {str(e)}")
            self.db.rollback()
            raise

    def get_stock_report(self, start_date: str = None, end_date: str = None, category_id: int = None, page: int = 1,
                         page_size: int = 10):
        try:
            query = self.db.query(
                Product.product_id,
                Product.name.label('product_name'),
                Category.name.label('category_name'),
                InventoryItem.quantity,
                PurchaseItem.quantity.label('quantity_sold'),
                PurchaseItem.total_price.label('revenue'),
                Purchase.purchase_date
            ).join(
                InventoryItem, Product.product_id == InventoryItem.product_id
            ).join(
                Category, Product.category_id == Category.category_id
            ).join(
                PurchaseItem, Product.product_id == PurchaseItem.product_id
            ).join(
                Purchase, PurchaseItem.purchase_id == Purchase.purchase_id
            )

            if start_date:
                query = query.filter(Purchase.purchase_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                query = query.filter(Purchase.purchase_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            if category_id:
                query = query.filter(Product.category_id == category_id)

            total = query.count()
            results = query.offset((page - 1) * page_size).limit(page_size).all()
            df = pd.DataFrame(
                results,
                columns=['product_id', 'product_name', 'category_name', 'quantity', 'quantity_sold', 'revenue',
                         'purchase_date']
            )
            df.to_excel('stock_report.xlsx', index=False, encoding='utf-8')
            logging.info(f"Generated paginated stock report: page={page}, size={page_size}")
            return {"data": df.to_dict(orient="records"), "total": total, "page": page, "page_size": page_size}

        except Exception as e:
            logging.error(f"Error generating stock report: {str(e)}")
            raise

    def load_excel_data(self, file_path: str):
        try:
            xl = pd.ExcelFile(file_path)

            # Загрузка categories
            if 'categories' in xl.sheet_names:
                categories_df = pd.read_excel(file_path, sheet_name='categories')
                for _, row in categories_df.iterrows():
                    category = Category(category_id=int(row['category_id']), name=str(row['name']))
                    self.db.merge(category)

            # Загрузка products
            if 'products' in xl.sheet_names:
                products_df = pd.read_excel(file_path, sheet_name='products')
                for _, row in products_df.iterrows():
                    product = Product(
                        product_id=int(row['product_id']),
                        name=str(row['name']),
                        category_id=int(row['category_id']),
                        price=float(row['price']),
                        unit=str(row['unit'])
                    )
                    self.db.merge(product)

            # Загрузка customers
            if 'customers' in xl.sheet_names:
                customers_df = pd.read_excel(file_path, sheet_name='customers')
                for _, row in customers_df.iterrows():
                    customer = Customer(
                        customer_id=int(row['customer_id']),
                        full_name=str(row['full_name']),
                        phone=str(row['phone']) if pd.notna(row['phone']) else None,
                        email=str(row['email']) if pd.notna(row['email']) else None,
                        registered_at=pd.to_datetime(row['registered_at'])
                    )
                    self.db.merge(customer)

            # Загрузка suppliers
            if 'suppliers' in xl.sheet_names:
                suppliers_df = pd.read_excel(file_path, sheet_name='suppliers')
                for _, row in suppliers_df.iterrows():
                    supplier = Supplier(
                        supplier_id=int(row['supplier_id']),
                        full_name=str(row['name']),
                        contact_email=str(row['contact_email']) if pd.notna(row['contact_email']) else None,
                        phone=str(row['phone']) if pd.notna(row['phone']) else None
                    )
                    self.db.merge(supplier)

            # Загрузка inventory
            if 'inventory' in xl.sheet_names:
                inventory_df = pd.read_excel(file_path, sheet_name='inventory')
                for _, row in inventory_df.iterrows():
                    inventory = InventoryItem(
                        inventory_id=int(row['inventory_id']),
                        product_id=int(row['product_id']),
                        quantity=int(row['quantity']),
                        last_updated=pd.to_datetime(row['last_updated'])
                    )
                    self.db.merge(inventory)

            # Загрузка purchases
            if 'purchases' in xl.sheet_names:
                purchases_df = pd.read_excel(file_path, sheet_name='purchases')
                for _, row in purchases_df.iterrows():
                    purchase = Purchase(
                        purchase_id=int(row['purchase_id']),
                        customer_id=int(row['customer_id']),
                        purchase_date=pd.to_datetime(row['purchase_date']),
                        total_amount=float(row['total_amount'])
                    )
                    self.db.merge(purchase)

            # Загрузка purchase_items
            if 'purchase_items' in xl.sheet_names:
                purchase_items_df = pd.read_excel(file_path, sheet_name='purchase_items')
                for _, row in purchase_items_df.iterrows():
                    purchase_item = PurchaseItem(
                        purchase_item_id=int(row['purchase_item_id']),
                        purchase_id=int(row['purchase_id']),
                        product_id=int(row['product_id']),
                        quantity=int(row['quantity']),
                        unit_price=float(row['unit_price']),
                        total_price=float(row['total_price'])
                    )
                    self.db.merge(purchase_item)

            # Загрузка restocks
            if 'restocks' in xl.sheet_names:
                restocks_df = pd.read_excel(file_path, sheet_name='restocks')
                for _, row in restocks_df.iterrows():
                    restock = Restock(
                        restock_id=int(row['restock_id']),
                        supplier_id=int(row['supplier_id']),
                        restock_date=pd.to_datetime(row['restock_date'])
                    )
                    self.db.merge(restock)

            # Загрузка restock_items
            if 'restock_items' in xl.sheet_names:
                restock_items_df = pd.read_excel(file_path, sheet_name='restock_items')
                for _, row in restock_items_df.iterrows():
                    restock_item = RestockItem(
                        restock_item_id=int(row['restock_item_id']),
                        restock_id=int(row['restock_id']),
                        product_id=int(row['product_id']),
                        quantity=int(row['quantity']),
                        unit_cost=float(row['unit_cost'])
                    )
                    self.db.merge(restock_item)

            self.db.commit()
            logging.info(f"Loaded data from {file_path} into database")
            return {"message": "Excel data loaded successfully"}
        except Exception as e:
            logging.error(f"Error loading Excel data: {str(e)}")
            self.db.rollback()
            raise