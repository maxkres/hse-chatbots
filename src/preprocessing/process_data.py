import json
import os

RAW_DATA_DIR = "data/raw"
CONFIG_FILE_PATH = 'bot_configs.json'
OUTPUT_FILE_PATH = 'data/filtered_chat.json'

def read_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

def filter_messages(data, selected_users):
    selected_users = {user['user_id'] for user in selected_users}
    filtered_messages = []

    for message in data.get('messages', []):
        if message.get('from_id') in selected_users:
            filtered_messages.append(message)

    return filtered_messages

def process_json_files(json_files, bot_configs):
    all_filtered_messages = []
    new_id = 1

    for file_path in json_files:
        filtered_messages = filter_messages(read_json(file_path), bot_configs)
        for message in filtered_messages:
            message['id'] = new_id
            new_id += 1
        all_filtered_messages.extend(filtered_messages)

    return all_filtered_messages

def main():
    bot_configs = read_json(CONFIG_FILE_PATH)
    json_files = [os.path.join(RAW_DATA_DIR, file) for file in
                  os.listdir(RAW_DATA_DIR) if file.endswith('.json')]

    write_json(OUTPUT_FILE_PATH, process_json_files(json_files, bot_configs))
    print(f"Filtered chat saved to {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    main()
