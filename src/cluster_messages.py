import json
import os
from datetime import datetime, timedelta

RAW_DATA_DIR = "data/raw/"
OUTPUT_DIR = "data/"
OUTPUT_PROBABILITY_FILE = os.path.join(OUTPUT_DIR, "cluster_data.json")
OUTPUT_CLUSTERED_MESSAGES_FILE = os.path.join(OUTPUT_DIR, "clustered_messages.json")
CLUSTER_TIME_GAP = timedelta(minutes=15)
MAX_CLUSTER_SIZE = 250
REDISTRIBUTION_STEP = 0.0001
MAX_CLUSTER_DELAY_SECONDS = 86400

def load_raw_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_messages(raw_data):
    messages = []
    for message in raw_data["messages"]:
        if "date" in message and "text" in message:
            timestamp = datetime.strptime(message["date"], '%Y-%m-%dT%H:%M:%S')
            text = message["text"]
            messages.append((timestamp, message))
    return sorted(messages, key=lambda x: x[0])

def cluster_messages(messages):
    clusters = []
    current_cluster = [messages[0][1]]
    for i in range(1, len(messages)):
        if messages[i][0] - messages[i - 1][0] > CLUSTER_TIME_GAP:
            clusters.append(current_cluster)
            current_cluster = [messages[i][1]]
        else:
            current_cluster.append(messages[i][1])
    if current_cluster:
        clusters.append(current_cluster)
    return clusters

def save_clustered_messages_to_json(clusters, output_file):
    clustered_data = {
        "clusters": []
    }
    cluster_id = 1
    
    for cluster in clusters:
        clustered_messages = []
        for message in cluster:
            message_data = {
                "id": message["id"],
                "cluster_id": cluster_id,
                **{key: message[key] for key in message if key != "id" and key != "cluster_id"}
            }
            clustered_messages.append(message_data)
        
        clustered_data["clusters"].append({
            "cluster_id": cluster_id,
            "messages": clustered_messages
        })
        cluster_id += 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clustered_data, f, ensure_ascii=False, indent=1)

def calculate_cluster_length_probabilities(clusters):
    cluster_lengths = [min(len(cluster), MAX_CLUSTER_SIZE) for cluster in clusters]
    max_length = MAX_CLUSTER_SIZE
    total_clusters = len(cluster_lengths)
    length_counts = {i: 0 for i in range(1, max_length + 1)}
    length_delays = {i: [] for i in range(1, max_length + 1)}
    
    for cluster in clusters:
        cluster_length = min(len(cluster), MAX_CLUSTER_SIZE)
        length_counts[cluster_length] += 1
        if len(cluster) > 1:
            total_delay = 0
            for i in range(1, len(cluster)):
                delay = (datetime.strptime(cluster[i]["date"], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(cluster[i - 1]["date"], '%Y-%m-%dT%H:%M:%S')).total_seconds()
                total_delay += delay
            avg_delay = total_delay / (len(cluster) - 1)
            length_delays[cluster_length].append(avg_delay)
    
    length_probabilities = {length: count / total_clusters for length, count in length_counts.items()}
    excess_clusters = sum(1 for cluster in clusters if len(cluster) > MAX_CLUSTER_SIZE)
    excess_probability = excess_clusters / total_clusters
    length_probabilities[MAX_CLUSTER_SIZE] -= excess_probability
    current_length = MAX_CLUSTER_SIZE
    while excess_probability > 0 and current_length >= 1:
        to_add = min(REDISTRIBUTION_STEP, excess_probability)
        length_probabilities[current_length] += to_add
        excess_probability -= to_add
        current_length -= 1
    return length_probabilities, length_delays

def calculate_average_delay(delays):
    if not delays:
        return 0
    return sum(delays) / len(delays)

def calculate_global_average_delay(length_delays):
    valid_delays = []
    for delays in length_delays.values():
        valid_delays.extend([delay for delay in delays if delay > 0])
    if valid_delays:
        return sum(valid_delays) / len(valid_delays)
    return 0

def assign_custom_zeros(length_delays, global_average_delay):
    divisor = 5
    zero_count = 0
    for length in range(MAX_CLUSTER_SIZE, 0, -1):
        if calculate_average_delay(length_delays[length]) == 0:
            zero_count += 1
            length_delays[length] = [global_average_delay / divisor]
            if divisor > 1:
                divisor -= 0.02
            else:
                divisor = 1

def smooth_inconsistent_delays(length_delays):
    length_keys = sorted(length_delays.keys())
    for i in range(1, len(length_keys) - 1):
        current_length = length_keys[i]
        previous_length = length_keys[i - 1]
        next_length = length_keys[i + 1]
        current_delay = calculate_average_delay(length_delays[current_length])
        prev_delay = calculate_average_delay(length_delays[previous_length])
        next_delay = calculate_average_delay(length_delays[next_length])
        if (current_delay > 1.25 * max(prev_delay, next_delay)) or (current_delay < 0.8 * min(prev_delay, next_delay)):
            smoothed_delay = (prev_delay + next_delay) / 2
            length_delays[current_length] = [smoothed_delay]

def calculate_average_cluster_delay(clusters):
    cluster_delays = {i: [] for i in range(1, MAX_CLUSTER_SIZE + 1)}
    for i in range(1, len(clusters)):
        current_cluster_length = min(len(clusters[i]), MAX_CLUSTER_SIZE)
        delay_between_clusters = (datetime.strptime(clusters[i][0]["date"], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(clusters[i-1][-1]["date"], '%Y-%m-%dT%H:%M:%S')).total_seconds()
        delay_between_clusters = min(delay_between_clusters, MAX_CLUSTER_DELAY_SECONDS)
        cluster_delays[current_cluster_length].append(delay_between_clusters)
    return {length: calculate_average_delay(delays) for length, delays in cluster_delays.items()}

def assign_custom_zeros_cluster(cluster_delays, global_avg_cluster_delay):
    divisor = 5
    for length in range(MAX_CLUSTER_SIZE, 0, -1):
        if cluster_delays[length] == 0:
            cluster_delays[length] = global_avg_cluster_delay / divisor
            if divisor > 1:
                divisor -= 0.02
            else:
                divisor = 1

def smooth_inconsistent_cluster_delays(cluster_delays):
    cluster_keys = sorted(cluster_delays.keys())
    for i in range(1, len(cluster_keys) - 1):
        current_length = cluster_keys[i]
        previous_length = cluster_keys[i - 1]
        next_length = cluster_keys[i + 1]
        current_cluster_delay = cluster_delays[current_length]
        prev_cluster_delay = cluster_delays[previous_length]
        next_cluster_delay = cluster_delays[next_length]
        if (current_cluster_delay > 1.25 * max(prev_cluster_delay, next_cluster_delay)) or (current_cluster_delay < 0.8 * min(prev_cluster_delay, next_cluster_delay)):
            smoothed_cluster_delay = (prev_cluster_delay + next_cluster_delay) / 2
            cluster_delays[current_length] = smoothed_cluster_delay

def save_probabilities_to_file(probabilities, delays, cluster_avg_delays, global_average_delay, output_file):
    message_cluster_data = []
    for length in range(1, MAX_CLUSTER_SIZE + 1):
        probability = probabilities.get(length, 0)
        avg_message_delay = calculate_average_delay(delays[length])
        avg_cluster_delay = cluster_avg_delays.get(length, 0)
        message_cluster_data.append({
            "probability": probability,
            "avg_message_delay": avg_message_delay,
            "avg_cluster_delay": avg_cluster_delay
        })

    output_data = {
        "message_cluster_data": message_cluster_data,
        "total_probability": sum(probabilities.values())
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    raw_files = ["course_2.json", "course_3.json", "course_4.json", "delivery.json"]
    all_clusters = []
    for raw_file in raw_files:
        raw_data = load_raw_data(os.path.join(RAW_DATA_DIR, raw_file))
        messages = process_messages(raw_data)
        clusters = cluster_messages(messages)
        all_clusters.extend(clusters)

    save_clustered_messages_to_json(all_clusters, OUTPUT_CLUSTERED_MESSAGES_FILE)

    cluster_probabilities, cluster_delays = calculate_cluster_length_probabilities(all_clusters)
    global_avg_delay = calculate_global_average_delay(cluster_delays)
    assign_custom_zeros(cluster_delays, global_avg_delay)
    smooth_inconsistent_delays(cluster_delays)
    cluster_avg_delays = calculate_average_cluster_delay(all_clusters)
    
    global_avg_cluster_delay = sum(cluster_avg_delays.values()) / len([v for v in cluster_avg_delays.values() if v > 0])
    assign_custom_zeros_cluster(cluster_avg_delays, global_avg_cluster_delay)
    smooth_inconsistent_cluster_delays(cluster_avg_delays)

    save_probabilities_to_file(cluster_probabilities, cluster_delays, cluster_avg_delays, global_avg_delay, OUTPUT_PROBABILITY_FILE)

    print(f"Clustered data and message cluster probabilities saved to {OUTPUT_DIR}.")
