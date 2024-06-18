from grsmodel.main_runner.grs_module import GrsModule
from grsmodel.module_factory.module_creator import ModuleCreator
from discord import Intents, Client
from discord.ext import commands
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Final

if not os.path.exists('log'):
    os.mkdir('log')

formatted_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logging.basicConfig(level=logging.INFO, filename=f'log/discord_bot-{formatted_date}.log', filemode='w')

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
USE_GEMINI: Final[bool] = False if os.getenv('USE_GEMINI') is None else os.getenv('USE_GEMINI')
logging.info(f"{USE_GEMINI = }")

modes = ['chat', 'aggregation', 'recommendation']
module_creator: ModuleCreator = ModuleCreator()

for mode in modes:
    current_step: GrsModule = module_creator.factory(mode)
    current_step.execute_module(client)
