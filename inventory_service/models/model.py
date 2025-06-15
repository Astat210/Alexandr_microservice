from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    sales = relationship("Sales", back_populates="stock")

class Sales(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("stock.product_id"), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    sale_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    revenue = Column(Float, nullable=False)
    stock = relationship("Stock", back_populates="sales")