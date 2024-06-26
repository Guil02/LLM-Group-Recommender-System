import asyncio
import discord
from discord.ui import View

from grsmodel.main_runner.grs_module import GrsModule
from discord import Client

recipe_states = {}


class RecommendationModule(GrsModule):

    def __init__(self):
        super().__init__()
        self.num_users = 5
        self.chat_data = None
        self.max_attempts = 3  # has to match the number of best recipes recommended
        self.lock = asyncio.Lock()

    async def execute_module(self, bot: Client, *args, **kwargs):
        self.chat_data = kwargs.get('chat_data')
        self.num_users = self.chat_data.num_users
        message = kwargs.get('message')

        recipes = self.chat_data.recipes
        attempt = 0
        while attempt < self.max_attempts:
            recipe_recommended = self.chat_data.get_recommended_recipes()[attempt]
            print(f'RECOMMENDING RECIPE {recipe_recommended}')
            recipe = recipes.loc[recipes['id'] == recipe_recommended, :]

            print('CREATING APPROVAL VIEW')
            approval_view = ApprovalView(message, self)
            recipe_states[message.id] = {
                'recipe_id': recipe['id'],  # Accessing the ID from the pandas DataFrame
                'approved': False,
                'ratings': {str(i): 0 for i in range(1, 6)},
                'voters': {},
                'approval_view': approval_view,
            }

            print('BEFORE LOCK')
            async with self.lock:
                await self.recommend_recipe(message, recipe, approval_view)
                await self.lock.acquire()

            print('AFTER LOCK')
            if recipe_states[message.id]['approved']:  # Recipe was accepted
                self.chat_data.set_finished(True)
                return self.chat_data
            else:  # Recipe was rejected, attempt another recommendation
                self.chat_data.set_finished(False)
                attempt += 1

        return self.chat_data

    async def recommend_recipe(self, message, recipe, view):
        ingredients = [f"{i}. {ing}" for i, ing in enumerate(recipe['ingredients_tags'])]
        steps = [f"{i}. {step}" for i, step in enumerate(recipe['steps'])]
        details = (
                f"**Name:**\n{recipe['name']}** 🍽️\n\n"
                f"**Description:**\n{recipe['description'].iloc[0]} 📖\n\n"
                f"**Time to cook:** {recipe['minutes'].iloc[0]} minutes ⏲️\n\n"
                f"**Ingredients:** 🛒\n" + '\n'.join(ingredients) + "\n\n"
                f"**Steps:** 👩‍🍳\n" + '\n'.join(steps) + "\n\n"
                "Please accept or reject this recipe:"
        )

        await message.channel.send(details, view=view)

    async def handle_rejection(self, message_id):
        state = recipe_states.get(message_id)

        if state:
            current_attempt = state.get('attempt', 0)
            if current_attempt < self.max_attempts:
                state['attempt'] = current_attempt + 1
                await state['approval_view'].message.channel.send(f"Rejected, attempt #{state['attempt'] + 1}.")
            else:
                await state['approval_view'].message.channel.send("All recipes have been rejected. End process.")

        # Signal to execute_module to try recommending another recipe
        state['approved'] = False
        self.lock.release()

    async def handle_acceptance(self, message_id):
        state = recipe_states.get(message_id)
        if state:
            rating_view = RatingView(state['approval_view'].message, self)
            state['approval_view'] = rating_view
            await rating_view.message.channel.send("The recipe has been accepted. Please rate the recipe.",
                                                   view=rating_view)

    async def finalize_ratings(self, message_id):
        state = recipe_states.get(message_id)
        if state:
            total_ratings = sum(state['ratings'].values())
            avg_rating = sum(int(key) * value for key, value in state['ratings'].items()) / total_ratings
            await state['approval_view'].message.channel.send(
                f"The recipe has been accepted with an average rating of {avg_rating:.2f} stars based on {total_ratings} ratings.")

        state['approved'] = True
        self.lock.release()


class ApprovalView(View):
    def __init__(self, message, module):
        super().__init__(timeout=None)
        self.message = message
        self.message_id = message.id
        self.module = module
        self.approve_count = 0
        self.reject_count = 0

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, custom_id="approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.approve_count += 1
        state = recipe_states.get(self.message_id)
        if self.approve_count >= self.module.num_users:
            state['approved'] = True
            await interaction.response.send_message("Thank you for your approval!", ephemeral=True)
            await self.module.handle_acceptance(self.message_id)
        else:
            await interaction.response.send_message(
                f"Approval received ({self.approve_count}/{self.module.num_users}).", ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger, custom_id="reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.reject_count += 1
        state = recipe_states.get(self.message_id)
        state['approved'] = False
        await interaction.response.send_message("Thank you for your feedback!", ephemeral=True)
        await self.module.handle_rejection(self.message_id)


class RatingView(View):
    def __init__(self, message, module):
        super().__init__(timeout=None)
        self.message = message
        self.message_id = self.message.id
        self.module = module

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

            if total_ratings >= self.module.num_users:
                await self.module.finalize_ratings(self.message_id)
