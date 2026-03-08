from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import os

# 1. Database Connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "nextmeal.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. CUSTOMER TABLE
class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    address_lat = Column(Float)
    address_lng = Column(Float)
    max_budget = Column(Integer)
    pref_spice_level = Column(Integer)
    pref_is_veg = Column(Boolean, default=False)

# 3. CHEF TABLE
class Chef(Base):
    __tablename__ = "chefs"
    chef_id = Column(Integer, primary_key=True, index=True)
    kitchen_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    kitchen_lat = Column(Float)
    kitchen_lng = Column(Float)
    is_accepting_orders = Column(Boolean, default=True)
    average_rating = Column(Float, default=0.0)
    total_earnings = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)

# 4. COURIER TABLE
class Courier(Base):
    __tablename__ = "couriers"
    courier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    vehicle_type = Column(String)
    current_lat = Column(Float)
    current_lng = Column(Float)
    is_online = Column(Boolean, default=False)

# 5. Create all tables
Base.metadata.create_all(bind=engine)