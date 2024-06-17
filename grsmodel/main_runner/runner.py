from grsmodel.main_runner.grs_module import GrsModule
from grsmodel.module_factory.module_creator import ModuleCreator
from discord import Intents, Client
from discord.ext import commands

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.reactions = True
client: Client = commands.Bot(command_prefix='!', intents=intents)

modes = ['chat', 'aggregation', 'recommendation']
module_creator: ModuleCreator = ModuleCreator()

for mode in modes:
    current_step: GrsModule = module_creator.factory(mode)
    current_step.execute_module(client)
