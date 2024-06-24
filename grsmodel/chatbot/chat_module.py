from grsmodel.main_runner.chat_data import ChatData
from grsmodel.main_runner.grs_module import GrsModule
from discord import Client, Message
from grsmodel.chatbot.gemini import Gemini
from grsmodel.chatbot.tag_rating import TagRating
import os

class ChatModule(GrsModule):
    def __init__(self):
        super().__init__()

    async def execute_module(self, bot: Client, *args, **kwargs):
        print('Chat module is running')
        chat_data: ChatData = kwargs['chat_data']
        tags = ['test1', 'test2', 'test3']
        special_tags = ['occasion', 'easy', 'main-dish', 'equipment', 'number-of-servings']

        # TODO add pca selection of categories
        for tag in tags:
            rating = TagRating(chat_data)
            chat_data = await rating.send_rating(tag)
            del rating

        return chat_data
