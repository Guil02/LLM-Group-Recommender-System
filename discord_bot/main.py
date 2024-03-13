from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import logging
from datetime import datetime

if not os.path.exists('log'):
    os.mkdir('log')

formatted_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logging.basicConfig(level=logging.INFO, filename=f'log/discord_bot-{formatted_date}.log', filemode='w')

# LOAD THE TOKEN
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# SETUP BOT
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)


# MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        logging.info(response)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# HANDLING STARTUP FOR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')


# HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author.name)
    user_message: str = message.content
    channel: str = str(message.channel.name)

    logging.info(f'[{datetime.now()}][{channel}] {username}: "{user_message}"')
    print(f'[{datetime.now()}][{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


# MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
