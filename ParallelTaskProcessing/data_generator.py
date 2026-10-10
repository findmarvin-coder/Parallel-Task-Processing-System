import random

def generate_data(size):
    # Generate a list of random integers between 1 and 100.
    return [random.randint(1, 100) for _ in range(size)]