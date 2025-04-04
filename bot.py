import asyncio
import random
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telebot import TeleBot
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError

# List of session strings (replace with your actual session strings)
session_strings = [
    "1BZWaqwUAUE7AFkpH8rQhjrOcz4zQ86O5oiUGotqbNOHYnUEUFcWSFNtIyW2-M2EUxK3EnTGeQGETXS-_No4W6ALv8PGALvVTn3bOEXQslP6CYQKpTI48iJkL9ybAKZ4PMLzkYPCbib5hllldOXM17bsZuU0o9fndeyGKZbnfrTA7aGNR9NlgQMbL1HusNIDMYccfkT20RLTkuVQkxCkTQ0iaQof5ct8rfMnQPwi3E5P8MP0PkTAIh3m_1yY2n_0yYeHzuF5kBKJxbEC2MWtA-kq7_bPNRT9CctT4ja9fM9JPC0NTDN9EPlCSJjZdy7QL_Meokg-xPMmy8pTufF8HxIkhgjgVz7I=",
    # Add 9 more session strings here... (Leave empty strings if you don't have all 10 sessions yet)
    "", "", "", "", "", "", "", "", ""
]

BOT_TOKEN = "6590125561:AAEK-yex0S4eaAnx6d0VbrPxXCGcpeMCiYc" # Replace with your bot token
bot = TeleBot(BOT_TOKEN)

emojis = ['❤️', '😍', '🥳', '💯', '🔥', '👍', '☺️', '🥰', '😱', '🤯']

async def react_to_message(client, chat, message_id):
    try:
        random_emoji = random.choice(emojis)
        await client(SendReactionRequest(
            peer=chat,
            msg_id=message_id,
            reaction=[ReactionEmoji(emoticon=random_emoji)]
        ))
        logging.info(f"Reacted with {random_emoji} using session: {client.session.user.username if client.session.user else 'unknown'}")
    except FloodWaitError as e:
        logging.warning(f"FloodWaitError: {e}. Waiting...")
        await asyncio.sleep(e.seconds)
        await react_to_message(client, chat, message_id)
    except SessionPasswordNeededError as e:
        logging.error(f"2FA required! {e}")
    except RPCError as e:
        logging.error(f"RPC Error: {e}")
    except Exception as e:
        logging.error(f"Error reacting to message: {e}")


async def handle_message(message):
    tasks = []
    for i, session_string in enumerate(session_strings):
        if session_string: # Skip if the session string is empty
            try:
                client_name = f"client_{i+1}"
                async with TelegramClient(client_name, api_id=0, api_hash=0, session=session_string) as client:
                    tasks.append(asyncio.create_task(react_to_message(client, message.chat.id, message.message_id)))
            except Exception as e:
                logging.error(f"Error with session {i+1}: {e}")

    await asyncio.gather(*tasks)


@bot.message_handler(func=lambda message: True)
def on_message(message):
    asyncio.run(handle_message(message))

bot.polling()
