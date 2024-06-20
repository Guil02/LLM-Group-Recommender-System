import itertools
import pandas as pd
import random
import recommender
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm
from utils.helper import Helper

COLUMNS = ['time_tags', 'country_tags', 'dietary_tags', 'special_tags', 'ingredients_tags']

def load_data():
    # Load the recipes and interactions data
    recipes = pd.read_csv("/Users/alexanderleonidas/Documents/Maastricht University/AI Masters/Research Project LLM for Group RS/archive/cleaned_recipes_with_country.csv")
    interactions = pd.read_csv("/Users/alexanderleonidas/Documents/Maastricht University/AI Masters/Research Project LLM for Group RS/archive/RAW_interactions.csv")

    # Extract unique tags from the dataset
    unique_tags = set()
    for name in COLUMNS:
        for tag_list in recipes[name]:
            # Correcting parsing based on your description that tags appear like a Python list in string format
            tag_list = tag_list.strip('[]').replace("'", "").split(', ')
            for tag in tag_list:
                cleaned_tag = tag.strip()  # Remove any leading/trailing spaces
                if cleaned_tag:  # Ensure the tag is not empty
                    unique_tags.add(cleaned_tag)

    # Extract unique users from the dataset
    users = interactions['user_id'].unique()

    return recipes, interactions, users

def make_user_profiles(filtered_users, filtered_interactions, recipes):
    # Create an empty dictionary to store the tags for each user
    user_tags = {user: {} for user in filtered_users}
    number_appeared = {user: {} for user in filtered_users}

    # Iterate over the interactions data to update the user_tags dictionary
    for name in tqdm(COLUMNS):
        for index, row in filtered_interactions.iterrows():
            user_id = row['user_id']
            recipe_id = row['recipe_id']
            rating = row['rating']

            # Filter the recipes DataFrame to find the tags for the current recipe_id
            recipe_row = recipes[recipes['id'] == recipe_id]
            
            # Check if the recipe_row is not empty
            if not recipe_row.empty:
                recipe_tags = recipe_row[name].values[0]
                recipe_tags = recipe_tags.strip('[]').replace("'", "").split(', ')

                # Process each tag and update user_tags and number_appeared dictionaries
                for tag in recipe_tags:
                    cleaned_tag = tag.strip()
                    if cleaned_tag:
                        if cleaned_tag not in user_tags[user_id]:
                            user_tags[user_id][cleaned_tag] = 0
                            number_appeared[user_id][cleaned_tag] = 0
                        user_tags[user_id][cleaned_tag] += rating
                        number_appeared[user_id][cleaned_tag] += 1

    # Calculate the average rating for each tag
    for user in user_tags:
        for tag in user_tags[user]:
            if number_appeared[user][tag] > 0:
                user_tags[user][tag] /= number_appeared[user][tag]
    
    Helper().save_data(user_tags, '.../results/user_profiles.pkl')
    return user_tags


def create_groups(user_tags):
    # Set maximum group size
    max_group_size = 5
    group_preferences = []
    group_info = []

    # Get the list of users
    users_list = list(user_tags.keys())

    # Shuffle the list to ensure randomness
    random.shuffle(users_list)

    # Divide the shuffled list into groups of 5
    for i in range(0, len(users_list), max_group_size):
        group = users_list[i:i + max_group_size]
        
        # Collect preferences for the entire group
        group_pref = []
        temp = []
        for user in group:
            t = {user: user_tags[user].items()}
            temp.append(t)
            print(temp)
            user_preferences = {tag: rating for tag, rating in user_tags[user].items()}
            group_pref.append(user_preferences)
        
        # Append the group's preferences to group_preferences
        group_preferences.append(group_pref)
        group_info.append(temp)

    # Helper().save_data(group_info, 'results/test.pkl')
    return group_preferences

def get_traditional_scores(group_preferences):
    average = []
    least_misery = []
    most_pleasure = []

    for group in group_preferences:
        average.append(recommender.average_recommendation(group))
        least_misery.append(recommender.least_misery_recommendation(group))
        most_pleasure.append(recommender.most_pleasure_recommendation(group))
    
    return average, least_misery, most_pleasure

# Compute similarity scores between group tags and recipes
# def compute_similarity(group_vector, recipe_matrix):
#     group_vector = np.array(group_vector).reshape(1, -1)
#     similarity_scores = cosine_similarity(group_vector, recipe_matrix)
#     return similarity_scores.flatten()

def compute_similarity(group_vector, recipe_matrix):
    similarity_scores = []
    for recipe_vector in recipe_matrix:
        common_tags = set(group_vector.keys()).intersection(set(recipe_vector.keys()))
        similarity = sum(group_vector[tag] * recipe_vector[tag] for tag in common_tags)
        similarity_scores.append(similarity)
    return similarity_scores

def get_recommendation(recipes, aggregations):
     # Convert the recipe tags to a list of dictionaries
    recipe_tag_matrix = []
    recipe_ids = []
    recipe_names = []
    all_tags = set()

    print('converting recipes...')
    for index, row in recipes.iterrows():
        for name in COLUMNS:
            recipe_id = row['id']
            recipe_tags = row[name].strip('[]').replace("'", "").split(', ')
            recipe_tags = [tag.strip() for tag in recipe_tags if tag.strip()]
            tag_vector = {tag: 1 for tag in recipe_tags}
            recipe_tag_matrix.append(tag_vector)
            recipe_ids.append(recipe_id)
            recipe_names.append(row['name'])
            all_tags.update(recipe_tags)

    all_tags = list(all_tags)

    print('getting recommended recipes...')
    recommendations = [[], [], []]

    for I, method in enumerate(aggregations):
        for group in tqdm(method):
            group_preferences = dict(group)
            # Generate recommendations for the group based on similarity
            group_vector = {tag: group_preferences.get(tag, 0) for tag in all_tags}
            similarity_scores = compute_similarity(group_vector, recipe_tag_matrix)
            recommended_indices = np.argsort(similarity_scores)[::-1]  # Sort in descending order
            recommended_recipes = [recipe_names[idx] for idx in recommended_indices]
            # Get the top 10 recipes
            recommendations[I].append(recommended_recipes[:10])

    return recommendations

def main():
    recipes, interactions, _ = load_data()

    number_user_ratings = {}
    for user in interactions['user_id']:
        if user not in number_user_ratings:
            number_user_ratings[user] = 0
        number_user_ratings[user] += 1

    # sort by descending order
    number_user_ratings = dict(sorted(number_user_ratings.items(), key=lambda item: item[1], reverse=True))

    # get top users
    top_users = dict(list(number_user_ratings.items())[200:400])

    # interactions for only the top 200 users with the most recipe reviews
    filtered_interactions = interactions[interactions['user_id'].isin(top_users)]
    filtered_users = filtered_interactions['user_id'].unique()

    print('creating profiles...')
    user_tags = make_user_profiles(filtered_users, filtered_interactions, recipes)
    print('creating groups...')
    group_preferences = create_groups(user_tags)
    print('aggregating preferences...')
    aggregations = get_traditional_scores(group_preferences)
    print('getting recommendations for each group...')
    recommendations = get_recommendation(recipes, aggregations)

    Helper().save_data(recommendations, '.../results/recommendations_exp_2.pkl')


main()