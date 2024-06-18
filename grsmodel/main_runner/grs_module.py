from abc import ABC, abstractmethod
from discord import Client


class GrsModule(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute_module(self, bot: Client, *args, **kwargs):
        pass
