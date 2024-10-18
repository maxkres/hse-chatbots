import json
import os
from collections import defaultdict

CLUSTERED_MESSAGES_FILE = "data/clustered_messages.json"
OUTPUT_PARTICIPATION_FILE = "data/cluster_reply_participation.json"
BOT_CONFIGS_FILE = "bot_configs.txt"

def load_clustered_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_bot_configs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_clusters_started_by_user(clusters, user_id):
    """Get all clusters started by a specific user (user_n)."""
    user_clusters = []
    for cluster in clusters:
        first_message = cluster['messages'][0]
        if first_message.get('from_id') == user_id:
            user_clusters.append(cluster)
    return user_clusters

def calculate_participation_rate(clusters, allowed_users):
    """Calculate the participation rate of all allowed users (user_k) in the clusters started by user_n."""
    total_message_count = defaultdict(int)
    user_names = {}

    for cluster in clusters:
        for message in cluster['messages']:
            sender_id = message.get('from_id')
            if sender_id in allowed_users:
                total_message_count[sender_id] += 1
                user_names[sender_id] = message.get('from', 'Unknown Name')

    participation_rates = {}
    total_messages_by_allowed_users = sum(total_message_count.values())

    for user_id in allowed_users:
        if total_messages_by_allowed_users > 0:
            participation_rates[user_id] = total_message_count[user_id] / total_messages_by_allowed_users
        else:
            participation_rates[user_id] = 0

    return participation_rates, user_names

def generate_participation_data(clusters, allowed_users):
    """Generate the participation data for each user n."""
    participation_data = {}

    for user_n in allowed_users:
        user_n_clusters = get_clusters_started_by_user(clusters, user_n)
        participation_rates, user_names = calculate_participation_rate(user_n_clusters, allowed_users)

        participation_data[user_n] = {
            "from": user_names.get(user_n, "Unknown Name"),
            "participation_rates": {}
        }
        sorted_participation = sorted(participation_rates.items(), key=lambda x: x[1], reverse=True)

        for user_k, rate in sorted_participation:
            participation_data[user_n]["participation_rates"][user_k] = {
                "rate": rate,
                "name": user_names.get(user_k, "Unknown Name")
            }

    return participation_data

def save_participation_data_to_json(participation_data, output_file):
    """Save participation data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(participation_data, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":

    clustered_data = load_clustered_messages(CLUSTERED_MESSAGES_FILE)
    clusters = clustered_data.get("clusters", [])

    bot_configs = load_bot_configs(BOT_CONFIGS_FILE)
    allowed_users = {user['user_id'] for user in bot_configs}
    participation_data = generate_participation_data(clusters, allowed_users)

    save_participation_data_to_json(participation_data, OUTPUT_PARTICIPATION_FILE)
    print(f"Participation data saved to {OUTPUT_PARTICIPATION_FILE}.")
