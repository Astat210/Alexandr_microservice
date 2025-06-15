import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    category_id INTEGER REFERENCES categories(category_id),
                    price DECIMAL(10, 2) NOT NULL,
                    unit TEXT NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    registered_at TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INTEGER PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    contact_email TEXT,
                    phone TEXT
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    inventory_id INTEGER PRIMARY KEY,
                    product_id INTEGER REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS purchases (
                    purchase_id INTEGER PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id),
                    purchase_date TIMESTAMP NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS purchase_items (
                    purchase_item_id INTEGER PRIMARY KEY,
                    purchase_id INTEGER REFERENCES purchases(purchase_id),
                    product_id INTEGER REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS restocks (
                    restock_id INTEGER PRIMARY KEY,
                    supplier_id INTEGER REFERENCES suppliers(supplier_id),
                    restock_date TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS restock_items (
                    restock_item_id INTEGER PRIMARY KEY,
                    restock_id INTEGER REFERENCES restocks(restock_id),
                    product_id INTEGER REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    unit_cost DECIMAL(10, 2) NOT NULL
                );
            """))
            connection.commit()
        logging.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logging.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()