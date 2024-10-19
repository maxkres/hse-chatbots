import json
import os
import random
from collections import defaultdict, Counter

BIGRAMS_DATA_DIR = "data/tokenized/bigrams"
TRIGRAMS_DATA_DIR = "data/tokenized/trigrams"

def load_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ngrams(user_n, user_k, ngram_type="bigrams"):
    if ngram_type == "bigrams":
        ngram_file = os.path.join(BIGRAMS_DATA_DIR, f"{user_n}_to_{user_k}_bigrams.json")
    elif ngram_type == "trigrams":
        ngram_file = os.path.join(TRIGRAMS_DATA_DIR, f"{user_n}_to_{user_k}_trigrams.json")
    return load_json_file(ngram_file)

def extract_most_common_words(user_n, user_k, n_top=10):
    bigrams = load_ngrams(user_n, user_k, ngram_type="bigrams")
    trigrams = load_ngrams(user_n, user_k, ngram_type="trigrams")
    
    all_ngrams = bigrams + trigrams
    all_tokens = [token for ngram in all_ngrams for token in ngram]
    word_counts = Counter(all_tokens)
    most_common_words = [word for word, count in word_counts.most_common(n_top)]
    
    return most_common_words

def build_transition_table(ngrams):
    transition_table = defaultdict(lambda: defaultdict(int))
    
    for ngram in ngrams:
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

def generate_message_for_users(user_n, user_k, max_words=25):
    bigrams = load_ngrams(user_n, user_k, ngram_type="bigrams")
    trigrams = load_ngrams(user_n, user_k, ngram_type="trigrams")
    all_ngrams = bigrams + trigrams
    
    transition_table = build_transition_table(all_ngrams)
    most_common_words = extract_most_common_words(user_n, user_k, n_top=10)
    generated_message = ""
    
    while not generated_message.strip():
        generated_message = generate_text(transition_table, max_words, 
                                          fallback_tokens=None, most_common_words=most_common_words)
    return generated_message
