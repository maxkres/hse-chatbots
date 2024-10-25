import json


def find_similar_messages(
    lemmatized_data,
    test_message,
    inverse_z_scores,
    specific_user_id,
    min_messages=5,
    max_messages=10
):
    test_message_set = set(test_message)
    message_scores = []

    for message in lemmatized_data:
        if message['user_id'] != specific_user_id:
            continue
        common_words = test_message_set.intersection(message['lemmatized'])
        if common_words:
            avg_inv_zscore = (
                sum(inverse_z_scores[word] for word in common_words)
                / len(common_words)
            )
            message_scores.append((avg_inv_zscore, message['message_id']))

    if not message_scores:
        print(f"No messages found for user {specific_user_id} with common words.")
        return []

    message_scores.sort(reverse=True)
    selected_messages = [
        msg_id for score, msg_id in message_scores[:max_messages]
    ]
    print(f"Selected message IDs from user {specific_user_id}: {selected_messages}")
    return selected_messages


def process_similarity(
    test_message,
    specific_user_id,
    min_messages=5,
    max_messages=10
):
    input_path = 'data/lemmatized_output.json'
    inv_zscore_path = 'data/word_inverse_zscore.txt'
    print(test_message, specific_user_id)

    with open(input_path, 'r', encoding='utf-8') as file:
        lemmatized_data = json.load(file)

    with open(inv_zscore_path, 'r', encoding='utf-8') as file:
        inverse_z_scores = {
            line.split(': ')[0]: float(line.split(': ')[2].strip())
            for line in file.readlines()
        }

    message_ids = find_similar_messages(
        lemmatized_data,
        test_message,
        inverse_z_scores,
        specific_user_id,
        min_messages,
        max_messages
    )
    return message_ids


if __name__ == "__main__":
    test_message = ['гордей', 'опубликовать', 'инфа', 'объявление']
    specific_user_id = 'user726029390'
    process_similarity(test_message, specific_user_id)
