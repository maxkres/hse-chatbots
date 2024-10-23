import os
import json

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
    return [ {
            'message_id': idx + 1,
            'user_id': message['from_id'],
            'text': ' '.join(entity.get('text', '') for entity in message['text_entities'])
        }
        for idx, message in enumerate(
            message
            for json_file in json_files
            for message in read_json(json_file).get('messages', [])
            if message.get('text_entities') and message['from_id'] in user_id
        )
    ]

def process_data():
    data_folder = 'data/raw'
    output_path = 'data/merged/merged.json'
    config_path = "data/configs/config.json"

    user_id = read_user_id(config_path)
    json_files = [
        os.path.join(data_folder, file)
        for file in os.listdir(data_folder)
        if file.endswith('.json')
    ]
    merged_data = extract_and_merge(json_files, user_id)
    write_json(merged_data, output_path)
    print(f"Merged data has been saved to {output_path}.")

if __name__ == "__main__":
    process_data()
