from grsmodel.main_runner.grs_module import GrsModule
from grsmodel.module_factory.module_creator import ModuleCreator
from discord import Intents, Client, Message, NotFound, Reaction, User
from discord.ext import commands
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Final
from grsmodel.chatbot.gemini import Gemini

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
client: Client = commands.Bot(command_prefix='!', intents=intents)

module_modes = ['chat', 'aggregation', 'recommendation']
module: GrsModule = GrsModule()
module_creator: ModuleCreator = ModuleCreator()

for mode in module_modes:
    module = module_creator.factory(mode)
    module.execute_module(client, gemini=gemini)
