import json
import os
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
from nltk import bigrams, trigrams

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

RAW_DATA_DIR = "data/raw/"
PROCESSED_DATA_DIR = "data/processed/"
MARKOV_DATA_DIR = "data/markov/"
os.makedirs(MARKOV_DATA_DIR, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_and_tokenize(text):
    tokens = word_tokenize(text.lower())
    return [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]

def process_chat_data(file_name):
    print(f"Processing chat file: {file_name}")
    data = load_json(RAW_DATA_DIR + file_name)
    user_messages = defaultdict(list)

    for message in data['messages']:
        user_id = message.get('from_id')
        text = message.get('text', "")
        
        if user_id and isinstance(text, str):
            cleaned_tokens = clean_and_tokenize(text)
            user_messages[f"{user_id}"].append(cleaned_tokens)

    for user_id, messages in user_messages.items():
        print(f"Processing user: {user_id}")
        with open(os.path.join(PROCESSED_DATA_DIR, f"{user_id}_processed.json"), 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)

def process_all_chats():
    for file_name in os.listdir(RAW_DATA_DIR):
        if file_name.endswith(".json"):
            process_chat_data(file_name)

def get_top_users():
    token_counts = {}

    for file_name in os.listdir(PROCESSED_DATA_DIR):
        if file_name.endswith("_processed.json"):
            user_id = file_name.split("_")[0]
            user_data = load_json(os.path.join(PROCESSED_DATA_DIR, file_name))

            total_tokens = sum(len(message) for message in user_data)
            token_counts[user_id] = total_tokens

    top_10_users = dict(Counter(token_counts).most_common(10))
    return top_10_users

def generate_ngrams(user_id, n=2):
    user_data = load_json(os.path.join(PROCESSED_DATA_DIR, f"{user_id}_processed.json"))

    all_tokens = []
    for message in user_data:
        all_tokens.extend(message)

    if n == 2:
        ngrams_list = list(bigrams(all_tokens))
    elif n == 3:
        ngrams_list = list(trigrams(all_tokens))
    else:
        raise ValueError("n should be 2 or 3 for bigrams or trigrams")

    return ngrams_list

def save_ngrams_for_users(top_users):
    for user_id in top_users:
        print(f"Generating n-grams for user: {user_id}")

        bigrams_data = generate_ngrams(user_id, n=2)
        trigrams_data = generate_ngrams(user_id, n=3)

        bigram_file = os.path.join(MARKOV_DATA_DIR, f"{user_id}_bigrams.json")
        with open(bigram_file, 'w', encoding='utf-8') as f:
            json.dump(bigrams_data, f, indent=4, ensure_ascii=False)

        trigram_file = os.path.join(MARKOV_DATA_DIR, f"{user_id}_trigrams.json")
        with open(trigram_file, 'w', encoding='utf-8') as f:
            json.dump(trigrams_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    process_all_chats()
    top_users = get_top_users()
    print(f"Top 10 users: {top_users}")
    save_ngrams_for_users(top_users)
