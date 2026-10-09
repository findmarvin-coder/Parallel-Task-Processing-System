"""Performance comparison helpers."""


def compare_performance(sequential_result: list[int], parallel_result: list[int]) -> None:
    """Compare results from sequential and parallel processing."""
    if sequential_result != parallel_result:
        raise ValueError("Sequential and parallel results do not match")
