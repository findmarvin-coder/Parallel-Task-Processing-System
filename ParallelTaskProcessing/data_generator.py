import random

def generate_data(size):
    """Generate a list of random numbers of the given size."""
    # Using numbers 1 to 100 for simplicity and easy math
    return [random.randint(1, 100) for _ in range(size)]