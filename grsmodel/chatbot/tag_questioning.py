from discord.ui import Button, View
import discord
import re
import ast

from grsmodel.chatbot.gemini import Gemini
from grsmodel.main_runner.chat_data import ChatData


def extract_tag_list_re(message: str):
    match = re.search(r"\[.*?\]", message)
    if match:
        extracted_list = ast.literal_eval(match.group())
        return extracted_list
    return []


class TagQuestioning(View):
    def __init__(self, chat_data: ChatData, client: discord.Client, gemini: Gemini):
        super().__init__(timeout=None)
        self.chat_data = chat_data
        self.client = client
        self.gemini = gemini

    async def start_questioning(self, unique_tags: list):
        await self.chat_data.get_channel().send("Is there any specific interest you have in mind?")

        def check(m):
            return m.channel == self.chat_data.get_channel()

        done = False
        suggestions = []
        while not done:
            msg = await self.client.wait_for('message', check=check)
            done = msg.content.startswith('StopQuestioning')
            if not done:
                suggestions.append(msg.content)

        chosen_tags = []
        query = '\n '.join(suggestions)

        gemini_query = ('the users sent us all these messages: ' + query +
                        ' these are all the possible tags: ' + str(unique_tags) +
                        'please retrieve from the possible which ones are mentioned in the user\'s message'
                        'and return them in the following format [\'tag1\', \'tag2\', \'tag3\'] please only return'
                        'this list and nothing else. keep the list simple')

        results = self.gemini.generate_text(gemini_query)
        chosen_tags.extend(extract_tag_list_re(results))
        self.chat_data.add_chosen_tags(chosen_tags)
        return self.chat_data
