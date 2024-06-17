from abc import ABC
from grsmodel.chatbot.chat_module import ChatModule
from grsmodel.aggregationbot.aggregation_module import AggregationModule
from grsmodel.recommendationbot.recommendation_module import RecommendationModule


class ModuleCreator(ABC):
    def factory(self, module_type: str):
        if module_type == "chat":
            return ChatModule()
        elif module_type == "aggregation":
            return AggregationModule()
        elif module_type == "recommendation":
            return RecommendationModule()
        else:
            raise ValueError("Invalid module type")
