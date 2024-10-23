import json
import math
from collections import Counter

def compute_mean_and_std(word_counter):
    total_words = sum(word_counter.values())
    unique_words = len(word_counter)
    mean_frequency = total_words / unique_words
    variance = sum((count - mean_frequency) ** 2 for count in word_counter.values()) / unique_words
    return mean_frequency, math.sqrt(variance)

def compute_inverse_z_scores(lemmatized_data, output_inv_zscore):
    word_counter = Counter(word for message in lemmatized_data for word in message['lemmatized'])
    mean_freq, std_dev = compute_mean_and_std(word_counter)
    inverse_z_scores = {word: 1 / (1 + abs((count - mean_freq) / std_dev)) for word, count in word_counter.items()}

    with open(output_inv_zscore, 'w', encoding='utf-8') as file:
        for word, count in word_counter.items():
            file.write(f"{word}: {count}, Inverse Z-Score: {inverse_z_scores[word]:.4f}\n")
    return inverse_z_scores

def process_z_scores(input_path, inv_zscore_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        lemmatized_data = json.load(file)
    compute_inverse_z_scores(lemmatized_data, inv_zscore_path)

if __name__ == "__main__":
    input_path = 'data/lemmatized_output.json'
    inv_zscore_path = 'data/word_inverse_zscore.txt'
    
    process_z_scores(input_path, inv_zscore_path)
    print(f"Word Inverse Z-scores have been saved to {inv_zscore_path}.")
