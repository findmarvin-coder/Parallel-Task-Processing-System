import time
import multiprocessing as mp

def process_chunk(chunk):
    """Task assigned to a single process."""
    if not chunk:
        return 0, 0, float('inf'), float('-inf'), 0, 0
        
    total = sum(chunk)
    min_val = min(chunk)
    max_val = max(chunk)
    even = sum(1 for x in chunk if x % 2 == 0)
    odd = len(chunk) - even
    
    return total, len(chunk), min_val, max_val, even, odd

def run_parallel(data, num_processes):
    """Divide data and process using multiprocessing."""
    start_time = time.time()

    # Divide dataset into equal chunks for each process
    chunk_size = max(1, len(data) // num_processes)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Run processes in parallel
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, chunks)

    # Combine results
    total = sum(r[0] for r in results)
    count = sum(r[1] for r in results)
    avg = total / count if count else 0
    min_val = min((r[2] for r in results), default=0)
    max_val = max((r[3] for r in results), default=0)
    even = sum(r[4] for r in results)
    odd = sum(r[5] for r in results)

    end_time = time.time()

    return {
        "processes": num_processes,
        "total": total,
        "average": avg,
        "min": min_val,
        "max": max_val,
        "even": even,
        "odd": odd,
        "time": end_time - start_time
    }