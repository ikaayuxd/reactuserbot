import asyncio
import random
import logging
from telethon import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from telebot import TeleBot
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError

# List of session strings (REPLACE WITH YOUR ACTUAL SESSION STRINGS)
session_strings = [
    "1BZWaqwUAUE7AFkpH8rQhjrOcz4zQ86O5oiUGotqbNOHYnUEUFcWSFNtIyW2-M2EUxK3EnTGeQGETXS-_No4W6ALv8PGALvVTn3bOEXQslP6CYQKpTI48iJkL9ybAKZ4PMLzkYPCbib5hllldOXM17bsZuU0o9fndeyGKZbnfrTA7aGNR9NlgQMbL1HusNIDMYccfkT20RLTkuVQkxCkTQ0iaQof5ct8rfMnQPwi3E5P8MP0PkTAIh3m_1yY2n_0yYeHzuF5kBKJxbEC2MWtA-kq7_bPNRT9CctT4ja9fM9JPC0NTDN9EPlCSJjZdy7QL_Meokg-xPMmy8pTufF8HxIkhgjgVz7I=",
    "", "", "", "", "", "", "", "", "" # Add more or leave empty if you don't have 10 sessions.
]

BOT_TOKEN = "6590125561:AAEK-yex0S4eaAnx6d0VbrPxXCGcpeMCiYc" # REPLACE WITH YOUR BOT TOKEN
bot = TeleBot(BOT_TOKEN)

logging.basicConfig(level=logging.INFO) # Set logging level for better debugging

async def send_simple_message(client, chat, message):
    try:
        await client(SendMessageRequest(
            peer=chat,
            message=message
        ))
        logging.info(f"Sent message '{message}' using client: {client.session.user.username if client.session.user else 'unknown'}")
    except FloodWaitError as e:
        logging.warning(f"FloodWaitError: {e}. Waiting...")
        await asyncio.sleep(e.seconds)
        await send_simple_message(client, chat, message)
    except SessionPasswordNeededError as e:
        logging.error(f"2FA required! {e}")
    except RPCError as e:
        logging.error(f"RPC Error: {e}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")



async def handle_message(message):
    tasks = []
    for i, session_string in enumerate(session_strings):
        if session_string:
            try:
                client_name = f"client_{i+1}"
                async with TelegramClient(client_name, api_id=0, api_hash=0, session=session_string) as client:
                    tasks.append(asyncio.create_task(send_simple_message(client, message.chat.id, "Hello from session " + str(i+1))))
            except Exception as e:
                logging.error(f"Error with session {i+1}: {e}")

    await asyncio.gather(*tasks)


@bot.message_handler(func=lambda message: True)
def on_message(message):
    asyncio.run(handle_message(message))

bot.polling()
