"""Sequential processing implementation."""


def run_sequential(data: list[int]) -> list[int]:
    """Process tasks sequentially."""
    return [value * value for value in data]
