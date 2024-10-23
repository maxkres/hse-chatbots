import json
import os
from collections import defaultdict

def find_similar_messages(lemmatized_data, test_message, inverse_z_scores, output_dir, specific_user_id):
    os.makedirs(output_dir, exist_ok=True)
    test_message_set = set(test_message)
    message_ids_with_score = []

    for message in lemmatized_data:
        if message['user_id'] != specific_user_id:
            continue  # Skip messages from other users
        common_words = test_message_set.intersection(message['lemmatized'])
        if common_words:
            avg_inv_zscore = sum(inverse_z_scores[word] for word in common_words) / len(common_words)
            if avg_inv_zscore >= 0.1:
                message_ids_with_score.append(message['message_id'])
    
    print(f"Message IDs with score >= 0.1 from user {specific_user_id}: {message_ids_with_score}")
    return message_ids_with_score

def process_similarity(test_message, specific_user_id):
    input_path = 'data/lemmatized_output.json'
    inv_zscore_path = 'data/word_inverse_zscore.txt'
    output_dir = 'data/similar_messages'
    print(test_message, specific_user_id)

    with open(input_path, 'r', encoding='utf-8') as file:
        lemmatized_data = json.load(file)
    with open(inv_zscore_path, 'r', encoding='utf-8') as file:
        inverse_z_scores = {line.split(': ')[0]: float(line.split(': ')[2].strip()) for line in file.readlines()}
    
    message_ids = find_similar_messages(lemmatized_data, test_message, inverse_z_scores, output_dir, specific_user_id)
    return message_ids

if __name__ == "__main__":
    
    test_message = ['гордей', 'опубликовать', 'инфа', 'объявление']
    specific_user_id = 'user726029390'  # Replace with the actual user ID you want to filter by

