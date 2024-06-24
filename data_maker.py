import openai
import pandas as pd
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

        with open("recipe_ids.pkl","wb") as f:
            pickle.dump(recipe_ids, f)

        with open("recipe_names.pkl","wb") as f:
            pickle.dump(recipe_names, f)


def execute_module_2():
    print("Loading data...")
    recipes = pd.read_csv('cleaned_recipes_with_country.csv')

    # Define a function to extract and clean tags from a column
    def extract_tags(tags):
        return [tag.strip() for tag in eval(tags) if tag.strip()]

    # Apply the function to each tag column
    print("Extracting tags...")
    recipes['time_tags'] = recipes['time_tags'].apply(extract_tags)
    recipes['country_tags'] = recipes['country_tags'].apply(extract_tags)
    recipes['dietary_tags'] = recipes['dietary_tags'].apply(extract_tags)
    recipes['special_tags'] = recipes['special_tags'].apply(extract_tags)
    recipes['ingredients_tags'] = recipes['ingredients_tags'].apply(extract_tags)

    # Combine all tags into one column
    print("Combining tags...")
    recipes['all_tags'] = recipes.apply(
        lambda row: row['time_tags'] + row['country_tags'] + row['dietary_tags'] + row['special_tags'] + row[
            'ingredients_tags'],
        axis=1
    )

    # Create the tag matrix using MultiLabelBinarizer
    print("Creating tag matrix...")
    mlb = MultiLabelBinarizer()
    recipe_tag_matrix = mlb.fit_transform(recipes['all_tags'])

    # Create a DataFrame to store the vector and id
    print("Creating DataFrame with tag vectors and IDs...")
    recipe_tag_df = pd.DataFrame(recipe_tag_matrix, columns=mlb.classes_)
    recipe_tag_df['id'] = recipes['id'].values

    # Save the DataFrame and the necessary info
    print("Saving DataFrame to csv...")
    recipe_tag_df.to_csv("recipe_tag_df.csv")

    print("Process completed.")


execute_module_2()
