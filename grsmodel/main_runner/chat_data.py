import discord
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from collections import deque
import ast


class ChatData:
    def __init__(self, num_users=5):
        self.num_users = num_users
        self.collected_tags = {}
        self.collected_tags_rate_count = {}
        self.finished = False
        self.channel = None
        self.manual_tag_collect_stop = False
        self.recommended_recipes = []
        self.recipes = None

        self.special_tags = deque(['occasion', 'easy', 'main-dish'], maxlen=3)
        self.time_tags = ['60-minutes-or-less', '30-minutes-or-less', '15-minutes-or-less', '1-day-or-more']
        self.country_tags = deque(['north-american', 'european', 'asian', 'south-west-pacific'], maxlen=4)
        self.dietary_tags = deque(
            ['low-cholesterol', 'meat', 'vegetables', 'dietary', 'low-carb', 'pasta-rice-and-grains'], maxlen=6)
        self.chosen_tags = []

        self.recipe_tag_matrix = self.preload()

        self.model_loops = 0

    def add_tag(self, user_id, tag, rating):
        if user_id not in self.collected_tags:
            self.collected_tags[user_id] = {}
        self.collected_tags[user_id][tag] = rating

    def get_tag(self, user_id, tag):
        return self.collected_tags.get(user_id, {}).get(tag, 0)

    def get_tags(self, user_id):
        return self.collected_tags.get(user_id, {})

    def get_all_tags(self):
        return self.collected_tags

    async def get_finished(self):
        return self.finished

    def set_finished(self, finished: bool):
        self.finished = finished

    def set_channel(self, channel: discord.Message.channel):
        self.channel = channel

    def get_channel(self):
        return self.channel

    def set_manual_tag_collect_stop(self, stop: bool):
        self.manual_tag_collect_stop = stop

    def get_manual_tag_collect_stop(self):
        return self.manual_tag_collect_stop

    def get_recommended_recipes(self):
        return self.recommended_recipes

    def set_recommended_recipes(self, recipes):
        self.recommended_recipes = recipes

    def get_num_users(self):
        return self.num_users

    def get_special_tags(self):
        return self.special_tags

    def get_time_tags(self):
        return self.time_tags

    def get_country_tags(self):
        return self.country_tags

    def get_dietary_tags(self):
        return self.dietary_tags

    def get_random_ingredient_tag(self):
        pass

    def get_tag_matrix(self):
        return self.recipe_tag_matrix

    def preload(self):
        def extract_tags(tags):
            return [tag.strip() for tag in eval(tags) if tag.strip()]

        def row_function(row):
            new_row = extract_tags(row['time_tags']) + \
                      extract_tags(row['country_tags']) + \
                      extract_tags(row['dietary_tags']) + \
                      extract_tags(row['special_tags'])
            #          + \        extract_tags(row['ingredients_tags'])
            return new_row

        self.recipes = pd.read_csv('cleaned_recipes_with_country.csv')
        self.recipes['all_tags'] = self.recipes.apply(row_function, axis=1)

        mlb = MultiLabelBinarizer()
        recipe_tag_matrix = mlb.fit_transform(self.recipes['all_tags'])

        tag_dicts = {}
        for i, recipe_id in enumerate(self.recipes['id']):
            tag_dicts[recipe_id] = {tag: int(recipe_tag_matrix[i, j]) for j, tag in enumerate(mlb.classes_)}

        return tag_dicts

    def get_model_loops(self):
        return self.model_loops

    def increment_model_loops(self):
        self.model_loops += 1

    def add_chosen_tags(self, tags):
        country = self.recipes['country_tags'].apply(ast.literal_eval).explode().unique()
        special = self.recipes['special_tags'].apply(ast.literal_eval).explode().unique()
        dietary = self.recipes['dietary_tags'].apply(ast.literal_eval).explode().unique()
        time = self.recipes['time_tags'].apply(ast.literal_eval).explode().unique()
        for tag in tags:
            if tag in country:
                self.country_tags.appendleft(tag)
            elif tag in special:
                self.special_tags.appendleft(tag)
            elif tag in dietary:
                self.dietary_tags.appendleft(tag)
            elif tag in time:
                continue
            else:
                self.chosen_tags.append(tag)

        self.chosen_tags = list(set(self.chosen_tags))

    def get_tag_ratings(self, tag):
        ratings = {}
        for user in self.collected_tags.keys():
            ratings[user] = self.collected_tags[user].get(tag, 0)

        return ratings
