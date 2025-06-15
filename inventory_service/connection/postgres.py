import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5433/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category_id INTEGER REFERENCES categories(category_id),
                    price DECIMAL(10, 2) NOT NULL,
                    unit VARCHAR(10) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    registered_at TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    contact_email VARCHAR(100),
                    phone VARCHAR(20)
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS inventory (
                    inventory_id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS purchases (
                    purchase_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id),
                    purchase_date TIMESTAMP NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS purchase_items (
                    purchase_item_id SERIAL PRIMARY KEY,
                    purchase_id INTEGER REFERENCES purchases(purchase_id),
                    product_id INTEGER REFERENCES products(product_id),
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS restocks (
                    restock_id SERIAL PRIMARY KEY,
                    supplier_id INTEGER REFERENCES suppliers(supplier_id),
                    restock_date TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS restock_items (
                    restock_item_id SERIAL PRIMARY KEY,
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