from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    price = Column(Float, nullable=False)
    unit = Column(String(10), nullable=False)
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    restock_items = relationship("RestockItem", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    registered_at = Column(DateTime, nullable=False)
    purchases = relationship("Purchase", back_populates="customer")

class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_email = Column(String(100))
    phone = Column(String(20))
    restocks = relationship("Restock", back_populates="supplier")

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    product = relationship("Product", back_populates="inventory")

class Purchase(Base):
    __tablename__ = "purchases"
    purchase_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    purchase_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    customer = relationship("Customer", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    purchase_item_id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.purchase_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")

class Restock(Base):
    __tablename__ = "restocks"
    restock_id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    restock_date = Column(DateTime, nullable=False)
    supplier = relationship("Supplier", back_populates="restocks")
    items = relationship("RestockItem", back_populates="restock")

class RestockItem(Base):
    __tablename__ = "restock_items"
    restock_item_id = Column(Integer, primary_key=True)
    restock_id = Column(Integer, ForeignKey("restocks.restock_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    restock = relationship("Restock", back_populates="items")
    product = relationship("Product", back_populates="restock_items")