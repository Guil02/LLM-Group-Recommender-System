from grsmodel.main_runner.grs_module import GrsModule
from discord import Client
import recommender
from sklearn.metrics.pairwise import cosine_similarity
import pickle

import numpy as np
import pandas as pd


class AggregationModule(GrsModule):

    def __init__(self):
        super().__init__()

    def execute_module(self, bot: Client, *args, **kwargs):
        recipes = pd.read_csv('cleaned_recipes.csv')
        user_tags = args[0]
        agg_method = kwargs['aggregation_method']
        
        group_preferences = []
        for user in user_tags:
            user_preferences = {tag: rating for tag, rating in user_tags[user].items()}
            group_preferences.append(user_preferences)
        
        if agg_method == 'average':
            recommendations = recommender.average_recommendation(group_preferences)
        elif agg_method == 'least_misery':
            recommendations = recommender.least_misery_recommendation(group_preferences)
        elif agg_method == 'most_pleasure':
            recommendations = recommender.most_pleasure_recommendation(group_preferences)
        elif agg_method == 'llm':
            recommendations = recommender.openai_recommendation(group_preferences)
        else:
            raise ValueError(f'Invalid aggregation method: {agg_method}')
                   
        # Convert the recipe tags to a DataFrame
        recipe_names = []

        recipe_tag_df = pd.read_pickle('recipe_tag_df.pkl')
        with open("recipe_names.pkl","rb") as f:
            recipe_names = pickle.load(f)
        
        # Compute similarity scores between group tags and recipes
        def compute_similarity(group_vector, recipe_matrix):
            group_vector = np.array(group_vector).reshape(1, -1)
            similarity_scores = cosine_similarity(group_vector, recipe_matrix)
            return similarity_scores.flatten()
        
        recommendations = dict(recommendations)

        # Generate recommendations for the group based on similarity
        group_vector = [recommendations.get(tag, 0) for tag in recipe_tag_df.columns]
        similarity_scores = compute_similarity(group_vector, recipe_tag_df.values)
        recommended_indices = np.argsort(similarity_scores)[::-1]  # Sort in descending order
        recommended_recipes = [recipe_names[idx] for idx in recommended_indices]
        
        return recommended_recipes
            
        
        
        
        
    
    

