import json
import os

CONFIG_PATH = "data/configs/config.json"
INPUT_FILE = "data/clustered_messages.json"
OUTPUT_FILE = "data/filtered_clustered_messages.json"

def load_selected_user_ids(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return {entry['user_id'] for entry in config_data}

def load_clustered_messages(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_clusters_by_users(data, selected_user_ids):
    filtered_clusters = []
    message_id = 1
    
    for cluster in data.get("clusters", []):
        filtered_messages = []
        
        for message in cluster["messages"]:
            if (
                message.get("type") == "message" and
                (message.get("from_id") in selected_user_ids or message.get("actor_id") in selected_user_ids)
            ):
                message["id"] = message_id
                filtered_messages.append(message)
                message_id += 1

        if filtered_messages:
            filtered_clusters.append({
                "cluster_id": cluster["cluster_id"],
                "messages": filtered_messages
            })
    
    return {"clusters": filtered_clusters}

def save_filtered_data(output_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=1)

def main():
    selected_user_ids = load_selected_user_ids(CONFIG_PATH)
    clustered_data = load_clustered_messages(INPUT_FILE)
    filtered_data = filter_clusters_by_users(clustered_data, selected_user_ids)
    save_filtered_data(filtered_data, OUTPUT_FILE)
    print(f"Filtered data has been saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
