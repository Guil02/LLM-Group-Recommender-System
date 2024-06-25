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
        user_tags = kwargs['chat_data'].get_all_tags()
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

        tag_dicts = kwargs['chat_data'].get_tag_matrix()
        recipe_ids = tag_dicts.keys()
        recipe_tag_matrix = np.array([list(tag_dicts[recipe_id].values()) for recipe_id in recipe_ids])

        # Compute similarity scores between group tags and recipes
        def compute_similarity(gv, recipe_matrix):
            gv = np.array(gv).reshape(1, -1)
            sim_scores = cosine_similarity(gv, recipe_matrix)
            return sim_scores.flatten()

        recommendations = dict(recommendations)

        # Generate recommendations for the group based on similarity
        group_vector = [recommendations.get(tag, 0) for tag in tag_dicts[recipe_ids[0]].keys()]
        similarity_scores = compute_similarity(group_vector, recipe_tag_matrix)
        recommended_indices = np.argsort(similarity_scores)[::-1]       # Sort in descending order
        recommended_recipe_ids = [recipe_ids[idx] for idx in recommended_indices]

        kwargs['chat_data'].set_recommended_recipes(recommended_recipe_ids[:3])     # best three
        return kwargs['chat_data']
