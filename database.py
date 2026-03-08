from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
import os

# 1. Database Connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CHANGE THE NAME ON THIS LINE ---
db_path = os.path.join(BASE_DIR, "nextmeal_prod.db") 

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

# 5. SUBSCRIPTIONS TABLE (Restored!)
class Subscription(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    chef_id = Column(Integer, ForeignKey("chefs.chef_id"))
    plan_type = Column(String)
    price = Column(Float)
    start_date = Column(Date, default=date.today)
    is_paused = Column(Boolean, default=False)
    delivery_time = Column(String)

# 6. Create all tables
Base.metadata.create_all(bind=engine)