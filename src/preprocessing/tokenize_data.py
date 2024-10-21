import json
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import pymorphy3
import os
from itertools import islice

nltk.download('punkt')
nltk.download('stopwords')

morph = pymorphy3.MorphAnalyzer()
russian_stopwords = set(stopwords.words('russian'))
russian_stopwords.add('это')

def read_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

def extract_text(message):
    if isinstance(message.get('text'), str):
        return message['text']
    if 'text_entities' in message:
        return ' '.join([entity['text'] for entity in message['text_entities']])
    return ''

def preprocess_text_for_sentence_detection(text):
    processed_text = re.sub(r"\)+", ".", text)
    processed_text = processed_text.replace('\n', '.')
    return processed_text

def tokenize_message_with_regex(message_text):
    pattern = r"\([^)]+\)|[«»“”‘’„”“]?[\wА-Яа-яёЁ-]+[^\s\wА-Яа-яёЁ]*[«»“”‘’„”“]?"
    return re.findall(pattern, message_text)

def lemmatize_and_remove_stopwords(tokens):
    lemmatized_tokens = []
    for token in tokens:
        if token.lower() not in russian_stopwords and re.match(r"^\w+$", token) and not token.isdigit():
            lemma = morph.parse(token)[0].normal_form
            lemmatized_tokens.append(lemma)
    return lemmatized_tokens

def generate_ngrams(tokens, n):
    return zip(*(islice(tokens, i, None) for i in range(n)))

def process_messages(data):
    tokenized_data_by_user = {}
    lemmatized_data_by_user = {}
    bigrams_by_user = {}
    trigrams_by_user = {}

    for message in data:
        text = extract_text(message)
        message_id = message.get('id')
        from_id = message.get('from_id')

        if text:
            processed_text = preprocess_text_for_sentence_detection(text)
            sentences = sent_tokenize(processed_text)

            for sentence in sentences:
                original_sentence = text[:len(sentence)].strip()
                text = text[len(sentence):].strip()

                tokenized_message = tokenize_message_with_regex(original_sentence)
                if tokenized_message:
                    tokenized_message_with_markers = ["__START__"] + tokenized_message + ["__END__"]
                    if from_id not in tokenized_data_by_user:
                        tokenized_data_by_user[from_id] = []
                    tokenized_data_by_user[from_id].append({
                        'message_id': message_id,
                        'tokens': tokenized_message_with_markers
                    })

                    lemmatized_message = lemmatize_and_remove_stopwords(tokenized_message)
                    if lemmatized_message:
                        if from_id not in lemmatized_data_by_user:
                            lemmatized_data_by_user[from_id] = []
                        lemmatized_data_by_user[from_id].append({
                            'message_id': message_id,
                            'tokens': lemmatized_message
                        })
                    
                    bigrams = list(generate_ngrams(tokenized_message, 2))
                    trigrams = list(generate_ngrams(tokenized_message, 3))
                    
                    if from_id not in bigrams_by_user:
                        bigrams_by_user[from_id] = []
                    bigrams_by_user[from_id].append({
                        'message_id': message_id,
                        'bigrams': bigrams
                    })
                    
                    if from_id not in trigrams_by_user:
                        trigrams_by_user[from_id] = []
                    trigrams_by_user[from_id].append({
                        'message_id': message_id,
                        'trigrams': trigrams
                    })
    return tokenized_data_by_user, lemmatized_data_by_user, bigrams_by_user, trigrams_by_user

def write_user_files(data_by_user, output_dir, file_suffix):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for user_id, messages in data_by_user.items():
        output_file = os.path.join(output_dir, f"{user_id}_{file_suffix}.json")
        write_json(output_file, messages)
        print(f"Saved {file_suffix} data for user {user_id} to {output_file}")

if __name__ == "__main__":
    input_file_path = 'data/filtered_chat.json'
    tokenized_output_dir = 'data/tokenized_users'
    lemmatized_output_dir = 'data/lemmatized_users'
    bigrams_output_dir = 'data/bigrams_users'
    trigrams_output_dir = 'data/trigrams_users'

    chat_data = read_json(input_file_path)
    tokenized_data_by_user, lemmatized_data_by_user, bigrams_by_user, trigrams_by_user = process_messages(chat_data)

    write_user_files(tokenized_data_by_user, tokenized_output_dir, "tokenized")
    write_user_files(lemmatized_data_by_user, lemmatized_output_dir, "lemmatized")
    write_user_files(bigrams_by_user, bigrams_output_dir, "bigrams")
    write_user_files(trigrams_by_user, trigrams_output_dir, "trigrams")
