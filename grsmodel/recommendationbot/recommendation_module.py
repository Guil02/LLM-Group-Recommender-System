import discord
import pandas as pd
from discord.ui import View

from grsmodel.main_runner.grs_module import GrsModule
from discord import Client

recipe_states = {}

class RecommendationModule(GrsModule):

    def __init__(self):
        super().__init__()
        self.num_users = 5
        self.chat_data = None
        self.message = None

    def execute_module(self, bot: Client, *args, **kwargs):
        """
        Executes the process of a recipe recommendation.

        Parameters:
            bot (Client): The bot client instance to interact with.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
                - message (object): The message object associated with the recommendation start.
                - recipe_id (int): The ID of the recipe to process.

        Returns:
        None
        """
        self.message = kwargs.get('message')
        self.chat_data = kwargs.get('chat_data')

        self.num_users = self.chat_data.num_users

        recipe_recommended = self.chat_data.get_recommended_recipes()[0]
        approval_view = ApprovalView(self.message.id, self)
        recipe_states[self.message.id] = {
            'recipe_id': recipe_recommended['id'],
            'approved': False,
            'ratings': {str(i): 0 for i in range(1, 6)},
            'voters': {},
            'approval_view': approval_view,
        }

        chat_data = self.recommend_recipe(recipe_recommended, approval_view)
        return chat_data

    async def recommend_recipe(self, recipe, view):
        details = (
            f"**{recipe['name']}** 🍽️\n\n"
            f"**Description:**\n{recipe['description']} 📖\n\n"
            f"**Time to cook:** {recipe['minutes']} minutes ⏲️\n\n"
            f"**Ingredients:** 🛒\n" + '\n'.join([f"- {i}" for i in eval(recipe['ingredients_tags'])]) + "\n\n"
            f"**Steps:** 👩‍🍳\n" + '\n'.join([f"{i + 1}. {s}" for i, s in enumerate(eval(recipe['steps']))]) + "\n\n"
            "Please accept or reject this recipe:"
        )

        await self.message.channel.send(details, view=view)
        return self.chat_data

    async def handle_rejection(self):
        state = recipe_states.get(self.message.id)
        if state:
            await state['approval_view'].message.channel.send("The recipe has been rejected.")
            del recipe_states[self.message.id]

    async def handle_acceptance(self):
        state = recipe_states.get(self.message.id)
        if state:
            rating_view = RatingView(self.message.id, self)
            state['approval_view'] = rating_view
            await state['approval_view'].message.channel.send("The recipe has been accepted. Please rate the recipe.", view=rating_view)

    async def finalize_ratings(self):
        state = recipe_states.get(self.message.id)
        if state:
            total_ratings = sum(state['ratings'].values())
            avg_rating = sum(int(key) * value for key, value in state['ratings'].items()) / total_ratings
            await state['approval_view'].message.channel.send(f"The recipe has been accepted with an average rating of {avg_rating:.2f} stars based on {total_ratings} ratings.")
            self.chat_data.set_finished(True)
            del recipe_states[self.message.id]


class ApprovalView(View):
    def __init__(self, message_id, module):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.module = module
        self.approve_count = 0
        self.reject_count = 0
        self.message = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve")
    async def approve_button(self, interaction: discord.Interaction):
        self.approve_count += 1
        state = recipe_states.get(self.message_id)
        if self.approve_count >= self.module.num_users:
            state['approved'] = True
            await interaction.response.send_message("Thank you for your approval!", ephemeral=True)
            await self.module.handle_acceptance(self.message_id)
        else:
            await interaction.response.send_message(f"Approval received ({self.approve_count}/{self.module.num_users}).", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.reject_count += 1
        state = recipe_states.get(self.message_id)
        state['approved'] = False
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
        await self.module.handle_rejection(self.message_id)


class RatingView(View):
    def __init__(self, message_id, module):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.module = module

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, custom_id="1")
    async def button_1(self, interaction: discord.Interaction):
        await self.rate_recipe(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, custom_id="2")
    async def button_2(self, interaction: discord.Interaction):
        await self.rate_recipe(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, custom_id="3")
    async def button_3(self, interaction: discord.Interaction):
        await self.rate_recipe(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary, custom_id="4")
    async def button_4(self, interaction: discord.Interaction):
        await self.rate_recipe(interaction, 4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, custom_id="5")
    async def button_5(self, interaction: discord.Interaction):
        await self.rate_recipe(interaction, 5)

    async def rate_recipe(self, interaction: discord.Interaction, rating: int):
        state = recipe_states.get(self.message_id)
        if state:
            user_id = interaction.user.id
            previous_rating = state['voters'].get(user_id)

            # If the user has already rated, adjust the previous rating
            if previous_rating is not None:
                state['ratings'][str(previous_rating)] -= 1

            # Update with the new rating
            state['ratings'][str(rating)] += 1
            state['voters'][user_id] = rating

            total_ratings = sum(state['ratings'].values())
            avg_rating = sum(int(key) * value for key, value in state['ratings'].items()) / total_ratings

            rating_message = f"**Current average rating:** {avg_rating:.2f} stars based on {total_ratings} ratings."

            if previous_rating is None:
                response_message = "Thank you for rating this recipe!"
            else:
                response_message = "Your rating has been updated!"

            await interaction.response.send_message(f"{response_message}\n\n{rating_message}", ephemeral=True)

            if total_ratings >= self.module.num_users:
                await self.module.finalize_ratings(self.message_id)
