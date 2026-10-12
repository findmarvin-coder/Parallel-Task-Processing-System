import time
import math
import multiprocessing as mp
import heapq

def process_chunk(args):
    """Task assigned to a single worker process."""
    chunk, target = args
    if not chunk:
        return 0, 0, float('inf'), float('-inf'), 0, 0, 0, []
        
    total = 0
    min_val = float('inf')
    max_val = float('-inf')
    even = 0
    odd = 0
    found = 0
    
    for x in chunk:
        _ = math.factorial(15)
        
        total += x
        if x < min_val: min_val = x
        if x > max_val: max_val = x
        if x % 2 == 0: even += 1
        else: odd += 1
        
        # Searching Task
        if target is not None and x == target:
            found += 1
            
    # Sorting Task, the worker sorts just its own small chunk
    sorted_chunk = sorted(chunk)
        
    return total, len(chunk), min_val, max_val, even, odd, found, sorted_chunk

def run_parallel(data, num_processes, target=None):

    start_time = time.time()

    # Divide dataset into equal chunks for each process
    chunk_size = max(1, len(data) // num_processes)
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Package the target number with each chunk so the worker knows what to look for
    args = [(chunk, target) for chunk in chunks]

    # Run processes in parallel
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, args)


    total = sum(r[0] for r in results)
    count = sum(r[1] for r in results)
    avg = total / count if count else 0
    min_val = min((r[2] for r in results), default=0)
    max_val = max((r[3] for r in results), default=0)
    even = sum(r[4] for r in results)
    odd = sum(r[5] for r in results)
    found = sum(r[6] for r in results)
    
    # For Additional Task 4: Merge the pre-sorted chunks together rapidly
    sorted_chunks = [r[7] for r in results]
    final_sorted_data = list(heapq.merge(*sorted_chunks))

    end_time = time.time()

    return {
        "processes": num_processes,
        "total": total,
        "average": avg,
        "min": min_val if min_val != float('inf') else 0,
        "max": max_val if max_val != float('-inf') else 0,
        "even": even,
        "odd": odd,
        "found": found,
        "time": end_time - start_time
    }