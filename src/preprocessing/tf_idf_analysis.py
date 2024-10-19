import json
import math
from collections import defaultdict

COMBINED_FILE = "data/tokenized/combined_tokenized.json"
OUTPUT_FILE = "data/tokenized/tfidf_output.txt"

def load_combined_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def preprocess_for_tfidf(tokenized_messages):
    documents = [' '.join(tokens) for tokens in tokenized_messages.values()]
    return documents

def compute_tf(document):
    tf = defaultdict(float)
    words = document.split()
    total_words = len(words)
    
    for word in words:
        tf[word] += 1 / total_words
    
    return tf

def compute_idf(documents):
    idf = defaultdict(float)
    total_documents = len(documents)
    document_count = defaultdict(int)

    for document in documents:
        unique_terms = set(document.split())
        for term in unique_terms:
            document_count[term] += 1
    for term, count in document_count.items():
        idf[term] = math.log(total_documents / (1 + count))

    return idf

def compute_tfidf(documents):
    tfidf = []
    idf = compute_idf(documents)

    for document in documents:
        tf = compute_tf(document)
        tfidf_document = {}
        
        for term, tf_value in tf.items():
            tfidf_document[term] = tf_value * idf[term]
        
        tfidf.append(tfidf_document)
    
    return tfidf

def save_tfidf_to_file(tfidf_matrix, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, document_tfidf in enumerate(tfidf_matrix):
            f.write(f"Document {idx + 1}:\n")
            for term, score in document_tfidf.items():
                f.write(f"  {term}: {score:.4f}\n")
            f.write("\n")

if __name__ == "__main__":
    tokenized_data = load_combined_data(COMBINED_FILE)
    tokenized_data_first_100 = tokenized_data
    documents = preprocess_for_tfidf(tokenized_data_first_100)
    tfidf_matrix = compute_tfidf(documents)
    save_tfidf_to_file(tfidf_matrix, OUTPUT_FILE)

    print(f"TF-IDF scores saved to {OUTPUT_FILE}.")
