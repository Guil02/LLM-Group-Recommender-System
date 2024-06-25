from discord.ui import Button, View
import discord

from grsmodel.main_runner.chat_data import ChatData


class TimeTagRating(View):
    def __init(self, chat_data: ChatData):
        super().__init__(timeout=None)
        self.chat_data = chat_data
        self.member_count = 0
        self.msg = None
        self.user_rated = {}

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

    async def evaluate_time(self, interaction: discord.Interaction, chosen: int):
        user_id = interaction.user.id
        if self.user_rated.get(user_id, 0) == 1:
            await interaction.response.defer()
            return
