import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# 1. Load the synthetic data
try:
    orders = pd.read_csv('orders.csv')
except FileNotFoundError:
    print("Error: Make sure 'orders.csv' is saved in the same folder as this script.")
    exit()

# 2. Filter orders for a specific cook to organize their delivery batches
# Let's test this on cook_id 80008 (Biryani Master) who has a high volume of orders
cook_orders = orders[orders['cook_id'] == 80008].copy()

# 3. Extract the geographic coordinates
coords = cook_orders[['customer_lat', 'customer_lng']].values

# 4. Configure the Mathematical Optimization (DBSCAN)
# We want to group orders that are within 1.5 km of each other.
# Scikit-learn's 'haversine' metric calculates distance over the curve of the Earth.
# It requires distances in radians, so we divide our target (1.5 km) by the Earth's radius (6371 km).
max_distance_km = 1.5
epsilon = max_distance_km / 6371.0

# Minimum number of orders required to justify grouping them into a single courier batch
min_orders = 2

# Initialize the machine learning model
db = DBSCAN(eps=epsilon, min_samples=min_orders, algorithm='ball_tree', metric='haversine')

# Convert coordinates to radians and run the prediction
cook_orders['cluster_id'] = db.fit_predict(np.radians(coords))

# 5. Output the Optimized Batches
print("\n" + "="*60)
print(f"NEXTMEAL ROUTING ENGINE: Batching Results for Cook 80008")
print("="*60)

for cluster_id in sorted(cook_orders['cluster_id'].unique()):
    # DBSCAN labels outliers (points too far away to batch) as -1
    if cluster_id == -1:
        print("\n[UNBATCHED ORDERS] -> Assign to individual couriers:")
    else:
        print(f"\n[BATCH ROUTE #{cluster_id + 1}] -> Highly efficient group for a single courier:")
        
    cluster_data = cook_orders[cook_orders['cluster_id'] == cluster_id]
    
    for _, row in cluster_data.iterrows():
        print(f"  - Order {row['order_id']}: {row['quantity']}x {row['dish_name']} "
              f"(Lat: {row['customer_lat']}, Lng: {row['customer_lng']})")
print("\n")