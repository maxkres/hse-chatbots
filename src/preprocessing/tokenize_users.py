import json
import os
from nltk import bigrams, trigrams

BIGRAMS_DATA_DIR = "data/tokenized/bigrams"
TRIGRAMS_DATA_DIR= "data/tokenized/trigrams"
TOKENIZED_DATA_DIR = "data/tokenized/user-to-user/"

os.makedirs(BIGRAMS_DATA_DIR, exist_ok=True)
os.makedirs(TRIGRAMS_DATA_DIR, exist_ok=True)
os.makedirs(TOKENIZED_DATA_DIR, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_ngrams(tokens, n=3):
    if n == 2:
        return list(bigrams(tokens))
    elif n == 3:
        return list(trigrams(tokens))
    else:
        raise ValueError("Require n=2 for bigrams or n=3 for trigrams")

def process_tokenized_data(user_n, user_k):
    token_file = os.path.join(TOKENIZED_DATA_DIR, f"{user_n}_to_{user_k}.json")
    if not os.path.exists(token_file):
        print(f"Token file for {user_n}_to_{user_k} not found.")
        return None
    
    token_data = load_json(token_file)
    all_tokens = []

    for message in token_data['tokenized_messages']:
        tokens = message['tokens']
        all_tokens.extend(tokens)

    bigrams_data = generate_ngrams(all_tokens, n=2)
    trigrams_data = generate_ngrams(all_tokens, n=3)

    return bigrams_data, trigrams_data

def save_ngrams(user_n, user_k, bigrams_data, trigrams_data):
    bigram_file = os.path.join(BIGRAMS_DATA_DIR, f"{user_n}_to_{user_k}_bigrams.json")
    with open(bigram_file, 'w', encoding='utf-8') as f:
        json.dump(bigrams_data, f, ensure_ascii=False, indent=1)

    trigram_file = os.path.join(TRIGRAMS_DATA_DIR, f"{user_n}_to_{user_k}_trigrams.json")
    with open(trigram_file, 'w', encoding='utf-8') as f:
        json.dump(trigrams_data, f, ensure_ascii=False, indent=1)

def process_user_to_user():
    tokenized_files = [file for file in os.listdir(TOKENIZED_DATA_DIR)]

    for token_file in tokenized_files:
        file_name, _ = os.path.splitext(token_file)
        user_n = file_name.split("_")[0]
        user_k = file_name.split("_")[2] 

        bigrams_data, trigrams_data = process_tokenized_data(user_n, user_k)

        if bigrams_data and trigrams_data:
            save_ngrams(user_n, user_k, bigrams_data, trigrams_data)
            print(f"N-grams for {user_n} to {user_k} are generated.")

if __name__ == "__main__":
    process_user_to_user()
