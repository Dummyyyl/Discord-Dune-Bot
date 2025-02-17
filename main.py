from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, File
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message empty because intents were not enabled probably)')
        return
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if response is None:
            return  # Ignore the message if no response is generated
        if response == "wallets.xlsx":
            await message.channel.send(file=File(response))
            os.remove(response)
        else:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        await message.channel.send(f'Error: {e}')

@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'{username} in {channel} said: {user_message}')
    await send_message(message, user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()