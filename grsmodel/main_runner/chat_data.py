import discord


class ChatData:
    def __init__(self, num_users=5):
        self.num_users = num_users
        self.collected_tags = {}
        self.collected_tags_rate_count = {}
        self.finished = False
        self.channel = None
        self.manual_tag_collect_stop = False
        self.recommended_recipes = []

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
