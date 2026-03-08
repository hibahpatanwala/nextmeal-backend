import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load your 10k-compatible datasets
users = pd.read_csv('test_users.csv')
menu = pd.read_csv('test_menu.csv')

def get_recommendations(user_id, top_n=5):
    # Find the specific user's taste profile
    user_profile = users[users['user_id'] == user_id]
    if user_profile.empty:
        return "User not found."

    # Select the features for comparison (Spice, Sweet, Veg, South, North)
    features = ['pref_spice_level', 'pref_sweet_level', 'pref_is_veg', 'pref_south_indian', 'pref_north_indian']
    dish_features = ['dish_spice_level', 'dish_sweet_level', 'dish_is_veg', 'dish_south_indian', 'dish_north_indian']

    # Inside your get_recommendations function, add this:

# 1. Normalize scales (Divide 1-10 scores by 10)
    menu_vectors = menu[dish_features].values / 10.0
    user_vector = user_profile[features].values / 10.0

# 2. Add a 'Hard Constraint' for Vegetarian preference
# If User is Veg (1) and Dish is Non-Veg (0), we want a huge penalty.
# You can do this by multiplying the 'is_veg' column by a weight of 5.
    # 2. Calculate Cosine Similarity (The Math)
    # This measures the angle between the user's "desire" vector and the dish's "attribute" vector
    similarities = cosine_similarity(user_vector, menu_vectors)[0]

    # 3. Rank the dishes
    menu_copy = menu.copy()
    menu_copy['match_score'] = similarities
    
    # Sort by highest score first
    recommendations = menu_copy.sort_values(by='match_score', ascending=False)
    
    return recommendations[['dish_id', 'cook_id', 'match_score']].head(top_n)

# Test it for User 1001 (One of your 2,000 generated users)
print("--- TOP 5 MEAL RECOMMENDATIONS FOR USER 1001 ---")
print(get_recommendations(1001))