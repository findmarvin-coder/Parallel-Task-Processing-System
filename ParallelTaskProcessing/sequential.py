import time
import math

def run_sequential(data, target=None):
    start_time = time.time()
    
    if not data:
        return {"total": 0, "average": 0, "min": 0, "max": 0, "even": 0, "odd": 0, "found": 0, "time": 0}

    total = 0
    min_val = float('inf')
    max_val = float('-inf')
    even = 0
    odd = 0
    found = 0
    
    # Task 1, 2, and 3: Math, Classification, and Searching
    for x in data:
        _ = math.factorial(15) 
        
        total += x
        if x < min_val: min_val = x
        if x > max_val: max_val = x
        if x % 2 == 0: even += 1
        else: odd += 1
        
        # Searching Task
        if target is None or x == target: 
            found += 1
            
    avg = total / len(data)
    
    # Task 4: Sorting
    sorted_data = sorted(data)

    end_time = time.time()

    return {
        "total": total,
        "average": avg,
        "min": min_val if min_val != float('inf') else 0,
        "max": max_val if max_val != float('-inf') else 0,
        "even": even,
        "odd": odd,
        "found": found,
        "time": end_time - start_time
    }