import os
import asyncio
import logging
from collections import deque, defaultdict
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from generate_markov_chain import load_ngrams, build_transition_table, generate_text

API_TOKEN = os.getenv('API_TOKEN')
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

message_history = deque(maxlen=5)

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def tokenize_recent_messages_with_weights():
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
        prefix_candidates = [("__START__",)]

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

    return " ".join(generated_words)

async def store_and_print_messages(message: Message):
    message_history.append(message.text)

    print(f"Last 15 messages in chat {message.chat.id}:")
    for msg in message_history:
        print(msg)

@dp.message()
async def handle_new_message(message: Message):
    print(f"New message received in chat {message.chat.id}")
    
    await store_and_print_messages(message)

    keywords = tokenize_recent_messages_with_weights()
    print(f"Extracted Weighted Keywords: {keywords}")

    user_id = 'user726029390'
    ngrams = load_ngrams(user_id, ngram_type="bigrams")
    
    valid_starting_keywords = get_valid_starting_keywords(ngrams)

    transition_table = build_transition_table(ngrams)

    generated_text = generate_text_with_valid_keyword(transition_table, keywords, valid_starting_keywords, max_words=20)
    
    await message.answer(generated_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit.')
