import json
import os
import random
from collections import defaultdict, Counter

BIGRAMS_DATA_DIR = "data/bigrams_users"
TRIGRAMS_DATA_DIR = "data/trigrams_users"
STARTER_BIGRAMS_DIR = "data/starter_messages"
STARTER_TRIGRAMS_DIR = "data/starter_messages"

def load_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ngrams(user_n, user_k, ngram_type="bigrams", starter=False):
    if starter:
        if ngram_type == "bigrams":
            ngram_file = os.path.join(STARTER_BIGRAMS_DIR, f"{user_n}_bigrams.json")
        elif ngram_type == "trigrams":
            ngram_file = os.path.join(STARTER_TRIGRAMS_DIR, f"{user_n}_trigrams.json")
    else:
        if ngram_type == "bigrams":
            ngram_file = os.path.join(BIGRAMS_DATA_DIR, f"{user_n}_bigrams.json")
        elif ngram_type == "trigrams":
            ngram_file = os.path.join(TRIGRAMS_DATA_DIR, f"{user_n}_trigrams.json")
    
    ngram_data = load_json_file(ngram_file)
    
    ngrams = []
    if isinstance(ngram_data, list):
        for entry in ngram_data:
            if isinstance(entry, dict):
                ngrams.extend(entry.get(ngram_type, []))
            elif isinstance(entry, list):
                ngrams.extend(entry)
            else:
                print(f"Unexpected entry format: {entry}")
    elif isinstance(ngram_data, dict):
        ngrams.extend(ngram_data.get(ngram_type, []))
    else:
        print(f"Unexpected ngram data format in {ngram_file}")
    
    return ngrams


def extract_most_common_words(user_n, user_k, n_top=10):
    bigrams = load_ngrams(user_n, user_k, ngram_type="bigrams")
    trigrams = load_ngrams(user_n, user_k, ngram_type="trigrams")
    
    all_tokens = []
    for ngram in bigrams + trigrams:
        all_tokens.extend(ngram)
    
    word_counts = Counter(all_tokens)
    most_common_words = [word for word, count in word_counts.most_common(n_top)]
    
    return most_common_words


def build_transition_table(ngrams):
    transition_table = defaultdict(lambda: defaultdict(int))
    
    for ngram in ngrams:
        if len(ngram) < 2:
            continue
        prefix = tuple(ngram[:-1])
        next_token = ngram[-1]
        transition_table[prefix][next_token] += 1
    
    probabilities = {}
    for prefix, next_tokens in transition_table.items():
        total_count = sum(next_tokens.values())
        probabilities[prefix] = {token: count / total_count for token, count in next_tokens.items()}
    
    return probabilities

def generate_text(transition_table, max_words, fallback_tokens=None, most_common_words=None):
    prefix = ('__START__',)
    generated_words = []

    while len(generated_words) < max_words:
        next_word_candidates = transition_table.get(prefix, None)
        
        if not next_word_candidates:
            if fallback_tokens:
                next_word = random.choice(fallback_tokens)
            else:
                if len(prefix) > 1:
                    prefix = prefix[1:]
                    continue
                else:
                    if most_common_words:
                        next_word = random.choice(most_common_words)
                    else: break
        else:
            next_word = random.choices(list(next_word_candidates.keys()), 
                                       weights=next_word_candidates.values())[0]
        if next_word == '__END__': break
        generated_words.append(next_word)
        prefix = tuple(generated_words[-len(prefix):])

    return " ".join(generated_words).capitalize()

def generate_starter_message(user_n, max_words=25):
    bigrams = load_ngrams(user_n, None, ngram_type="bigrams", starter=True)
    trigrams = load_ngrams(user_n, None, ngram_type="trigrams", starter=True)
    starter_ngrams = bigrams + trigrams

    if not starter_ngrams:
        print(f"No starter ngrams found for user {user_n}")
        return ""

    transition_table = build_transition_table(starter_ngrams)
    if not transition_table:
        print(f"Transition table is empty for user {user_n}")
        return ""

    most_common_words = extract_most_common_words(user_n, None, n_top=10)
    generated_message = ""

    while not generated_message.strip():
        generated_message = generate_text(transition_table, max_words, 
                                          fallback_tokens=None, most_common_words=most_common_words)
        if not generated_message:
            print(f"Failed to generate starter message for user {user_n}")
            return ""
    print(f"Generated starter message: {generated_message}")
    return generated_message

def generate_reply_message(user_n, user_k, max_words=25):
    bigrams = load_ngrams(user_n, user_k, ngram_type="bigrams")
    trigrams = load_ngrams(user_n, user_k, ngram_type="trigrams")
    all_ngrams = bigrams + trigrams

    if not all_ngrams:
        print(f"No ngrams found for user {user_n} replying to {user_k}")
        return ""

    transition_table = build_transition_table(all_ngrams)
    if not transition_table:
        print(f"Transition table is empty for user {user_n} replying to {user_k}")
        return ""

    most_common_words = extract_most_common_words(user_n, user_k, n_top=10)
    generated_message = ""

    while not generated_message.strip():
        generated_message = generate_text(transition_table, max_words, 
                                          fallback_tokens=None, most_common_words=most_common_words)
        if not generated_message:
            print(f"Failed to generate reply message from user {user_n} to {user_k}")
            return ""
    print(f"Generated reply message: {generated_message}")
    return generated_message
