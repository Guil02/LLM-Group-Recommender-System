from grsmodel.main_runner.grs_module import GrsModule
from grsmodel.module_factory.module_creator import ModuleCreator
from discord import Intents, Client, Message, NotFound, Reaction, User
from discord.ext import commands
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Final
from grsmodel.chatbot.gemini import Gemini
from chat_data import ChatData

if not os.path.exists('log'):
    os.mkdir('log')

formatted_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logging.basicConfig(level=logging.INFO, filename=f'log/discord_bot-{formatted_date}.log', filemode='w')

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
else:
    gemini = None

# SETUP BOT
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.reactions = True  # NOQA
intents.members = True  # NOQA
client: Client = commands.Bot(command_prefix='!', intents=intents)

module_modes = ['chat', 'aggregation', 'recommendation']
module: GrsModule = None
module_creator: ModuleCreator = ModuleCreator()
current_mode = 'chat'


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author.name)
    user_message: str = message.content
    channel: str = str(message.channel.name)

    logging.info(f'[{datetime.now()}][{channel}] {username}: "{user_message}"')

    if not user_message.startswith('!startGRS'):
        return

    # Extract the number of users after '!startGRS-' if it exists
    match = re.match(r'!startGRS-(\d+)', user_message)
    num_users = int(match.group(1)) if match else None

    if num_users is not None:
        logging.info(f'Setting number of users: {num_users}')
        chat_data = ChatData(num_users)
    else:
        logging.info(f'Setting default number of users: 5')
        chat_data = ChatData()

    global module
    global current_mode

    chat_data.set_channel(message.channel)

    done = False
    while not done:
        module = module_creator.factory(current_mode)
        chat_data = await module.execute_module(client, message, gemini=gemini, chat_data=chat_data)

        # current_mode = module_modes[1]
        # logging.info(f'Current mode: {current_mode}')
        # module = module_creator.factory(current_mode)
        # chat_data = await module.execute_module(client, message, gemini=gemini, chat_data=chat_data,
        #                                         aggregation_method='average')
        #
        # current_mode = module_modes[2]
        # logging.info(f'Current mode: {current_mode}')
        # module = module_creator.factory(current_mode)
        # chat_data = await module.execute_module(client, message, gemini=gemini, chat_data=chat_data)
        # done = chat_data.get_finished()


def main():
    client.run(TOKEN)


if __name__ == '__main__':
    main()
