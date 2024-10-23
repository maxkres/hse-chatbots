import json
import random
import time
from generate_message import generate_message
from build_ngrams import run_ngrams_with_similarity

CLUSTER_DATA_FILE = "data/cluster_data.json"
STARTER_PROB_FILE = "data/starter_message_probabilities.json"
CLUSTER_REPLY_FILE = "data/cluster_reply_participation.json"

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_cluster():
    cluster_data = load_json(CLUSTER_DATA_FILE)["message_cluster_data"]
    starter_data = load_json(STARTER_PROB_FILE)
    
    probabilities = [cluster['probability'] for cluster in cluster_data]
    selected_cluster = random.choices(cluster_data, weights=probabilities, k=1)[0]
    selected_cluster["length"] = random.randint(1, 50)
    
    user_probabilities = [user['probability'] for user in starter_data]
    starter_user = random.choices(starter_data, weights=user_probabilities, k=1)[0]
    
    return {
        "cluster": selected_cluster,
        "starter_user": starter_user
    }

def choose_next_user(starter_user, participation_data):
    participation_rates = participation_data[starter_user]["participation_rates"]
    users = list(participation_rates.keys())
    probabilities = [participation_rates[user]["rate"] for user in users]
    
    next_user = random.choices(users, weights=probabilities, k=1)[0]
    return next_user

def simulate_replies_one_by_one(cluster_info, participation_data):
    starter_user = cluster_info['starter_user']
    print(f"Starter User: {starter_user}")
    starter_message, lemmatized_message = generate_message(starter_user["user_id"], mode="starter")
    
    yield {
        "from": starter_user['user_id'],
        "message": starter_message
    }
    
    cluster = cluster_info['cluster']
    cluster_length = cluster["length"]
    avg_message_delay = cluster["avg_message_delay"]
    
    current_user = choose_next_user(starter_user['user_id'], participation_data)
    
    for i in range(cluster_length - 1):
        next_user = choose_next_user(current_user, participation_data)
        print(next_user)
        run_ngrams_with_similarity(lemmatized_message, next_user)
        reply_message, lemmatized_message = generate_message(next_user, mode="reply")
        time.sleep(avg_message_delay / 10)
        
        yield {
            "from": current_user,
            "message": reply_message
        }
        current_user = next_user

def simulate_cluster_conversation():
    while True:
        cluster_info = initialize_cluster()
        participation_data = load_json(CLUSTER_REPLY_FILE)
        cluster_delay = cluster_info['cluster']['avg_cluster_delay']
        reply_generator = simulate_replies_one_by_one(cluster_info, participation_data)
        
        for reply in reply_generator:
            yield reply
        
        time.sleep(cluster_delay / 100)
