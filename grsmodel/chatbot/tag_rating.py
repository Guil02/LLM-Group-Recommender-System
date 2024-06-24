from discord.ui import Button, View
import discord

from grsmodel.main_runner.chat_data import ChatData


class TagRating(View):
    def __init__(self, chat_data: ChatData):
        super().__init__(timeout=None)
        self.chat_data = chat_data
        self.tag = None
        self.member_count = 0
        self.msg = None
        self.user_rated = {}

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, custom_id="1")
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_tag(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, custom_id="2")
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_tag(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, custom_id="3")
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_tag(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary, custom_id="4")
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_tag(interaction, 4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, custom_id="5")
    async def button_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_tag(interaction, 5)

    def evaluated_count(self):
        counter = 0
        for key, value in self.user_rated.items():
            if value == 1:
                counter += 1

        return counter

    async def rate_tag(self, interaction: discord.Interaction, rating: int):
        user_id = interaction.user.id
        if self.user_rated.get(user_id, 0) == 1:
            await interaction.response.defer()
            return

        current_value = self.chat_data.get_tag(user_id, self.tag)
        if current_value == 0:
            self.chat_data.add_tag(user_id, self.tag, rating)
            if user_id not in self.chat_data.collected_tags_rate_count:
                self.chat_data.collected_tags_rate_count[user_id] = {}
            self.chat_data.collected_tags_rate_count[user_id][self.tag] = 1
        else:
            self.chat_data.collected_tags_rate_count[user_id][self.tag] += 1
            self.chat_data.add_tag(user_id, self.tag,
                                   (current_value * (self.chat_data.collected_tags_rate_count[user_id][
                                                         self.tag] - 1) + rating) /
                                   self.chat_data.collected_tags_rate_count[user_id][
                                       self.tag])

        self.user_rated[user_id] = 1

        await self.msg.edit(content=f'How would you rate the tag {self.tag}? be careful, you cannot change your answer.'
                                    f'\n {self.evaluated_count()}/{self.chat_data.get_num_users()} have rated so far',
                            view=self)

        if self.evaluated_count() == self.chat_data.get_num_users():
            await self.msg.edit(content='Thank you for your ratings!', view=None)
            self.stop()
        else:
            await interaction.response.defer()

    async def send_rating(self, tag: str):
        self.tag = tag

        self.msg: discord.Message = await (self.chat_data
                                           .get_channel()
                                           .send(f'How would you rate the tag {tag}? '
                                                 f'be careful, you cannot change your answer.', view=self))
        await self.wait()
        return self.chat_data

    def initialize_rated_users(self):
        for member in self.chat_data.get_channel().members:
            self.user_rated[member.id] = 0
