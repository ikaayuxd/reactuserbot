import asyncio
import random
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telebot import TeleBot


logging.basicConfig(level=logging.INFO)

# Load Telegram sessions from config.txt
def load_sessions():
    sessions = []
    try:
        with open('config.txt', 'r') as f:
            for line in f:
                session_path = line.strip()
                sessions.append(session_path)
    except FileNotFoundError:
        logging.error("config.txt not found. Please create it with paths to your session files.")
        return []
    return sessions

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
    except Exception as e:
        logging.error(f"Error reacting to message: {e}")
        # Add more sophisticated error handling here (e.g., retry mechanism)


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
