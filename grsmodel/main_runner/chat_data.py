import discord


class ChatData:
    def __init__(self):
        self.collected_tags = {}
        self.collected_tags_rate_count = {}
        self.finished = False
        self.channel = None
        self.manual_tag_collect_stop = False

    def add_tag(self, user_id, tag, rating):
        if user_id not in self.collected_tags:
            self.collected_tags[user_id] = {}
        self.collected_tags[user_id][tag] = rating

    def get_tag(self, user_id, tag):
        return self.collected_tags.get(user_id, {}).get(tag, 0)

    def get_finished(self):
        return self.finished

    def set_channel(self, channel: discord.Message.channel):
        self.channel = channel

    def get_channel(self):
        return self.channel

    def set_manual_tag_collect_stop(self, stop: bool):
        self.manual_tag_collect_stop = stop

    def get_manual_tag_collect_stop(self):
        return self.manual_tag_collect_stop
