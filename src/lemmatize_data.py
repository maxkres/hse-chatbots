import json
import nltk
import pymorphy3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')
morph = pymorphy3.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
stop_words.add('это')

def lemmatize_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in filtered_tokens]
    return lemmatized_tokens

def process_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    for message in data:
        message['lemmatized'] = lemmatize_text(message['text'])
        del message['text']

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    input_path = 'data/merged/merged.json'
    output_path = 'data/lemmatized_output.json'
    
    process_json(input_path, output_path)
    print(f"Lemmatized data has been saved to {output_path}.")
