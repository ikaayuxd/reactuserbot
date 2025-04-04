import asyncio
import random
import logging
import importlib
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telebot import TeleBot
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError


logging.basicConfig(level=logging.INFO)

# Function to load sessions from config.py
def load_sessions():
    try:
        config = importlib.import_module('config') # Import config.py
        sessions = []
        for i in range(1, 11): # Adjust the range if you have more sessions
            session_var_name = f'S{i}'
            session_path = getattr(config, session_var_name, None) # Handle missing variables gracefully.
            if session_path: # Check if the variable is defined and not empty
                sessions.append(session_path)
        return sessions
    except ImportError:
        logging.error("config.py not found or import failed. Please create it with your session paths.")
        return []
    except AttributeError:
        logging.error(
            "One or more session variables (S1, S2, etc.) are missing or not properly defined in config.py."
        )
        return []
    except Exception as e:
        logging.exception(f"An unexpected error occurred while loading sessions: {e}")
        return []



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
        logging.info(f"Reacted with {random_emoji} using session: {client.session.user.username if client.session.user else 'unknown'}")
    except FloodWaitError as e:
        logging.warning(f"FloodWaitError: {e}. Waiting...")
        await asyncio.sleep(e.seconds) # Wait before retrying
        await react_to_message(client,chat, message_id) #Retry the reaction
    except SessionPasswordNeededError as e:
        logging.error(f"2FA required for session! {e}")
        # Handle 2FA here (you'll need to implement 2FA code input)

    except RPCError as e:
        logging.error(f"RPC Error: {e}. Check your session file.")
    except Exception as e:
        logging.error(f"Error reacting to message: {e}")


async def handle_message(message):
    tasks = []
    sessions = load_sessions()
    if not sessions:
        return

    for session_path in sessions:
        try:
            async with TelegramClient(session_path, 0, 0) as client: # 0,0 because no api_id and api_hash needed
                tasks.append(asyncio.create_task(react_to_message(client, message.chat.id, message.message_id)))
        except Exception as e:
            logging.error(f"Error initializing client for session {session_path}: {e}")

    await asyncio.gather(*tasks)


@bot.message_handler(func=lambda message: True) # Handle all messages
def on_message(message):
    asyncio.run(handle_message(message))

bot.polling()
