from grsmodel.main_runner.grs_module import GrsModule
from discord import Client


class RecommendationModule(GrsModule):

    def __init__(self):
        super().__init__()

    def execute_module(self, bot: Client, *args, **kwargs):
        pass
