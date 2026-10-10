import time
import math

def run_sequential(data):
    "Process the dataset sequentially on a single thread."
    start_time = time.time()
    
    if not data:
        return {"total": 0, "average": 0, "min": 0, "max": 0, "even": 0, "odd": 0, "time": 0}

    total = 0
    min_val = float('inf')
    max_val = float('-inf')
    even = 0
    odd = 0
    
    # Process each number one by one
    for x in data:
        _ = math.factorial(15) 
        
        total += x
        if x < min_val: min_val = x
        if x > max_val: max_val = x
        if x % 2 == 0: even += 1
        else: odd += 1
        
    avg = total / len(data)
    end_time = time.time()

    return {
        "total": total,
        "average": avg,
        "min": min_val if min_val != float('inf') else 0,
        "max": max_val if max_val != float('-inf') else 0,
        "even": even,
        "odd": odd,
        "time": end_time - start_time
    }