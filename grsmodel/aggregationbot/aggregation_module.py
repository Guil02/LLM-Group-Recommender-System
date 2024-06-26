import os

from grsmodel.main_runner.grs_module import GrsModule
from discord import Client
import recommender
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pickle

import numpy as np
import pandas as pd


class AggregationModule(GrsModule):

    def __init__(self):
        super().__init__()

    async def execute_module(self, bot: Client, *args, **kwargs):
        chat_data = kwargs['chat_data']
        user_tags = chat_data.get_all_tags()
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
            recommendations = recommender.openai_recommendation(group_preferences, api_key=os.getenv('OPEN_AI_API_KEY'))
        else:
            raise ValueError(f'Invalid aggregation method: {agg_method}')

        tag_dicts = chat_data.get_tag_matrix()
        recipe_ids = list(tag_dicts.keys())
        all_tags = list(tag_dicts[next(iter(recipe_ids))].keys())  # Get the list of all tags

        # Create the recipe tag matrix
        tag_matrix = np.array([[tag_dicts[recipe_id].get(tag, 0) for tag in all_tags] for recipe_id in recipe_ids])

        # Convert recommendations to a dictionary for easy lookup
        recommendations_dict = dict(ast.literal_eval(recommendations))

        # Generate the group vector based on the recommendations
        group_vector = [recommendations_dict.get(tag, 0) for tag in all_tags]

        # Compute similarity scores between the group vector and recipe tag matrix
        group_vector = np.array(group_vector).reshape(1, -1)
        similarity_scores = cosine_similarity(group_vector, tag_matrix).flatten()

        # Get the indices of the top recipes sorted by similarity scores in descending order
        recommended_indices = np.argsort(similarity_scores)[::-1]

        # Set the top 3 recommended recipe IDs in chat_data
        top_recommended_recipe_ids = [recipe_ids[idx] for idx in recommended_indices[:3]]
        chat_data.set_recommended_recipes(top_recommended_recipe_ids)

        return chat_data
