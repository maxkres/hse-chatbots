import json
import os
from datetime import datetime

RAW_DATA_DIR = "data/raw/"
USER_ID = "user726029390"
TIME_THRESHOLD_BASE = 5
TIME_PER_WORD = 2
OUTPUT_FILE = "clustering_result_user726029390.txt"

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_time_difference(time1, time2):
    time_format = "%Y-%m-%dT%H:%M:%S"
    dt1 = datetime.strptime(time1[:19], time_format)
    dt2 = datetime.strptime(time2[:19], time_format)
    return abs((dt2 - dt1).total_seconds())


def is_clustered(previous_message, current_message):
    prev_text = previous_message.get("text", "")
    curr_text = current_message.get("text", "")
    prev_time = previous_message.get("date")
    curr_time = current_message.get("date")

    if not prev_text or not curr_text or not prev_time or not curr_time:
        return False

    time_diff = calculate_time_difference(prev_time, curr_time)
    curr_word_count = len(curr_text.split())
    threshold = TIME_THRESHOLD_BASE + (curr_word_count * TIME_PER_WORD)

    return time_diff <= threshold

def analyze_user_clustering(data, user_id, output_file):
    messages = [msg for msg in data['messages'] if msg.get('from_id') == user_id and isinstance(msg.get('text'), str)]
    clustered_messages = []

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Analyzing clustering behavior for user {user_id}...\n\n")

        for i in range(1, len(messages)):
            prev_message = messages[i - 1]
            curr_message = messages[i]

            clustered = is_clustered(prev_message, curr_message)
            clustered_messages.append((curr_message, clustered))

            f.write(f"Message {i}:\n")
            f.write(f"  Text: {curr_message['text']}\n")
            f.write(f"  Time Difference: {calculate_time_difference(prev_message['date'], curr_message['date'])} sec\n")
            f.write(f"  Word Count: {len(curr_message['text'].split())}\n")
            f.write(f"  Clustered with previous: {'Yes' if clustered else 'No'}\n")
            f.write("\n")

    return clustered_messages

if __name__ == "__main__":
    raw_file_path = os.path.join(RAW_DATA_DIR, "delivery_raw.json")
    chat_data = load_json(raw_file_path)
    clustered_results = analyze_user_clustering(chat_data, USER_ID, OUTPUT_FILE)

    print(f"Clustering analysis saved to {OUTPUT_FILE}.")
