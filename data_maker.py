import openai
import pandas as pd
import recommender
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
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
        
        