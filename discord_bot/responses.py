from random import choice, randint
from gemini import Gemini


def get_response(user_input: str, use_gemini: bool = False, gemini_model: Gemini = None) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'I am a bot, I cannot respond to nothing.'
    elif use_gemini and lowered.startswith('!gemini'):
        return gemini_model.generate_text(user_input[8:])
    elif not use_gemini and lowered.startswith('!gemini'):
        return 'Gemini is not enabled.'
    elif 'hello' in lowered:
        return 'Hello!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1, 6)}'
    else:
        return choice(['I do not understand...',
                       'What are you talking about?',
                       'Do you mind rephrasing that?'])
