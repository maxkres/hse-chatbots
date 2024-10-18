import json
import os
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

CLUSTERED_MESSAGES_FILE = "data/clustered_messages.json"
OUTPUT_DIR = "data/tokenized/user-to-user"
BOT_CONFIGS_FILE = "bot_configs.txt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_and_tokenize(text):
    tokens = re.findall(r"\w+[\w'-]*[.,!?;]?", text.lower())
    return ['__START__'] + [lemmatizer.lemmatize(token) for token in tokens] + ['__END__']

def get_clusters_started_by_user(clusters, user_id):
    user_clusters = []
    for cluster in clusters:
        first_message = cluster['messages'][0]
        if first_message.get('from_id') == user_id:
            user_clusters.append(cluster)
    return user_clusters

def tokenize_user_messages_in_clusters(clusters, user_n, allowed_users):
    tokenized_data = defaultdict(list)

    for cluster in clusters:
        for message in cluster['messages']:
            user_k = message.get('from_id')
            user_name = message.get('from', "Unknown Name")
            if user_k in allowed_users:
                if 'text' in message and isinstance(message['text'], str):
                    tokens = clean_and_tokenize(message['text'])
                    tokenized_data[user_k].append({
                        "from": user_name,
                        "tokens": tokens
                    })

    return tokenized_data

def save_tokenized_data(user_n, tokenized_data):
    """Save tokenized data for each user k in JSON files."""
    for user_k, tokenized_messages in tokenized_data.items():
        output_file = os.path.join(OUTPUT_DIR, f"{user_n}_to_{user_k}.json")
        output_data = {
            "user_n": user_n,
            "user_k": user_k,
            "tokenized_messages": tokenized_messages
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    clustered_data = load_json(CLUSTERED_MESSAGES_FILE)
    clusters = clustered_data.get("clusters", [])

    bot_configs = load_json(BOT_CONFIGS_FILE)
    allowed_users = {user['user_id'] for user in bot_configs}

    for user_n in allowed_users:
        user_n_clusters = get_clusters_started_by_user(clusters, user_n)
        tokenized_data = tokenize_user_messages_in_clusters(user_n_clusters, user_n, allowed_users)
        save_tokenized_data(user_n, tokenized_data)

    print(f"Tokenized message data saved to {OUTPUT_DIR}.")
