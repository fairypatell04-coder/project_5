# app/models/__init__.py

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

# Use the modern declarative_base from sqlalchemy.orm
Base = declarative_base()

# ---------------- Example Models ---------------- #

# Orders table
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # link to User

# Users table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    orders = relationship("Order", backref="user")  # one-to-many with Order

# Add additional models below as needed
