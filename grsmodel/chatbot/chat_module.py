from grsmodel.chatbot.time_tag_rating import TimeTagRating
from grsmodel.main_runner.chat_data import ChatData
from grsmodel.main_runner.grs_module import GrsModule
from discord import Client, Message
from grsmodel.chatbot.gemini import Gemini
from grsmodel.chatbot.tag_rating import TagRating
from grsmodel.chatbot.tag_questioning import TagQuestioning
import ast


class ChatModule(GrsModule):
    def __init__(self):
        super().__init__()

    async def execute_module(self, bot: Client, *args, **kwargs):
        print('Chat module is running')
        chat_data: ChatData = kwargs['chat_data']
        gemini: Gemini = kwargs['gemini']

        unique_tags = chat_data.recipes['all_tags'].explode().unique()
        questioning = TagQuestioning(chat_data, bot, gemini)
        chat_data = await questioning.start_questioning(unique_tags)
        del questioning

        special_tags = chat_data.special_tags
        country_tags = chat_data.country_tags
        dietary_tags = chat_data.dietary_tags
        all_tags = []
        all_tags.extend(special_tags)
        all_tags.extend(country_tags)
        all_tags.extend(dietary_tags)

        for tag in chat_data.chosen_tags:
            rating = TagRating(chat_data)
            chat_data = await rating.send_rating(tag)
            del rating

        if chat_data.get_model_loops() == 0:
            rating = TimeTagRating(chat_data)
            chat_data = await rating.start_rating()
            del rating

        for tag in all_tags:
            rating = TagRating(chat_data)
            chat_data = await rating.send_rating(tag)
            del rating

        return chat_data
