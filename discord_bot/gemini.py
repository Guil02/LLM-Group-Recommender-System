import vertexai
from vertexai.generative_models import GenerativeModel, Part
from dotenv import load_dotenv
from typing import Final
import os

load_dotenv()
PROJECT_ID: Final[str] = os.getenv('PROJECT_ID')
PROJECT_LOCATION: Final[str] = os.getenv('PROJECT_LOCATION')


class Gemini:
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel("gemini-1.0-pro")

    def generate_text(self, input_text: str) -> str:
        response = self.model.generate_content([input_text])
        return response.text
