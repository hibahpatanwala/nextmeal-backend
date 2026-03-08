from database import SessionLocal, Chef, Courier

# 1. Open a connection to the database
db = SessionLocal()

def seed_marketplace():
    # 2. Create a Mock Chef (for the "I Can Cook" dashboard)
    # Location: Bandra West, Mumbai
    new_chef = Chef(
        kitchen_name="Maya's Coastal Kitchen",
        email="maya@nextmeal.com",
        password_hash="hashed_password_123",
        kitchen_lat=19.0544,
        kitchen_lng=72.8402,
        total_earnings=12500.50,
        total_expenses=4200.00
    )

    # 3. Create a Mock Courier (for the "I Can Deliver" dashboard)
    # Location: Starting near Bandra Station
    new_courier = Courier(
        name="Arjun Delivery",
        email="arjun@nextmeal.com",
        phone="9876543210",
        vehicle_type="Electric Scooter",
        current_lat=19.0510,
        current_lng=72.8415,
        is_online=True,
        total_delivery_earnings=850.00
    )

    # 4. Save them to the database
    try:
        db.add(new_chef)
        db.add(new_courier)
        db.commit()
        print("✅ Success: One Chef and one Courier added to NextMeal database!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_marketplace()