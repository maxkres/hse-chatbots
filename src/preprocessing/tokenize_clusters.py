import json
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy3
import nltk
import string

nltk.download('punkt')
nltk.download('stopwords')
morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
punctuation = set(string.punctuation)

CLUSTERED_MESSAGES_FILE = "data/clustered_messages.json"
TOKENIZED_DIR = "data/tokenized"
COMBINED_OUTPUT_FILE = "data/tokenized/combined_tokenized.json"
BOT_CONFIGS_FILE = "bot_configs.json"

if not os.path.exists(TOKENIZED_DIR):
    os.makedirs(TOKENIZED_DIR)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_and_tokenize(text):
    tokens = word_tokenize(text.lower())

    filtered_tokens = []
    for token in tokens:
        if token not in stop_words and token not in punctuation and token.isalpha():
            lemma = morph.parse(token)[0].normal_form
            filtered_tokens.append(lemma)
    return filtered_tokens

def get_all_messages_by_user(clusters, allowed_users):
    user_messages = {user_id: [] for user_id in allowed_users}

    for cluster in clusters:
        for message in cluster['messages']:
            user_id = message.get('from_id')
            if user_id in allowed_users:
                if 'text' in message and isinstance(message['text'], str):
                    user_messages[user_id].append(message['text'])
    
    return user_messages

def tokenize_user_messages(user_messages):
    tokenized_users = {}
    
    for user_id, messages in user_messages.items():
        if messages:
            tokenized_messages = []
            for message in messages:
                tokens = clean_and_tokenize(message)
                tokenized_messages.append(tokens)
            
            flattened_tokens = [token for sublist in tokenized_messages for token in sublist]
            tokenized_users[user_id] = ['__START__'] + flattened_tokens + ['__END__']
            print(f"User {user_id}: First 5 tokens: {flattened_tokens[:5]}")

    return tokenized_users

def save_individual_tokenized_data(tokenized_users):
    for user_id, tokens in tokenized_users.items():
        output_file = os.path.join(TOKENIZED_DIR, f"{user_id}_tokenized.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({user_id: tokens}, f, ensure_ascii=False, indent=1)
        print(f"Saved {output_file}")

def merge_json_files(output_file):
    combined_data = {}
    for file_name in os.listdir(TOKENIZED_DIR):
        if file_name.endswith('_tokenized.json'):
            file_path = os.path.join(TOKENIZED_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                combined_data.update(user_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=1)
    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    clustered_data = load_json(CLUSTERED_MESSAGES_FILE)
    clusters = clustered_data.get("clusters", [])

    bot_configs = load_json(BOT_CONFIGS_FILE)
    allowed_users = {user['user_id'] for user in bot_configs}
    user_messages = get_all_messages_by_user(clusters, allowed_users)

    tokenized_users = tokenize_user_messages(user_messages)
    save_individual_tokenized_data(tokenized_users)

    merge_json_files(COMBINED_OUTPUT_FILE)

    print(f"Individual tokenized message data for each user saved to {TOKENIZED_DIR}.")
    print(f"Merged tokenized data saved to {COMBINED_OUTPUT_FILE}.")
