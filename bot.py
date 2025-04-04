import asyncio
import random
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telebot import TeleBot
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError

#Your API details. DO NOT HARDCODE THESE IN PRODUCTION CODE! Use environment variables instead.
API_ID = 7630000
API_HASH = "f70361ddf4ec755395b4b6f1ab2d4fae"


logging.basicConfig(level=logging.INFO)


# Bot Initialization
BOT_TOKEN = "6590125561:AAEK-yex0S4eaAnx6d0VbrPxXCGcpeMCiYc" # Replace with your bot token
bot = TeleBot(BOT_TOKEN)

# Reaction Emojis
emojis = ['❤️', '😍', '🥳', '💯', '🔥', '👍', '☺️', '🥰', '😱', '🤯']

async def react_to_message(client, chat, message_id):
    try:
        random_emoji = random.choice(emojis)
        await client(SendReactionRequest(
            peer=chat,
            msg_id=message_id,
            reaction=[ReactionEmoji(emoticon=random_emoji)]
        ))
        logging.info(f"Reacted with {random_emoji} using client: {client.session.user.username if client.session.user else 'unknown'}")
    except FloodWaitError as e:
        logging.warning(f"FloodWaitError: {e}. Waiting...")
        await asyncio.sleep(e.seconds) # Wait before retrying
        await react_to_message(client, chat, message_id) # Retry the reaction
    except SessionPasswordNeededError as e:
        logging.error(f"2FA required! {e}")
        # Handle 2FA here (you'll need to implement 2FA code input)
    except RPCError as e:
        logging.error(f"RPC Error: {e}. Check your connection.")
    except Exception as e:
        logging.error(f"Error reacting to message: {e}")


async def handle_message(message):
    tasks = []
    for i in range(10): #Creating 10 clients.
        try:
            client_name = f"client_{i+1}"
            async with TelegramClient(client_name, API_ID, API_HASH) as client:
                await client.start() #Start the client, handles OTP if necessary.
                tasks.append(asyncio.create_task(react_to_message(client, message.chat.id, message.message_id)))
        except Exception as e:
            logging.error(f"Error initializing client {i+1}: {e}")

    await asyncio.gather(*tasks)


@bot.message_handler(func=lambda message: True) # Handle all messages
def on_message(message):
    asyncio.run(handle_message(message))


bot.polling()
