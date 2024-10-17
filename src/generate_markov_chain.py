import json
import os
import random
from collections import defaultdict

MARKOV_DATA_DIR = "data/markov/"

def load_ngrams(user_id, ngram_type="bigrams"):
    ngram_file = os.path.join(MARKOV_DATA_DIR, f"{user_id}_{ngram_type}.json")
    with open(ngram_file, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def generate_text(transition_table, max_words=20, fallback_tokens=None):
    prefix = ('__START__',)
    generated_words = []

    while len(generated_words) < max_words:
        next_word_candidates = transition_table.get(prefix, None)
        
        if not next_word_candidates:
            # Fallback: choose a random word from the corpus (other than __START__)
            if fallback_tokens:
                next_word = random.choice(fallback_tokens)
            else:
                break
        else:
            next_word = random.choices(list(next_word_candidates.keys()), 
                                       weights=next_word_candidates.values())[0]

        if next_word == '__END__':
            break

        generated_words.append(next_word)
        prefix = tuple(generated_words[-len(prefix):])

    return " ".join(generated_words).capitalize()

def save_transition_table_to_file(transition_table, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for prefix, next_tokens in transition_table.items():
            f.write(f"Prefix: {prefix}\n")
            for token, prob in next_tokens.items():
                f.write(f"    {token}: {prob}\n")
            f.write("\n")

if __name__ == "__main__":
    top_users = ['user6060256091', 'user1948911068', 'user5564229156', 'user1485427289', 
                 'user629116733', 'user463594918', 'user971032879', 'user726029390', 
                 'user625210535', 'user384879817']
    user_id = top_users[0]

    print(f"Building custom Markov chain for user {user_id}...")

    ngrams = load_ngrams(user_id, ngram_type="bigrams")
    transition_table = build_transition_table(ngrams)

    # Use fallback tokens from the original corpus to avoid __START__ repetition
    fallback_tokens = list(set([word for ngram in ngrams for word in ngram if word != '__START__' and word != '__END__']))

    # Generate text with improved fallback
    generated_text = generate_text(transition_table, max_words=20, fallback_tokens=fallback_tokens)

    print("Generated text:")
    print(generated_text)
