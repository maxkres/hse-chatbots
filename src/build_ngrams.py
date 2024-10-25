import json
import os
from collections import defaultdict
from similar_messages import process_similarity

def build_ngrams(tokens, n):
    return [tokens[i:i + n] for i in range(len(tokens) - n + 1)]

def load_data(input_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_user_ngrams(data, similar_message_ids=None):
    user_ngrams = defaultdict(lambda: {
        'bigrams': [], 'trigrams': [], 
        'similar_bigrams': [], 'similar_trigrams': []
    })
    
    for message in data:
        user_id, message_id, tokens = message['user_id'], message['message_id'], message['tokenized']
        user_ngrams[user_id]['bigrams'].append({'message_id': message_id, 'bigrams': build_ngrams(tokens, 2)})
        user_ngrams[user_id]['trigrams'].append({'message_id': message_id, 'trigrams': build_ngrams(tokens, 3)})

        if similar_message_ids and message_id in similar_message_ids:
            user_ngrams[user_id]['similar_bigrams'].append({'message_id': message_id, 'bigrams': build_ngrams(tokens, 2)})
            user_ngrams[user_id]['similar_trigrams'].append({'message_id': message_id, 'trigrams': build_ngrams(tokens, 3)})
    
    return user_ngrams

def save_ngrams(user_ngrams, output_dir_bigrams, output_dir_trigrams, similar=False):
    for user_id, ngrams in user_ngrams.items():
        dir_bigrams, dir_trigrams = output_dir_bigrams, output_dir_trigrams
        if similar:
            dir_bigrams, dir_trigrams = output_dir_bigrams.replace('user_bigrams', 'similar_bigrams'), output_dir_trigrams.replace('user_trigrams', 'similar_trigrams')

        os.makedirs(dir_bigrams, exist_ok=True)
        os.makedirs(dir_trigrams, exist_ok=True)

        with open(os.path.join(dir_bigrams, f"{user_id}_bigrams.json"), 'w', encoding='utf-8') as f:
            json.dump(ngrams['similar_bigrams' if similar else 'bigrams'], f, ensure_ascii=False, indent=1)
        with open(os.path.join(dir_trigrams, f"{user_id}_trigrams.json"), 'w', encoding='utf-8') as f:
            json.dump(ngrams['similar_trigrams' if similar else 'trigrams'], f, ensure_ascii=False, indent=1)

def process_ngrams(input_path, output_dir_bigrams, output_dir_trigrams, similar_message_ids=None):
    data = load_data(input_path)
    user_ngrams = generate_user_ngrams(data, similar_message_ids)
    save_ngrams(user_ngrams, output_dir_bigrams, output_dir_trigrams)
    if similar_message_ids:
        save_ngrams(user_ngrams, output_dir_bigrams, output_dir_trigrams, similar=True)

def run_ngrams_with_similarity(test_message, specific_user_id):
    input_path = 'data/tokenized_output.json'
    similar_message_ids = process_similarity(test_message, specific_user_id)
    process_ngrams(input_path, 'data/user_bigrams', 'data/user_trigrams', similar_message_ids)
