import json
import os
import pymorphy3
from collections import defaultdict

LEMMATIZED_DIR = "data/lemmatized_users/"
OUTPUT_DIR = "data/similarity_ranking/"
WORD_SCORE_FILE = "data/tokenized/word_score_output.json"
# input test message
INPUT_MESSAGE = "а я же правильно помню, что сегодня дедлайн по презентации к курсачу фейковый и можно просто пустой слайд загрузить?"

morph = pymorphy3.MorphAnalyzer()

def lemmatize_message(message):
    tokens = message.split()
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens]
    return lemmatized_tokens

def load_word_scores(word_score_file):
    with open(word_score_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def compute_similarity_score(lemmatized_message, user_message, word_scores):
    user_tokens = user_message['tokens']
    matching_score = sum(word_scores.get(word, 0) for word in lemmatized_message if word in user_tokens)
    return matching_score

def find_most_similar_messages(user_data, lemmatized_message, word_scores):
    most_similar_messages_by_user = {}
    
    for user_id, messages in user_data.items():
        scored_messages = []

        for message in messages:
            score = compute_similarity_score(lemmatized_message, message, word_scores)
            if score > 0:
                message['similarity_score'] = score
                scored_messages.append(message)

        sorted_messages = sorted(scored_messages, key=lambda msg: msg['similarity_score'], reverse=True)
        most_similar_messages_by_user[user_id] = sorted_messages
    
    return most_similar_messages_by_user

def load_combined_data(directory):
    user_data = {}

    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data[file_name] = json.load(f)
    
    return user_data

def save_similar_messages_to_file(user_id, messages, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"similar_to_input_user_{user_id}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

    print(f"Similar messages for user {user_id} saved to {output_file}")

if __name__ == "__main__":
    lemmatized_input_message = lemmatize_message(INPUT_MESSAGE)
    user_data = load_combined_data(LEMMATIZED_DIR)
    word_scores = load_word_scores(WORD_SCORE_FILE)
    most_similar_messages_by_user = find_most_similar_messages(user_data, lemmatized_input_message, word_scores)

    for user_id, messages in most_similar_messages_by_user.items():
        save_similar_messages_to_file(user_id, messages, OUTPUT_DIR)
