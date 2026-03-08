import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

print("Generating 10,000 records for NextMeal Algorithm Testing...")

# --- 1. GENERATE USERS (For Cosine Similarity & Routing Destinations) ---
# Mumbai Bounding Box approx: Lat 18.90 to 19.25, Lng 72.80 to 72.95
num_users = 2000
users_data = {
    'user_id': range(1001, 1001 + num_users),
    'user_lat': np.random.uniform(18.90, 19.25, num_users),
    'user_lng': np.random.uniform(72.80, 72.95, num_users),
    # Taste Profile Vectors (Scale 1-10 or Binary) for Cosine Similarity
    'pref_spice_level': np.random.randint(1, 11, num_users),
    'pref_sweet_level': np.random.randint(1, 11, num_users),
    'pref_is_veg': np.random.choice([0, 1], num_users, p=[0.4, 0.6]),
    'pref_south_indian': np.random.choice([0, 1], num_users),
    'pref_north_indian': np.random.choice([0, 1], num_users)
}
users_df = pd.DataFrame(users_data)
users_df.to_csv('test_users.csv', index=False)
print("✅ Created test_users.csv (2,000 users with taste profiles)")

# --- 2. GENERATE COOKS & MENU (For Cosine Similarity & Routing Origins) ---
num_dishes = 500
cook_ids = range(80000, 80100) # 100 cooks
menu_data = {
    'dish_id': range(5001, 5001 + num_dishes),
    'cook_id': np.random.choice(cook_ids, num_dishes),
    'cook_lat': np.random.uniform(18.90, 19.25, num_dishes),
    'cook_lng': np.random.uniform(72.80, 72.95, num_dishes),
    'prep_time_mins': np.random.randint(10, 45, num_dishes),
    # Dish Taste Vectors to match against users
    'dish_spice_level': np.random.randint(1, 11, num_dishes),
    'dish_sweet_level': np.random.randint(1, 11, num_dishes),
    'dish_is_veg': np.random.choice([0, 1], num_dishes, p=[0.5, 0.5]),
    'dish_south_indian': np.random.choice([0, 1], num_dishes),
    'dish_north_indian': np.random.choice([0, 1], num_dishes)
}
menu_df = pd.DataFrame(menu_data)
menu_df.to_csv('test_menu.csv', index=False)
print("✅ Created test_menu.csv (500 dishes with taste attributes)")

# --- 3. GENERATE 10,000 ORDERS (The Main Fact Table) ---
num_orders = 10000
start_time = datetime(2026, 3, 1, 18, 0, 0) # Start generating from 6 PM

orders_data = {
    'order_id': range(90000, 90000 + num_orders),
    'user_id': np.random.choice(users_df['user_id'], num_orders),
    'dish_id': np.random.choice(menu_df['dish_id'], num_orders),
    'quantity': np.random.randint(1, 5, num_orders),
    # Generate random timestamps over a 30-day period
    'order_time': [start_time + timedelta(minutes=random.randint(0, 43200)) for _ in range(num_orders)]
}
orders_df = pd.DataFrame(orders_data)
# Sort by time to make it realistic for simulation
orders_df = orders_df.sort_values('order_time')
orders_df.to_csv('test_orders_10k.csv', index=False)
# Change the print statements at the very end of your script to this:
print("Created test_users.csv (2,000 users with taste profiles)")
print("Created test_menu.csv (500 dishes with taste attributes)")
print("Created test_orders_10k.csv (10,000 transactions)")
print("\nAll 10,000 datasets generated successfully! Ready for algorithmic testing.")