import json
import os
import nltk
from nltk import word_tokenize, bigrams, trigrams

RAW_DATA_DIR = "data/raw/"
OUTPUT_DIR = "data/starter_messages/"
BOT_CONFIG_FILE = "bot_configs.json"
CLUSTERED_MESSAGES_FILE = "data/clustered_messages.json"

nltk.download('punkt')

def load_bot_configs():
    with open(BOT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_clustered_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_starter_messages_for_user(user_id, clusters):
    starter_messages = []
    for cluster in clusters:
        if cluster["messages"]:
            first_message = cluster["messages"][0]
            
            if first_message.get("from_id") == user_id or first_message.get("actor_id") == user_id:
                starter_messages.append(first_message)
    return starter_messages

def tokenize_message(text):
    if isinstance(text, str):
        return word_tokenize(text)
    elif isinstance(text, list):
        tokens = []
        for part in text:
            if isinstance(part, str):
                tokens.extend(word_tokenize(part))
            elif isinstance(part, dict) and 'text' in part:
                tokens.extend(word_tokenize(part['text']))
        return tokens
    return []

def generate_ngrams(tokens):
    return list(bigrams(tokens)), list(trigrams(tokens))

def process_user_starter_messages(user_id, starter_messages):
    user_bigrams = []
    user_trigrams = []
    
    for message in starter_messages:
        tokens = tokenize_message(message["text"])
        message_bigrams, message_trigrams = generate_ngrams(tokens)
        user_bigrams.extend(message_bigrams)
        user_trigrams.extend(message_trigrams)
    
    return user_bigrams, user_trigrams

def save_bigrams_to_json(user_id, user_bigrams):
    bigrams_file = os.path.join(OUTPUT_DIR, f"{user_id}_bigrams.json")
    with open(bigrams_file, 'w', encoding='utf-8') as f:
        json.dump(user_bigrams, f, ensure_ascii=False, indent=1)

def save_trigrams_to_json(user_id, user_trigrams):
    trigrams_file = os.path.join(OUTPUT_DIR, f"{user_id}_trigrams.json")
    with open(trigrams_file, 'w', encoding='utf-8') as f:
        json.dump(user_trigrams, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    bot_configs = load_bot_configs()
    clustered_data = load_clustered_messages(CLUSTERED_MESSAGES_FILE)
    clusters = clustered_data["clusters"]
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for config in bot_configs:
        user_id = config["user_id"]
        starter_messages = extract_starter_messages_for_user(user_id, clusters)
        
        user_bigrams, user_trigrams = process_user_starter_messages(user_id, starter_messages)
        save_bigrams_to_json(user_id, user_bigrams)
        save_trigrams_to_json(user_id, user_trigrams)

    print(f"Bigrams and trigrams for all users saved separately to {OUTPUT_DIR}.")
