import os
import json
from collections import defaultdict

def read_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(data, path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

def read_user_id(path):
    config = read_json(path) 
    return {entry['user_id'] for entry in config}

def extract_and_merge(json_files, user_id):
    return [
        {
            'message_id': idx + 1,
            'user_id': message['from_id'],
            'text': ' '.join(entity.get('text', '') for entity in message['text_entities']),
            'reply_to': message.get('reply_to_message_id')
        }
        for idx, message in enumerate(
            message
            for json_file in json_files
            for message in read_json(json_file).get('messages', [])
            if message.get('text_entities') and message['from_id'] in user_id
        )
    ]

def calculate_reply_matrix(data, user_ids):
    reply_count = {user: defaultdict(int) for user in user_ids}
    total_messages = defaultdict(int)
    message_lookup = {msg['message_id']: msg['user_id'] for msg in data}

    for message in data:
        user_id = message['user_id']
        total_messages[user_id] += 1
        if 'reply_to' in message and message['reply_to'] in message_lookup:
            replied_user = message_lookup[message['reply_to']]
            if replied_user in user_ids:
                reply_count[user_id][replied_user] += 1

    reply_matrix = {
        user: {
            replied_user: round(reply_count[user][replied_user] / total_messages[user], 2) if total_messages[user] > 0 else 0.0
            for replied_user in user_ids
        }
        for user in user_ids
    }
    
    return reply_matrix

def process_data():
    data_folder = 'data/raw'
    output_path = 'data/merged/merged.json'
    config_path = "data/configs/config.json"
    reply_matrix_path = "data/merged/reply_matrix.json"

    user_id = read_user_id(config_path)
    json_files = [
        os.path.join(data_folder, file)
        for file in os.listdir(data_folder)
        if file.endswith('.json')
    ]
    merged_data = extract_and_merge(json_files, user_id)
    write_json(merged_data, output_path)

    reply_matrix = calculate_reply_matrix(merged_data, user_id)
    write_json(reply_matrix, reply_matrix_path)
    print(f"Merged data saved to {output_path}. Reply matrix saved to {reply_matrix_path}.")

if __name__ == "__main__":
    process_data()
