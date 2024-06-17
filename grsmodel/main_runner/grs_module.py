from abc import ABC, abstractmethod
from discord import Client


class GrsModule(ABC):
    @abstractmethod
    def execute_module(self, bot: Client):
        pass
