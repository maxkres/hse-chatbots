import os
import asyncio
import logging
from collections import deque, defaultdict
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import random
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from generate_markov_chain import load_ngrams, build_transition_table, generate_text
from dotenv import load_dotenv

load_dotenv()

with open('bot_configs.txt', 'r') as file:
    BOT_CONFIGS = json.load(file)

GROUP_CHAT_ID = -1002311774343
logging.basicConfig(level=logging.INFO)

nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def tokenize_recent_messages_with_weights(message_history):
    all_keywords = []
    total_messages = len(message_history)

    for idx, message in enumerate(reversed(message_history)):
        if message:
            tokens = word_tokenize(message)
            keywords = [word.lower() for word in tokens if word.isalpha() and word.lower() not in stop_words]
            weight = idx + 1
            all_keywords.extend(keywords * weight)

    return all_keywords

def get_valid_starting_keywords(ngrams):
    valid_starting_keywords = set()

    for ngram in ngrams:
        if ngram[0] == '__START__':
            valid_starting_keywords.add(ngram[1])

    return valid_starting_keywords

def generate_text_with_valid_keyword(transition_table, keywords, valid_starting_keywords, max_words=20):
    starting_keywords = [kw for kw in keywords if kw in valid_starting_keywords]

    if starting_keywords:
        keyword = random.choice(starting_keywords)
        prefix_candidates = [prefix for prefix in transition_table.keys() if keyword in prefix]
    else:
        prefix_candidates = list(transition_table.keys())

    prefix = random.choice(prefix_candidates)
    generated_words = list(prefix)

    while len(generated_words) < max_words:
        next_word_candidates = transition_table.get(prefix, None)
        if not next_word_candidates:
            break

        next_word = random.choices(list(next_word_candidates.keys()), weights=next_word_candidates.values())[0]

        if next_word == '__END__' or len(generated_words) >= max_words:
            break

        generated_words.append(next_word)
        prefix = tuple(generated_words[-len(prefix):])

    return " ".join(generated_words).capitalize()

async def store_and_print_messages(message, message_history):
    message_history.append(message.text)

    print(f"Last messages in chat {message.chat.id}:")
    for msg in message_history:
        print(msg)

async def handle_new_message(message: Message, message_history):
    if message.chat.id == GROUP_CHAT_ID:
        print(f"New message received in group chat {message.chat.id}")

        await store_and_print_messages(message, message_history)

        keywords = tokenize_recent_messages_with_weights(message_history)
        print(f"Extracted Weighted Keywords: {keywords}")

async def send_periodic_messages(bot: Bot, user_id: str, message_history):
    while True:
        ngrams = load_ngrams(user_id, ngram_type="bigrams")
        valid_starting_keywords = get_valid_starting_keywords(ngrams)
        transition_table = build_transition_table(ngrams)

        keywords = tokenize_recent_messages_with_weights(message_history)
        print(f"Using Keywords for Generation: {keywords}")

        generated_text = generate_text_with_valid_keyword(transition_table, keywords, valid_starting_keywords, max_words=20)

        await bot.send_message(GROUP_CHAT_ID, generated_text)

        delay = random.randint(50, 300)
        print(f"Delaying for {delay} seconds before sending the next message...")
        await asyncio.sleep(delay)

async def start_bot(api_token: str, user_id: str):
    bot = Bot(token=api_token)
    dp = Dispatcher()

    message_history = deque(maxlen=5)

    @dp.message()
    async def new_message_handler(message: Message):
        await handle_new_message(message, message_history)

    asyncio.create_task(send_periodic_messages(bot, user_id, message_history))
    await dp.start_polling(bot)

async def main():
    tasks = []
    for config in BOT_CONFIGS:
        tasks.append(start_bot(config['api_token'], config['user_id']))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit.')
