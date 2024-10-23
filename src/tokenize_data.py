import json
import re

def attach_floating_punctuation(text):
    return re.sub(r'\s([,;.!?])\s', r'\1 ', text)

def extract_links(message_text):
    url_pattern = r'(https?://[^\s]+)'
    return re.findall(url_pattern, message_text)

def tokenize_with_regex(message_text):
    message_text = attach_floating_punctuation(message_text)
    links = extract_links(message_text)

    for i, link in enumerate(links):
        message_text = message_text.replace(link, f"__LINK_{i}__")

    pattern = r"@[\wА-Яа-яёЁ-]+|[«»“”‘’„”“]?[\wА-Яа-яёЁ-]+[^\s\wА-Яа-яёЁ]*[«»“”‘’„”“]?"
    lines = message_text.split('\n')
    tokenized_with_tags = []

    for line in lines:
        tokens = re.findall(pattern, line)
        if tokens:
            tokenized_with_tags.append("__START__")
        
        for i, token in enumerate(tokens):
            tokenized_with_tags.append(token)
            if token.endswith('.') or i == len(tokens) - 1:
                tokenized_with_tags.append("__END__")
                if i != len(tokens) - 1:
                    tokenized_with_tags.append("__START__")
    for i, link in enumerate(links):
        tokenized_with_tags = [token.replace(f"__LINK_{i}__", link) for token in tokenized_with_tags]
    return tokenized_with_tags

def process_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for message in data:
        message['tokenized'] = tokenize_with_regex(message['text'])

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    input_path = 'data/merged/merged.json'
    output_path = 'data/tokenized_output.json'
    
    process_json(input_path, output_path)
    print(f"Tokenized data has been saved to {output_path}.")
