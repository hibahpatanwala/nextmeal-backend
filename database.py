from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

# 1. Database Connection
import os

# This ensures the database is created in the folder the server is running in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "nextmeal.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    address_lat = Column(Float)
    address_lng = Column(Float)
    max_budget = Column(Integer)
    # Taste Vectors
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
    average_rating = Column(Float, default=0.0) # Added for your new UI!
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
    total_time_online = Column(Integer, default=0)
    total_delivery_earnings = Column(Float, default=0.0)

# 5. NEW: SUBSCRIPTIONS TABLE (The Core of the Tiffin Model)
class Subscription(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys linking to the exact Customer and Chef
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    chef_id = Column(Integer, ForeignKey("chefs.chef_id"))
    
    plan_type = Column(String) # "Weekly" or "Monthly"
    price = Column(Float)
    start_date = Column(Date, default=date.today)
    
    # "Holiday Mode" Toggle
    is_paused = Column(Boolean, default=False) 
    
    # e.g., "Lunch" or "Dinner" (Helps your routing algorithm sort by time of day!)
    delivery_time = Column(String) 

# 6. Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database updated! The Subscriptions table is now live.")