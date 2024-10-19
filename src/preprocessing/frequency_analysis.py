import json
from collections import defaultdict

COMBINED_FILE = "data/tokenized/combined_tokenized.json"
OUTPUT_FILE = "data/tokenized/word_frequency_output.txt"

def load_combined_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def preprocess_for_frequency_analysis(tokenized_data):
    words = []
    for user_id, tokens in tokenized_data.items():
        words.extend(tokens)
    return words

def compute_word_frequency(words):
    word_frequency = defaultdict(int)
    
    for word in words:
        word_frequency[word] += 1
    
    return word_frequency

def save_word_frequency_to_file(word_frequency, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for word, count in sorted(word_frequency.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{word}: {count}\n")

if __name__ == "__main__":
    tokenized_data = load_combined_data(COMBINED_FILE)
    words = preprocess_for_frequency_analysis(tokenized_data)
    word_frequency = compute_word_frequency(words)
    save_word_frequency_to_file(word_frequency, OUTPUT_FILE)

    print(f"Word frequency analysis saved to {OUTPUT_FILE}.")
