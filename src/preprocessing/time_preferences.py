import json
import os
from collections import defaultdict
from datetime import datetime

RAW_DATA_DIR = "data/raw/"
OUTPUT_DIR = "data/time_preference/"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_raw_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_messages(raw_data):
    messages_by_user = defaultdict(list)
    user_info = {}

    for message in raw_data["messages"]:
        if "date" in message and "text" in message and "from_id" in message and "from" in message:
            timestamp = datetime.strptime(message["date"], '%Y-%m-%dT%H:%M:%S')
            user_id = message["from_id"]
            user_name = message["from"]
            messages_by_user[user_id].append(timestamp)
            if user_id not in user_info:
                user_info[user_id] = user_name

    return messages_by_user, user_info

def calculate_time_preferences(messages):
    interval_counts = defaultdict(int)
    total_messages = len(messages)

    for timestamp in messages:
        hour = timestamp.hour
        minute = timestamp.minute
        interval_index = (hour * 6) + (minute // 10)
        interval_counts[interval_index] += 1

    interval_probabilities = {interval: count / total_messages for interval, count in interval_counts.items()}

    return interval_probabilities

def save_time_preferences_to_file(user_id, user_name, interval_probabilities, output_dir):
    total_probability = sum(interval_probabilities.values())
    output_file = os.path.join(output_dir, f"{user_id}_time_preferences.txt")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Time Preferences for User {user_name} (ID: {user_id}) (10-Minute Interval Probabilities):\n")
        for interval in range(120):
            hour = interval // 6
            minute_start = (interval % 6) * 10
            minute_end = minute_start + 10
            probability = interval_probabilities.get(interval, 0)
            f.write(f"Hour {hour:02}:{minute_start:02} - {hour:02}:{minute_end:02} -> Probability: {probability:.4f}\n")
        
        f.write(f"\nTotal Probability: {total_probability:.4f}\n")

if __name__ == "__main__":
    raw_files = ["course_2_raw.json", "course_3_raw.json", "course_4_raw.json", "delivery_raw.json"]
    
    for raw_file in raw_files:
        raw_data = load_raw_data(os.path.join(RAW_DATA_DIR, raw_file))
        messages_by_user, user_info = process_messages(raw_data)
        
        for user_id, messages in messages_by_user.items():
            interval_probabilities = calculate_time_preferences(messages)
            user_name = user_info.get(user_id, "Unknown User")
            save_time_preferences_to_file(user_id, user_name, interval_probabilities, OUTPUT_DIR)

    print(f"Time preferences for all users saved to {OUTPUT_DIR}.")
