import json
import os
from collections import defaultdict
from similar_messages import process_similarity  # Import the function

def build_ngrams(tokens, n):
    return [tokens[i:i+n] for i in range(len(tokens) - n + 1)]

def process_ngrams(input_path, output_dir_bigrams, output_dir_trigrams, similar_message_ids=None):
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    user_ngrams = defaultdict(lambda: {'bigrams': [], 'trigrams': []})
    user_similar_ngrams = defaultdict(lambda: {'bigrams': [], 'trigrams': []})

    for message in data:
        user_id = message['user_id']
        message_id = message['message_id']
        tokens = message['tokenized']

        # Build n-grams for the entire dataset
        user_ngrams[user_id]['bigrams'].append({
            'message_id': message_id,
            'bigrams': build_ngrams(tokens, 2)
        })
        user_ngrams[user_id]['trigrams'].append({
            'message_id': message_id,
            'trigrams': build_ngrams(tokens, 3)
        })

        # Build n-grams only for similar messages (based on passed IDs)
        if similar_message_ids and message_id in similar_message_ids:
            user_similar_ngrams[user_id]['bigrams'].append({
                'message_id': message_id,
                'bigrams': build_ngrams(tokens, 2)
            })
            user_similar_ngrams[user_id]['trigrams'].append({
                'message_id': message_id,
                'trigrams': build_ngrams(tokens, 3)
            })

    # Output directories for all messages
    os.makedirs(output_dir_bigrams, exist_ok=True)
    os.makedirs(output_dir_trigrams, exist_ok=True)

    # Write full data bigrams and trigrams
    for user_id, ngrams in user_ngrams.items():
        with open(os.path.join(output_dir_bigrams, f"{user_id}_bigrams.json"), 'w', encoding='utf-8') as f:
            json.dump(ngrams['bigrams'], f, ensure_ascii=False, indent=1)
        with open(os.path.join(output_dir_trigrams, f"{user_id}_trigrams.json"), 'w', encoding='utf-8') as f:
            json.dump(ngrams['trigrams'], f, ensure_ascii=False, indent=1)

    # Output directories for similar messages
    if similar_message_ids:
        similar_bigrams_dir = output_dir_bigrams.replace('user_bigrams', 'similar_bigrams')
        similar_trigrams_dir = output_dir_trigrams.replace('user_trigrams', 'similar_trigrams')
        
        os.makedirs(similar_bigrams_dir, exist_ok=True)
        os.makedirs(similar_trigrams_dir, exist_ok=True)

        # Write similar message bigrams and trigrams
        for user_id, ngrams in user_similar_ngrams.items():
            with open(os.path.join(similar_bigrams_dir, f"{user_id}_bigrams.json"), 'w', encoding='utf-8') as f:
                json.dump(ngrams['bigrams'], f, ensure_ascii=False, indent=1)
            with open(os.path.join(similar_trigrams_dir, f"{user_id}_trigrams.json"), 'w', encoding='utf-8') as f:
                json.dump(ngrams['trigrams'], f, ensure_ascii=False, indent=1)

def run_ngrams_with_similarity(test_message, specific_user_id):
    input_path = 'data/tokenized_output.json'
    output_dir_bigrams = 'data/similar_bigrams'
    output_dir_trigrams = 'data/similar_trigrams'
    
    # Call the process_similarity function to get the similar message IDs
    similar_message_ids = process_similarity(test_message, specific_user_id)
    
    process_ngrams(input_path, output_dir_bigrams, output_dir_trigrams, similar_message_ids)

