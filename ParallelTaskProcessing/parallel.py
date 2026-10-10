import time
import math
import multiprocessing as mp

def process_chunk(chunk):

    if not chunk:
        return 0, 0, float('inf'), float('-inf'), 0, 0
        
    total = 0
    min_val = float('inf')
    max_val = float('-inf')
    even = 0
    odd = 0
    
    for x in chunk:
        
        _ = math.factorial(15)
        
        total += x
        if x < min_val: min_val = x
        if x > max_val: max_val = x
        if x % 2 == 0: even += 1
        else: odd += 1
        
    return total, len(chunk), min_val, max_val, even, odd

def run_parallel(data, num_processes):

    start_time = time.time()


    chunk_size = max(1, len(data) // num_processes)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, chunks)


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
        "min": min_val if min_val != float('inf') else 0,
        "max": max_val if max_val != float('-inf') else 0,
        "even": even,
        "odd": odd,
        "time": end_time - start_time
    }