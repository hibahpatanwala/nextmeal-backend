from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Customer, Chef, Courier
import database # Make sure this import is at the top

# --- ADD THIS MAGIC LINE ---
database.Base.metadata.create_all(bind=database.engine)
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# --- ADD THIS RIGHT AFTER app = FastAPI() ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # This allows your Lovable app to talk to the backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 1. ALLOW LOVABLE TO TALK TO YOUR LOCAL COMPUTER (CORS)
# This is crucial so Lovable doesn't get blocked by security settings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd replace this with your Lovable URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Database Helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. Define what a Login Request looks like
class LoginRequest(BaseModel):
    email: str
    password: str
    role: str # "Customer", "Chef", or "Courier"

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 4. Search the correct table based on the role
    user = None
    if request.role == "Customer":
        user = db.query(Customer).filter(Customer.email == request.email).first()
    elif request.role == "Chef":
        user = db.query(Chef).filter(Chef.email == request.email).first()
    elif request.role == "Courier":
        user = db.query(Courier).filter(Courier.email == request.email).first()

    # 5. Check if user exists and password matches
    # (Note: In a real app, we would use password hashing here!)
    if not user or user.password_hash != request.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login Successful", "role": request.role, "user_id": getattr(user, f"{request.role.lower()}_id")}

# --- ADD THIS TO THE BOTTOM OF YOUR main.py ---

# 1. Define what a Registration Request looks like
class RegisterRequest(BaseModel):
    name: str 
    email: str
    password: str
    role: str 
    
    # --- NEW OPTIONAL FIELDS FROM THE UI WIZARD ---
    phone_number: str = None
    dob: str = None
    max_budget: int = 1500
    pref_is_veg: bool = False
    pref_spice_level: int = 5
    # Defaulting roughly to Mira Bhayandar coordinates for the prototype
    address_lat: float = 19.28 
    address_lng: float = 72.85

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 2. Check which table we are adding this user to
    if request.role == "Customer":
        if db.query(Customer).filter(Customer.email == request.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Save all the newly collected data to the database
        new_user = Customer(
            name=request.name, 
            email=request.email, 
            password_hash=request.password,
            phone_number=request.phone_number,
            dob=request.dob,
            max_budget=request.max_budget,
            pref_is_veg=request.pref_is_veg,
            pref_spice_level=request.pref_spice_level,
            address_lat=request.address_lat,
            address_lng=request.address_lng
        )
        
    elif request.role == "Chef":
        if db.query(Chef).filter(Chef.email == request.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = Chef(kitchen_name=request.name, email=request.email, password_hash=request.password)
        
    elif request.role == "Courier":
        if db.query(Courier).filter(Courier.email == request.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = Courier(name=request.name, email=request.email, password_hash=request.password)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid role. Must be Customer, Chef, or Courier.")

    # 3. Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Refreshes to get the newly generated ID

    # 4. Return success and the new ID
    user_id = getattr(new_user, f"{request.role.lower()}_id")
    return {"message": f"{request.role} registered successfully!", "user_id": user_id}

# --- ADD THIS TO THE BOTTOM OF YOUR main.py ---
from database import Subscription
from datetime import date

# 1. Define what a Subscription Request looks like
class SubscriptionRequest(BaseModel):
    customer_id: int
    chef_id: int
    plan_type: str       # "Weekly" or "Monthly"
    price: float
    delivery_time: str   # "Lunch" or "Dinner"

@app.post("/subscribe")
def create_subscription(request: SubscriptionRequest, db: Session = Depends(get_db)):
    # 2. Check if the Customer and Chef actually exist
    customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
    chef = db.query(Chef).filter(Chef.chef_id == request.chef_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not chef:
        raise HTTPException(status_code=404, detail="Chef not found")

    # 3. Create the new Tiffin Subscription
    new_sub = Subscription(
        customer_id=request.customer_id,
        chef_id=request.chef_id,
        plan_type=request.plan_type,
        price=request.price,
        delivery_time=request.delivery_time,
        start_date=date.today(),
        is_paused=False # Holiday mode is off by default
    )

    # 4. Save to database
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    return {
        "message": f"Successfully subscribed to {chef.kitchen_name} for a {request.plan_type} tiffin!",
        "subscription_id": new_sub.subscription_id
    }
# --- ADD THIS TO THE BOTTOM OF YOUR main.py ---

# 1. Endpoint to load the Customer's Discovery Feed
@app.get("/kitchens")
def get_active_kitchens(db: Session = Depends(get_db)):
    # Fetch all chefs who are currently accepting orders
    active_chefs = db.query(Chef).filter(Chef.is_accepting_orders == True).all()
    
    # We return just the public info needed for the Lovable cards
    kitchen_data = []
    for chef in active_chefs:
        kitchen_data.append({
            "chef_id": chef.chef_id,
            "kitchen_name": chef.kitchen_name,
            "average_rating": chef.average_rating,
            # We will mock a starting price for the UI for now
            "starting_price": 1200.00 
        })
    return {"kitchens": kitchen_data}

# 2. Endpoint to load the Chef's Dashboard Metrics
@app.get("/chef/{chef_id}/dashboard")
def get_chef_dashboard(chef_id: int, db: Session = Depends(get_db)):
    chef = db.query(Chef).filter(Chef.chef_id == chef_id).first()
    if not chef:
        raise HTTPException(status_code=404, detail="Chef not found")
    
    return {
        "kitchen_name": chef.kitchen_name,
        "total_earnings": chef.total_earnings,
        "average_rating": chef.average_rating,
        "is_accepting_orders": chef.is_accepting_orders
    }
from faker import Faker
import random

fake = Faker('en_IN') # Generates Indian names and phone numbers!

@app.post("/admin/seed-mock-data")
def seed_live_database(db: Session = Depends(get_db)):
    # 1. Create the Mock Chefs for the Lovable UI
    mock_chefs = [
        Chef(kitchen_name="Priya's Kitchen", email="priya@test.com", password_hash="pass", kitchen_lat=19.28, kitchen_lng=72.86, is_accepting_orders=True, average_rating=4.8),
        Chef(kitchen_name="Nonna's Table", email="nonna@test.com", password_hash="pass", kitchen_lat=19.29, kitchen_lng=72.85, is_accepting_orders=True, average_rating=4.9),
        Chef(kitchen_name="Ocean Bites", email="ocean@test.com", password_hash="pass", kitchen_lat=19.27, kitchen_lng=72.87, is_accepting_orders=True, average_rating=4.7)
    ]
    db.add_all(mock_chefs)

    # 2. Create 20 Mock Customers
    for _ in range(20):
        # Generate coordinates roughly around Mira Bhayandar
        lat = random.uniform(19.25, 19.35) 
        lng = random.uniform(72.80, 72.90)
        
        new_customer = Customer(
            name=fake.name(),
            email=fake.email(),
            password_hash="testpass123",
            address_lat=lat,
            address_lng=lng,
            max_budget=random.choice([1000, 1500, 2000, 2500]),
            pref_spice_level=random.randint(1, 10),
            pref_is_veg=random.choice([True, False])
        )
        db.add(new_customer)
    
    db.commit()
    return {"message": "Successfully generated 20 customers and 3 Kitchens for the PPT!"}

import math
import random

@app.get("/recommendations/{customer_id}")
def get_recommendations(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return {"recommendations": []}

    # 1. Define the Customer Vector A (Budget, Spice, Veg)
    # We use defaults just in case a field is empty to prevent math errors
    budget = customer.max_budget if customer.max_budget else 1500
    spice = customer.pref_spice_level if customer.pref_spice_level else 5
    is_veg = 1 if customer.pref_is_veg else 0
    
    A = [budget / 1000, spice, is_veg]
    
    active_chefs = db.query(Chef).filter(Chef.is_accepting_orders == True).all()
    scored_chefs = []

    for c in active_chefs:
        # 2. Define Kitchen Vector B (Price, Spice, Veg)
        c_price = c.starting_price if c.starting_price else 1200
        c_spice = c.spice_level if c.spice_level else 5
        c_veg = 1 if c.is_veg else 0
        
        B = [c_price / 1000, c_spice, c_veg]
        
        # 3. Calculate Cosine Similarity
        dot_product = sum(a * b for a, b in zip(A, B))
        mag_a = math.sqrt(sum(a**2 for a in A))
        mag_b = math.sqrt(sum(b**2 for b in B))
        
        similarity = dot_product / (mag_a * mag_b) if (mag_a * mag_b) > 0 else 0
        
        scored_chefs.append({
            "chef_id": c.chef_id,
            "kitchen_name": c.kitchen_name,
            "average_rating": c.average_rating,
            "starting_price": c.starting_price,
            "match_score": round(similarity * 100, 1) # Converts 0.98 to 98.0
        })

    # Sort by highest match score and return top 10
    scored_chefs.sort(key=lambda x: x["match_score"], reverse=True)
    return {"recommendations": scored_chefs[:10]}

@app.post("/admin/seed-10k")
def seed_10k_data(db: Session = Depends(get_db)):
    # Bulk insert for the NMIMS demo
    new_chefs = [
        Chef(
            kitchen_name=f"Cloud Kitchen {i}",
            email=f"chef{i}@nextmeal.com",
            password_hash="pass123",
            kitchen_lat=19.0 + (i / 10000),
            kitchen_lng=72.8 + (i / 10000),
            is_accepting_orders=True,
            average_rating=round(random.uniform(3.5, 5.0), 1),
            starting_price=100 + (i % 400),
            spice_level=(i % 10) + 1,
            is_veg=(i % 2 == 0)
        ) for i in range(10000)
    ]
    db.bulk_save_objects(new_chefs)
    db.commit()
    return {"message": "10,000 kitchens seeded successfully for the Cosine Similarity demo!"}