from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, NotFound, Reaction, User
from responses import get_response
import logging
from datetime import datetime
from gemini import Gemini

if not os.path.exists('log'):
    os.mkdir('log')

formatted_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logging.basicConfig(level=logging.INFO, filename=f'log/discord_bot-{formatted_date}.log', filemode='w')

# LOAD THE TOKEN
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
USE_GEMINI: Final[bool] = False if os.getenv('USE_GEMINI') is None else os.getenv('USE_GEMINI')
logging.info(f"{USE_GEMINI = }")

if USE_GEMINI:
    PROJECT_ID: Final[str] = os.getenv('PROJECT_ID')
    PROJECT_LOCATION: Final[str] = os.getenv('PROJECT_LOCATION')
    if PROJECT_ID is None or PROJECT_LOCATION is None:
        raise ValueError('Project ID and Location must be set if USE_GEMINI is True')
    gemini = Gemini(PROJECT_ID, PROJECT_LOCATION)
    response = gemini.generate_text(
        "You are now a recommender system that is going to give advise on food choice to a group, you do not have to "
        "respond to every prompt, I want you to internalize all the information you receive and I want you to respond "
        "when you feel like you have enough information to make a recommendation. I do not want you to invent any "
        "scenario, the prompts with information will come in one by one because they are fed to you from a group "
        "chat. the format of a message will be <Name>: <message>. Please respond to this message to affirm that you "
        "understand this.")
    print(response)
    logging.info(response)

# SETUP BOT
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.reactions = True
client: Client = Client(intents=intents)

# TODO: find better reactions for rating
# Define the allowed reactions
ALLOWED_REACTIONS = ['👍', '👎', '😂', '😮', '❤️'] # Just examples

# MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message, USE_GEMINI, gemini) if USE_GEMINI else get_response(user_message)
        logging.info(response)

        # if the response is longer than 2000 characters, split it into multiple messages
        if len(response) > 2000:
            while len(response) > 2000:
                await message.author.send(response[:2000]) if is_private else await message.channel.send(
                    response[:2000])
                response = response[2000:]
            await message.author.send(response) if is_private else await message.channel.send(response)
        else:
            await message.author.send(response) if is_private else await message.channel.send(response)
        
        # TODO: Reactions should only appear on specific messages, such as recommendations
        # Add allowed reactions to the bot's message
        for reaction in ALLOWED_REACTIONS:
            await message.add_reaction(reaction)
        
    except Exception as e:
        print(e)

# FUNCTION TO GET REACTIONS FROM A SPECIFIC MESSAGE
async def get_reactions_from_message(channel_id: int, message_id: int):
    channel = client.get_channel(channel_id)
    try:
        message = await channel.fetch_message(message_id)
        reactions = message.reactions
        reaction_data = []

        for reaction in reactions:
            users = await reaction.users().flatten()
            for user in users:
                reaction_data.append((user.name, str(reaction.emoji)))

        return reaction_data
    except NotFound:
        print("Message not found.")
        return []

# HANDLING STARTUP FOR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')

    # TODO: fix these parameters and find a way to use the reactions
    # Example usage of reactions
    channel_id = 123456789012345678  # Replace with your channel ID
    message_id = 987654321098765432  # Replace with your message ID
    reaction_data = await get_reactions_from_message(channel_id, message_id)
    for user, reaction in reaction_data:
        print(f'User: {user}, Reaction: {reaction}')

# HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author.name)
    user_message: str = message.content
    channel: str = str(message.channel.name)

    logging.info(f'[{datetime.now()}][{channel}] {username}: "{user_message}"')
    print(f'[{datetime.now()}][{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


@client.event
async def on_reaction_add(reaction: Reaction, user: User) -> None:
    if reaction.message.author == client.user:
        if str(reaction.emoji) not in ALLOWED_REACTIONS:
            await reaction.remove(user)

@client.event
async def on_reaction_remove(reaction: Reaction, user: User) -> None:
    if reaction.message.author == client.user:
        if str(reaction.emoji) not in ALLOWED_REACTIONS:
            await reaction.remove(user)

# MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
