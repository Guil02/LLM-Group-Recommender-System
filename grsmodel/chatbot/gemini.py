import vertexai
from vertexai.generative_models import GenerativeModel, Part
from typing import List


def split_text(text, max_length=2000) -> List[str]:
    words = text.split()
    current_length = 0
    current_chunk = []
    chunks = []

    for word in words:
        word_length = len(word) + 1  # adding 1 for the space or newline
        if current_length + word_length > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += word_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


class Gemini:
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel("gemini-1.0-pro")

    def generate_text(self, input_text: str) -> List[str]:
        response = self.model.generate_content([input_text])
        return split_text(response.text)
