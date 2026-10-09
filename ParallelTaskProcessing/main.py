import multiprocessing as mp
import os
import re
import sys

from data_generator import generate_data
from sequential import run_sequential
from parallel import run_parallel
from performance import run_benchmark, save_csv, save_graph, speedup, verify

# ======================================================================
# PART 1 - INTRODUCTION & SYSTEM DESIGN   (Marvin)
# Screen design, menu, program state, data generation
# ======================================================================
try:
    sys.stdout.reconfigure(encoding="utf-8")      # box characters on Windows
except Exception:
    pass
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
if USE_COLOR and os.name == "nt":
    os.system("")                                  # enable ANSI color code on Windows 10+

BOLD = "\033[1m" if USE_COLOR else ""
GREEN = "\033[92m" if USE_COLOR else ""            # good
RED = "\033[91m" if USE_COLOR else ""              # bad
RESET = "\033[0m" if USE_COLOR else ""

WIDTH = 66
state = {"data": None, "seq": None, "par": None, "processes": mp.cpu_count()}


def pad(text, width, align="left"):
    """Pad text to `width`, ignoring color codes."""
    gap = width - len(re.sub(r"\033\[[0-9;]*m", "", text))
    if align == "right":
        return " " * gap + text
    if align == "center":
        return " " * (gap // 2) + text + " " * (gap - gap // 2)
    return text + " " * gap


def box(lines, double=False, align="left", title=""):
    """Print text inside a border."""
    h, v, corners = ("═", "║", "╔╗╚╝") if double else ("─", "│", "┌┐└┘")
    if isinstance(lines, str):
        lines = [lines]
    top = f"{h} {title} " if title else ""
    print(corners[0] + top + h * (WIDTH - 2 - len(top)) + corners[1])
    for line in lines:
        print(f"{v} {pad(line, WIDTH - 4, align)} {v}")
    print(corners[2] + h * (WIDTH - 2) + corners[3])


def table(headers, rows, widths, aligns):

    def line(l, m, r):
        return l + m.join("─" * (w + 2) for w in widths) + r

    def row(cells, bold=False):
        cells = [f"{BOLD}{c}{RESET}" if bold else c for c in cells]
        return "│" + "│".join(f" {pad(c, w, a)} " for c, w, a in zip(cells, widths, aligns)) + "│"

    print(line("┌", "┬", "┐"))
    print(row(headers, bold=True))
    print(line("├", "┼", "┤"))
    for i, r in enumerate(rows):
        print(row(r, bold=(i == len(rows) - 1)))
    print(line("└", "┴", "┘"))


def bar(value, maximum, color, width=28):
    filled = max(1, round(width * value / maximum)) if maximum > 0 else 0
    return f"{color}{'█' * filled}{RESET}{'░' * (width - filled)}"


def good(msg):
    print(f"\n {GREEN}[OK]{RESET} {msg}")


def bad(msg):
    print(f"\n {RED}[ERROR]{RESET} {msg}")


def section(name):
    print()
    box(f"{BOLD}{name}{RESET}", align="center")


def ask_int(prompt, default, low=1, high=10_000_000):
    raw = input(f" {prompt} [{default:,}]: ").strip().replace(",", "")
    if raw == "":
        return default
    if raw.isdigit() and low <= int(raw) <= high:
        return int(raw)
    bad(f"Enter a number from {low:,} to {high:,}. Using {default:,}.")
    return default


def need_data():
    if state["data"] is None:
        bad("No data yet. Choose [1] Generate Data first.")
        return False
    return True


def show_menu():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")
    box(f"{BOLD}METRO BUSINESS COLLEGE{RESET}", double=True, align="center")
    box([f"{BOLD}PARALLEL TASK PROCESSING SYSTEM{RESET}",
         "Divide the Work. Process in Parallel. Measure the Performance."],
        double=True, align="center")
    d = state["data"]
    box([f"Dataset    : {GREEN + format(len(d), ',') + ' numbers' + RESET if d else RED + 'not generated' + RESET}",
         f"Processes  : {state['processes']}  (this PC has {mp.cpu_count()} cores)",
         f"Sequential : {GREEN + 'done' + RESET if state['seq'] else 'pending'}"
         f"     Parallel : {GREEN + 'done' + RESET if state['par'] else 'pending'}"],
        title="STATUS")
    box(["[1]  Generate Data", "[2]  Sequential Processing", "[3]  Parallel Processing",
         "[4]  Performance Comparison", "[5]  Display Results",
         "[6]  Run Dataset Tests  (CSV + Graph)", "[0]  Exit"], title="MAIN MENU")


def generate():
    section("GENERATE DATA")
    size = ask_int("\n Number of data", 100_000)
    state["data"] = generate_data(size)
    state["seq"] = state["par"] = None
    good(f"Data successfully generated! ({size:,} numbers)")


# ======================================================================
# PART 2 - SEQUENTIAL PROCESSING   (Member 2)
# ======================================================================
def show_result(r, parallel=False):
    rows = []
    if parallel:
        rows += [["Processes Used", str(r["processes"])],
                 ["Chunk Sizes", ", ".join(f"{c:,}" for c in r["chunk_sizes"][:4])
                  + (" ..." if len(r["chunk_sizes"]) > 4 else "")]]
    rows += [["Total", f"{r['total']:,}"], ["Average", f"{r['average']:.2f}"],
             ["Minimum", str(r["min"])], ["Maximum", str(r["max"])],
             ["Even Numbers", f"{r['even']:,}"], ["Odd Numbers", f"{r['odd']:,}"],
             ["Execution Time", f"{r['time']:.4f} seconds"]]
    table(["Metric", "Value"], rows, [22, 37], ["left", "right"])


def sequential():
    if not need_data():
        return
    section("SEQUENTIAL PROCESSING")
    print()
    state["seq"] = run_sequential(state["data"])
    show_result(state["seq"])


# ======================================================================
# PART 3 - PARALLEL PROCESSING   (Member 3)
# ======================================================================
def parallel():
    if not need_data():
        return
    section("PARALLEL PROCESSING")
    state["processes"] = ask_int("\n Number of processes", state["processes"], 1, 64)
    print()
    state["par"] = run_parallel(state["data"], state["processes"])
    show_result(state["par"], parallel=True)


# ======================================================================
# PART 4 - PERFORMANCE ANALYSIS   (Member 4)
# Comparison, saved results, dataset tests, CSV and graph
# ======================================================================
def compare():
    if not need_data():
        return
    if state["seq"] is None:
        state["seq"] = run_sequential(state["data"])
    if state["par"] is None:
        state["par"] = run_parallel(state["data"], state["processes"])
    s, p = state["seq"], state["par"]

    section("PERFORMANCE COMPARISON")
    print()
    table(["Metric", "Sequential", "Parallel"],
          [["Total", f"{s['total']:,}", f"{p['total']:,}"],
           ["Average", f"{s['average']:.2f}", f"{p['average']:.2f}"],
           ["Minimum / Maximum", f"{s['min']} / {s['max']}", f"{p['min']} / {p['max']}"],
           ["Even Numbers", f"{s['even']:,}", f"{p['even']:,}"],
           ["Odd Numbers", f"{s['odd']:,}", f"{p['odd']:,}"],
           ["Processes", "1", str(p["processes"])],
           ["Execution Time", f"{s['time']:.4f} s", f"{p['time']:.4f} s"]],
          [22, 17, 17], ["left", "right", "right"])

    faster = p["time"] < s["time"]
    top = max(s["time"], p["time"])
    print(f"\n  Sequential {bar(s['time'], top, RED if faster else GREEN)} {s['time']:.4f} s")
    print(f"  Parallel   {bar(p['time'], top, GREEN if faster else RED)} {p['time']:.4f} s\n")

    color = GREEN if faster else RED
    message = ["Parallel processing was faster for this workload."] if faster else [
        "Sequential was faster for this workload: the overhead of",
        "creating processes and moving data cost more than it saved."]
    box([f"{color}{BOLD}Speed Improvement: {speedup(s['time'], p['time']):.2f}x{RESET}"]
        + [color + m + RESET for m in message], align="center", title="VERDICT")
    if verify(s, p):
        good("Results match: both methods produced identical answers.")
    else:
        bad("Results DO NOT match - check the code!")


def display():
    if state["seq"] is None and state["par"] is None:
        bad("Nothing to display yet. Run a processing option first.")
        return
    if state["seq"]:
        section("SEQUENTIAL PROCESSING")
        print()
        show_result(state["seq"])
    if state["par"]:
        section("PARALLEL PROCESSING")
        print()
        show_result(state["par"], parallel=True)


def benchmark():
    section("DATASET TESTING")
    state["processes"] = ask_int("\n Number of processes", state["processes"], 1, 64)
    print("\n Running 5 tests...\n")

    def progress(i, n, r):
        color = GREEN if r["speedup"] > 1 else RED
        print(f"  Test {i}/{n}  {r['dataset']:>9,} numbers  {color}{r['speedup']:.2f}x{RESET}")

    rows = run_benchmark(state["processes"], progress=progress)
    print()
    table(["Test", "Dataset", "Sequential", "Parallel", "Speedup", "Faster"],
          [[str(i), f"{r['dataset']:,}", f"{r['sequential']:.4f} s", f"{r['parallel']:.4f} s",
            f"{GREEN if r['speedup'] > 1 else RED}{r['speedup']:.2f}x{RESET}",
            f"{GREEN}Parallel{RESET}" if r["parallel"] < r["sequential"] else f"{RED}Sequential{RESET}"]
           for i, r in enumerate(rows, 1)],
          [4, 9, 10, 10, 7, 10], ["center", "right", "right", "right", "right", "left"])

    top = max(max(r["sequential"], r["parallel"]) for r in rows)
    print(f"\n  Time per test:  {GREEN}green{RESET} = faster   {RED}red{RESET} = slower\n")
    for r in rows:
        seq_faster = r["sequential"] < r["parallel"]
        print(f"  {r['dataset']:>9,}  Seq {bar(r['sequential'], top, GREEN if seq_faster else RED, 32)}")
        print(f"  {r['dataset']:>9,}  Par {bar(r['parallel'], top, RED if seq_faster else GREEN, 32)}")

    if not all(r["correct"] for r in rows):
        bad("Some tests produced mismatched results!")
    good(f"CSV saved   : {save_csv(rows)}")
    graph = save_graph(rows, state["processes"])
    if graph:
        good(f"Graph saved : {graph}")
    else:
        bad("Graph skipped. Install matplotlib:  pip install matplotlib")


# ======================================================================
#                            MAIN PROGRAM
# ======================================================================
ACTIONS = {"1": generate, "2": sequential, "3": parallel,
           "4": compare, "5": display, "6": benchmark}


def main():
    while True:
        show_menu()
        choice = input("\n Enter your choice: ").strip()
        if choice == "0":
            print()
            box([f"{BOLD}PROGRAM COMPLETED{RESET}", "Thank you for using the system."],
                double=True, align="center")
            break
        if choice in ACTIONS:
            ACTIONS[choice]()
        else:
            bad("Invalid choice. Please enter a number from the menu.")
        input("\n Press Enter to return to the menu...")


if __name__ == "__main__":
    mp.freeze_support()
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n Program interrupted. Goodbye!")
