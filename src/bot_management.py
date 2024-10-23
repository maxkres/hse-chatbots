import json
import asyncio
import logging
from aiogram import Bot
from initialize_cluster import simulate_cluster_conversation


with open('data/configs/config.json', 'r') as file:
    BOT_CONFIGS = json.load(file)

GROUP_CHAT_ID = -1002311774343
logging.basicConfig(level=logging.INFO)

async def bot_send_message(bot: Bot, user_id, message_text):
    try:
        await bot.send_message(GROUP_CHAT_ID, message_text)
        print(f"[DEBUG] Bot {user_id}: Sending message: {message_text}")
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

async def main():
    print("[DEBUG] Starting main bot process.")
    bots = {config['user_id']: Bot(token=config['api_token']) for config in BOT_CONFIGS}
    conversation_data = simulate_cluster_conversation()

    for message_data in conversation_data:
        user_id = message_data['from']
        message_text = message_data['message']
        
        if user_id in bots:
            bot = bots[user_id]
            await bot_send_message(bot, user_id, message_text)
    await asyncio.sleep(1)

    for bot in bots.values():
        await bot.session.close()
        print(f"[DEBUG] Bot session closed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit.')
