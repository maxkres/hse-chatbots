import json
import os
import random
from collections import defaultdict

MARKOV_DATA_DIR = "data/markov/"

def load_ngrams(user_id, ngram_type="bigrams"):
    """Load the n-grams for the given user."""
    ngram_file = os.path.join(MARKOV_DATA_DIR, f"{user_id}_{ngram_type}.json")
    with open(ngram_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_transition_table(ngrams):
    """Build a transition table with probabilities from the n-grams."""
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

def generate_text(transition_table, max_words=20):
    prefix = ('__START__',)
    generated_words = []

    while len(generated_words) < max_words:
        next_word_candidates = transition_table.get(prefix, None)
        if not next_word_candidates:
            break

        next_word = random.choices(list(next_word_candidates.keys()), weights=next_word_candidates.values())[0]

        if next_word == '__END__':
            break

        generated_words.append(next_word)
        prefix = tuple(generated_words[-len(prefix):])

    return " ".join(generated_words)

if __name__ == "__main__":
    top_users = ['user6060256091', 'user1948911068', 'user5564229156', 'user1485427289', 
                 'user629116733', 'user463594918', 'user971032879', 'user726029390', 
                 'user625210535', 'user384879817']
    user_id = top_users[0]

    print(f"Building custom Markov chain for user {user_id}...")

    ngrams = load_ngrams(user_id, ngram_type="bigrams")
    transition_table = build_transition_table(ngrams)

    generated_text = generate_text(transition_table, max_words=20)

    print("Generated text:")
    print(generated_text)
