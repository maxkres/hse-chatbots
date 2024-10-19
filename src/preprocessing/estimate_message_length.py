import json
import os
from collections import defaultdict

PROCESSED_DATA_DIR = "data/processed/"
OUTPUT_MATRIX_FILE = "message_length_matrix.txt"

MAX_MESSAGE_LENGTH = 20

def load_user_data(user_id):
    file_path = os.path.join(PROCESSED_DATA_DIR, f"{user_id}_processed.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def categorize_message_length(length):
    return min(length, MAX_MESSAGE_LENGTH)

def build_transition_matrix(user_data):
    transition_matrix = [[0 for _ in range(MAX_MESSAGE_LENGTH + 1)] for _ in range(MAX_MESSAGE_LENGTH + 1)]

    message_lengths = [categorize_message_length(len(message)) for message in user_data]

    for i in range(len(message_lengths) - 1):
        current_length = message_lengths[i]
        next_length = message_lengths[i + 1]
        transition_matrix[current_length][next_length] += 1

    return transition_matrix

def calculate_probabilities(transition_matrix):
    probability_matrix = []

    for row in transition_matrix:
        row_sum = sum(row)
        if row_sum > 0:
            probability_row = [count / row_sum for count in row]
        else:
            probability_row = [0 for _ in row]
        probability_matrix.append(probability_row)

    return probability_matrix

def save_matrix_to_file(user_id, matrix, file):
    file.write(f"Message Length Transition Matrix for User: {user_id}\n")
    file.write("Current Length \\ Next Length:\n")
    for i, row in enumerate(matrix):
        file.write(f"Length {i}: {row}\n")
    file.write("\n")

def get_probability_for_transition(probability_matrix, current_length, next_length):
    if current_length <= MAX_MESSAGE_LENGTH and next_length <= MAX_MESSAGE_LENGTH:
        return probability_matrix[current_length][next_length]
    return 0

if __name__ == "__main__":
    top_users = ['user6060256091', 'user1948911068', 'user5564229156', 'user1485427289', 'user629116733']

    first_user_id = top_users[0]
    user_data = load_user_data(first_user_id)

    transition_matrix = build_transition_matrix(user_data)
    probability_matrix = calculate_probabilities(transition_matrix)

    with open(OUTPUT_MATRIX_FILE, 'w', encoding='utf-8') as file:
        save_matrix_to_file(first_user_id, probability_matrix, file)

    print(f"Message length transition matrix saved to {OUTPUT_MATRIX_FILE}.")

    while True:
        try:
            current_length = int(input("Enter the current message length (0-20): "))
            next_length = int(input("Enter the expected next message length (0-20): "))

            probability = get_probability_for_transition(probability_matrix, current_length, next_length)
            print(f"Probability of transitioning from length {current_length} to length {next_length}: {probability:.4f}")
        
        except ValueError:
            print("Invalid input. Please enter integers between 0 and 20.")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
