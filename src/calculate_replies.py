import json
from collections import defaultdict

INPUT_FILE = "data/filtered_clustered_messages.json"
OUTPUT_FILE = "data/reply_matrix.json"

def load_filtered_messages(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_reply_matrix(data):
    reply_counts = defaultdict(lambda: defaultdict(int))
    total_messages = defaultdict(int)
    
    message_lookup = {}
    for cluster in data["clusters"]:
        for message in cluster["messages"]:
            if message["type"] == "message":
                message_lookup[message["id"]] = message

    for cluster in data["clusters"]:
        for message in cluster["messages"]:
            if message["type"] != "message":
                continue

            user_id = message["from_id"]
            total_messages[user_id] += 1

            if "reply_to_message_id" in message:
                replied_message_id = message["reply_to_message_id"]
                if replied_message_id in message_lookup:
                    replied_user_id = message_lookup[replied_message_id]["from_id"]
                    reply_counts[user_id][replied_user_id] += 1

    reply_matrix = {
        user: {
            replied_user: round(reply_counts[user][replied_user] / total_messages[user], 3)
            if total_messages[user] > 0 else 0.0
            for replied_user in total_messages
        }
        for user in total_messages
    }
    
    return reply_matrix

def save_reply_matrix(reply_matrix, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reply_matrix, f, ensure_ascii=False, indent=1)

def main():
    filtered_data = load_filtered_messages(INPUT_FILE)
    reply_matrix = calculate_reply_matrix(filtered_data)
    save_reply_matrix(reply_matrix, OUTPUT_FILE)
    print(f"Reply matrix has been saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
