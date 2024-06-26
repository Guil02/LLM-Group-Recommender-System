from discord.ui import Button, View
import discord

from grsmodel.main_runner.chat_data import ChatData


class TimeTagRating(View):
    def __init__(self, chat_data: ChatData):
        super().__init__(timeout=None)
        self.chat_data = chat_data
        self.member_count = 0
        self.msg = None
        self.user_rated = {}
        self.tag_names = ['15 minutes or less', '30 minutes or less', '60 minutes or less', '1 day or more']

    @discord.ui.button(label="15 minutes", style=discord.ButtonStyle.secondary, custom_id="1")
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.evaluate_time(interaction, 1)

    @discord.ui.button(label="30 minutes", style=discord.ButtonStyle.secondary, custom_id="2")
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.evaluate_time(interaction, 2)

    @discord.ui.button(label="60 minutes", style=discord.ButtonStyle.secondary, custom_id="3")
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.evaluate_time(interaction, 3)

    @discord.ui.button(label="1 day", style=discord.ButtonStyle.secondary, custom_id="4")
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.evaluate_time(interaction, 4)

    def generate_values(self, choice: int, size=4):
        values = []
        for i in range(size):
            if i == choice:
                values.append(5)
            elif i == (choice - 1) % size or i == (choice + 1) % size:
                values.append(2.5)
            else:
                values.append(1)
        return values

    def evaluated_count(self):
        counter = 0
        for key, value in self.user_rated.items():
            if value == 1:
                counter += 1

        return counter

    async def evaluate_time(self, interaction: discord.Interaction, chosen: int):
        user_id = interaction.user.id
        if self.user_rated.get(user_id, 0) == 1:
            await interaction.response.defer()
            return

        valuations = self.generate_values(chosen)

        for index, tag in enumerate(self.tag_names):
            current_value = self.chat_data.get_tag(user_id, tag)
            if current_value == 0:
                self.chat_data.add_tag(user_id, tag, valuations[index])
                if user_id not in self.chat_data.collected_tags_rate_count:
                    self.chat_data.collected_tags_rate_count[user_id] = {}
                self.chat_data.collected_tags_rate_count[user_id][tag] = 1
            else:
                self.chat_data.collected_tags_rate_count[user_id][tag] += 1
                self.chat_data.add_tag(user_id, tag,
                                       (current_value * (self.chat_data.collected_tags_rate_count[user_id][tag] - 1) +
                                        valuations[index]) /
                                       self.chat_data.collected_tags_rate_count[user_id][tag])

            self.user_rated[user_id] = 1

        await self.msg.edit(content=f'What is your preferred tag? be careful, you cannot change your answer.'
                                    f'\n {self.evaluated_count()}/{self.chat_data.get_num_users()} have rated so far',
                            view=self)
        if self.evaluated_count() == self.chat_data.get_num_users():
            await self.msg.edit(content='Thank you for your ratings!', view=None)
            self.stop()
        else:
            await interaction.response.defer()

    async def start_rating(self):
        self.msg: discord.Message = await (self.chat_data
                                           .get_channel()
                                           .send(f'What is your preferred tag? '
                                                 f'be careful, you cannot change your answer.', view=self))
        await self.wait()
        return self.chat_data
