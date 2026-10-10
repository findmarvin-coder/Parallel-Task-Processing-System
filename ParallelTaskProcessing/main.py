import multiprocessing as mp
import os
import re
import sys
import time

from data_generator import generate_data
from sequential import run_sequential
from parallel import run_parallel
from performance import run_benchmark, save_csv, save_graph, speedup, verify

# PART 1 - Marvin

COLOR = sys.stdout.isatty()
if COLOR and os.name == "nt":
    os.system("")

GREEN, RED, RESET = ("\033[92m", "\033[91m", "\033[0m") if COLOR else ("", "", "")
WIDTH = 56

state = {
    "data": None, 
    "seq": None, 
    "par": None, 
    "processes": mp.cpu_count()
}

def clear():

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

def tprint(text, speed=0.01, end="\n"):
    "Typewriter print effect for specific lines."
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(end)
    sys.stdout.flush()

def paint(text, ok):
    return f"{GREEN if ok else RED}{text}{RESET}"

def screen(title, lines=None, typewrite=False):
    if lines is None:
        lines = []
    
    inner = WIDTH - 2
    print("┌" + "─" * inner + "┐")
    print("│" + title.center(inner) + "│")
    
    if lines:
        print("├" + "─" * inner + "┤")
        for line in lines:
            visible_len = len(re.sub(r"\033\[[0-9;]*m", "", line))
            gap = max(0, inner - 2 - visible_len)
            
            if typewrite:
                
                sys.stdout.write("│ ")
                sys.stdout.flush()
                tprint(line, speed=0.01, end="")
                print(" " * gap + " │")
            else:
                print("│ " + line + " " * gap + " │")
            
    print("└" + "─" * inner + "┘")
def ask_int(prompt, default, high=10_000_000):
    raw = input(f"\n{prompt} [{default:,}]: ").replace(",", "").strip()
    
    if raw.isdigit() and 0 < int(raw) <= high:
        return int(raw)
    if raw:
        print(paint(f"Invalid number. Using {default:,}.", False))
    return default

def has_data():
    if state["data"] is None:
        screen("NOTICE", [paint("No data yet. Choose [1] Generate Data.", False)])
        return False
    return True

def show_menu():
    # School banner only - MBC
    screen("METRO BUSINESS COLLEGE", ["FINAL PROJECT".center(WIDTH - 4)])
    screen("PARALLEL TASK PROCESSING SYSTEM", [
        "[1] Generate Data", 
        "[2] Sequential Processing", 
        "[3] Parallel Processing",
        "[4] Performance Comparison", 
        "[5] Display Results", 
        "[6] Exit"
    ])

def generate():
    screen("GENERATE DATA")
    size = ask_int("Number of data", 100_000)
    state["data"] = generate_data(size)
    state["seq"] = None
    state["par"] = None
    clear()
    screen("GENERATE DATA", [
        f"Generating {size:,} numbers...", 
        "",
        paint("Data successfully generated!", True)
    ], typewrite=True)

# PART 2 - Cris

def result_lines(r, parallel=False):
    lines = [f"Number of Processes: {r['processes']}", ""] if parallel else []
    return lines + [
        f"Total: {r['total']:,}", 
        f"Average: {r['average']:.2f}",
        f"Minimum: {r['min']}", 
        f"Maximum: {r['max']}", 
        "",
        f"Even Numbers: {r['even']:,}", 
        f"Odd Numbers: {r['odd']:,}", 
        "",
        f"Execution Time: {r['time']:.4f} seconds"
    ]

def sequential():
    if has_data():
        state["seq"] = run_sequential(state["data"])
        clear()
        screen("SEQUENTIAL PROCESSING", result_lines(state["seq"]), typewrite=True)

# PART 3 - Mia

def parallel():
    if has_data():
        screen("PARALLEL PROCESSING")
        state["processes"] = ask_int("Number of processes", state["processes"], 64)
        state["par"] = run_parallel(state["data"], state["processes"])
        clear()
        screen("PARALLEL PROCESSING", result_lines(state["par"], parallel=True), typewrite=True)

# PART 4 - Faye

def compare():
    if not has_data():
        return
        
    state["seq"] = state["seq"] or run_sequential(state["data"])
    state["par"] = state["par"] or run_parallel(state["data"], state["processes"])
    
    s = state["seq"]
    p = state["par"]
    faster = p["time"] < s["time"]
    gain = f"{speedup(s['time'], p['time']):.2f}x"
    match = verify(s, p)

    clear()
    screen("PERFORMANCE COMPARISON", [
        f"Sequential Time : {s['time']:.4f} seconds",
        f"Parallel Time   : {p['time']:.4f} seconds", 
        "",
        f"Speed Improvement: {paint(gain, faster)}", 
        "",
        paint("Parallel processing was faster" if faster else "Sequential processing was faster", faster),
        paint("for this workload.", faster), 
        "",
        "Results match: " + paint("YES" if match else "NO", match)
    ], typewrite=True)

    run_tests = input("\nRun the 5 dataset tests and save to results/? (Y/n): ").lower()
    
    if run_tests != "n":
        benchmark()

def display():
    screen("FINAL PERFORMANCE RESULT")

    if not (state["seq"] or state["par"]):
        screen("NOTICE", [paint("Nothing to display yet.", False)])
    if state["seq"]:
        screen("SEQUENTIAL PROCESSING", result_lines(state["seq"]), typewrite=True)
    if state["par"]:
        screen("PARALLEL PROCESSING", result_lines(state["par"], parallel=True), typewrite=True)

def benchmark():
    clear()
    screen("DATASET TESTING")
    print(f"\nRunning 5 tests with {state['processes']} processes...\n")
    rows = run_benchmark(state["processes"])
    
    clear()
    lines = [
        f"Number of Processes: {state['processes']}", 
        "",
        f"{'Dataset':>10}  {'Sequential':>11}  {'Parallel':>11}  {'Speedup':>7}"
    ]
    
    for r in rows:
        speedup_str = f"{r['speedup']:.2f}x".rjust(7)
        lines.append(f"{r['dataset']:>10,}  {r['sequential']:>8.4f} s  {r['parallel']:>8.4f} s  "
                     + paint(speedup_str, r["speedup"] > 1))
                     
    if not all(r["correct"] for r in rows):
        lines += ["", paint("Some tests produced mismatched results!", False)]
        
    screen("DATASET TESTING", lines, typewrite=True)
    
    print(paint("\nSaved: " + os.path.relpath(save_csv(rows)), True))
    graph = save_graph(rows, state["processes"])
    
    if graph:
        print(paint("Saved: " + os.path.relpath(graph), True))
    else:
        print(paint("Graph not saved. Run: pip install matplotlib", False))


ACTIONS = {
    "1": generate, 
    "2": sequential, 
    "3": parallel, 
    "4": compare, 
    "5": display
}

def main():
    while True:
        clear()
        show_menu()
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "6":
            clear()
            screen("PROGRAM COMPLETED")
            break
            
        clear() 
        if choice in ACTIONS:
            ACTIONS[choice]()
        else:
            screen("NOTICE", [paint("Invalid choice. Please enter 1-6.", False)])
            
        input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    mp.freeze_support()
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted. Goodbye!")