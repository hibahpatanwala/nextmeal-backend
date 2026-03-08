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
    name: str     # For Customers/Couriers this is their name, for Chefs this is 'kitchen_name'
    email: str
    password: str
    role: str     # "Customer", "Chef", or "Courier"

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 2. Check which table we are adding this user to
    if request.role == "Customer":
        # Check if email already exists
        if db.query(Customer).filter(Customer.email == request.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = Customer(name=request.name, email=request.email, password_hash=request.password)
        
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
    # Create 20 Mock Customers
    for _ in range(20):
        # Generate coordinates roughly around Mumbai/Mira Bhayandar
        lat = random.uniform(19.0, 19.3) 
        lng = random.uniform(72.8, 73.0)
        
        new_customer = Customer(
            name=fake.name(),
            email=fake.email(),
            password_hash="testpass123",
            address_lat=lat,
            address_lng=lng,
            max_budget=random.choice([1000, 1500, 2000, 2500]),
            # Random taste vectors for your Cosine Similarity math!
            pref_spice_level=random.randint(1, 10),
            pref_is_veg=random.choice([True, False])
        )
        db.add(new_customer)
    
    db.commit()
    return {"message": "Successfully generated 20 mock customers for the PPT!"}