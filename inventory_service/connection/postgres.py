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
                CREATE TABLE IF NOT EXISTS stock (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(50) UNIQUE NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    quantity INTEGER NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                );
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(50) NOT NULL,
                    quantity_sold INTEGER NOT NULL,
                    sale_date TIMESTAMP NOT NULL,
                    revenue DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES stock(product_id)
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