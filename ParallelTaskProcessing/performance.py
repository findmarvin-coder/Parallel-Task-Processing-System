import os
import csv
from data_generator import generate_data
from sequential import run_sequential
from parallel import run_parallel

def speedup(seq_time, par_time):
    
    if par_time <= 0: return 0
    return seq_time / par_time

def verify(seq_result, par_result):
    keys = ["total", "even", "odd", "min", "max"]
    for k in keys:
        if seq_result[k] != par_result[k]:
            return False

    if abs(seq_result["average"] - par_result["average"]) > 0.01:
        return False
    return True

def run_benchmark(processes):
    
    sizes = [10_000, 50_000, 100_000, 500_000, 1_000_000]
    rows = []
    
    for size in sizes:
        data = generate_data(size)
        seq_res = run_sequential(data)
        par_res = run_parallel(data, processes)
        
        rows.append({
            "dataset": size,
            "sequential": seq_res["time"],
            "parallel": par_res["time"],
            "speedup": speedup(seq_res["time"], par_res["time"]),
            "correct": verify(seq_res, par_res)
        })
    return rows

def save_csv(rows, folder="results"):
    """Save the benchmark results to a CSV file."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "performance_results.csv")
    
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Dataset Size", "Sequential Time (s)", "Parallel Time (s)", "Speedup"])
        for r in rows:
            writer.writerow([r["dataset"], f"{r['sequential']:.4f}", f"{r['parallel']:.4f}", f"{r['speedup']:.2f}x"])
            
    return filepath

def save_graph(rows, processes, folder="results"):

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None  # Return None if user hasn't installed matplotlib
        
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, "performance_graph.png")
    
    datasets = [f"{r['dataset']:,}" for r in rows]
    seq_times = [r["sequential"] for r in rows]
    par_times = [r["parallel"] for r in rows]
    
    plt.figure(figsize=(10, 6))
    plt.plot(datasets, seq_times, marker='o', label='Sequential', color='red')
    plt.plot(datasets, par_times, marker='o', label=f'Parallel ({processes} processes)', color='green')
    
    plt.title("Sequential vs Parallel Processing Performance")
    plt.xlabel("Dataset Size")
    plt.ylabel("Execution Time (seconds)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.savefig(filepath)
    plt.close()
    
    return filepath