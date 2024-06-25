import discord
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def preload():
    def extract_tags(tags):
        return [tag.strip() for tag in eval(tags) if tag.strip()]

    def row_function(row):
        new_row = extract_tags(row['time_tags']) + \
                  extract_tags(row['country_tags']) + \
                  extract_tags(row['dietary_tags']) + \
                  extract_tags(row['special_tags'])
        #          + \        extract_tags(row['ingredients_tags'])
        return new_row

    recipes = pd.read_csv('cleaned_recipes_with_country.csv')
    recipes['all_tags'] = recipes.apply(row_function, axis=1)

    mlb = MultiLabelBinarizer()
    recipe_tag_matrix = mlb.fit_transform(recipes['all_tags'])

    tag_dicts = {}
    for i, recipe_id in enumerate(recipes['id']):
        tag_dicts[recipe_id] = {tag: int(recipe_tag_matrix[i, j]) for j, tag in enumerate(mlb.classes_)}

    return tag_dicts


class ChatData:
    def __init__(self, num_users=5):
        self.num_users = num_users
        self.collected_tags = {}
        self.collected_tags_rate_count = {}
        self.finished = False
        self.channel = None
        self.manual_tag_collect_stop = False
        self.recommended_recipes = []

        self.special_tags = ['occasion', 'easy', 'main-dish', 'equipment', 'number-of-servings']
        self.time_tags = ['60-minutes-or-less', '30-minutes-or-less', '15-minutes-or-less', '1-day-or-more']
        self.country_tags = ['north-american', 'european', 'asian', 'american', 'south-west-pacific']
        self.dietary_tags = ['low-cholesterol', 'meat', 'vegetables', 'dietary', 'low-carb', 'pasta-rice-and-grains']

        self.recipe_tag_matrix = preload()

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

    def get_finished(self):
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
