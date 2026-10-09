"""Entry point for the Parallel Task Processing project."""

from sequential import run_sequential
from parallel import run_parallel
from performance import compare_performance


def main() -> None:
    """Run sequential and parallel demos, then compare performance."""
    data = [1, 2, 3, 4, 5]
    sequential_result = run_sequential(data)
    parallel_result = run_parallel(data)
    compare_performance(sequential_result, parallel_result)


if __name__ == "__main__":
    main()
