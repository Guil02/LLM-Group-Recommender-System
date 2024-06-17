from grsmodel.main_runner.grs_module import GrsModule
from discord import Client


class ChatModule(GrsModule):
    def __init__(self):
        super().__init__()
        self._collected_tags = {}

    def execute_module(self, bot: Client):
        pass
