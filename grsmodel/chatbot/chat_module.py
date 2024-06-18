from grsmodel.main_runner.grs_module import GrsModule
from discord import Client
from gemini import Gemini


class ChatModule(GrsModule):
    def __init__(self, gemini_project_id, gemini_location):
        super().__init__()
        self.gemini = Gemini(gemini_project_id, gemini_location)
        self._collected_tags = {}

    def execute_module(self, bot: Client, *args, **kwargs):
        pass
