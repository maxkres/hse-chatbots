import json
import os
from collections import defaultdict

CLUSTERED_MESSAGES_FILE = "data/clustered_messages.json"
OUTPUT_STARTER_PROBABILITIES_FILE = "data/starter_message_probabilities.json"
BOT_CONFIGS_FILE = "bot_configs.txt"

def load_clustered_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_bot_configs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def classify_message_type(message):
    if 'forwarded_from' in message:
        return 'Repost'
    elif any(media in message for media in ['photo', 'video', 'document', 'audio']):
        return 'Media'
    elif isinstance(message.get('text'), str):
        if message['text'].strip().endswith('?'):
            return 'Question'
        else:
            return 'Text'
    return 'Unknown'

def calculate_starter_probabilities(clusters):
    starter_counts = defaultdict(int)
    user_info = {}
    message_type_counts = defaultdict(lambda: defaultdict(int))
    total_clusters = len(clusters)
    
    for cluster in clusters:
        first_message = cluster['messages'][0]
        user_id = first_message.get('from_id', 'unknown')
        user_name = first_message.get('from', 'Unknown Name')
        starter_counts[user_id] += 1
        
        if user_id not in user_info:
            user_info[user_id] = user_name

        message_type = classify_message_type(first_message)
        message_type_counts[user_id][message_type] += 1

    starter_probabilities = {user_id: count / total_clusters for user_id, count in starter_counts.items()}
    sorted_probabilities = sorted(starter_probabilities.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_probabilities, user_info, message_type_counts, starter_counts

def filter_and_adjust_probabilities(sorted_probabilities, user_info, message_type_counts, starter_counts, allowed_user_ids):
    filtered_probabilities = []
    
    filtered_users = [entry for entry in sorted_probabilities if entry[0] in allowed_user_ids]
    total_probability = sum(prob for _, prob in filtered_users)
    
    adjusted_probabilities = [(user_id, prob / total_probability) for user_id, prob in filtered_users]

    output_data = []
    
    for user_id, probability in adjusted_probabilities:
        user_name = user_info.get(user_id, "Unknown Name")
        total_starts = starter_counts[user_id]

        text_prob = message_type_counts[user_id]['Text'] / total_starts if total_starts > 0 else 0
        question_prob = message_type_counts[user_id]['Question'] / total_starts if total_starts > 0 else 0
        media_prob = message_type_counts[user_id]['Media'] / total_starts if total_starts > 0 else 0
        repost_prob = message_type_counts[user_id]['Repost'] / total_starts if total_starts > 0 else 0

        output_data.append({
            "user_id": user_id,
            "name": user_name,
            "probability": probability,
            "message_type_probabilities": {
                "text": text_prob,
                "question": question_prob,
                "media": media_prob,
                "repost": repost_prob
            }
        })
    
    return output_data

def save_probabilities_to_json(output_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    clustered_data = load_clustered_messages(CLUSTERED_MESSAGES_FILE)
    clusters = clustered_data.get("clusters", [])

    bot_configs = load_bot_configs(BOT_CONFIGS_FILE)
    allowed_user_ids = {user['user_id'] for user in bot_configs}  # Extract allowed user_ids
    
    sorted_probabilities, user_info, message_type_counts, starter_counts = calculate_starter_probabilities(clusters)
    
    filtered_data = filter_and_adjust_probabilities(sorted_probabilities, user_info, message_type_counts, starter_counts, allowed_user_ids)
    
    save_probabilities_to_json(filtered_data, OUTPUT_STARTER_PROBABILITIES_FILE)
    print(f"Starter message probabilities and types saved to {OUTPUT_STARTER_PROBABILITIES_FILE}.")
