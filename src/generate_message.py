import json
import os
import random
from collections import defaultdict
from nltk.tokenize import word_tokenize
import pymorphy3
from nltk.corpus import stopwords
import nltk

nltk.download('punkt')
nltk.download('stopwords')

morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
stop_words.add('это')

BIGRAMS_DATA_DIR = "data/user_bigrams"
TRIGRAMS_DATA_DIR = "data/user_trigrams"
SIMILAR_BIGRAMS_DATA_DIR = "data/similar_bigrams"
SIMILAR_TRIGRAMS_DATA_DIR = "data/similar_trigrams"

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ngrams(user_n, ngram_type, similar=False):
    ngram_dir = (SIMILAR_BIGRAMS_DATA_DIR if ngram_type == "bigrams" else SIMILAR_TRIGRAMS_DATA_DIR) if similar else (BIGRAMS_DATA_DIR if ngram_type == "bigrams" else TRIGRAMS_DATA_DIR)
    ngram_file = os.path.join(ngram_dir, f"{user_n}_{ngram_type}.json")
    ngram_data = load_json_file(ngram_file)
    return [ngram for entry in ngram_data for ngram in entry[ngram_type]]

def build_transition_table(ngrams):
    transition_table = defaultdict(lambda: defaultdict(int))
    for ngram in ngrams:
        prefix = tuple(ngram[:-1])
        transition_table[prefix][ngram[-1]] += 1
    return {prefix: {token: count / sum(next_tokens.values()) for token, count in next_tokens.items()} 
            for prefix, next_tokens in transition_table.items()}

def generate_text(transition_table, max_words):
    prefix = ('__START__',)
    generated_words = []
    while len(generated_words) < max_words:
        next_word_candidates = transition_table.get(prefix)
        if not next_word_candidates:
            break
        next_word = random.choices(list(next_word_candidates.keys()), weights=next_word_candidates.values())[0]
        if next_word == '__END__':
            break
        generated_words.append(next_word)
        prefix = tuple(generated_words[-len(prefix):])
    return " ".join(generated_words).capitalize()

def lemmatize_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in filtered_tokens]
    return lemmatized_tokens

def generate_message(user_n, mode="starter", max_words=25):
    if mode == "starter":
        bigrams = load_ngrams(user_n, "bigrams")
        trigrams = load_ngrams(user_n, "trigrams")
    elif mode == "reply":
        bigrams = load_ngrams(user_n, "bigrams", similar=True)
        trigrams = load_ngrams(user_n, "trigrams", similar=True)

        if not bigrams and not trigrams:
            print(f"No similar n-grams found for {user_n} in reply mode, falling back to starter mode.")
            return generate_message(user_n, mode="starter", max_words=max_words)
    else:
        raise ValueError("Invalid mode. Choose either 'starter' or 'reply'.")
    
    transition_table = build_transition_table(bigrams + trigrams)
    generated_message = generate_text(transition_table, max_words)
    lemmatized_message = lemmatize_text(generated_message)

    return generated_message, lemmatized_message

if __name__ == "__main__":
    print(generate_message('user726029390', mode="starter"))
