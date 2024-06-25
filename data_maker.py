import openai
import pandas as pd
import polars as pl
import recommender
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import pickle


def execute_module():
    recipes = pd.read_csv('cleaned_recipes.csv')
    # Convert the recipe tags to a DataFrame
    recipe_tag_matrix = []
    recipe_ids = []
    recipe_names = []

    for index, row in recipes.iterrows():
        recipe_id = row['id']
        recipe_ids.append(recipe_id)
        recipe_names.append(row['name'])

        time_tags = row['time_tags'].strip('[]').replace("'", "").split(', ')
        time_tags = [tag.strip() for tag in time_tags if tag.strip()]

        country_tags = row['country_tags'].strip('[]').replace("'", "").split(', ')
        country_tags = [tag.strip() for tag in country_tags if tag.strip()]

        dietary_tags = row['dietary_tags'].strip('[]').replace("'", "").split(', ')
        dietary_tags = [tag.strip() for tag in dietary_tags if tag.strip()]

        special_tags = row['special_tags'].strip('[]').replace("'", "").split(', ')
        special_tags = [tag.strip() for tag in special_tags if tag.strip()]

        ingredient_tags = row['ingredient_tags'].strip('[]').replace("'", "").split(', ')
        ingredient_tags = [tag.strip() for tag in ingredient_tags if tag.strip()]

        tags = time_tags + country_tags + dietary_tags + special_tags + ingredient_tags

        tag_vector = {tag: 1 for tag in tags}
        recipe_tag_matrix.append(tag_vector)

    recipe_tag_df = pd.DataFrame(recipe_tag_matrix).fillna(0)

    recipe_tag_df.to_pickle("recipe_tag_df.pkl")

    with open("recipe_ids.pkl", "wb") as f:
        pickle.dump(recipe_ids, f)

    with open("recipe_names.pkl", "wb") as f:
        pickle.dump(recipe_names, f)


def execute_module_1():
    print("Loading data...")
    recipes = pd.read_csv('cleaned_recipes_with_country.csv')

    # Define a function to extract and clean tags from a column
    def extract_tags(tags):
        return [tag.strip() for tag in eval(tags) if tag.strip()]

    def row_function(row):
        new_row = extract_tags(row['time_tags']) + \
                  extract_tags(row['country_tags']) + \
                  extract_tags(row['dietary_tags']) + \
                  extract_tags(row['special_tags'])
#          + \        extract_tags(row['ingredients_tags'])
        return new_row

    # Apply the function to each tag column and combine all tags into one list
    print("Extracting and combining tags...")
    recipes['all_tags'] = recipes.apply(row_function, axis=1)

    # Create the tag matrix using MultiLabelBinarizer
    print("Creating tag matrix...")
    mlb = MultiLabelBinarizer()
    recipe_tag_matrix = mlb.fit_transform(recipes['all_tags'])

    tag_dicts = {}
    for i, recipe_id in enumerate(recipes['id']):
        tag_dicts[recipe_id] = {tag: int(recipe_tag_matrix[i, j]) for j, tag in enumerate(mlb.classes_)}

    # Print a sample of the dictionary
    sample_key = list(tag_dicts.keys())[0]
    print(f"Sample entry (Recipe ID: {sample_key}):")
    print(tag_dicts[sample_key])

    return tag_dicts


execute_module_1()
