import random

import pandas as pd
from discord import Client
import discord
from discord.ext import commands
from discord.ui import Button, View

# TODO: make sure this is added manually to the parent folder
recipes_df = pd.read_csv("..\\cleaned_recipes_with_country.csv")
recipe_states = {}
RATING_REACTIONS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']


# Function to recommend a recipe
async def recommend_recipe(message, recipe_id: int):
    if recipe_id == -1:     # random recipe
        rand_id = random.randint(0, len(recipes_df))
        recipe_id = recipes_df.iloc[rand_id].id

    if recipe_id not in recipes_df['id'].values:
        await message.channel.send("Recipe not found!")
        return

    recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
    details = (
            f"**{recipe['name']}** 🍽️\n\n"
            f"**Description:**\n{recipe['description']} 📖\n\n"
            f"**Time to cook:** {recipe['minutes']} minutes ⏲️\n\n"
            f"**Ingredients:** 🛒\n" + '\n'.join([f"- {i}" for i in eval(recipe['ingredients_tags'])]) + "\n\n"
            f"**Steps:** 👩‍🍳\n" + '\n'.join([f"{i + 1}. {s}" for i, s in enumerate(eval(recipe['steps']))]) + "\n\n"
            "Please accept or reject this recipe:"
    )

    recipe_states[message.id] = {
        'recipe_id': recipe_id,
        'approved': False,
        'ratings': {str(i): 0 for i in range(1, 6)},
        'voters': {},  # Track users and their ratings
        'approval_view': ApprovalView(message.id),
    }

    await message.channel.send(details, view=recipe_states[message.id]['approval_view'])


class ApprovalView(View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.approve_count = 0
        self.reject_count = 0

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.approve_recipe(interaction)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.reject_recipe(interaction)

    async def approve_recipe(self, interaction: discord.Interaction):
        state = recipe_states.get(self.message_id)
        if state:
            state['approved'] = True
            state['approval_view'].clear_items()
            await interaction.response.send_message("Thank you for your approval!", ephemeral=True)
            self.approve_count += 1
            # TODO: testing purposes.. remove
            # if self.approve_count + self.reject_count == len(interaction.message.mentions):
            if True:
                await self.start_rating(interaction)

    async def reject_recipe(self, interaction: discord.Interaction):
        state = recipe_states.get(self.message_id)
        if state:
            state['approved'] = False
            state['approval_view'].clear_items()
            await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
            self.reject_count += 1
            # TODO: testing purposes.. remove
            # if self.approve_count + self.reject_count == len(interaction.message.mentions):
            if True:
                await self.start_rating(interaction)

    async def start_rating(self, interaction: discord.Interaction):
        state = recipe_states.get(self.message_id)
        if state:
            rating_view = RatingView(self.message_id)
            state['approval_view'] = rating_view
            await interaction.message.edit(view=rating_view)


# Define a view for rating buttons
class RatingView(View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, custom_id="1")
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_recipe(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, custom_id="2")
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_recipe(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, custom_id="3")
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_recipe(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.secondary, custom_id="4")
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.rate_recipe(interaction, 4)

    @discord.ui.button(label="5", style=discord.ButtonStyle.secondary, custom_id="5")
    async def button_5(self, interaction: discord.Interaction, button: discord.ui.Button):
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
