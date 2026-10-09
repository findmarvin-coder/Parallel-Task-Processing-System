import multiprocessing as mp
import os
import sys

from data_generator import generate_data
from sequential import run_sequential
from parallel import run_parallel
from performance import run_benchmark, save_csv, save_graph, speedup, verify

# ======================================================================
# PART 1 - INTRODUCTION & SYSTEM DESIGN   (Marvin)
# Screen design, menu, program state, data generation
# ======================================================================
COLOR = sys.stdout.isatty()
if COLOR and os.name == "nt":
    os.system("")                                  # enable colors on Windows
GREEN, RED, RESET = ("\033[92m", "\033[91m", "\033[0m") if COLOR else ("", "", "")

state = {"data": None, "seq": None, "par": None, "processes": mp.cpu_count()}


def clear():
    if COLOR:
        os.system("cls" if os.name == "nt" else "clear")


def banner(text, line="="):
    """Centered banner between two lines."""
    print(f"{line * 40}\n{text.center(40).rstrip()}\n{line * 40}")


def paint(text, ok):
    return f"{GREEN if ok else RED}{text}{RESET}"


def ask_int(prompt, default, high=10_000_000):
    raw = input(f"{prompt} [{default:,}]: ").replace(",", "").strip()
    if raw.isdigit() and 0 < int(raw) <= high:
        return int(raw)
    if raw:
        print(paint(f"Invalid number. Using {default:,}.", False))
    return default


def has_data():
    if state["data"] is None:
        print(paint("No data yet. Choose [1] Generate Data first.", False))
    return state["data"] is not None


def show_menu():
    banner("PARALLEL TASK PROCESSING SYSTEM")
    print("[1] Generate Data\n[2] Sequential Processing\n[3] Parallel Processing")
    print("[4] Performance Comparison\n[5] Display Results\n[6] Exit")


def generate():
    banner("PARALLEL TASK PROCESSING SYSTEM")
    size = ask_int("Number of data", 100_000)
    print(f"Generating {size:,} numbers...")
    state["data"] = generate_data(size)
    state["seq"] = state["par"] = None
    print(paint("Data successfully generated!", True))


# ======================================================================
# PART 2 - SEQUENTIAL PROCESSING   (Member 2)
# ======================================================================
def show_result(r, parallel=False):
    if parallel:
        print(f"Number of Processes: {r['processes']}\n")
    print(f"Total: {r['total']:,}\nAverage: {r['average']:.2f}")
    print(f"Minimum: {r['min']}\nMaximum: {r['max']}\n")
    print(f"Even Numbers: {r['even']:,}\nOdd Numbers: {r['odd']:,}\n")
    print(f"Execution Time: {r['time']:.4f} seconds")


def sequential():
    if has_data():
        banner("SEQUENTIAL PROCESSING", "-")
        state["seq"] = run_sequential(state["data"])
        show_result(state["seq"])


# ======================================================================
# PART 3 - PARALLEL PROCESSING   (Member 3)
# ======================================================================
def parallel():
    if has_data():
        state["processes"] = ask_int("Number of processes", state["processes"], 64)
        banner("PARALLEL PROCESSING", "-")
        state["par"] = run_parallel(state["data"], state["processes"])
        show_result(state["par"], parallel=True)


# ======================================================================
# PART 4 - PERFORMANCE ANALYSIS   (Faye)
# Comparison, display results, dataset tests, CSV and graph
# ======================================================================
def compare():
    if not has_data():
        return
    state["seq"] = state["seq"] or run_sequential(state["data"])
    state["par"] = state["par"] or run_parallel(state["data"], state["processes"])
    s, p = state["seq"], state["par"]
    faster = p["time"] < s["time"]

    banner("PERFORMANCE COMPARISON", "-")
    print(f"Sequential Time : {s['time']:.4f} seconds")
    print(f"Parallel Time   : {p['time']:.4f} seconds\n")
    gain = f"{speedup(s['time'], p['time']):.2f}x"
    print(f"Speed Improvement: {paint(gain, faster)}\n")
    print(paint("Parallel processing was faster\nfor this workload." if faster else
                "Sequential processing was faster\nfor this workload.", faster))
    print("\nResults match:", paint("YES" if verify(s, p) else "NO", verify(s, p)))

    if input("\nRun the 5 dataset tests (CSV + graph)? (y/n): ").lower() == "y":
        benchmark()


def display():
    if not (state["seq"] or state["par"]):
        print(paint("Nothing to display yet. Run a processing option first.", False))
    if state["seq"]:
        banner("SEQUENTIAL PROCESSING", "-")
        show_result(state["seq"])
        print()
    if state["par"]:
        banner("PARALLEL PROCESSING", "-")
        show_result(state["par"], parallel=True)


def benchmark():
    clear()
    banner("DATASET TESTING", "-")
    print(f"Number of Processes: {state['processes']}\n")
    rows = run_benchmark(state["processes"])
    print(f"{'Dataset':>10}  {'Sequential':>12}  {'Parallel':>12}  {'Speedup':>8}")
    for r in rows:
        print(f"{r['dataset']:>10,}  {r['sequential']:>9.4f} sec  {r['parallel']:>9.4f} sec  "
              + paint(f"{r['speedup']:.2f}x".rjust(8), r["speedup"] > 1))
    if not all(r["correct"] for r in rows):
        print(paint("\nSome tests produced mismatched results!", False))
    print(f"\nCSV saved   : {save_csv(rows)}")
    graph = save_graph(rows, state["processes"])
    print(f"Graph saved : {graph}" if graph else paint("Graph skipped (pip install matplotlib)", False))


# ======================================================================
#                            MAIN PROGRAM
# ======================================================================
ACTIONS = {"1": generate, "2": sequential, "3": parallel, "4": compare, "5": display}


def main():
    while True:
        clear()
        show_menu()
        choice = input("Enter your choice: ").strip()
        if choice == "6":
            clear()
            banner("PROGRAM COMPLETED")
            break
        clear()
        if choice in ACTIONS:
            ACTIONS[choice]()
        else:
            print(paint("Invalid choice. Please enter 1-6.", False))
        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    mp.freeze_support()
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted. Goodbye!")
